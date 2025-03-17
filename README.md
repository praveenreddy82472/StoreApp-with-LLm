# Praveen Store - E-Commerce Platform for Organic Farming

Praveen Store is a feature-rich e-commerce application dedicated to organic farming and agriculture. It enables users to buy and sell products, track orders, and interact with an AI-powered assistant. The platform is built using Flask, MySQL, and AWS S3, integrating modern cloud and AI solutions for seamless functionality.

## 🚀 Features

- **User Authentication**: Secure registration, login, and profile management.
- **Product Management**: CRUD operations for products, with images stored on AWS S3.
- **Shopping Cart**: Add/remove products and checkout functionality.
- **Order Management**: Track orders, view history, and manage transactions.
- **Payment Integration**: Supports cash payments (UPI and card payments planned).
- **Blog System**: Dynamic blog content focused on organic farming and agriculture.
- **AI Chatbot**: Google Gemini-powered chatbot for customer queries and product recommendations.

## 🤖 AI-Powered Chatbot

The chatbot utilizes function calling with Google Gemini LLM to:

- Query the MySQL database for product availability, pricing, and user orders.
- Provide intelligent recommendations based on user behavior.
- Answer general inquiries about organic farming and store policies.

## 🛠 Tech Stack

### Backend
- **Python (Flask)**: Core backend framework
- **MySQL**: Relational database for user, product, and order data
- **Google Gemini API**: Generative AI-powered chatbot integration
- **AWS S3**: Cloud storage for product images

### Frontend
- **HTML, CSS, JavaScript**: Core frontend technologies
- **Bootstrap**: Responsive UI framework
- **Jinja2**: Templating engine for rendering dynamic content

### Deployment & CI/CD
- **Docker**: Containerized deployment
- **GitHub Actions**: Automated CI/CD pipeline for deployment
- **AWS EC2**: Hosting the Flask application
- **Amazon ECR**: Container registry for storing Docker images

## 📦 Installation & Setup

### Clone the repository
```sh
git clone https://github.com/praveenreddy82472/StoreApp-with-LLm.git
cd StoreApp-with-LLm
```

### Set up a virtual environment
```sh
python3 -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
```

### Install dependencies
```sh
pip install -r requirements.txt
```

### Configure environment variables
```sh
export FLASK_APP=app.py
export DATABASE_URL=mysql://user:password@localhost/storeapp
export AWS_ACCESS_KEY_ID=your_aws_key
export AWS_SECRET_ACCESS_KEY=your_aws_secret
export GOOGLE_GEMINI_API_KEY=your_api_key
```

### Run the application
```sh
flask run --host=0.0.0.0 --port=8080
```

## 🐳 Docker Deployment

### Build and run the Docker container
```sh
docker build -t storeapp .
docker run -p 8080:8080 storeapp
```

### Deploy using AWS Elastic Beanstalk
```sh
eb init -p docker storeapp
eb create storeapp-env
```

## ⚡ CI/CD with GitHub Actions

The application is automatically built and deployed using GitHub Actions:

- **On push to the main branch**: Docker image is built and pushed to Amazon ECR.
- **On new release**: AWS Elastic Beanstalk deployment is triggered.

### GitHub Actions Workflow Configuration

`.github/workflows/deploy.yml`
```yaml
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
```

## 📅 Roadmap

✅ Implement AI-powered chatbot with Google Gemini  
✅ Automate deployment with GitHub Actions  
🔜 Integrate UPI and credit card payments  
🔜 Implement recommendation engine for personalized shopping  

## 📜 License

This project is licensed under the **MIT License**.

## 👨‍💻 Contributors

**Praveen Kumar Thumati** - [GitHub](https://github.com/praveenreddy82472)
