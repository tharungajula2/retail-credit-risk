"""
CLI Interactive Loop for CreditRiskAnalyst.

Provides a terminal interface to ask regulatory and quantitative credit risk questions.
Requires GEMINI_API_KEY environment variable set in PowerShell.
"""

import os
import sys
from pathlib import Path

from creditrisk.ai.analyst import CreditRiskAnalyst


def main():
    api_key = os.environ.get("GEMINI_API_KEY")
    if not api_key:
        print("ERROR: GEMINI_API_KEY environment variable is not set.")
        print("Set your API key in PowerShell with:")
        print('  $env:GEMINI_API_KEY="your-gemini-api-key-here"\n')
        sys.exit(1)

    analyst = CreditRiskAnalyst()

    print("===========================================================================")
    print(" RETAIL CREDIT RISK AI ANALYST (RAG & FUNCTION CALLING ENGINE)")
    print(f" Model: {analyst.model_name} | Local Vector Index: outputs/models/rag_index/")
    print(" Type your question below. Type 'quit' or 'exit' to exit.")
    print("===========================================================================\n")

    while True:
        try:
            user_input = input("Analyst > ").strip()
            if not user_input:
                continue
            if user_input.lower() in ["quit", "exit"]:
                print("Exiting Credit Risk AI Analyst CLI. Goodbye!")
                break

            result = analyst.ask(user_input)
            print("\n" + "=" * 60)
            print("ANSWER:")
            print(result["answer"])
            print("\nCITATIONS / SOURCES:")
            if result["sources"]:
                for s in result["sources"]:
                    print(f" - {s['source']} (Page {s['page']}) [relevance score: {s['score']}]")
            else:
                print(" - No regulatory document citations applied.")
            print("=" * 60 + "\n")

        except (KeyboardInterrupt, EOFError):
            print("\nExiting CLI.")
            break


if __name__ == "__main__":
    main()
