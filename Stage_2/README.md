# Azure Utopia 
## I Want To Find Out More!

In this stage, we will learn how to create a retrival-augmented generation (RAG) solution. For simplicity, we will create a REST API to handle query requests and return the generated responses.

### Required Azure Resources
1. Azure AI Foundry
2. Azure API Management
3. Azure AI Search
4. Azure Open AI
5. Azure Container Registry
6. Azure Container Apps

### Actions To Perform
1. Upload documents to storage account
2. Ceate AI Search
3. Create vector seach index
4. Create Azure Container Registry
5. Build and push Docker image
6. Create Azure Container Apps
7. Create Azure API Management
8. Register the API with Azure API Management

### API Schema & Sample
Input
```json
{
  "message": "what is the campaign name?"
}
```
Output
```json
{
  "answer": "The campaign name is \"Humanity's Next Frontier\" [doc1]."
}
```

### Azure CLI Commands
#### Define Variables (Update accordingly)
```bash
RG_NAME="RG-azure-utopia"
LOCATION="eastus"
UNIQUE_NAME="<replace-with-your-unique-name>"
```

#### Step 1: Create Azure resources
```bash
# Create Azure API Management
az apim create --name ${UNIQUE_NAME}-apim --resource-group $RG_NAME --sku-name Consumption --publisher-email utopia@test.com --publisher-name utopia --no-wait

# Create Azure AI Search with managed identity enabled
az search service create --resource-group $RG_NAME --name ${UNIQUE_NAME}search --sku Basic --public-access enabled --identity-type SystemAssigned --no-wait

# Create Azure Container Registry
az acr create --resource-group $RG_NAME --name ${UNIQUE_NAME}acr --sku Basic --admin-enabled true
```

#### Step 2: Upload documents to storage account
```bash
# Get the storage account name
STORAGE_ACCOUNT=$(az storage account list --resource-group $RG_NAME --query "[0].name" -o tsv)

# Create a container in the storage account
az storage container create --name documents --account-name $STORAGE_ACCOUNT

# Upload a document to the container
az storage blob upload --container-name documents --file /Stage_2/sample.txt --name sample.txt --account-name $STORAGE_ACCOUNT

# Assign Blob Data Contributor role to the managed identity of Azure AI Search for azure storage account
az role assignment create --role "Storage Blob Data Contributor" --assignee-object-id $(az search service show --resource-group $RG_NAME --name ${UNIQUE_NAME}search --query identity.principalId -o tsv) --scope $(az storage account show --name $STORAGE_ACCOUNT --resource-group $RG_NAME --query id -o tsv)
```

#### Step 3: Create Azure Open AI Model
Create Azure Open AI model using the Azure AI Foundry. We will use the following model:
1. Embedding model: text-embedding-ada-002
2. LLM Model: GPT-4o mini

#### Step 4: Build and push Docker image
```bash
# Build the Docker image
az acr build -t utopia/backend:{{.Run.ID}} -r ${UNIQUE_NAME}acr .
```

#### Step 5: Create Azure Container Apps
```bash
# Create Azure Container Apps Environment
az containerapp env create -n ${UNIQUE_NAME}containerenv -g $RG_NAME --location $LOCATION

## Get the ACR password
ACR_PW=$(az acr credential show --name ${UNIQUE_NAME}acr --query 'passwords[0].value' --output tsv)

# Get Azure Container Registry
az acr login -n ${UNIQUE_NAME}acr --username ${UNIQUE_NAME}acr -p $ACR_PW

# Create Azure Container Apps
az containerapp create -n utopiabackend \
-g $RG_NAME --image ${UNIQUE_NAME}acr.azurecr.io/utopia/backend:ca2 \
--environment ${UNIQUE_NAME}containerenv \
--ingress external --target-port 5000 \
--registry-server ${UNIQUE_NAME}acr.azurecr.io --registry-username ${UNIQUE_NAME}acr --registry-password $ACR_PW \
--cpu 1 --memory 2Gi \
--env-vars AOAI_ENDPOINT_URL="https://xxxxxxxx.openai.azure.com/" DEPLOYMENT_NAME="4o-mini" SEARCH_ENDPOINT="https://xxxxxxxx.search.windows.net" SEARCH_KEY="xxxxxxxx" SEARCH_INDEX_NAME="utopia-index" AZURE_OPENAI_API_KEY="xxxxxxxx" EMBEDDING_DEPLOYMENT_NAME="text-embedding-ada-002" \
--query properties.configuration.ingress.fqdn

## get container apps ingress fqdn
FQDN="https://$(az containerapp show -n utopiabackend -g $RG_NAME --query properties.configuration.ingress.fqdn --output tsv)"
```

#### Step 6: Register API in Azure API Management
```bash
# Create new API ID in Azure API Management
az apim api create --service-name ${UNIQUE_NAME}-apim -g $RG_NAME --api-id utopiabackend --api-type http --path /utopiabackend --display-name utopiabackend --service-url $FQDN --protocols https --subscription-required false

# Create new API operation in Azure API Management
az apim api operation create --service-name ${UNIQUE_NAME}-apim -g $RG_NAME --api-id utopiabackend --operation-id query --display-name query --method POST --url-template "/query"

## Display the query operation url
APIM_GATEWAY_URL=$(az apim show --name ${UNIQUE_NAME}-apim -g $RG_NAME --query gatewayUrl --output tsv)

# Retrieve the URL template for the operation
API_PATH="/utopiabackend"
OPERATION_URL_TEMPLATE=$(az apim api operation show --service-name ${UNIQUE_NAME}-apim -g $RG_NAME --api-id utopiabackend --operation-id query --query urlTemplate --output tsv)

# Construct the full request URL
FULL_REQUEST_URL="${APIM_GATEWAY_URL}${API_PATH}${OPERATION_URL_TEMPLATE}"

# Print the full request URL
echo "Full request URL (RAG): ${FULL_REQUEST_URL}"
```

