"""
This endpoint posts the user queries with the relevant guardrails applied.
"""

# Imports:
import fastapi

from app.saved_query import saved_query

router = fastapi.APIRouter()

# Define data model class


# Write endpoint

@router.get("/processed_query")
async def get_processed_query():

    edited_query = saved_query.get("user query", "Query not found")

    return {"edited_query": edited_query}