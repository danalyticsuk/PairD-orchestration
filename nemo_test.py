import os
import sys
from langchain.chat_models import AzureChatOpenAI
from nemoguardrails import LLMRails, RailsConfig

# Define LLM and parameters to pass to the guardrails configuration
chat_model = AzureChatOpenAI(
    openai_api_base="https://deloittegpt35devmodel.openai.azure.com/",
    openai_api_version="2023-03-15-preview",
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
    new_message = app.generate(messages=[{
        "role": "user",
        "content": user_message
    }])

    print(f"new_message: {new_message}")

# Driver function
if __name__ == "__main__":
    run_app(sys.argv[1])
