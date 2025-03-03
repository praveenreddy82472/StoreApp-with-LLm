Praveen Store Application

Praveen Store is a full-fledged e-commerce application focused on organic farming and agriculture. The platform enables users to buy and sell products, track orders, and engage with AI-powered assistance. Built with Flask, MySQL, and AWS S3, it integrates modern cloud and AI solutions for enhanced functionality.

Features

User Authentication: Secure registration, login, and profile management.

Product Management: CRUD operations for products, with images stored on AWS S3.

Shopping Cart: Add/remove products and checkout functionality.

Order Management: Track orders, view history, and manage transactions.

Payment Integration: Supports cash payment (UPI and card payment planned).

Blog System: Dynamic blog content related to organic farming and agriculture.

AI Chatbot: A generative AI chatbot powered by Google Gemini that responds to customer queries and assists with product recommendations.

AI-Powered Chatbot

The chatbot utilizes function calling with Google Gemini LLM to:

Query the MySQL database for product availability, pricing, and user orders.

Provide intelligent recommendations based on user behavior.

Answer general inquiries about organic farming and store policies.

Tech Stack

Backend

Python (Flask): Core backend framework

MySQL: Relational database for storing user, product, and order data

Google Gemini API: Generative AI-powered chatbot integration

AWS S3: Cloud storage for product images

Frontend

HTML, CSS, JavaScript: Core frontend technologies

Bootstrap: Responsive UI framework

Jinja2: Templating engine for rendering dynamic content

Deployment & CI/CD

Docker: Containerized deployment

GitHub Actions: Automated CI/CD pipeline for deployment

AWS EC2: Hosting the Flask application

Amazon ECR: Container registry for storing Docker images

Installation & Setup

Clone the repository:

git clone https://github.com/praveenreddy82472/StoreApp-with-LLm.git
cd StoreApp-with-LLm

Set up a virtual environment:

python3 -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

Install dependencies:

pip install -r requirements.txt

Configure environment variables:

export FLASK_APP=app.py
export DATABASE_URL=mysql://user:password@localhost/storeapp
export AWS_ACCESS_KEY_ID=your_aws_key
export AWS_SECRET_ACCESS_KEY=your_aws_secret
export GOOGLE_GEMINI_API_KEY=your_api_key

Run the application:

flask run --host=0.0.0.0 --port=8080

Docker Deployment

Build and run the Docker container:

docker build -t storeapp .
docker run -p 8080:8080 storeapp

Deploy using AWS Elastic Beanstalk:

eb init -p docker storeapp
eb create storeapp-env

CI/CD with GitHub Actions

The application is automatically built and deployed using GitHub Actions:

On push to main branch: Docker image is built and pushed to Amazon ECR.

On new release: AWS Elastic Beanstalk deployment is triggered.

Workflow Configuration (GitHub Actions)

.github/workflows/deploy.yml

name: Deploy to AWS

on:
  push:
    branches:
      - main

jobs:
  deploy:
    runs-on: ubuntu-latest

    steps:
    - name: Checkout repository
      uses: actions/checkout@v3

    - name: Login to Amazon ECR
      run: aws ecr get-login-password --region us-east-1 | docker login --username AWS --password-stdin <aws-account-id>.dkr.ecr.us-east-1.amazonaws.com

    - name: Build and push Docker image
      run: |
        docker build -t storeapp .
        docker tag storeapp <aws-account-id>.dkr.ecr.us-east-1.amazonaws.com/storeapp:latest
        docker push <aws-account-id>.dkr.ecr.us-east-1.amazonaws.com/storeapp:latest

    - name: Deploy to AWS Elastic Beanstalk
      run: eb deploy storeapp-env

Roadmap

✅ Implement AI-powered chatbot with Google Gemini

✅ Automate deployment with GitHub Actions

🔜 Integrate UPI and credit card payments

🔜 Implement recommendation engine for personalized shopping

License

This project is licensed under the MIT License.

Contributors

Praveen Thoomati - GitHub