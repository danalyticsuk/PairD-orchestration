"""
This endpoint ingests raw user queries.
"""

# Imports:
import fastapi
from pydantic import BaseModel
import time

import pdb

from app.PII_Blocker.PIIBlocker import PIIBlocker
from app.Gibberish_Detector.GibberishDetector import GibberishDetector

from app.saved_query import saved_query

router = fastapi.APIRouter()

# Define data model class

class UserQuery(BaseModel):
    query: str


class InputGuardrails():

    def __init__(self, user_query):
        self.user_query = "Guardrails applied to: " + user_query

    def pii_blocker(self):

        pii_blocker = PIIBlocker()
        self.blocked_user_query = pii_blocker.block(self.user_query)
        self.pii_dict = pii_blocker.get_pii(self.user_query)
        self.pii_scrubber = pii_blocker._scrubber

        if self.pii_dict:
            self.pii_detected = True
        else:
            self.pii_detected = False

    def content_guardail(self):

        pass

    def adversarial_attack_blocker(self):

        self.gibberish_detector = GibberishDetector()
        self.gibberish_detector.process_sentences(self.user_query)


# Write endpoint

@router.post("/ingest_query")
async def ingest_query(user_query: UserQuery):

    passed_input_controls = True
    
    # Guardrails logic goes here:
    input_guardrails = InputGuardrails(user_query.query)

    if not user_query.query:
        raise fastapi.HTTPException(status_code=422, detail="Input string cannot be empty")

    start_time = time.time()
    input_guardrails.pii_blocker()
    print(f"PII blocker time taken: {time.time() - start_time}")
    start_time = time.time()
    input_guardrails.adversarial_attack_blocker()
    print(f"Adversarial Attack blocker time taken: {time.time() - start_time}")

    # Gibberish detector flag:
    if input_guardrails.gibberish_detector.detected_gibberish:
        gibberish_detected = True
        passed_input_controls = False
    else:
        gibberish_detected = False

    edited_query = input_guardrails.blocked_user_query

    saved_query["user query"] = edited_query
    saved_query["pii scrubber"] = input_guardrails.pii_scrubber
    saved_query["pii dict"] = input_guardrails.pii_dict
    saved_query["pii flag"] = input_guardrails.pii_detected
    saved_query["gibberish flag"] = gibberish_detected
    saved_query["passed input controls"] = passed_input_controls

    return {"message": "Query ingested successfully."}
