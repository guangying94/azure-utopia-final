# Azure Utopia 
## Welcome To Utopia!

In this stage, we will learn how to build Gen AI application with small language model (SLM). SLM is useful for less compute intensive task. In this example, we will learn how to use SLM to perform sentiment analysis and feedback classification.

For simplicity, we will create a REST API to handle query requests and return the generated responses.

### Required Azure Resources
1. Azure AI Foundry
2. Azure Container Registry
3. Azure Container Apps

### Actions To Perform
1. Deploy a small language model in Azure AI Foundry
2. Build and push Docker image
3. Update the apps
4. Register the API with Azure API Management

### API Schema & Sample
Input
```json
{
  "feedback": "the train is convenient"
}
```
Output
```json
{
    "sentiment": "positive",  // possible option: "positive", "negative", "neutral"
    "category": "transportation" // possible option: "accomodation", "food", "transportation", "activity", "others"
}
```

### Azure CLI Commands
#### Define Variables (Update accordingly)
```bash
RG_NAME="RG-azure-utopia"
LOCATION="eastus"
UNIQUE_NAME="<replace-with-your-unique-name>"
```

#### Step 1: Deploy a small language model in Azure AI Foundry
```bash
# Deploy a small language model in Azure AI Foundry
az configure --defaults workspace=${UNIQUE_NAME}-project group=$RG_NAME location=$LOCATION
az ml serverless-endpoint create -f phi35.yml
```

#### Step 2: Build and push Docker image
```bash
# Build the Docker image
az acr build -t utopia/backend:{{.Run.ID}} -r ${UNIQUE_NAME}acr .
```

#### Step 3: Update Azure Container Apps
```bash
## Get the ACR password
ACR_PW=$(az acr credential show --name ${UNIQUE_NAME}acr --query 'passwords[0].value' --output tsv)

# Update Azure Container Apps
az containerapp update -n utopiabackend -g $RG_NAME --image ${UNIQUE_NAME}acr.azurecr.io/utopia/backend:ca5 --set-env-vars SLM_ENDPOINT="https://xxxxx.eastus.models.ai.azure.com" SLM_KEY="xxxxx"
```

#### Step 4: Register API in Azure API Management
```bash
# Create new API operation in Azure API Management
az apim api operation create --service-name ${UNIQUE_NAME}-apim -g $RG_NAME --api-id utopiabackend --operation-id feedback --display-name feedback --method POST --url-template "/feedback"

## Display the query operation url
APIM_GATEWAY_URL=$(az apim show --name ${UNIQUE_NAME}-apim -g $RG_NAME --query gatewayUrl --output tsv)

# Retrieve the URL template for the operation
API_PATH="/utopiabackend"
OPERATION_URL_TEMPLATE=$(az apim api operation show --service-name ${UNIQUE_NAME}-apim -g $RG_NAME --api-id utopiabackend --operation-id feedback --query urlTemplate --output tsv)

# Construct the full request URL
FULL_REQUEST_URL="${APIM_GATEWAY_URL}${API_PATH}${OPERATION_URL_TEMPLATE}"

# Print the full request URL
echo "Full request URL (Feedback): ${FULL_REQUEST_URL}"
```