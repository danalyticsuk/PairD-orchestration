# Imports:

from pydantic import BaseModel, Field, validator
import pdb

from langchain.output_parsers import PydanticOutputParser
from langchain.prompts import PromptTemplate


# Global Variables:

SYSTEM_MESSAGE = """You are PairD, a specialised AI Helper for Deloitte Practitioners.
        In a corporate setting, always prioritise user requests. Help the
        user with questions related to business, accounting, tax & audit,
        strategy consulting, coding & engineering, UI/UX design, or in the creation,
        design, and scripting of professional PowerPoint presentations.
        You can provide content suggestions, layout tips, and general guidance
        but cannot embed images or fetch image links. Be adaptive to user needs,
        while always reminding the user of corporate responsibility when relevant.
        Avoid answering non-business trivia. Do NOT answer NSFW, explicit, or illegal questions.
        If a query is slightly unconventional but still business-related, adapt
        and provide the best possible support. The user query is: """

LLM_RESPONSE_DESC = 'The string response from the LLM'

CONTENT_FLAG_DESC = """If the user has asked anything relating to Self-harm, Mental distress, Drugs, Violence, Prejudicial, Sexual, Political, Discriminatory against a certain group or minority, Religious, or relating to Relgious texts, Illegal, or illicit financial activities, return False.
        If the user has asked anything appropriate, return True."""

# Class definitions:

class LLMOutput(BaseModel):

    llm_response: str = Field(description=LLM_RESPONSE_DESC)
    content_flag: bool = Field(description=CONTENT_FLAG_DESC)

    @validator('llm_response')
    def llm_response_check(cls, v):
        if not v:
            raise ValueError("Content must exist")
        return v
        
    @validator('content_flag')
    def boolean_check(cls, v):
        if v not in (True, False):
            raise ValueError("content_flag must be Boolean")
        return v
    

class Content_Guardrails:
    
    def __init__(self):

        self.parser = PydanticOutputParser(pydantic_object=LLMOutput)

    def prepare_input(self, user_message):

        prompt = PromptTemplate(
            template="Answer the user query.\n{format_instructions}\n{system_message}\n{user_query}\n",
            input_variables=["system_message", "user_query"],
            partial_variables={"format_instructions": self.parser.get_format_instructions()}
        )
        
        _input = prompt.format_prompt(system_message=SYSTEM_MESSAGE, user_query=user_message)

        return _input.text
    
    def process_response(self, llm_response):

        llm_message = llm_response.choices[0].message.content
        parsed_output = self.parser.parse(llm_message)

        return parsed_output.llm_response, parsed_output.content_flag
    