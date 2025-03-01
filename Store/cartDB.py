import mysql.connector
from utils.logger import logging
import os 
from dotenv import load_dotenv
# Load environment variables from the .env file
# Explicitly specify the path to the .env file
dotenv_path = r"D:\PraveenPresCod\python\PraveenStore\constant\.env"
# Load environment variables
load_dotenv(dotenv_path=dotenv_path)
db_host = os.getenv('DB_HOST')
db_user = os.getenv('DB_USER')
db_password = os.getenv('DB_PASSWORD')
db_name = os.getenv('DB_NAME')
# Create DB connection object
db_config = {
            'host': db_host,
            'user': db_user,
            'password': db_password,
            'database': db_name
}

def get_connection():
    logging.info("---- CartDB Connection----")
    """Establish and return a new database connection."""
    return mysql.connector.connect(**db_config)

def create_cart_table():
    logging.info("Cartdb Table created")
    """Create the cart table in the database."""
    connection = get_connection()
    cursor = connection.cursor()

    # Create the cart table
    table = cursor.execute("""
    CREATE TABLE IF NOT EXISTS cart (
        cart_id INT AUTO_INCREMENT PRIMARY KEY,
        user_id INT NOT NULL,
        product_id INT NOT NULL,
        quantity INT NOT NULL,
        FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE CASCADE,
        FOREIGN KEY (product_id) REFERENCES products(id) ON DELETE CASCADE,
        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
    );
    """)
    print('Table created')
    # Commit changes and close the connection
    connection.commit()
    cursor.close()
    connection.close()
    return table
