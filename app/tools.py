"""Task 2: deterministic tools the model calls through function calling.

The model must never compute these figures itself.
"""
from __future__ import annotations

from pathlib import Path

DATA_DIR = Path(__file__).resolve().parent.parent / "data"

# Provider-neutral sketch. Adapt it to your provider's tool format
# (OpenAI "tools", Anthropic "tools", Ollama "tools", ...).
DSCR_TOOL_SCHEMA = {
    "name": "calculate_dscr",
    "description": (
        "Calculate the debt service coverage ratio (DSCR) for one property, "
        "from the company's property and loan data."
    ),
    "parameters": {
        "type": "object",
        "properties": {
            "property_id": {
                "type": "string",
                "description": "Property id, e.g. 'P-101'",
            }
        },
        "required": ["property_id"],
    },
}


def calculate_dscr(property_id: str) -> dict:
    """Compute DSCR = NOI / total annual debt service.

    NOI = gross_income - vacancy_loss - operating_expenses  (data/properties.csv)
    Total annual debt service = sum of annual_debt_service over ALL loans for
    the property (data/loans.csv).

    Return a dict the model can explain, e.g.
        {"property_id": ..., "name": ..., "noi": ..., "annual_debt_service": ...,
         "dscr": ...}
    or, when it can't be computed, a clear error, e.g.
        {"error": "...", "property_id": ...}
    """
    raise NotImplementedError


# Map tool names to Python functions, for your tool-execution loop.
TOOLS = {"calculate_dscr": calculate_dscr}
