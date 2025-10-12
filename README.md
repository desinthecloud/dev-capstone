AI Image Description Generator

Capstone Project – DCT Developer Certification

Overview

This project demonstrates a full-stack AWS web application that uses Amazon Bedrock to generate AI-powered image descriptions. Users can upload images via a web interface, trigger serverless functions to analyze and describe them, and view all uploads in a dynamic gallery. The project highlights modern AWS cloud architecture, automation with GitHub Actions, and best practices in DevOps and CI/CD.

Application Workflow

Image Upload Interface

Hosted on AWS Fargate, accessed via a custom Route 53 domain.

The main page (index.html) routes users to upload.html via a Lambda Function URL.

Upload Process

Images are uploaded to an S3 bucket ($ACCOUNT_ID-upload-bucket-$REGION).

Metadata (image key, placeholder description) is stored in DynamoDB.

AI Description Generation

A Lambda trigger processes uploads, moves images to an asset bucket, and stores URLs.

Another Lambda integrates with Amazon Bedrock (Claude 3 Haiku) to generate descriptions, which are saved to DynamoDB.

Image Gallery

The main page fetches images and AI-generated descriptions from DynamoDB and displays them dynamically.

CI/CD Pipeline

Managed via GitHub Actions:

Commits to main trigger automated builds, Docker image creation, ECR updates, and ECS Fargate deployments.

Architecture Diagram

AWS Services Used:

AWS Fargate – Container hosting and scaling

Amazon S3 – Image and static asset storage

AWS Lambda – Serverless compute for upload, fetch, and AI workflows

Amazon DynamoDB – Metadata and description storage

Amazon Route 53 – Custom domain management

Amazon Bedrock – AI model integration (Claude 3 Haiku)

AWS CodePipeline / GitHub Actions – Continuous deployment

Amazon ECS & ECR – Container orchestration and image registry

Prerequisites

AWS CLI configured with Admin IAM permissions (or AWS CloudShell)

A registered domain name in Route 53

Docker installed (CloudShell includes it by default)

GitHub account (for version control and CI/CD)

Access to Amazon Bedrock Claude 3 Haiku model

Request access via the Bedrock console → Providers → Anthropic → Request Access

Setup & Deployment
Step 1: Infrastructure Setup

Create your DynamoDB table and S3 buckets:

TABLE_NAME="ImageMetadata"
aws dynamodb create-table \
  --table-name "$TABLE_NAME" \
  --attribute-definitions AttributeName=ImageKey,AttributeType=S \
  --key-schema AttributeName=ImageKey,KeyType=HASH \
  --billing-mode PAY_PER_REQUEST

ACCOUNT_ID=$(aws sts get-caller-identity --query "Account" --output text)
REGION="us-east-1"

aws s3 mb s3://"$ACCOUNT_ID"-website-assets-"$REGION"
aws s3 mb s3://"$ACCOUNT_ID"-upload-bucket-"$REGION"

Step 2: Lambda Functions

Build and deploy the following functions:

upload-page-function

fetch-image-function

ai-function

Each function:

Uses IAM roles with S3, DynamoDB, and Bedrock permissions.

Has an associated Function URL with public access.

Step 3: Build Web Application with Docker & ECS Fargate

Build the Docker image:

docker build -t my-ai-app .


Push to ECR:

aws ecr create-repository --repository-name my-ai-app
docker tag my-ai-app:latest $ACCOUNT_ID.dkr.ecr.$REGION.amazonaws.com/my-ai-app:latest
docker push $ACCOUNT_ID.dkr.ecr.$REGION.amazonaws.com/my-ai-app:latest


Deploy via ECS Fargate behind an ALB with HTTPS (SSL via ACM).

Step 4: Continuous Deployment (GitHub Actions)

Set up SSH and IAM credentials for GitHub Actions.

Add repository secrets:

AWS_ACCESS_KEY_ID

AWS_SECRET_ACCESS_KEY

AWS_REGION

Commit and push the workflow file to trigger automated deployments:

git add .github/workflows/deploy.yaml
git commit -m "Add GitHub Actions deploy workflow"
git push origin main

AI Integration

The AI layer leverages Amazon Bedrock and the Claude 3 Haiku model to:

Analyze uploaded images

Generate natural language descriptions.

Store results in DynamoDB

Example prompt flow:

“Describe this image in one sentence with a focus on its subject and mood.”

Key Learning Outcomes

Real-world Serverless + Containerized Architecture

Hands-on AWS CLI automation

Integration of AI with Bedrock

Implementation of CI/CD with GitHub Actions

Deployment using ECS Fargate + Route 53 + ACM

License

This project is part of the DCT Developer Capstone Program and is licensed for educational and demonstration purposes.
