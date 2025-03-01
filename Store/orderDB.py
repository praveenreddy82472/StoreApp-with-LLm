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
    """Establish and return a new database connection."""
    return mysql.connector.connect(**db_config)

def create_orders_table():
    """Create the orders table in the database."""
    connection = get_connection()
    cursor = connection.cursor()

    # Create the orders table
    otbale  = cursor.execute("""
    CREATE TABLE IF NOT EXISTS orders (
        order_id INT AUTO_INCREMENT PRIMARY KEY,
        user_id INT NOT NULL,
        total_price DECIMAL(10, 2) NOT NULL,
        shipping_address TEXT NOT NULL,
        payment_method ENUM('COD', 'UPI', 'Card') NOT NULL,
        status ENUM('Pending', 'Completed', 'Cancelled') DEFAULT 'Pending',
        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
        FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE CASCADE
    );
    """)
    logging.info("Order Table Created")
    # Commit changes and close the connection
    connection.commit()
    cursor.close()
    connection.close()
    return otbale

def create_order_items_table():
    """Create the order_items table in the database."""
    connection = get_connection()
    cursor = connection.cursor()

    # Create the order_items table
    oitable  = cursor.execute("""
    CREATE TABLE IF NOT EXISTS order_items (
        id INT AUTO_INCREMENT PRIMARY KEY,
        order_id INT NOT NULL,
        product_id INT NOT NULL,
        quantity INT NOT NULL,
        price DECIMAL(10, 2) NOT NULL,  -- Store the price at the time of order
        FOREIGN KEY (order_id) REFERENCES orders(order_id) ON DELETE CASCADE,
        FOREIGN KEY (product_id) REFERENCES products(id) ON DELETE CASCADE
    );
    """)

    # Commit changes and close the connection
    connection.commit()
    cursor.close()
    connection.close()
    logging.info("Order items table created successfully!")
    return oitable

def get_user_by_id(user_id):
    """Fetch a user by their ID."""
    connection = get_connection()
    cursor = connection.cursor(dictionary=True)  # Use dictionary=True to get results as dictionaries

    # SQL query to fetch user by user_id
    cursor.execute("SELECT * FROM users WHERE id = %s", (user_id,))
    user = cursor.fetchone()

    # Close the cursor and connection
    cursor.close()
    connection.close()

    return user  # Return the user data as a dictionary or None if not found



