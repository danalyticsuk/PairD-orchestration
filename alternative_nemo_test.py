import urllib.request, json
import ssl
import os
from nemoguardrails import LLMRails, RailsConfig
 
ssl._create_default_https_context = ssl._create_unverified_context

os.environ["OPENAI_API_KEY"] = 'c87e82f47c95472582fdca50efc16e38'
 
try:
    # url = "https://paird-test.developer.uk.deloitte.com/deployments/UK-CON-AZU-NPD-OPENAI-MOD35T/chat/completions?api-version=2023-05-15"
    # url = "https://api.paird-test.developer.uk.deloitte.com/deployments/UK-CON-AZU-NPD-OPENAI-MOD35T/chat/completions?api-version=2023-05-15"
    # url = "https://paird-test.developer.deloitte.co.uk/deployments/UK-CON-AZU-NPD-OPENAI-MOD35T/chat/completions?api-version=2023-05-15"
    url = "https://deloittegptdevapim.azure-api.net/deployments/DeloitteGPTDEV01/chat/completions?api-version=2023-05-15"
 
    hdr ={
    # Request headers
    'Content-Type': 'application/json',
    'Cache-Control': 'no-cache',
    'Ocp-Apim-Subscription-Key': 'f52734222b314e2da49abce87701c62d',
    }

    # Guardrails section:
    # Load configuration
    config = RailsConfig.from_path("./nemo_config")

    # Configuration of LLMs is passed
    app = LLMRails(config=config)
 
    # Request body
    data = {
    "model": "gpt-35-turbo",
    "messages": [{
        "role": "user",
        "content": "what's the location of Deloitte UK"
    }]}
    
    app.generate(messages=data["messages"])

    data = json.dumps(data)
    req = urllib.request.Request(url, headers=hdr, data = bytes(data.encode("utf-8")))
 
    req.get_method = lambda: 'POST'
    response = urllib.request.urlopen(req)
    print(response.getcode())
    print(response.read())
except Exception as e:
    print(e)