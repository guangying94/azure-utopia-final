import os
import json
from openai import AzureOpenAI
from dotenv import load_dotenv
from azure.cosmos import CosmosClient, exceptions
import time
import os
import uuid
from .stage3_inference import infer

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

def stage3_predict(applicant_details):
    client = AzureOpenAI(  
        azure_endpoint=endpoint,  
        api_key=subscription_key,  
        api_version="2024-05-01-preview",  
    )

    assistant = client.beta.assistants.create(
        name="test-assistant",
        instructions="You are an AI assistant that process applicant details. You classify the applicant for approval. No further explanation is required.",
        model=deployment,
        tools=[
            {
                "type": "function",
                "function": {
                    "name": "ml_prediction",
                    "description": "Make a prediction using ML model, to check if the applicant is approved or not.",
                    "parameters": {
                        "type": "object",
                        "properties": {
                            "id": {
                                "type": "string"
                            },
                            "age": {
                                "type": "number"
                            },
                            "sex": {
                                "type": "string"
                            },
                            "occupation":{
                                "type": "string"
                            },
                            "crime_history":{
                                "type": "boolean"
                            },
                            "health":{
                                "type": "number"
                            },
                            "diabetes":{
                                "type": "boolean"
                            }
                        },
                        "required": ["id", "age", "sex", "occupation", "crime_history", "health", "diabetes"]
                    }
                }
            }
        ]
    )

    thread = client.beta.threads.create()

    run = client.beta.threads.runs.create(
        thread_id=thread.id,
        assistant_id=assistant.id,
        instructions=applicant_details + " \n\nYou only reply a single word on the approval status, which is true or false. Sample output: true",
    )
    
    poll_run_till_completion(
        client=client,
        thread_id=thread.id,
        run_id=run.id,
        available_functions={"ml_prediction": ml_prediction}
    )

    message = retrieve_and_print_messages(client, thread.id)

    return message

def ml_prediction(id, age, sex, occupation, crime_history, health, diabetes):
    ## Do some ML prediction here using Azure ML AutoML

    input_data = {
        'age': age,
        'sex': sex,
        'occupation': occupation,
        'crime_history': crime_history,
        'health': health,
        'diabetes': diabetes
    }

    approved = infer(input_data)
    
    if approved:
        insert_db(id, age, approved)
    
    return f"{id} application result is {approved}"

def insert_db(passenger_id, age, approved):
    # Create a document to insert
    document = {
        "id": str(uuid.uuid4()),
        "passenger_id": passenger_id,
        "age": age,
        "approved": approved
    }
    
    try:
        # Insert the document into the container
        container.upsert_item(body=document)
        print(f"Passenger id {passenger_id} inserted successfully.")
    except exceptions.CosmosHttpResponseError as e:
        print(f"An error occurred: {e}")


def poll_run_till_completion(
    client, thread_id, run_id, available_functions,max_steps: int = 10,wait: int = 2,
):

    if (client is None and thread_id is None) or run_id is None:
        print("Client, Thread ID and Run ID are required.")
        return
    try:
        cnt = 0
        while cnt < max_steps:
            run = client.beta.threads.runs.retrieve(thread_id=thread_id, run_id=run_id)
            print("Poll {}: {}".format(cnt, run.status))
            cnt += 1
            if run.status == "requires_action":
                tool_responses = []
                if (
                    run.required_action.type == "submit_tool_outputs"
                    and run.required_action.submit_tool_outputs.tool_calls is not None
                ):
                    tool_calls = run.required_action.submit_tool_outputs.tool_calls

                    for call in tool_calls:
                        if call.type == "function":
                            if call.function.name not in available_functions:
                                raise Exception("Function requested by the model does not exist")
                            function_to_call = available_functions[call.function.name]
                            print("Calling function: ", call.function.name)
                            print("Arguments: ", call.function.arguments)
                            tool_response = function_to_call(**json.loads(call.function.arguments))
                            tool_responses.append({"tool_call_id": call.id, "output": tool_response})

                run = client.beta.threads.runs.submit_tool_outputs(
                    thread_id=thread_id, run_id=run.id, tool_outputs=tool_responses
                )
            if run.status == "failed":
                print("Run failed.")
                break
            if run.status == "completed":
                break
            time.sleep(wait)

    except Exception as e:
        print(e)

def retrieve_and_print_messages(client, thread_id):
    if client is None and thread_id is None:
        print("Client and Thread ID are required.")
        return None
    try:
        messages = client.beta.threads.messages.list(thread_id=thread_id)
        
        content_texts = []
        for message in messages.data:
            for content_block in message.content:
                if content_block.type == 'text':
                    content_texts.append(content_block.text.value)
        return content_texts[-1]
    
    except Exception as e:
        print(e)
        return None