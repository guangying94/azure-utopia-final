import os
from openai import AzureOpenAI
from dotenv import load_dotenv

load_dotenv()

endpoint = os.getenv("AOAI_ENDPOINT_URL")  
deployment = os.getenv("DEPLOYMENT_NAME")
embedding_deployment = os.getenv("EMBEDDING_DEPLOYMENT_NAME")
search_endpoint = os.getenv("SEARCH_ENDPOINT")  
search_key = os.getenv("SEARCH_KEY")  
search_index = os.getenv("SEARCH_INDEX_NAME")  
subscription_key = os.getenv("AZURE_OPENAI_API_KEY")  

def stage2_query(message):
    client = AzureOpenAI(  
        azure_endpoint=endpoint,  
        api_key=subscription_key,  
        api_version="2024-05-01-preview",  
    )

    chat_prompt = [
        {
            "role": "system",
            "content": "You are an AI assistant that helps people find information."
        },
        {
            "role": "user",
            "content": message
        }
    ]

    completion = client.chat.completions.create(
        model=deployment,
        messages=chat_prompt,
        max_tokens=800,
        temperature=0.7,
        top_p=0.95,
        frequency_penalty=0,
        presence_penalty=0,
        stop=None,
        stream=False,
        extra_body={
        "data_sources": [{
          "type": "azure_search",
          "parameters": {
            "filter": None,
            "endpoint": f"{search_endpoint}",
            "index_name": f"{search_index}",
            "semantic_configuration": f"{search_index}-semantic-configuration",
            "authentication": {
              "type": "api_key",
              "key": f"{search_key}"
            },
            "embedding_dependency": {
              "type": "endpoint",
              "endpoint": f"{endpoint}openai/deployments/{embedding_deployment}/embeddings?api-version=2023-03-15-preview",
              "authentication": {
                "type": "api_key",
                "key": f"{subscription_key}"
              }
            },
            "query_type": "vector_simple_hybrid",
            "in_scope": True,
            "role_information": "You are an AI assistant that helps people find information.",
            "strictness": 3,
            "top_n_documents": 5
          }
        }]
      }
    )

    return completion.choices[0].message.content