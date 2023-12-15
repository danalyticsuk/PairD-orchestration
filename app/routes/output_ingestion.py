"""
This endpoint ingests LLM responses 
"""

# Imports:
from fastapi import APIRouter, Body
from pydantic import BaseModel
from typing import List, Dict

import pdb

from app.saved_query import saved_query
from app.PII_Blocker.PIIBlocker import PIIBlocker
from app.Content_Guardrails.ContentGuardrails import Content_Guardrails

router = APIRouter()

# Class definitions:

class Message(BaseModel):
    role: str
    content: str

class Choice(BaseModel):
    finish_reason: str
    index: int
    message: Message


class LLMResponse(BaseModel):
    id: str
    object: str
    created: int
    model: str
    choices: List[Choice]
    usage: Dict[str, int]


@router.post("/ingest_llm_response")
async def ingest_llm_response(llm_response: LLMResponse):

    # Output Guardrails logic here:
    llm_response, content_flag = Content_Guardrails().process_response(llm_response)

    # PII mask applied - possibly need to make this more robust - if there's no PII blocker, don't need to go through the indent
    if saved_query:
        pii_dict = saved_query.get("pii scrubber", "Query not found")

        pii_blocker = PIIBlocker()
        pii_blocker._scrubber = pii_dict
        
        llm_response = pii_blocker.remask(llm_response)

    saved_query["llm response"] = llm_response
    saved_query["content flag"] = content_flag

    return {"message": "LLM Response ingested successfully."}
