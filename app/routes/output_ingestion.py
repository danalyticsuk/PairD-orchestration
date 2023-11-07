"""
This endpoint ingests LLM responses 
"""

# Imports:
import fastapi
from pydantic import BaseModel

import pdb

from app.saved_query import saved_query
from app.PIIBlocker import PIIBlocker

router = fastapi.APIRouter()

# Class definitions:

class LLMResponse(BaseModel):
    llm_response: str


@router.post("/ingest_llm_response")
async def ingest_llm_response(llm_response: LLMResponse):

    # Output Guardrails logic here:

    # PII mask applied
    if saved_query:
        pii_dict = saved_query.get("pii scrubber", "Query not found")

        pii_blocker = PIIBlocker()
        pii_blocker._scrubber = pii_dict
        
        llm_response = pii_blocker.remask(llm_response.llm_response)

    saved_query["llm response"] = llm_response

    return {"message": "LLM Response ingested successfully."}