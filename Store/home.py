from db import DBConnection
from PraveenStore.utils.filehandling import FileHandling  # Import your FileHandling class
from PraveenStore.utils.exception import PraveenStoreException
import sys
from PraveenStore.utils.log import *
from products import *
from productsDB import PDBConnection
from db import *
import json

class Main:
    def __init__(self, name=None, dob=None, email=None, pwd=None, db_params=None):
        self.name = name
        self.dob = dob
        self.email = email
        self.pwd = pwd
        self.user_data_file = 'user_data.json'

        # Single DB connection for both users and products
        self.db = DBConnection(db_params)
        self.db.connect()

        # Ensure tables are created
        self.db.create_user_table()# Create user table if not exists


        # Initialize the PDBConnection class
        self.product_db = PDBConnection(db_params)
        self.product_db.connect()
        # Create the products table
        self.product_db.create_products_table()# Create product table if not exists

        logging.info("Initialized Main class with one database connection")

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

    def save_product(self):
        """Save product to the database and files."""
        try:
            # Collect product details
            name, category, price, description, nutritional_info, image_url = self.get_product_details()

            # Insert product into database
            self.product_db.insert_product(name, category, price, description, nutritional_info, image_url)

            # Save product details to files
            product_data = {
                "Name": name,
                "Category": category,
                "Price": price,
                "Description": description,
                "Nutritional Info": nutritional_info,
                "Image URL": image_url
            }

            file_handler = FileHandling(product_data)
            file_handler.save_to_txt(r'D:\PraveenPresCod\python\PraveenStore\artifacts\products\products')
            file_handler.save_to_json(r'D:\PraveenPresCod\python\PraveenStore\artifacts\products\product_data.json')
            file_handler.save_to_csv(r'D:\PraveenPresCod\python\PraveenStore\artifacts\products\products')

            print(f"Product '{name}' added successfully!")
            logging.info(f"Product '{name}' added successfully!")
        except Exception as e:
            raise PraveenStoreException(e, sys)

if __name__ == "__main__":
    db_params = {
        'host': 'localhost',
        'user': 'root',
        'password': 'praveen987@',
        'database': 'praveenstore_db'
    }

    user_choice = input("Do you want to (register/login/save_product): ").lower()

    if user_choice == "register":
        name = input("Enter your name: ")
        dob = input("Enter your DOB (YYYY-MM-DD): ")
        email = input("Enter your email: ")
        password = input("Enter your password: ")

        app = Main(name=name, dob=dob, email=email, pwd=password, db_params=db_params)
        app.register()

    elif user_choice == "login":
        email = input("Enter your email: ")
        password = input("Enter your password: ")

        app = Main(email=email, pwd=password, db_params=db_params)

        if app.login():
            print("Login successful!")
        else:
            print("Login failed. Please try again.")

    elif user_choice == "save_product":
        app = Main(db_params=db_params)  # Initialize the app
        app.save_product()  # Use the existing save_product method
