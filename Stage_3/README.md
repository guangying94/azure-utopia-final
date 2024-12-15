# Azure Utopia 
## You Are The Lucky One

In this stage, we will learn how to integrate statistical machine learning into generative AI applications. We will leverage assistant API capability from Azure Open AI to achieve this. To illustrate this, we will train a simple machine learning model, to classify if the passenger can onboard to the spaceship or not. For successful onboard, we will then store accepted passenger details into a database.

For simplicity, we will create a REST API to handle query requests and return the generated responses.

### Required Azure Resources
1. Azure AI Foundry
2. Azure API Management
3. Azure Open AI
4. Azure Cosmos DB
5. Azure Container Registry
6. Azure Container Apps

### Actions To Perform
1. Train a machine learning model
2. Expose the model as a function
3. Create API with Azure Open AI assistant API
4. Build and push Docker image
5. Update the apps
6. Register the API with Azure API Management

### API Schema & Sample
Input
```json
{
  "application_details": "my name is john. my passenger id is 123. I'm a male, 46 years old. i work as an engineer. i dont have any crime history. i dont have diabetes as well. my health category is 7."
}
```
Output
```json
{
  "approved": true
}
```

### Azure CLI Commands
#### Define Variables (Update accordingly)
```bash
RG_NAME="RG-azure-utopia"
LOCATION="eastus"
UNIQUE_NAME="<replace-with-your-unique-name>"
```

#### Step 1: Create Machine Learning model
We will use GitHub Copilot to gererate training scripts for the model, and expose as a function.
🤖 Sample GitHub Copilot Prompt
```text
Here's my data. create a simple classification model to predict the column 'accepted'. Ignore the column 'id'. Then, expose the trained machine learning model as a function for other code to consume. Tell me what libraries to install as well.
```
#### Step 2: Create Azure Cosmos DB
```bash
## Create a cosmos DB (sql API)
az cosmosdb create --name ${UNIQUE_NAME}cosmos --resource-group $RG_NAME --kind GlobalDocumentDB --locations regionName=$LOCATION

## Create a database
az cosmosdb sql database create --account-name ${UNIQUE_NAME}cosmos --name utopia --resource-group $RG_NAME --throughput 400

## Create sql container
az cosmosdb sql container create --account-name ${UNIQUE_NAME}cosmos --database-name utopia --name application --partition-key-path /passenger_id --resource-group $RG_NAME --throughput 400
```

#### Step 3: Build and push Docker image
```bash
# Build the Docker image
az acr build -t utopia/backend:{{.Run.ID}} -r ${UNIQUE_NAME}acr .
```

#### Step 4: Update Azure Container Apps
```bash
## Get the ACR password
ACR_PW=$(az acr credential show --name ${UNIQUE_NAME}acr --query 'passwords[0].value' --output tsv)

# Update Azure Container Apps
az containerapp update -n utopiabackend -g $RG_NAME --image ${UNIQUE_NAME}acr.azurecr.io/utopia/backend:ca3 --set-env-vars COSMOS_ENDPOINT="https://xxxxxxxx.documents.azure.com:443/" COSMOS_KEY="xxxxxxxx==" COSMOS_DATABASE_NAME="utopia" COSMOS_CONTAINER_NAME="application"
```

#### Step 5: Register API in Azure API Management
```bash
# Create new API operation in Azure API Management
az apim api operation create --service-name ${UNIQUE_NAME}-apim -g $RG_NAME --api-id utopiabackend --operation-id apply --display-name apply --method POST --url-template "/apply"

## Display the query operation url
APIM_GATEWAY_URL=$(az apim show --name ${UNIQUE_NAME}-apim -g $RG_NAME --query gatewayUrl --output tsv)

# Retrieve the URL template for the operation
API_PATH="/utopiabackend"
OPERATION_URL_TEMPLATE=$(az apim api operation show --service-name ${UNIQUE_NAME}-apim -g $RG_NAME --api-id utopiabackend --operation-id apply --query urlTemplate --output tsv)

# Construct the full request URL
FULL_REQUEST_URL="${APIM_GATEWAY_URL}${API_PATH}${OPERATION_URL_TEMPLATE}"

# Print the full request URL
echo "Full request URL (ML): ${FULL_REQUEST_URL}"
```