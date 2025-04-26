#!/bin/bash

# This script helps set up the necessary Vercel secrets for GitHub Actions

echo "====================================================="
echo "       Vercel Secrets Setup Helper for GitHub        "
echo "====================================================="
echo "This script will help you get the necessary Vercel information for GitHub Actions."
echo "You will need to add these as secrets in your GitHub repository."
echo ""
echo "IMPORTANT: You need to have a Vercel account and project already set up."
echo "           If you haven't deployed to Vercel yet, please do that first."
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
echo "====================================================="
echo "Step 1: Get your Vercel Project ID"
echo "====================================================="
echo "Getting Vercel project information..."
echo ""

# Get project information
vercel project ls

echo ""
echo "Please enter your Vercel project ID from the list above:"
read PROJECT_ID

# Validate project ID
if [ -z "$PROJECT_ID" ]; then
    echo "Error: Project ID cannot be empty."
    echo "Please run the script again and enter a valid Project ID."
    exit 1
fi

# Get team/org information
echo ""
echo "====================================================="
echo "Step 2: Get your Vercel Organization/Team ID"
echo "====================================================="
echo "Getting Vercel team/organization information..."
echo ""
vercel teams ls

echo ""
echo "Please enter your Vercel team/organization ID from the list above"
echo "(or press Enter if you're using a personal account):"
read ORG_ID

# If no org ID is provided, get the user ID
if [ -z "$ORG_ID" ]; then
    echo "No team/organization ID provided. Using personal account."
    USER_INFO=$(vercel whoami --json)
    ORG_ID=$(echo $USER_INFO | grep -o '"id":"[^"]*"' | head -1 | cut -d'"' -f4)
    echo "Your personal account ID is: $ORG_ID"
fi

# Validate org ID
if [ -z "$ORG_ID" ]; then
    echo "Error: Could not determine Organization/Team ID."
    echo "Please run the script again and enter a valid Organization/Team ID."
    exit 1
fi

echo ""
echo "====================================================="
echo "Step 3: Create a Vercel API Token"
echo "====================================================="
echo "You need to create a Vercel API token with the following permissions:"
echo "- Global scope (or at least access to the project you want to deploy)"
echo ""
echo "Go to: https://vercel.com/account/tokens"
echo "Click 'Create' and give your token a name (e.g., 'GitHub Actions')"
echo ""
echo "Please enter your Vercel token:"
read -s VERCEL_TOKEN  # -s flag hides the input (for security)
echo ""

# Validate token
if [ -z "$VERCEL_TOKEN" ]; then
    echo "Error: Token cannot be empty."
    echo "Please run the script again and enter a valid token."
    exit 1
fi

# Create .env.vercel file with the information
echo "VERCEL_PROJECT_ID=$PROJECT_ID" > .env.vercel
echo "VERCEL_ORG_ID=$ORG_ID" >> .env.vercel
echo "VERCEL_TOKEN=$VERCEL_TOKEN" >> .env.vercel

echo ""
echo "====================================================="
echo "Step 4: Add Secrets to GitHub Repository"
echo "====================================================="
echo "Vercel information saved to .env.vercel"
echo ""
echo "Now, you need to add the following secrets to your GitHub repository:"
echo ""
echo "1. VERCEL_TOKEN: [Your Vercel API Token]"
echo "2. VERCEL_PROJECT_ID: $PROJECT_ID"
echo "3. VERCEL_ORG_ID: $ORG_ID"
echo ""
echo "To add these secrets:"
echo "1. Go to: https://github.com/bniladridas/software/settings/secrets/actions"
echo "2. Click 'New repository secret'"
echo "3. Add each secret with the exact name and value shown above"
echo ""
echo "====================================================="
echo "Testing Vercel Configuration"
echo "====================================================="
echo "Testing if the provided credentials work with Vercel..."

# Test the token
TEST_RESULT=$(curl -s -H "Authorization: Bearer $VERCEL_TOKEN" "https://api.vercel.com/v9/projects/$PROJECT_ID?teamId=$ORG_ID")

if echo "$TEST_RESULT" | grep -q "\"id\":\"$PROJECT_ID\""; then
    echo "✅ Success! Your Vercel credentials are valid."
    echo "   You can now add these secrets to your GitHub repository."
else
    echo "❌ Error: Could not validate Vercel credentials."
    echo "   Please check that your Project ID, Organization ID, and Token are correct."
    echo "   Error details: $(echo "$TEST_RESULT" | grep -o '\"error\":{[^}]*}')"
fi

echo ""
echo "====================================================="
echo "                  Setup Complete                     "
echo "====================================================="
