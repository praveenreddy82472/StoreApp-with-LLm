import mysql.connector
from mysql.connector import Error
from werkzeug.security import generate_password_hash, check_password_hash
from werkzeug.utils import secure_filename  # For password hashing
import os
from PraveenStore.utils.log import logging


class DBConnection:
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
                print("Connection successful.")
            else:
                logging.error("Failed to connect to the database.")
                print("Failed to connect.")
        except Error as e:
            logging.error(f"Error connecting to MySQL: {e}")
            print(f"Error connecting to MySQL: {e}")

    def create_user_table(self):
        """Create the users table if it doesn't already exist."""
        try:
            cursor = self.connection.cursor()
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS users (
                    id INT AUTO_INCREMENT PRIMARY KEY,
                    name VARCHAR(255) NOT NULL,
                    dob DATE NOT NULL,
                    email VARCHAR(255) NOT NULL UNIQUE,
                    password VARCHAR(255) NOT NULL,
                    profile_picture VARCHAR(255),  # Add profile_picture column
                    role ENUM('admin', 'customer') DEFAULT 'customer',
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                )
            """)
            logging.info("Table `users` is ready.")
            print("Table `users` is ready.")
        except Error as e:
            logging.error(f"Error creating table: {e}")
            print(f"Error creating table: {e}")

    def insert_user(self, name, dob, email, password, profile_picture=None, role='customer'):
        """Insert a new user into the users table."""
        hashed_password = generate_password_hash(password)  # Hash the password
        try:
            cursor = self.connection.cursor()
            cursor.execute("""
                INSERT INTO users (name, dob, email, password, profile_picture, role)
                VALUES (%s, %s, %s, %s, %s, %s)
            """, (name, dob, email, hashed_password, profile_picture, role))
            self.connection.commit()
            logging.info(f"User '{name}' added successfully.")
            print(f"User '{name}' added successfully.")
        except Error as e:
            logging.error(f"Error inserting user '{name}': {e}")
            print(f"Error inserting user '{name}': {e}")

    def authenticate_user(self, email, password):
        """Authenticate user login by checking email and password."""
        try:
            cursor = self.connection.cursor(dictionary=True)
            cursor.execute("SELECT * FROM users WHERE email = %s;", (email,))
            user = cursor.fetchone()

            # Verify the password hash
            if user and check_password_hash(user['password'], password):
                logging.info(f"User '{email}' authenticated successfully.")
                return user  # Return the user details if authentication succeeds
            else:
                logging.warning(f"Failed authentication attempt for user '{email}'.")
                return None  # Return None if authentication fails
        except Error as e:
            logging.error(f"Error authenticating user '{email}': {e}")
            print(f"Error authenticating user: {e}")
            return None  # Return None in case of an error

    def check_email_exists(self, email):
        """Check if an email already exists in the users table."""
        try:
            cursor = self.connection.cursor()
            cursor.execute("SELECT * FROM users WHERE email = %s;", (email,))
            user = cursor.fetchone()
            exists = user is not None
            logging.info(f"Email check for '{email}': {exists}")
            return exists  # Return True if email exists, else False
        except Error as e:
            logging.error(f"Error checking if email exists for '{email}': {e}")
            print(f"Error checking if email exists: {e}")
            return False

    def get_user_by_id(self, user_id):
        """Fetch user by their ID."""
        try:
            cursor = self.connection.cursor()
            query = "SELECT * FROM users WHERE id = %s"
            cursor.execute(query, (user_id,))

            # Fetch the result
            user = cursor.fetchone()

            # If a user is found, create a dictionary with column names as keys
            if user:
                columns = [desc[0] for desc in cursor.description]  # Get column names
                logging.info(f"User with ID {user_id} fetched successfully.")
                return dict(zip(columns, user))  # Return a dictionary with column names as keys
            else:
                logging.warning(f"No user found with ID {user_id}.")
                return None
        except Error as e:
            logging.error(f"Error fetching user by ID {user_id}: {e}")
            print(f"Error checking user by ID: {e}")
            return None

    def update_user_details(self, user_id, name=None, dob=None, email=None, profile_picture=None):
        """Update user details."""
        try:
            query = "UPDATE users SET "
            updates = []
            params = []

            # Only update the fields that were changed
            if name:
                updates.append("name = %s")
                params.append(name)
            if dob:
                updates.append("dob = %s")
                params.append(dob)
            if email:
                updates.append("email = %s")
                params.append(email)
            if profile_picture:
                updates.append("profile_picture = %s")
                params.append(profile_picture)

            query += ", ".join(updates) + " WHERE id = %s"
            params.append(user_id)

            # Execute the query
            cursor = self.connection.cursor()
            cursor.execute(query, tuple(params))
            self.connection.commit()

            logging.info(f"User details for ID {user_id} updated successfully.")
            print(f"User details for ID {user_id} updated successfully.")
            return True
        except Exception as e:
            logging.error(f"Error updating user details for ID {user_id}: {e}")
            print(f"Error updating user details: {e}")
            return False
