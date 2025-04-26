# Deploying Synthara AI on Vercel

This guide provides step-by-step instructions for deploying the Synthara AI application on Vercel.

## Prerequisites

- [GitHub](https://github.com/) account
- [Vercel](https://vercel.com/) account
- [Together AI](https://www.together.ai/) API key

## Deployment Steps

### 1. Fork or Clone the Repository

First, fork or clone this repository to your GitHub account:

```bash
git clone https://github.com/bniladridas/software.git
cd software
```

### 2. Connect to Vercel

There are two ways to deploy to Vercel:

#### Option 1: Using the Vercel CLI

1. Install the Vercel CLI:
   ```bash
   npm install -g vercel
   ```

2. Login to Vercel:
   ```bash
   vercel login
   ```

3. Deploy the application:
   ```bash
   vercel
   ```

4. Follow the prompts to complete the deployment.

#### Option 2: Using the Vercel Web Interface

1. Go to [Vercel](https://vercel.com/) and sign in with your GitHub account.
2. Click "New Project" and select your repository.
3. Configure the project:
   - Framework Preset: Other
   - Root Directory: ./
   - Build Command: None
   - Output Directory: None

### 3. Configure Environment Variables

Add your Together AI API key as an environment variable:

1. Go to your project settings in Vercel.
2. Navigate to the "Environment Variables" tab.
3. Add a new variable:
   - Name: `TOGETHER_API_KEY`
   - Value: Your Together AI API key

### 4. Deploy

Click "Deploy" to start the deployment process. Vercel will automatically build and deploy your application.

### 5. Verify Deployment

Once the deployment is complete, Vercel will provide you with a URL to access your application. Open this URL in your browser to verify that the application is working correctly.

## Customizing Your Deployment

### Custom Domain

To use a custom domain:

1. Go to your project settings in Vercel.
2. Navigate to the "Domains" tab.
3. Add your domain and follow the instructions to configure DNS settings.

### Environment Variables

You can add additional environment variables as needed:

1. Go to your project settings in Vercel.
2. Navigate to the "Environment Variables" tab.
3. Add new variables as required.

### Deployment Regions

Vercel allows you to deploy to multiple regions for better performance:

1. Go to your project settings in Vercel.
2. Navigate to the "Functions" tab.
3. Configure the regions where you want to deploy your application.

## Troubleshooting

### Deployment Fails

If your deployment fails, check the following:

1. Verify that your `requirements.txt` file includes all necessary dependencies.
2. Check the build logs in Vercel for specific error messages.
3. Ensure that your `vercel.json` file is correctly configured.

### Application Errors

If your application is deployed but not working correctly:

1. Check the function logs in Vercel for error messages.
2. Verify that your environment variables are correctly set.
3. Test the API endpoints to ensure they are working as expected.

## Size Limitations

Vercel has a size limit of 250 MB for Serverless Functions. If your application exceeds this limit, consider:

1. Reducing the size of your dependencies.
2. Using a different deployment platform for larger applications.
3. Splitting your application into smaller functions.

## Continuous Deployment

### Vercel Git Integration

Vercel automatically deploys your application when you push changes to your repository. To disable this:

1. Go to your project settings in Vercel.
2. Navigate to the "Git" tab.
3. Configure the auto-deployment settings as needed.

### GitHub Actions

This repository includes GitHub Actions workflows for automated deployment to Vercel. To set up GitHub Actions:

1. Get your Vercel deployment information by running the provided script:
   ```bash
   ./setup-vercel-secrets.sh
   ```

2. Add the following secrets to your GitHub repository:
   - `VERCEL_TOKEN`: Your Vercel API token
   - `VERCEL_PROJECT_ID`: Your Vercel project ID
   - `VERCEL_ORG_ID`: Your Vercel organization/team ID

3. The GitHub Actions workflow will automatically deploy your application to Vercel when you push to the main branch.

#### Available Workflows

- **vercel-deploy.yml**: Uses the Vercel CLI directly
- **vercel-action-deploy.yml**: Uses the official Vercel GitHub Action

You can enable or disable these workflows in the GitHub Actions settings of your repository.

## Additional Resources

- [Vercel Documentation](https://vercel.com/docs)
- [Flask on Vercel](https://vercel.com/guides/deploying-flask-with-vercel)
- [Environment Variables in Vercel](https://vercel.com/docs/concepts/projects/environment-variables)
