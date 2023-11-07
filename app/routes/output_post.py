"""
This endpoint posts the llm response with the relevant ouptut guardrails applied.
"""

# Imports:
import fastapi

import pdb

from app.saved_query import saved_query

router = fastapi.APIRouter()

# Define data model class


# Write endpoint

@router.get("/processed_llm_response")
async def get_processed_query():

    llm_response = saved_query.get("llm response", "Query not found")
    pii_dict = saved_query.get("pii dict", "PII not found")
    pii_flag = saved_query.get("pii flag", "Error")

    return {"edited_query": llm_response, "PII dict": pii_dict, "PII flag": pii_flag}