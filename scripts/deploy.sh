#!/bin/bash

# Code Review Quest - AWS Deployment Script
# Usage: ./scripts/deploy.sh [environment] [region]

set -e

# Default values
ENVIRONMENT=${1:-dev}
REGION=${2:-us-east-1}
ACCOUNT_ID=$(aws sts get-caller-identity --query Account --output text)

echo "🚀 Code Review Quest - AWS Deployment"
echo "======================================"
echo "Environment: $ENVIRONMENT"
echo "Region: $REGION"
echo "Account: $ACCOUNT_ID"
echo ""

# Validate environment
if [[ ! "$ENVIRONMENT" =~ ^(dev|staging|prod)$ ]]; then
    echo "❌ Error: Environment must be one of: dev, staging, prod"
    exit 1
fi

# Check AWS CLI and CDK
if ! command -v aws &> /dev/null; then
    echo "❌ Error: AWS CLI is not installed"
    exit 1
fi

if ! command -v cdk &> /dev/null; then
    echo "❌ Error: AWS CDK is not installed"
    exit 1
fi

# Check if logged in to AWS
if ! aws sts get-caller-identity &> /dev/null; then
    echo "❌ Error: Not logged in to AWS. Please run 'aws configure' or 'aws sso login'"
    exit 1
fi

# Set environment variables
export CDK_DEFAULT_ACCOUNT=$ACCOUNT_ID
export CDK_DEFAULT_REGION=$REGION
export ENVIRONMENT=$ENVIRONMENT

echo "📦 Step 1: Installing CDK dependencies..."
cd infrastructure
npm install

echo "🔨 Step 2: Building CDK project..."
npm run build

echo "🏗️  Step 3: Bootstrapping CDK (if needed)..."
cdk bootstrap aws://$ACCOUNT_ID/$REGION

echo "📋 Step 4: Synthesizing CloudFormation templates..."
cdk synth

echo "🔍 Step 5: Showing deployment diff..."
cdk diff CodeReviewQuest-$ENVIRONMENT || true

# Confirmation for production
if [ "$ENVIRONMENT" = "prod" ]; then
    echo ""
    echo "⚠️  WARNING: You are about to deploy to PRODUCTION!"
    echo "This will create real AWS resources and may incur costs."
    read -p "Are you sure you want to continue? (yes/no): " -r
    if [[ ! $REPLY =~ ^[Yy][Ee][Ss]$ ]]; then
        echo "❌ Deployment cancelled"
        exit 1
    fi
fi

echo "🚀 Step 6: Deploying infrastructure..."
cdk deploy CodeReviewQuest-$ENVIRONMENT --require-approval never

# Deploy pipeline for production
if [ "$ENVIRONMENT" = "prod" ]; then
    echo "🔄 Step 7: Deploying CI/CD pipeline..."
    cdk deploy CodeReviewQuest-Pipeline --require-approval never
fi

echo ""
echo "✅ Deployment completed successfully!"
echo ""

# Get outputs
echo "📊 Deployment Information:"
echo "========================="

# Get CloudFormation outputs
STACK_NAME="CodeReviewQuest-$ENVIRONMENT"
OUTPUTS=$(aws cloudformation describe-stacks --stack-name $STACK_NAME --region $REGION --query 'Stacks[0].Outputs' --output table 2>/dev/null || echo "No outputs available")

echo "$OUTPUTS"

echo ""
echo "🎯 Next Steps:"
echo "=============="
echo "1. Build and push Docker images:"
echo "   cd ../backend && docker build -t code-review-quest-backend ."
echo "   # Tag and push to ECR (see ECR console for commands)"
echo ""
echo "2. Build and deploy frontend:"
echo "   cd ../frontend && npm run build"
echo "   # Upload dist/ contents to S3 bucket"
echo ""
echo "3. Initialize database:"
echo "   # Connect to RDS and run database migrations"
echo ""
echo "4. Test the deployment:"
echo "   # Visit the CloudFront URL from the outputs above"
echo ""

# Cost estimation
echo "💰 Estimated Monthly Costs ($ENVIRONMENT):"
echo "========================================="
case $ENVIRONMENT in
    dev)
        echo "• RDS Aurora Serverless v2: ~$10-20/month"
        echo "• ECS Fargate Spot: ~$5-15/month"
        echo "• ElastiCache Serverless: ~$5-10/month"
        echo "• ALB: ~$16/month"
        echo "• CloudFront: ~$1-5/month"
        echo "• S3: ~$1-3/month"
        echo "• Total Estimated: ~$38-69/month"
        ;;
    staging)
        echo "• RDS Aurora Serverless v2: ~$15-30/month"
        echo "• ECS Fargate Spot: ~$10-25/month"
        echo "• ElastiCache Serverless: ~$8-15/month"
        echo "• ALB: ~$16/month"
        echo "• CloudFront: ~$2-8/month"
        echo "• S3: ~$2-5/month"
        echo "• Total Estimated: ~$53-99/month"
        ;;
    prod)
        echo "• RDS Aurora Serverless v2: ~$30-80/month"
        echo "• ECS Fargate (Mixed): ~$25-60/month"
        echo "• ElastiCache Serverless: ~$15-30/month"
        echo "• ALB: ~$16/month"
        echo "• CloudFront: ~$5-20/month"
        echo "• S3: ~$3-10/month"
        echo "• Total Estimated: ~$94-216/month"
        ;;
esac

echo ""
echo "💡 Cost Optimization Tips:"
echo "========================="
echo "• Use Spot instances for development (already configured)"
echo "• Enable auto-shutdown for dev/staging (already configured)"
echo "• Monitor usage with AWS Cost Explorer"
echo "• Set up billing alerts (configured in CDK)"
echo "• Review and optimize resource sizes regularly"

cd ..
echo ""
echo "🎉 Deployment script completed!"
