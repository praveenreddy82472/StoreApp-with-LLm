import google.generativeai as genai
import mysql.connector
import os
from dotenv import load_dotenv
import logging

logging.basicConfig(level=logging.ERROR)  # Set to ERROR to suppress warnings

# Load environment variables from the .env file
dotenv_path = r"D:\PraveenPresCod\python\PraveenStore\constant\.env"
load_dotenv(dotenv_path=dotenv_path)

# Fetch API key for Google Generative AI
GOOGLE_API_KEY = os.getenv("GOOGLE_API_KEY")  # Ensure this is set in your environment
client = genai.configure(api_key=GOOGLE_API_KEY)

# Database connection setup from environment variables
db_host = os.getenv('DB_HOST')
db_user = os.getenv('DB_USER')
db_password = os.getenv('DB_PASSWORD')
db_name = os.getenv('DB_NAME')

def get_db_connection():
    return mysql.connector.connect(
        host=db_host,
        user=db_user,
        password=db_password,
        database=db_name
    )

def list_tables(conn):
    """Retrieve the names of all tables in the database."""
    cursor = conn.cursor()
    cursor.execute("SHOW TABLES")
    tables = cursor.fetchall()
    return [t[0] for t in tables]

def describe_table(conn, table_name):
    """Look up the schema of a table in the database."""
    cursor = conn.cursor()
    cursor.execute(f"DESCRIBE {table_name};")
    schema = cursor.fetchall()
    return [(col[0], col[1]) for col in schema]

def execute_query(conn, sql):
    """Execute a SELECT statement, returning the results."""
    cursor = conn.cursor()
    cursor.execute(sql)
    return cursor.fetchall()

# Define the instruction for the LLM chatbot
instruction = """
You are a helpful chatbot that can interact with an SQL database for an Organic Farming store and also provide general knowledge.

For store-related queries:
- Use `list_tables` to see what tables are present in the database.
- Use `describe_table` to understand the schema of any given table.
- Use `execute_query` to issue SQL SELECT queries to fetch the relevant data, such as product details, user orders, etc.
- Answer queries such as 'Tell me about the products' or 'What’s the latest product in the store?' by fetching data from the products table.

For general knowledge inquiries:
- You can answer questions on a wide variety of topics including recipes, diet-friendly product suggestions, and more.
- For example, you can suggest a biryani recipe or provide information about popular dishes or cooking tips.

Your role is to combine knowledge from the store's database (for store-specific queries) and general knowledge (for broader topics) to assist the user effectively.
"""


# Function to start the chatbot with database functionality
def start_chat(user_query):
    tools = [
        {
            "function_declarations": [
                {
                    "name": "list_tables",
                    "description": "List all tables in the database"
                },
                {
                    "name": "describe_table",
                    "description": "Describe the structure of a database table",
                    "parameters": {
                        "type": "object",
                        "properties": {
                            "table_name": {"type": "string", "description": "Name of the table to describe"}
                        },
                        "required": ["table_name"]
                    }
                },
                {
                    "name": "execute_query",
                    "description": "Execute a query to fetch data from the database",
                    "parameters": {
                        "type": "object",
                        "properties": {
                            "sql": {"type": "string", "description": "The SQL query to execute"}
                        },
                        "required": ["sql"]
                    }
                }
            ]
        }
    ]

    model = genai.GenerativeModel(
        "models/gemini-1.5-pro-latest",
        tools=tools,
        system_instruction=instruction
    )

    chat = model.start_chat(enable_automatic_function_calling=True)

    try:
        response = chat.send_message(user_query).text  # Use the model for other types of queries
        print("Model Response:", response)  # Log the response for debugging
        return response  # Return the chatbot's response
    except Exception as e:
        print(f"Error during chat processing: {e}")
        return "Sorry, an error occurred while processing your request."
