"""
This endpoint returns an error message to the user if their query fails the input controls. This can happen for the following reasons:
    1. Gibberish detected
    2. Toxicity (in one of the catergories) detected
"""

# Imports:
import fastapi

from app.saved_query import saved_query

router = fastapi.APIRouter()

# Define data model class


# Write endpoint

@router.get("/failed_query")
async def get_failed_query():

    # Initalizations of content flags:
    gibberish_flag = saved_query.get("gibberish flag", "Flag not found")
    attack_flag = saved_query.get("attack flag", "Flag not found")

    # Declaration of error message:
    if gibberish_flag:
        error_message = "Cannot process this request as gibberish has been detected."

    if attack_flag:
        error_message = "Cannot process this request as a possible adversarial attack has been detected."

    if gibberish_flag and attack_flag:
        error_message = "Cannot process this request as a possible adversarial attack and gibberish has been detected."

    return {"error message": error_message, "gibberish flag": gibberish_flag, "attack flag": attack_flag}