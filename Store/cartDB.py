import mysql.connector
from PraveenStore.utils.logger import logging

# Database configuration
db_config = {'host': 'localhost', 'user': 'root', 'password': 'praveen987@', 'database': 'praveenstore_db'}

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
    cursor.execute("""
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

    # Commit changes and close the connection
    connection.commit()
    cursor.close()
    connection.close()

create_cart_table()
#print("Cart table created successfully!")
