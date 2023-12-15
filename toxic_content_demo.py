
# Imports:
import sys
import openai
import urllib.request
import json
from pydantic import BaseModel, Field, validator
import pdb

from langchain.output_parsers import PydanticOutputParser
from langchain.prompts import PromptTemplate

from langchain.chat_models import AzureChatOpenAI
from langchain.schema import (
    AIMessage,
    HumanMessage,
    SystemMessage
)

from ConfidentialityControl.PIIBlocker import PIIBlocker
import os



# Global variables:
os.environ['REQUESTS_CA_BUNDLE'] = 'DigiCert Global Root G2.cer'

# Class definitions:
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
    

class ContentBlocker(object):

    def __init__(self, user_message):

        self.user_message = user_message
        self.llm_input = self.prepare_input()
    
    def run(self):
        try:
            url = "https://deloittegptdevapim.azure-api.net/deployments/DeloitteGPTDEV01/chat/completions?api-version=2023-05-15"

            hdr ={
            # Request headers
            'Content-Type': 'application/json',
            'Cache-Control': 'no-cache',
            'Ocp-Apim-Subscription-Key': 'f52734222b314e2da49abce87701c62d', #change to your sub key
            }

            # Request body
            data = {
            "model": "gpt-35-turbo",
            "messages": [{
                "role": "user",
                "content": self.llm_input
            }]}

            data = json.dumps(data)

            req = urllib.request.Request(url, headers=hdr, data = bytes(data.encode("utf-8")))
            req.get_method = lambda: 'POST'
            response = urllib.request.urlopen(req)
            response_data = response.read().decode("utf-8")
            response_json = json.loads(response_data)

            chatbot_response = response_json['choices'][0]['message']['content']

            parsed_response = self.parse_output(chatbot_response)
            
            return parsed_response.llm_response, parsed_response.content_flag

        except Exception as e:
            print(e)

            return e

    def prepare_input(self):

        self.parser = PydanticOutputParser(pydantic_object=LLMOutput)

        prompt = PromptTemplate(
            template="Answer the user query.\n{format_instructions}\n{system_message}\n{user_query}\n",
            input_variables=["system_message", "user_query"],
            partial_variables={"format_instructions": self.parser.get_format_instructions()}
        )
        
        _input = prompt.format_prompt(system_message=system_message, user_query=self.user_message)

        input = [
            HumanMessage(content=_input.to_string())
        ]

        return input[0].content
    
    def parse_output(self, llm_response):

        parsed_output = self.parser.parse(llm_response)
        
        return parsed_output     


def driver(user_message):

    content_blocker = ContentBlocker(user_message)
    llm_response, content_flag = content_blocker.run()

    print(llm_response)
    print(content_flag)
    
    return llm_response, content_flag


if __name__ == "__main__":
    driver(sys.argv[1])