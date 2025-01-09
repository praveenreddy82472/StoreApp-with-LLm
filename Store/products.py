from PraveenStore.utils.logger import logging
from PraveenStore.Store.productsDB import PDBConnection
from PraveenStore.utils.filehandling import FileHandling
from dotenv import load_dotenv
# Load environment variables from the .env file
# Explicitly specify the path to the .env file
dotenv_path = r"D:\PraveenPresCod\python\PraveenStore\constant\.env"
# Load environment variables
load_dotenv(dotenv_path=dotenv_path)
import os
class Product:
    def __init__(self, name, category, price, description, nutritional_info, image_url, db_params=None):
        self.name = name
        self.category = category
        self.price = price
        self.description = description
        self.nutritional_info = nutritional_info
        self.image_url = image_url
        # Accessing database credentials from environment variables
        db_host = os.getenv('DB_HOST')
        db_user = os.getenv('DB_USER')
        db_password = os.getenv('DB_PASSWORD')
        db_name = os.getenv('DB_NAME')

        # Create DB connection object
        product_db_params = {
            'host': db_host,
            'user': db_user,
            'password': db_password,
            'database': db_name
        }
        # Create DB connection object
        self.db = PDBConnection(product_db_params)
        self.db.connect()  # Establish the connection
        self.db.create_products_table()  # Ensure the table is created
        logging.info(f"Product object initialized: {self.name}, {self.category}, {self.price}")

    def save_to_db(self):
        """Save product data to the database."""
        try:
            self.db.insert_product(self.name, self.category, self.price, self.description, self.nutritional_info, self.image_url)
            logging.info(f"Product '{self.name}' saved to database.")
        except Exception as e:
            logging.error(f"Error saving product '{self.name}' to database: {e}")

    def update_product(self, product_id):
        """Update existing product data in the database."""
        try:
            self.db.update_product(product_id, self.name, self.category, self.price, self.description, self.nutritional_info, self.image_url)
            logging.info(f"Product '{self.name}' updated in database (ID: {product_id}).")
        except Exception as e:
            logging.error(f"Error updating product '{self.name}' in database: {e}")

    def delete_product(self, product_id):
        """Delete product from the database."""
        try:
            self.db.delete_product(product_id)
            logging.info(f"Product deleted from database (ID: {product_id}).")
        except Exception as e:
            logging.error(f"Error deleting product from database (ID: {product_id}): {e}")

    def save_to_files(self):
        """Save product data to JSON and CSV files using the FileHandler class."""
        product_data = [{
            'name': self.name,
            'category': self.category,
            'price': self.price,
            'description': self.description,
            'nutritional_info': self.nutritional_info,
            'image_url': self.image_url
        }]

        file_handler = FileHandling(product_data)

        try:
            file_handler.save_to_txt(r'D:\PraveenPresCod\python\PraveenStore\artifacts\products\products')
            logging.info(f"Product data saved to TXT file for product '{self.name}'.")
        except Exception as e:
            logging.error(f"Error saving product data to TXT file for product '{self.name}': {e}")

        try:
            file_handler.save_to_json(r'D:\PraveenPresCod\python\PraveenStore\artifacts\products\products')
            logging.info(f"Product data saved to JSON file for product '{self.name}'.")
        except Exception as e:
            logging.error(f"Error saving product data to JSON file for product '{self.name}': {e}")

        try:
            file_handler.save_to_json(r'D:\PraveenPresCod\python\PraveenStore\artifacts\products\products')
            logging.info(f"Product data saved to CSV file for product '{self.name}'.")
        except Exception as e:
            logging.error(f"Error saving product data to CSV file for product '{self.name}': {e}")

    def close_db_connection(self):
        """Close the database connection."""
        try:
            self.db.close_connection()
            logging.info(f"Database connection closed for product '{self.name}'.")
        except Exception as e:
            logging.error(f"Error closing database connection for product '{self.name}': {e}")
