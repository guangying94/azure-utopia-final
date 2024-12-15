import os
from openai import AzureOpenAI 
from dotenv import load_dotenv
import requests
from azure.ai.inference import ChatCompletionsClient
from azure.core.credentials import AzureKeyCredential

load_dotenv()

endpoint = os.getenv("SLM_ENDPOINT")  
subscription_key = os.getenv("SLM_KEY")

def stage5_feedback(message):
    client = ChatCompletionsClient(
        endpoint=endpoint,
        credential=AzureKeyCredential(subscription_key)
    )

    payload = {
        "messages": [
            {
                "role": "system",
                "content": "You are an AI assistant that process feedback. You classify the feedback for sentiment and category. No further explanation is required.\n\nHere's the option you can choose:\nsentiment: [positive, neutral, negative]\ncategory: [accomodation, food, transportation, activity, others]\n\nYou only reply in JSON. Sample output: {\"sentiment\": \"positive\", \"category\": \"food\"}"
            },
            {
                "role": "user",
                "content": message
            }
        ],
        "max_tokens": 800,
        "temperature": 0.8,
        "top_p": 0.1,
        "presence_penalty": 0,
        "frequency_penalty": 0
    }

    response = client.complete(payload)
    print("Response:", response.choices[0].message.content)
    print("Model:", response.model)
    print("Usage:")
    print("	Prompt tokens:", response.usage.prompt_tokens)
    print("	Total tokens:", response.usage.total_tokens)
    print("	Completion tokens:", response.usage.completion_tokens)
    return response.choices[0].message.content