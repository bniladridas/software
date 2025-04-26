#!/bin/bash

# Check if Vercel CLI is installed
if ! command -v vercel &> /dev/null; then
    echo "Vercel CLI is not installed. Installing..."
    npm install -g vercel
fi

# Check if user is logged in to Vercel
if ! vercel whoami &> /dev/null; then
    echo "Please log in to Vercel:"
    vercel login
fi

# Check for environment variables
if [ -f .env ]; then
    echo "Found .env file. Loading environment variables..."
    export $(grep -v '^#' .env | xargs)
fi

# Deploy to Vercel
echo "Deploying to Vercel..."

# Check if we have project and org IDs from environment
if [ -n "$VERCEL_PROJECT_ID" ] && [ -n "$VERCEL_ORG_ID" ]; then
    echo "Using project ID and org ID from environment variables..."
    vercel --prod --confirm --scope $VERCEL_ORG_ID
else
    echo "No project ID or org ID found in environment variables. Using interactive mode..."
    vercel --prod --confirm
fi

echo "Deployment complete!"
echo "Note: Make sure to set the TOGETHER_API_KEY environment variable in your Vercel project settings."

# Provide instructions for setting up GitHub Actions
echo ""
echo "To set up GitHub Actions for automatic deployment, you need to add the following secrets to your repository:"
echo "1. VERCEL_TOKEN - Your Vercel API token"
echo "2. VERCEL_PROJECT_ID - Your Vercel project ID"
echo "3. VERCEL_ORG_ID - Your Vercel organization ID"
echo ""
echo "You can find these values by running:"
echo "- VERCEL_TOKEN: Create a token at https://vercel.com/account/tokens"
echo "- VERCEL_PROJECT_ID and VERCEL_ORG_ID: Run 'vercel project ls' and 'vercel teams ls'"
