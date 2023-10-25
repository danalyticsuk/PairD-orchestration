"""
This endpoint ingests raw user queries.
"""
# Imports:
import fastapi
from pydantic import BaseModel

from app.saved_query import saved_query


router = fastapi.APIRouter()

# Define data model class

class UserQuery(BaseModel):
    query: str


# Write endpoint

@router.post("/ingest_query")
async def ingest_query(user_query: UserQuery):

    # Guardrails logic goes here:
    edited_query = apply_guardrails(user_query.query)
    saved_query["user query"] = edited_query

    return {"message": "Query ingested successfully."}


def apply_guardrails(user_query):

    return "Guardrails applied to: " + user_query



