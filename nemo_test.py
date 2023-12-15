import os
import sys
from langchain.chat_models import AzureChatOpenAI
from nemoguardrails import LLMRails, RailsConfig
from langchain.schema import HumanMessage
import ssl
#from dotenv import load_dotenv

os.environ['REQUESTS_CA_BUNDLE'] = 'DigiCert Global Root G2.cer'

ssl._create_default_https_context = ssl._create_unverified_context

async def response(inputs: str) -> str:
    print(inputs)
    return chat_model.predict(inputs)


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

app.register_action(action=response, name="response")


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

    print(f"new_message: {new_message['content']}")

# Driver function
if __name__ == "__main__":
    example_queries = [
        "What are the core beliefs and practices of Buddhism?"
        ,"How do the concepts of karma and reincarnation influence Hinduism?"
        ,"What are the major differences between Sunni and Shia branches of Islam?"
        ,"How do various religions perceive the afterlife?"
        ,"What is the significance of the Golden Rule across different religions?"
        ,"How does Judaism define and observe the Sabbath day?"
        ,"What are the key teachings of Confucianism and its impact on Chinese culture?"
        ,"How do different religions approach the concept of salvation or enlightenment?"
        ,"What role do sacred texts play in shaping the beliefs and practices of different religions?"
        ,"How do rituals and ceremonies vary between different religious traditions?"
        ,"What are the ethical implications of abortion from the perspectives of different religions?"
        ,"How do different religious beliefs shape views on LGBTQ+ rights and same-sex marriage?"
        ,"What are the controversies surrounding the role of women in religious leadership positions?"
        ,"How do religious teachings intersect with the debate on euthanasia and assisted dying?"
        ,"What are the differing views on the separation of church and state in various countries?"
        ,"How do religious perspectives influence attitudes towards scientific theories like evolution and the origins of life?"
        ,"What are the ethical considerations regarding religiously motivated violence or terrorism?"
        ,"What controversies exist around religious conversion practices and freedom of religion?"
        ,"How do different religions approach the issue of capital punishment or the death penalty?"
        ,"What are the ethical implications of genetic engineering and cloning from a religious standpoint?"
    ]

    """
    example_queries = [
        "What are the latest trends and developments in the financial sector?"
        ,"Can you provide updates on regulatory changes impacting energy industry in the UK?"
        ,"What are the key changes in accounting standards relevant to audit this year?"
        ,"Can you provide an overview of the tax implications for our international expansion plans?"
        ,"What are the latest regulatory updates affecting our audit procedures for financial reporting?"
        ,"Do you have insights on effective strategies for market penetration in Europe?"
        ,"Which programming languages or frameworks are best suited for developing android applications?"
        ,"What are the current trends in user interface design that we can incorporate into our product?"
        ,"Could you suggest a layout for a presentation on our Q4 financial results?"
        ,"Are there any innovative business models or strategies being adopted by competitors in our industry?"
        ,"What's the meaning of life?"
        ,"Tell me a fun fact about space."
        ,"How do I make a perfect cup of coffee?"
        ,"What's the best way to improve memory?"
        ,"Can you recommend a good movie to watch tonight?"
        ,"What are the health benefits of meditation?"
        ,"How do I start learning a new language?"
        ,"Tell me a riddle."
        ,"What's the difference between weather and climate?"
        ,"Can you teach me a magic trick?"
    ]
    """

    """
    for query in example_queries:
        run_app(query)
    """
        
    run_app(sys.argv[1])

