# Azure Utopia 
## Onboard Now

In this stage, we will learn how to build an API with multi-modal, in this case, images and data from database. For simplicity, it takes an image of a luggage whether it contains dangerous object, and check if the passenger has successfully applied in previous task.

For simplicity, we will create a REST API to handle query requests and return the generated responses.

### Required Azure Resources
1. Azure AI Foundry
2. Azure API Management
3. Azure Open AI
4. Azure Cosmos DB
5. Azure Container Registry
6. Azure Container Apps

### Actions To Perform
1. Create API with Azure Open AI that udnerstand images
2. Build and push Docker image
3. Update the apps
4. Register the API with Azure API Management

### API Schema & Sample
Input
```json
{
    "image_url": "https://thumbs.dreamstime.com/b/overhead-view-traveler-s-accessories-organized-open-luggage-wooden-floor-94372663.jpg",
    "passenger_id": "123" // passenger id from previous task
}
```
Output
```json
{
    "valid": true,
    "dangerous": false
}
```

### Azure CLI Commands
#### Define Variables (Update accordingly)
```bash
RG_NAME="RG-azure-utopia"
LOCATION="eastus2"
UNIQUE_NAME="<replace-with-your-unique-name>"
```

#### Step 1: Build and push Docker image
```bash
# Build the Docker image
az acr build -t utopia/backend:{{.Run.ID}} -r ${UNIQUE_NAME}acr .
```

#### Step 2: Update Azure Container Apps
```bash
## Get the ACR password
#ACR_PW=$(az acr credential show --name ${UNIQUE_NAME}acr --query 'passwords[0].value' --output tsv)

# Update Azure Container Apps
az containerapp update -n utopiabackend -g $RG_NAME --image ${UNIQUE_NAME}acr.azurecr.io/utopia/backend:ca4
```

#### Step 3: Register API in Azure API Management
```bash
# Create new API operation in Azure API Management
az apim api operation create --service-name ${UNIQUE_NAME}-apim -g $RG_NAME --api-id utopiabackend --operation-id check --display-name check --method POST --url-template "/check"

## Display the query operation url
APIM_GATEWAY_URL=$(az apim show --name ${UNIQUE_NAME}-apim -g $RG_NAME --query gatewayUrl --output tsv)

# Retrieve the URL template for the operation
API_PATH="/utopiabackend"
OPERATION_URL_TEMPLATE=$(az apim api operation show --service-name ${UNIQUE_NAME}-apim -g $RG_NAME --api-id utopiabackend --operation-id check --query urlTemplate --output tsv)

# Construct the full request URL
FULL_REQUEST_URL="${APIM_GATEWAY_URL}${API_PATH}${OPERATION_URL_TEMPLATE}"

# Print the full request URL
echo "Full request URL (Check): ${FULL_REQUEST_URL}"
```