# Azure Utopia 
## Who Are We? Brand Ourselves!

In this stage, we will learn how to create Azure AI Foundry, Azure OpenAI, DALL-E 3 endpoints, and generate images using the DALL-E 3 model.

Azure CLI Reference: [Azure CLI ml workspace](https://learn.microsoft.com/en-us/azure/machine-learning/how-to-configure-cli?view=azureml-api-2&tabs=public)

### Required Azure Resources
1. Azure AI Foundry

### Actions To Perform
1. Create Azure AI Foundry
2. Create Base Model (DALL-E 3)
3. Create Image

### Azure CLI Commands
#### Define Variables
```bash
RG_NAME="RG-azure-utopia"
LOCATION="eastus"
UNIQUE_NAME="<replace-with-your-unique-name>"
```

## Login to Azure
az login

### Install Azure CLI Extensions
```bash
# reinstall azure ml extension
az extension remove -n ml
az extension add -n ml
az extension update -n ml
```

### Create Resource Group for entire project
```bash
az group create --name $RG_NAME --location $LOCATION
```

#### Step 1: Create Azure AI Foundry & AI Project
```bash
## Create Azure AI Foundry
az ml workspace create --kind hub --resource-group $RG_NAME --name $UNIQUE_NAME-aihub

output=$(az ml workspace show --name $UNIQUE_NAME-aihub --resource-group $RG_NAME)
id=$(echo $output | jq -r '.id')

## Create a project
az ml workspace create --kind project --hub-id $id --name $UNIQUE_NAME-project -g $RG_NAME -l $LOCATION --description "Azure Utopia Project"

az configure --defaults group=$RG_NAME workspace=$UNIQUE_NAME-project
```

#### Step 2: Create Base Model (DALL-E 3)
Navigate to the [Azure AI Foundry](https://ai.azure.com) and create a new model.

#### Step 3: Create Image
Leverage built-in UI (Playground) to generate images using the DALL-E 3 model.