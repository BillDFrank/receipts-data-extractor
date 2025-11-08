# Azure Web App Deployment Guide

This guide will help you deploy the Receipts Data Extractor FastAPI application to Azure Web App.

## Prerequisites

1. An Azure account with an active subscription
2. Azure CLI installed (optional, for command-line setup)
3. A GitHub repository with your code

## Step 1: Create an Azure Web App

### Option A: Using Azure Portal (Recommended for beginners)

1. Go to [Azure Portal](https://portal.azure.com)
2. Click **"Create a resource"**
3. Search for **"Web App"** and click **Create**
4. Configure the following:
   - **Subscription**: Select your subscription
   - **Resource Group**: Create new or select existing
   - **Name**: Choose a unique name (e.g., `receipts-extractor-app`)
   - **Publish**: Code
   - **Runtime stack**: Python 3.10
   - **Operating System**: Linux
   - **Region**: Choose closest to your users
   - **Pricing plan**: Choose based on your needs (B1 or higher recommended)
5. Click **"Review + create"** then **"Create"**

### Option B: Using Azure CLI

```bash
# Login to Azure
az login

# Create a resource group
az group create --name receipts-extractor-rg --location eastus

# Create an App Service plan
az appservice plan create \
  --name receipts-extractor-plan \
  --resource-group receipts-extractor-rg \
  --sku B1 \
  --is-linux

# Create the web app
az webapp create \
  --resource-group receipts-extractor-rg \
  --plan receipts-extractor-plan \
  --name receipts-extractor-app \
  --runtime "PYTHON:3.10"
```

## Step 2: Configure the Web App

### Set Startup Command

1. In Azure Portal, go to your Web App
2. Navigate to **Settings > Configuration**
3. Under **General settings**, set the **Startup Command**:
   ```bash
   gunicorn -w 4 -k uvicorn.workers.UvicornWorker src.api.main:app --bind=0.0.0.0:8000 --timeout 600
   ```
4. Click **Save**

Alternatively, use Azure CLI:
```bash
az webapp config set \
  --resource-group receipts-extractor-rg \
  --name receipts-extractor-app \
  --startup-file "gunicorn -w 4 -k uvicorn.workers.UvicornWorker src.api.main:app --bind=0.0.0.0:8000 --timeout 600"
```

### Configure Application Settings (if needed)

If your app requires environment variables:

```bash
az webapp config appsettings set \
  --resource-group receipts-extractor-rg \
  --name receipts-extractor-app \
  --settings KEY1=VALUE1 KEY2=VALUE2
```

## Step 3: Set Up GitHub Actions Deployment

### Get Publish Profile

1. In Azure Portal, go to your Web App
2. Click **"Get publish profile"** in the Overview page
3. This will download an XML file
4. Copy the entire contents of this file

### Add Secret to GitHub

1. Go to your GitHub repository
2. Navigate to **Settings > Secrets and variables > Actions**
3. Click **"New repository secret"**
4. Name: `AZUREAPPSERVICE_PUBLISHPROFILE`
5. Value: Paste the publish profile XML content
6. Click **"Add secret"**

### Update Workflow Configuration

1. Edit `.github/workflows/azure-webapps-python.yml`
2. Change the `AZURE_WEBAPP_NAME` environment variable to your actual app name:
   ```yaml
   env:
     AZURE_WEBAPP_NAME: receipts-extractor-app  # Change this to your app name
     PYTHON_VERSION: '3.10'
   ```

## Step 4: Deploy

Once everything is configured, deployment will happen automatically:

1. Commit and push your changes to the `main` branch
2. GitHub Actions will automatically:
   - Build your application
   - Install dependencies
   - Deploy to Azure Web App
3. Monitor the deployment in the **Actions** tab of your GitHub repository

### Manual Deployment Trigger

You can also trigger deployment manually:

1. Go to **Actions** tab in GitHub
2. Select the **"Build and deploy Python app to Azure Web App"** workflow
3. Click **"Run workflow"**
4. Select the branch and click **"Run workflow"**

## Step 5: Verify Deployment

After deployment completes:

1. Visit your app URL: `https://your-app-name.azurewebsites.net`
2. Check the health endpoint: `https://your-app-name.azurewebsites.net/health`
3. View the API docs: `https://your-app-name.azurewebsites.net/docs`

## Troubleshooting

### View Application Logs

#### Using Azure Portal:
1. Go to your Web App
2. Navigate to **Monitoring > Log stream**
3. View real-time logs

#### Using Azure CLI:
```bash
az webapp log tail \
  --resource-group receipts-extractor-rg \
  --name receipts-extractor-app
```

### Common Issues

1. **Application fails to start**
   - Check the startup command is correct
   - Verify all dependencies are in `pyproject.toml`
   - Check application logs for errors

2. **500 Internal Server Error**
   - Enable diagnostic logging
   - Check if all required packages are installed
   - Verify environment variables are set correctly

3. **Build fails in GitHub Actions**
   - Check Python version compatibility
   - Verify `pyproject.toml` is correct
   - Check workflow logs for specific errors

### Enable Diagnostic Logging

```bash
az webapp log config \
  --resource-group receipts-extractor-rg \
  --name receipts-extractor-app \
  --application-logging filesystem \
  --level information
```

## Scaling Options

### Vertical Scaling (Increase instance size)

```bash
az appservice plan update \
  --name receipts-extractor-plan \
  --resource-group receipts-extractor-rg \
  --sku B2
```

### Horizontal Scaling (Add more instances)

```bash
az appservice plan update \
  --name receipts-extractor-plan \
  --resource-group receipts-extractor-rg \
  --number-of-workers 2
```

## Cost Optimization

- Start with **B1** (Basic) tier for development/testing
- Use **S1** (Standard) or higher for production
- Enable **auto-scaling** for variable workloads
- Set up **deployment slots** for staging (requires S1+)

## Additional Resources

- [Azure App Service Python documentation](https://docs.microsoft.com/en-us/azure/app-service/quickstart-python)
- [GitHub Actions for Azure](https://github.com/Azure/actions)
- [FastAPI Deployment Guide](https://fastapi.tiangolo.com/deployment/)
- [Azure CLI Reference](https://docs.microsoft.com/en-us/cli/azure/)

## Security Best Practices

1. **Enable HTTPS only**: In Configuration > General settings
2. **Set minimum TLS version**: Use TLS 1.2 or higher
3. **Enable authentication**: Configure Azure AD if needed
4. **Use managed identities**: For accessing other Azure resources
5. **Regular updates**: Keep dependencies updated
6. **Monitor**: Set up Application Insights for monitoring and alerts

## Custom Domain (Optional)

To use a custom domain:

```bash
# Add custom domain
az webapp config hostname add \
  --webapp-name receipts-extractor-app \
  --resource-group receipts-extractor-rg \
  --hostname www.yourdomain.com

# Bind SSL certificate
az webapp config ssl bind \
  --certificate-thumbprint <thumbprint> \
  --ssl-type SNI \
  --name receipts-extractor-app \
  --resource-group receipts-extractor-rg
```
