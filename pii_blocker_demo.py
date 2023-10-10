
# Imports:
import sys
import openai
import urllib.request
import json
from pydantic import BaseModel, Field, validator
import spacy_transformers
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

from ConfidentialityControl.PIIBlocker import PIIBlocker




# Global variables:





# Class definitions:

class ApiTest(object):

    def run(self, user_message):
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
                "content": user_message
            }]}
            data = json.dumps(data)

            req = urllib.request.Request(url, headers=hdr, data = bytes(data.encode("utf-8")))
            req.get_method = lambda: 'POST'
            response = urllib.request.urlopen(req)
            response_data = response.read().decode("utf-8")
            response_json = json.loads(response_data)

            # return response_json

            chatbot_response = response_json['choices'][0]['message']['content']

            return chatbot_response

        except Exception as e:
            print(e)

            return e

def read_text_file(file_path):

    # Open the file in read mode ('r')
    try:
        with open(file_path, 'r') as file:
            # Read the entire contents of the file
            file_contents = file.read()

            return file_contents

    except FileNotFoundError:
        print(f"File '{file_path}' not found.")
    except Exception as e:
        print(f"An error occurred: {str(e)}")


# Driver Function:



def pii_blocer_driver(file_path):

    user_message = read_text_file(file_path)

    print(f"initial user message: {user_message}")
    pii_blocker = PIIBlocker()
    blocked_user_message = pii_blocker.block(user_message)

    print(f"blocked user messgae: {blocked_user_message}")

    api_test = ApiTest()
    llm_response = api_test.run(blocked_user_message)

    print(f"blocked llm response: {llm_response}")

    remasked_response = pii_blocker.remask(llm_response)

    print(f"Final llm response: {remasked_response}")

    return remasked_response


if __name__ == "__main__":
    pii_blocer_driver(sys.argv[1])