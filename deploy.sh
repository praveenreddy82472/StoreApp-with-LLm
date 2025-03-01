#!/bin/bash

# Set Variables
AWS_REGION="us-east-1"
ECR_REPO="381492082704.dkr.ecr.$AWS_REGION.amazonaws.com/praveenstore-app"
EB_APP_NAME="praveenstore-app"
EB_ENV_NAME="PraveenStore-env"
VERSION_LABEL="v$(date +%Y%m%d%H%M%S)"  # Unique version based on timestamp
S3_BUCKET="elasticbeanstalk-$AWS_REGION-381492082704"
DEPLOY_ZIP="deploy.zip"

echo "🚀 Starting deployment..."

# Step 1: Create ECR repository if it doesn't exist
echo "🛠 Checking if ECR repository exists..."
aws ecr describe-repositories --repository-names praveenstore-app --region $AWS_REGION || \
  aws ecr create-repository --repository-name praveenstore-app --region $AWS_REGION

# Step 2: Authenticate Docker with AWS ECR
echo "🔑 Authenticating Docker with AWS ECR..."
aws ecr get-login-password --region $AWS_REGION | docker login --username AWS --password-stdin $ECR_REPO

# Step 3: Build and Push Docker Image to ECR
echo "🐳 Building Docker image..."
docker build -t praveenstore-app .

echo "📌 Tagging Docker image..."
docker tag praveenstore-app:latest $ECR_REPO:latest

echo "⬆️ Pushing Docker image to AWS ECR..."
docker push $ECR_REPO:latest

# Step 4: Initialize Elastic Beanstalk application
echo "🛠️ Initializing Elastic Beanstalk application..."
eb init -p docker $EB_APP_NAME --region $AWS_REGION

# Step 5: Prepare `Dockerrun.aws.json`
echo "📝 Creating Dockerrun.aws.json..."
cat <<EOL > Dockerrun.aws.json
{
    "AWSEBDockerrunVersion": "2",
    "containerDefinitions": [
      {
        "name": "app",
        "image": "$ECR_REPO:latest",
        "memory": 500,
        "essential": true,
        "portMappings": [
          {
            "containerPort": 5000,
            "hostPort": 5000
          }
        ],
        "environment": [
          {
            "name": "DB_HOST",
            "value": "host.docker.internal"
          },
          {
            "name": "DB_USER",
            "value": "root"
          },
          {
            "name": "DB_PASSWORD",
            "value": "praveen987@"
          },
          {
            "name": "DB_NAME",
            "value": "praveenstore_db"
          },
          {
            "name": "GOOGLE_API_KEY",
            "value": "AIzaSyDPvYNiln3Jq3qxT20m_lc0tJH4Z4DG-78"
          }
        ]
      }
    ]
  }
EOL

# Step 6: Create Elastic Beanstalk environment
echo "🌐 Creating Elastic Beanstalk environment..."
eb create $EB_ENV_NAME --region $AWS_REGION --single

# Step 7: Zip the Dockerrun file
echo "📦 Creating deployment package..."
zip -r $DEPLOY_ZIP Dockerrun.aws.json

# Step 8: Upload ZIP file to S3
echo "☁️ Uploading deployment package to S3..."
aws s3 cp $DEPLOY_ZIP s3://$S3_BUCKET/

# Step 9: Create new Elastic Beanstalk application version
echo "📢 Creating new Elastic Beanstalk application version: $VERSION_LABEL..."
aws elasticbeanstalk create-application-version --application-name $EB_APP_NAME \
  --version-label $VERSION_LABEL --source-bundle S3Bucket="$S3_BUCKET",S3Key="$DEPLOY_ZIP"

# Step 10: Deploy new version to Elastic Beanstalk
echo "🚀 Updating Elastic Beanstalk environment..."
aws elasticbeanstalk update-environment --application-name $EB_APP_NAME \
  --environment-name $EB_ENV_NAME --version-label $VERSION_LABEL

echo "✅ Deployment completed! Check the AWS Elastic Beanstalk console for status."
