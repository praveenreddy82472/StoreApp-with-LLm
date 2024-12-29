import mysql.connector
from mysql.connector import Error
from PraveenStore.utils.log import logging


class PDBConnection:
    def __init__(self, db_params):
        self.host = db_params.get('host')
        self.user = db_params.get('user')
        self.password = db_params.get('password')
        self.database = db_params.get('database')
        self.connection = None

    def connect(self):
        """Establish the connection to the database."""
        try:
            self.connection = mysql.connector.connect(
                host=self.host,
                user=self.user,
                password=self.password,
                database=self.database
            )
            if self.connection.is_connected():
                logging.info("Connection to the database successful.")
            else:
                logging.error("Failed to connect to the database.")
        except Error as e:
            logging.error(f"Error connecting to MySQL: {e}")

    def create_products_table(self):
        """Create the products table if it doesn't already exist."""
        try:
            cursor = self.connection.cursor()
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS products (
                    id INT AUTO_INCREMENT PRIMARY KEY,
                    name VARCHAR(255) NOT NULL,
                    category VARCHAR(255) NOT NULL,
                    price FLOAT NOT NULL,
                    description TEXT,
                    nutritional_info TEXT,
                    image_url VARCHAR(255),
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                )
            """)
            logging.info("Table `products` is ready.")
        except Error as e:
            logging.error(f"Error creating table: {e}")

    def insert_product(self, name, category, price, description, nutritional_info, image_url):
        """Insert a new product into the products table."""
        try:
            cursor = self.connection.cursor()
            cursor.execute("""
                INSERT INTO products (name, category, price, description, nutritional_info, image_url)
                VALUES (%s, %s, %s, %s, %s, %s)
            """, (name, category, price, description, nutritional_info, image_url))
            self.connection.commit()
            logging.info(f"Product '{name}' added successfully to the database.")
        except Error as e:
            logging.error(f"Error inserting product '{name}': {e}")

    def update_product(self, product_id, name, category, price, description, nutritional_info, image_url):
        """Update an existing product in the database."""
        try:
            cursor = self.connection.cursor()
            cursor.execute("""
                UPDATE products
                SET name = %s, category = %s, price = %s, description = %s, nutritional_info = %s, image_url = %s
                WHERE id = %s
            """, (name, category, price, description, nutritional_info, image_url, product_id))
            self.connection.commit()
            logging.info(f"Product with ID {product_id} updated successfully.")
        except Error as e:
            logging.error(f"Error updating product with ID {product_id}: {e}")

    def delete_product(self, product_id):
        """Delete a product from the database."""
        try:
            cursor = self.connection.cursor()
            cursor.execute("DELETE FROM products WHERE id = %s", (product_id,))
            self.connection.commit()
            logging.info(f"Product with ID {product_id} deleted successfully.")
        except Error as e:
            logging.error(f"Error deleting product with ID {product_id}: {e}")

    def fetch_all_products(self):
        """Fetch all products from the products table."""
        try:
            cursor = self.connection.cursor(dictionary=True)
            cursor.execute("SELECT * FROM products")
            products = cursor.fetchall()
            logging.info(f"Fetched {len(products)} products from the database.")
            return products
        except Error as e:
            logging.error(f"Error fetching products: {e}")
            return []

    def fetch_product_by_id(self, product_id):
        """Fetch a product by its ID."""
        try:
            cursor = self.connection.cursor(dictionary=True)
            cursor.execute("SELECT * FROM products WHERE id = %s", (product_id,))
            product = cursor.fetchone()
            if product:
                logging.info(f"Fetched product with ID {product_id}.")
            else:
                logging.info(f"No product found with ID {product_id}.")
            return product
        except Error as e:
            logging.error(f"Error fetching product with ID {product_id}: {e}")
            return None

    def close_connection(self):
        """Close the database connection."""
        try:
            if self.connection.is_connected():
                self.connection.close()
                logging.info("Database connection closed.")
        except Error as e:
            logging.error(f"Error closing database connection: {e}")
