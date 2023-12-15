"""
This endpoint posts the user queries with the relevant guardrails applied.
"""

# Imports:
import fastapi

from app.saved_query import saved_query
from app.Content_Guardrails.ContentGuardrails import Content_Guardrails

router = fastapi.APIRouter()

# Write endpoint

@router.get("/processed_query")
async def get_processed_query():

    edited_query = saved_query.get("user query", "Query not found")
    embedded_query = Content_Guardrails().prepare_input(edited_query)

    # Embedded query:

    return {"edited_query": embedded_query}