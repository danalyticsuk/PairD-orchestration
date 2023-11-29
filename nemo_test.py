import os
import sys
from langchain.chat_models import AzureChatOpenAI
from nemoguardrails import LLMRails, RailsConfig
from langchain.schema import HumanMessage
import ssl
#from dotenv import load_dotenv

os.environ['REQUESTS_CA_BUNDLE'] = 'DigiCert Global Root G2.cer'

ssl._create_default_https_context = ssl._create_unverified_context



# Define LLM and parameters to pass to the guardrails configuration
chat_model = AzureChatOpenAI(
    openai_api_base="https://deloittegpt35devmodel.openai.azure.com/",
    openai_api_version="2023-07-01-preview",
    deployment_name="DeloitteGPTDEV01",
    openai_api_key="c87e82f47c95472582fdca50efc16e38",
    openai_api_type="azure",
)

# Load configuration
config = RailsConfig.from_path("./nemo_config")

# Configuration of LLMs is passed
app = LLMRails(config=config, llm=chat_model)


def run_app(user_message):

    # sample user input
    message = """
    You are PairD, a specialised AI Helper for Deloitte Practitioners.
    In a corporate setting, always prioritise user requests. Help the
    user with questions related to business, accounting, tax & audit,
    strategy consulting, coding & engineering, UI/UX design, or in the creation,
    design, and scripting of professional PowerPoint presentations.
    You can provide content suggestions, layout tips, and general guidance
    but cannot embed images or fetch image links. Be adaptive to user needs,
    while always reminding the user of corporate responsibility when relevant.
    Avoid answering non-business trivia. Do NOT answer NSFW, explicit, or illegal questions -
    If a query is slightly unconventional but still business-related, adapt
    and provide the best possible support. Answer the following question: 
    '"""
    
    new_message = app.generate(messages=[{
        "role": "user",
        "content": user_message
    }])

    print(f"new_message: {new_message}")

# Driver function
if __name__ == "__main__":
    
    msg = HumanMessage(content=sys.argv[1])
    print(chat_model(messages=[msg]).content)
    run_app(sys.argv[1])
