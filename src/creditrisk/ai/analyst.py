"""
CreditRiskAnalyst RAG & Tool Integration Module.

Integrates local document retriever with Google Gemini (gemini-flash-latest) function calling
to deliver regulatory and quantitative credit risk analysis with strict source attribution.
"""

import logging
import os
from pathlib import Path
from typing import Any, Dict, List, Optional

import google.generativeai as genai
import yaml

from creditrisk.ai.retriever import Retriever
from creditrisk.ai.tools import (
    tool_basel_capital,
    tool_expected_loss,
    tool_ifrs9_ecl,
    tool_score_to_pd,
)

logger = logging.getLogger(__name__)

SYSTEM_INSTRUCTION = (
    "You are a credit risk analyst assistant for a commercial bank. "
    "Answer questions using ONLY the provided regulatory context and the calculation tools. "
    "Cite the exact source document and page for regulatory claims. "
    "If you don't have the context or tools to answer, state that clearly—never invent regulatory text or numbers."
)

TOOL_MAP = {
    "tool_basel_capital": tool_basel_capital,
    "tool_expected_loss": tool_expected_loss,
    "tool_ifrs9_ecl": tool_ifrs9_ecl,
    "tool_score_to_pd": tool_score_to_pd,
}


def load_ai_config(config_path: Path = Path("config/ai.yaml")) -> Dict[str, Any]:
    """Loads AI configuration parameters from YAML file."""
    if config_path.exists():
        try:
            with open(config_path, "r", encoding="utf-8") as f:
                return yaml.safe_load(f) or {}
        except Exception as err:
            logger.warning(f"Failed to read {config_path}: {err}")
    return {}


def list_available_gemini_models() -> List[str]:
    """Queries Google Gemini API for available models supporting content generation.

    Returns:
        List of supported model names.
    """
    supported_models = []
    try:
        models = genai.list_models()
        for m in models:
            if "generateContent" in getattr(m, "supported_generation_methods", []):
                # Format model name (removing 'models/' prefix for user convenience if present)
                name = m.name.replace("models/", "")
                supported_models.append(name)
    except Exception as err:
        logger.error(f"Failed to list Gemini models: {err}")

    return supported_models


class CreditRiskAnalyst:
    """RAG + Tool calling assistant powered by Gemini Flash."""

    def __init__(
        self,
        index_dir: Path = Path("outputs/models/rag_index"),
        model_name: Optional[str] = None,
        api_key: Optional[str] = None,
        config_path: Path = Path("config/ai.yaml")
    ):
        self.retriever = Retriever(index_dir=index_dir)
        
        # Read model name from config/ai.yaml if not explicitly provided
        config = load_ai_config(config_path)
        self.model_name = model_name or config.get("gemini_model", "gemini-flash-latest")

        resolved_key = api_key or os.environ.get("GEMINI_API_KEY")
        if resolved_key:
            genai.configure(api_key=resolved_key)
        else:
            logger.warning("GEMINI_API_KEY is not set in environment.")

        # Register tools with Gemini model
        tools_list = [tool_basel_capital, tool_expected_loss, tool_ifrs9_ecl, tool_score_to_pd]
        self.model = genai.GenerativeModel(
            model_name=self.model_name,
            system_instruction=SYSTEM_INSTRUCTION,
            tools=tools_list
        )

    def ask(self, question: str) -> Dict[str, Any]:
        """Answers user question using RAG context retrieval and quantitative calculation tools.

        Args:
            question: User inquiry string.

        Returns:
            Dict containing answer, source document citations, and max score.
        """
        # 1. Retrieve top-5 chunks from RAG index
        retrieved_chunks = self.retriever.search(question, k=5)

        # 2. Guardrail check: max retrieval score threshold
        max_score = max([c["score"] for c in retrieved_chunks]) if retrieved_chunks else 0.0
        if max_score < 0.30:
            return {
                "answer": (
                    "The knowledge base does not contain sufficient regulatory context "
                    "to answer this question (retrieval relevance score below threshold)."
                ),
                "sources": [],
                "max_score": round(max_score, 4),
            }

        # 3. Format retrieved passages for prompt context
        context_blocks = []
        sources = []

        for chunk in retrieved_chunks:
            src = chunk["source"]
            pg = chunk["page"]
            sources.append({"source": src, "page": pg, "score": round(chunk["score"], 4)})
            context_blocks.append(f"--- Document: {src} (Page {pg}) ---\n{chunk['text']}")

        context_str = "\n\n".join(context_blocks)
        full_prompt = f"RETRIEVED REGULATORY CONTEXT:\n{context_str}\n\nUSER QUESTION: {question}"

        # 4. Invoke Gemini with context and function tools
        try:
            chat = self.model.start_chat(enable_automatic_function_calling=True)
            response = chat.send_message(full_prompt)
            answer_text = response.text
        except Exception as exc:
            err_msg = str(exc)
            logger.error(f"Gemini API invocation error: {err_msg}")
            
            # Check for 404 / Model Not Found error
            if "404" in err_msg or "not found" in err_msg.lower():
                available = list_available_gemini_models()
                avail_str = "\n".join([f"  - {m}" for m in available]) if available else "  (Could not fetch models list)"
                answer_text = (
                    f"API Error 404: Model '{self.model_name}' was not found or is deprecated.\n\n"
                    f"Available models supporting content generation:\n{avail_str}\n\n"
                    f"Please update gemini_model in 'config/ai.yaml' with one of the available models above."
                )
            else:
                answer_text = f"API Error: {exc}"

        return {
            "answer": answer_text,
            "sources": sources,
            "max_score": round(max_score, 4),
        }
