
#Imports:
import os
import sys
from pydantic import BaseModel, Field, validator
import spacy
spacy.load("en_core_web_trf")

from langchain.output_parsers import PydanticOutputParser
from langchain.prompts import PromptTemplate

from langchain.chat_models import AzureChatOpenAI
from langchain.schema import (
    AIMessage,
    HumanMessage,
    SystemMessage
)

# Global Variables:
os.environ["OPENAI_API_TYPE"] = "azure"
os.environ["OPENAI_API_BASE"] = "https://deloittegpt35devmodel.openai.azure.com/"
os.environ["OPENAI_API_KEY"] = 'c87e82f47c95472582fdca50efc16e38'
os.environ["OPENAI_API_VERSION"] = "2023-03-15-preview"

chat_model = AzureChatOpenAI(
    openai_api_base="https://deloittegpt35devmodel.openai.azure.com/",
    openai_api_version="2023-03-15-preview",
    deployment_name="DeloitteGPTDEV01",
    openai_api_key="c87e82f47c95472582fdca50efc16e38",
    openai_api_type="azure",
)

# Pydantic parser:

system_message = """You are PairD, a specialised AI Helper for Deloitte Practitioners.
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

llm_response_desc = 'The string response from the LLM'
content_flag_desc = """If the user has asked anything relating to Self-harm, Mental distress, Drugs, Violence, Prejudicial, Sexual, Political, Discriminatory against a certain group or minority, Religious, or relating to Relgious texts, Illegal, or illicit financial activities, return False.
        If the user has asked anything appropriate, return True."""

class LLMOutput(BaseModel):

    llm_response: str = Field(description=llm_response_desc)
    content_flag: bool = Field(description=content_flag_desc)

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
    

def pydantic_content_guardrails_test(user_message, chat_model=chat_model):

    print(user_message)

    parser = PydanticOutputParser(pydantic_object=LLMOutput)

    prompt = PromptTemplate(
        template="Answer the user query.\n{format_instructions}\n{system_message}\n{user_query}\n",
        input_variables=["system_message", "user_query"],
        partial_variables={"format_instructions": parser.get_format_instructions()}
    )
    
    _input = prompt.format_prompt(system_message=system_message, user_query=user_message)

    input = [
        HumanMessage(content=_input.to_string())
    ]

    output = chat_model(input)
    parsed_output = parser.parse(output.content)

    print(parsed_output.llm_response)
    print(parsed_output.content_flag)
    
    return parsed_output


def content_guardrails_poc(user_message):

    output = pydantic_content_guardrails_test(user_message)
    return output


if __name__ == "__main__":
    content_guardrails_poc(sys.argv[1])