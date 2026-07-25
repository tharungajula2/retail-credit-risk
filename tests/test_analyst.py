"""
Unit tests for AI Credit Risk Analyst tools, retriever integration, and mocked Gemini calls.
"""

from unittest.mock import MagicMock, patch
import pytest

from creditrisk.ai.analyst import CreditRiskAnalyst
from creditrisk.ai.tools import (
    tool_basel_capital,
    tool_expected_loss,
    tool_ifrs9_ecl,
    tool_score_to_pd,
)


def test_tool_expected_loss():
    # tool_expected_loss(0.03, 0.9, 10000) == 270.0
    res = tool_expected_loss(0.03, 0.9, 10000.0)
    assert res["expected_loss_usd"] == 270.0


def test_tool_basel_capital():
    res = tool_basel_capital(0.03, 0.45, 100000.0)
    assert "capital_requirement_k" in res
    assert "risk_weight_pct" in res
    assert "rwa_usd" in res
    assert res["rwa_usd"] > 0.0


def test_tool_ifrs9_ecl():
    res_stg1 = tool_ifrs9_ecl(0.02, 0.08, 0.5, 10000.0, stage=1)
    assert res_stg1["ecl_usd"] == 100.0

    res_stg2 = tool_ifrs9_ecl(0.02, 0.08, 0.5, 10000.0, stage=2)
    assert res_stg2["ecl_usd"] == 400.0

    res_stg3 = tool_ifrs9_ecl(0.02, 0.08, 0.5, 10000.0, stage=3)
    assert res_stg3["ecl_usd"] == 5000.0


def test_tool_score_to_pd():
    # Test valid score in Grade 1 range (614-639)
    res = tool_score_to_pd(620)
    assert res["grade"] == "1"
    assert "observed_default_rate" in res


@patch("creditrisk.ai.analyst.genai.GenerativeModel")
def test_analyst_guardrail_low_score(mock_model_cls):
    analyst = CreditRiskAnalyst(api_key="mock-key")

    # Mock retriever search to return low relevance scores (< 0.30)
    analyst.retriever.search = MagicMock(return_value=[
        {"chunk_id": "c1", "source": "doc.pdf", "page": 1, "text": "irrelevant", "score": 0.15}
    ])

    result = analyst.ask("What is the capital requirement for obscure assets?")
    assert "does not contain sufficient regulatory context" in result["answer"]
    assert result["sources"] == []


@patch("creditrisk.ai.analyst.genai.GenerativeModel")
def test_analyst_ask_with_mocked_gemini(mock_model_cls):
    # Mock Gemini chat response
    mock_chat = MagicMock()
    mock_response = MagicMock()
    mock_response.text = "Under Basel III IRB rules, risk-weighted assets are derived from PD, LGD, and EAD."
    mock_chat.send_message.return_value = mock_response

    mock_instance = MagicMock()
    mock_instance.start_chat.return_value = mock_chat
    mock_model_cls.return_value = mock_instance

    analyst = CreditRiskAnalyst(api_key="mock-key")
    analyst.retriever.search = MagicMock(return_value=[
        {"chunk_id": "c1", "source": "bcbs128.pdf", "page": 64, "text": "Risk weighted assets derivation", "score": 0.75}
    ])

    result = analyst.ask("How are risk weighted assets calculated under Basel IRB?")

    assert "Basel III IRB rules" in result["answer"]
    assert len(result["sources"]) == 1
    assert result["sources"][0]["source"] == "bcbs128.pdf"


def test_tool_call_routing():
    # Verify tool functions directly map to core math/lookup outputs
    el_res = tool_expected_loss(pd_val=0.03, lgd_val=0.9, ead_val=10000.0)
    assert el_res["expected_loss_usd"] == 270.0

    basel_res = tool_basel_capital(pd_val=0.03, lgd_val=0.45, ead_val=100000.0)
    assert basel_res["rwa_usd"] > 0
    assert basel_res["risk_weight_pct"] > 0

    score_res = tool_score_to_pd(score=600)
    assert score_res["grade"] == "3"


@patch("creditrisk.ai.analyst.genai.list_models")
@patch("creditrisk.ai.analyst.genai.GenerativeModel")
def test_analyst_404_model_not_found_handling(mock_model_cls, mock_list_models):
    mock_chat = MagicMock()
    mock_chat.send_message.side_effect = Exception("404 models/gemini-1.5-flash is not found")
    mock_instance = MagicMock()
    mock_instance.start_chat.return_value = mock_chat
    mock_model_cls.return_value = mock_instance

    # Mock list_models return
    m1 = MagicMock(name="models/gemini-flash-latest", supported_generation_methods=["generateContent"])
    m1.name = "models/gemini-flash-latest"
    mock_list_models.return_value = [m1]

    analyst = CreditRiskAnalyst(api_key="mock-key", model_name="gemini-1.5-flash")
    analyst.retriever.search = MagicMock(return_value=[
        {"chunk_id": "c1", "source": "bcbs128.pdf", "page": 64, "text": "Basel text", "score": 0.85}
    ])

    result = analyst.ask("What is IRB?")
    assert "API Error 404" in result["answer"]
    assert "gemini-flash-latest" in result["answer"]


