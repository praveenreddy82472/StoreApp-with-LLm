from PraveenStore.Store.db import DBConnection
from PraveenStore.utils.filehandling import FileHandling
from PraveenStore.utils.exception import PraveenStoreException
import sys
from PraveenStore.utils.logger import logging
from PraveenStore.Store.products import *
from PraveenStore.Store.productsDB import PDBConnection
from PraveenStore.Store.db import *
import json
from dotenv import load_dotenv
# Load environment variables from the .env file
# Explicitly specify the path to the .env file
dotenv_path = r"D:\PraveenPresCod\python\PraveenStore\constant\.env"
# Load environment variables
load_dotenv(dotenv_path=dotenv_path)
import os

class Main:
    def __init__(self, name=None, dob=None, email=None, pwd=None, db_params=None):
        self.name = name
        self.dob = dob
        self.email = email
        self.pwd = pwd
        self.user_data_file = 'user_data.json'
        # Accessing database credentials from environment variables
        db_host = os.getenv('DB_HOST')
        db_user = os.getenv('DB_USER')
        db_password = os.getenv('DB_PASSWORD')
        db_name = os.getenv('DB_NAME')

        print(f"DB_HOST={db_host}, DB_USER={db_user}, DB_PASSWORD={db_password}, DB_NAME={db_name}")

        # Create DB connection object
        product_db_params = {
            'host': db_host,
            'user': db_user,
            'password': db_password,
            'database': db_name
        }
        user_db_params = {
            'host': db_host,
            'user': db_user,
            'password': db_password,
            'database': db_name
        }
        # Single DB connection for both users and products
        self.db = DBConnection(user_db_params)
        self.db.connect()

        # Ensure tables are created
        self.db.create_user_table()# Create user table if not exists


        # Initialize the PDBConnection class
        self.product_db = PDBConnection(product_db_params)
        self.product_db.connect()
        # Create the products table
        self.product_db.create_products_table()# Create product table if not exists

        logging.info("Main class of the user and Product")

    def register(self):
        """Register a new user."""
        try:
            if not self.name:
                self.name = input("Enter your name: ")
            if not self.dob:
                self.dob = input("Enter your date of birth (YYYY-MM-DD): ")
            if not self.email:
                self.email = input("Enter your email: ")
            if not self.pwd:
                self.pwd = input("Enter your password: ")

            # Insert user data into the database
            self.db.insert_user(self.name, self.dob, self.email, self.pwd)

            # Save user data in files (txt, json, csv)
            user_data = {
                "Name": self.name,
                "DOB": self.dob,
                "Email": self.email,
                "Password": self.pwd
            }

            file_handler = FileHandling(user_data)
            file_handler.save_to_txt(r'D:\PraveenPresCod\python\PraveenStore\artifacts\users\store')
            file_handler.save_to_json(fr'D:\PraveenPresCod\python\PraveenStore\artifacts\users\{self.user_data_file}')
            file_handler.save_to_csv(r'D:\PraveenPresCod\python\PraveenStore\artifacts\users\store')

            print("Registration successful!")
            logging.info("User registration successful")
        except Exception as e:
            raise PraveenStoreException(e, sys)

    def login(self):
        """Login logic (check if user exists and passwords match)."""
        try:
            if self.db.authenticate_user(self.email, self.pwd):
                print("Login successful!")
                logging.info("Login successful")
                return True
            else:
                print("Login failed. Incorrect email or password.")
                logging.info("Login failed. Incorrect email or password.")
                return False
        except Exception as e:
            raise PraveenStoreException(e, sys)

    def get_product_details(self):
        """Collect product details."""
        name = input("Enter product name: ")
        category = input("Enter product category: ")
        price = float(input("Enter product price: "))
        description = input("Enter product description: ")
        # Prompt for nutritional information as text input
        nutritional_info = input("Enter product nutritional info (e.g., calories=200 kcal, fat=10 g, protein=5 g): ")

        image_url = input("Enter product image URL: ")

        return name, category, price, description, nutritional_info,image_url

    def save_user_to_files(self):
        """Save Users to the files"""
        user_data = {
            "Name": self.name,
            "DOB": self.dob,
            "Email": self.email,
            "Password": self.pwd
        }

        file_handler = FileHandling(user_data)

        try:
            file_handler.save_to_txt(r'D:\PraveenPresCod\python\PraveenStore\artifacts\user\Userdata')
            logging.info(f"Product data saved to TXT file for user '{self.name}'.")
        except Exception as e:
            logging.error(f"Error saving product data to TXT file for user '{self.name}': {e}")

        try:
            file_handler.save_to_json(fr'D:\PraveenPresCod\python\PraveenStore\artifacts\user\UserData')
            logging.info(f"Product data saved to JSON file for User '{self.name}'.")
        except Exception as e:
            logging.error(f"Error saving product data to JSON file for user '{self.name}': {e}")

        try:
            file_handler.save_to_csv(r'D:\PraveenPresCod\python\PraveenStore\artifacts\user\UserData')
            logging.info(f"Product data saved to CSV file for user '{self.name}'.")
        except Exception as e:
            logging.error(f"Error saving product data to CSV file for user '{self.name}': {e}")
