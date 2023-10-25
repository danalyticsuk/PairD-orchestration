"""
This endpoint ingests raw user queries.
"""
# Imports:
import fastapi
from pydantic import BaseModel


router = fastapi.APIRouter()

# Define data model class

class UserQuery(BaseModel):
    query: str


# Write endpoint

@router.post("/ingest_query")
async def ingest_query(user_query: UserQuery):

    # Guardrails logic goes here:

    return {"message": "Query ingested successfully."}



