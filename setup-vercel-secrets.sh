#!/bin/bash

# This script helps set up the necessary Vercel secrets for GitHub Actions

echo "Vercel Secrets Setup Helper"
echo "=========================="
echo "This script will help you get the necessary Vercel information for GitHub Actions."
echo ""

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

echo ""
echo "Getting Vercel project information..."
echo ""

# Get project information
vercel project ls

echo ""
echo "Please enter your Vercel project ID from the list above:"
read PROJECT_ID

# Get team/org information
echo ""
echo "Getting Vercel team/organization information..."
echo ""
vercel teams ls

echo ""
echo "Please enter your Vercel team/organization ID from the list above (or press Enter if you're using a personal account):"
read ORG_ID

# If no org ID is provided, get the user ID
if [ -z "$ORG_ID" ]; then
    echo "No team/organization ID provided. Using personal account."
    USER_INFO=$(vercel whoami --json)
    ORG_ID=$(echo $USER_INFO | grep -o '"id":"[^"]*"' | head -1 | cut -d'"' -f4)
    echo "Your personal account ID is: $ORG_ID"
fi

echo ""
echo "To create a Vercel token, go to: https://vercel.com/account/tokens"
echo "Please enter your Vercel token:"
read VERCEL_TOKEN

# Create .env.vercel file with the information
echo "VERCEL_PROJECT_ID=$PROJECT_ID" > .env.vercel
echo "VERCEL_ORG_ID=$ORG_ID" >> .env.vercel
echo "VERCEL_TOKEN=$VERCEL_TOKEN" >> .env.vercel

echo ""
echo "Vercel information saved to .env.vercel"
echo ""
echo "To set up GitHub Actions, add the following secrets to your repository:"
echo "1. VERCEL_TOKEN: $VERCEL_TOKEN"
echo "2. VERCEL_PROJECT_ID: $PROJECT_ID"
echo "3. VERCEL_ORG_ID: $ORG_ID"
echo ""
echo "You can add these secrets at: https://github.com/bniladridas/software/settings/secrets/actions"
