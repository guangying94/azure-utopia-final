import os
from openai import AzureOpenAI
from dotenv import load_dotenv
from azure.cosmos import CosmosClient, exceptions

load_dotenv()

endpoint = os.getenv("AOAI_ENDPOINT_URL")  
deployment = os.getenv("DEPLOYMENT_NAME")
subscription_key = os.getenv("AZURE_OPENAI_API_KEY")
cosmos_endpoint = os.getenv("COSMOS_ENDPOINT")
cosmos_key = os.getenv("COSMOS_KEY")
database_name = os.getenv("COSMOS_DATABASE_NAME")
container_name = os.getenv("COSMOS_CONTAINER_NAME")

cosmos_client = CosmosClient(cosmos_endpoint, cosmos_key)
database = cosmos_client.get_database_client(database_name)
container = database.get_container_client(container_name)

def stage4_check(image_url, passenger_id):
    client = AzureOpenAI(  
        azure_endpoint=endpoint,  
        api_key=subscription_key,  
        api_version="2024-05-01-preview",  
    )

    chat_prompt = [
        {
            "role": "system",
            "content": "You are an AI assistant that identify potential dangerous object in the image. You only return 'true' or 'false'. 'true' if the image contains dangerous object, 'false' if otherwise."
        },
        {
            "role": "user",
            "content": [
                {
                    "type": "image_url",
                    "image_url": {
                        "url": image_url
                    }
                }
            ]
        }
    ]

    completion = client.chat.completions.create(
        model=deployment,
        messages=chat_prompt,
        max_tokens=800,
        temperature=0.7,
        top_p=0.95,
    )

    query = f"SELECT * FROM c WHERE c.passenger_id = '{passenger_id}'"
    items = list(container.query_items(query=query, enable_cross_partition_query=True))

    if items:
        return completion.choices[0].message.content, True
    else:
        return completion.choices[0].message.content, False