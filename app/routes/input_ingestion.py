"""
This endpoint ingests raw user queries.
"""

# Imports:
import fastapi
from pydantic import BaseModel

from app.PIIBlocker import PIIBlocker
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

    def content_guardail(self):

        pass

    def adversarial_attack_blocker(self):

        pass


# Write endpoint

@router.post("/ingest_query")
async def ingest_query(user_query: UserQuery):

    # Guardrails logic goes here:
    input_guardrails = InputGuardrails(user_query.query)
    input_guardrails.pii_blocker()

    edited_query = input_guardrails.blocked_user_query
    pii_dict = input_guardrails.pii_dict

    # edited_query = apply_guardrails(user_query.query)

    saved_query["user query"] = edited_query
    # saved_query["pii dict"] = pii_dict

    saved_query["pii dict"] = input_guardrails.pii_scrubber

    return {"message": "Query ingested successfully."}


"""
def apply_guardrails(user_query):

    # PII Blocker:
    pii_blocker = PIIBlocker()
    blocked_user_query = pii_blocker.block(user_query)
    
    return "Guardrails applied to: " + blocked_user_query

"""

