# Azure Deployment Checklist - Fix "No credentials found" Error

## The Problem
You're getting: `Error: No credentials found. Add an Azure login action before this action.`

This happens because GitHub Actions doesn't have credentials to deploy to your Azure Web App.

## Quick Fix - Follow These Steps

### ✅ Step 1: Get Your Publish Profile from Azure

1. Open [Azure Portal](https://portal.azure.com)
2. Navigate to your Web App: **`receipts-data-extractor`**
3. On the Overview page, click **"Download publish profile"** button (top toolbar)
4. A file will download: `receipts-data-extractor.PublishSettings`
5. Open this file in any text editor (Notepad, VS Code, etc.)
6. **Select ALL content** (Ctrl+A / Cmd+A) and copy it

### ✅ Step 2: Add the Secret to GitHub

1. Go to: https://github.com/BillDFrank/receipts-data-extractor/settings/secrets/actions
2. Click **"New repository secret"** (green button)
3. Enter:
   - **Name**: `AZUREAPPSERVICE_PUBLISHPROFILE`
   - **Value**: Paste the entire XML content you copied
4. Click **"Add secret"**

### ✅ Step 3: Verify Your Workflow Configuration

Make sure your workflow file has the correct app name:

1. Open: `.github/workflows/azure-webapps-python.yml`
2. Check line 24:
   ```yaml
   env:
     AZURE_WEBAPP_NAME: receipts-data-extractor  # ← Should match your Azure app name
   ```
3. This should match exactly what you see in Azure Portal

### ✅ Step 4: Deploy Again

Now you can deploy:

**Option A - Push to trigger automatic deployment:**
```bash
git add .
git commit -m "Fix deployment configuration"
git push origin main
```

**Option B - Manual trigger:**
1. Go to: https://github.com/BillDFrank/receipts-data-extractor/actions
2. Click on "Build and deploy Python app to Azure Web App"
3. Click "Run workflow" → Select "main" branch → "Run workflow"

## Verification

After deployment runs:
- ✅ Check the Actions tab - the workflow should complete successfully
- ✅ Visit: https://receipts-data-extractor.azurewebsites.net/health
- ✅ Should see: `{"status":"healthy","message":"Supermarket Receipt Extractor API is running"}`

## Still Having Issues?

### Double-check these common mistakes:

1. **Secret name is wrong**
   - Must be EXACTLY: `AZUREAPPSERVICE_PUBLISHPROFILE`
   - No typos, no spaces, case-sensitive

2. **Didn't copy full XML content**
   - The publish profile should start with `<?xml`
   - Should end with `</publishData>`
   - Should be several hundred lines long

3. **Wrong Azure Web App**
   - Make sure you downloaded from `receipts-data-extractor` app
   - Not from a different app

4. **App name mismatch**
   - Workflow file: `AZURE_WEBAPP_NAME: receipts-data-extractor`
   - Should match what's in Azure Portal exactly

### Need more help?

Check the full guide: `AZURE_DEPLOYMENT.md`

Or view Azure logs:
```bash
az webapp log tail --name receipts-data-extractor --resource-group <your-resource-group>
```
