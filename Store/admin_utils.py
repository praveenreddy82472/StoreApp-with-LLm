# admin_utils.py
from flask import session, flash, redirect, url_for
from utils .logger import logging
from Store.db import DBConnection

from functools import wraps
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

user_db_params = {
            'host': db_host,
            'user': db_user,
            'password': db_password,
            'database': db_name
}
user_db = DBConnection(user_db_params)
user_db.connect()
# Admin-only access decorator
def admin_only(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        logging.info("------ Admin Decorator -----")
        if not session.get('user_id'):  # Ensure the user is logged in
            logging.info("Please log in to access this page.", "error")
            flash("Please log in to access this page.", "error")
            return redirect(url_for('login'))  # Redirect to login if not logged in

        # Fetch the logged-in user details
        user = user_db.get_user_by_id(session['user_id'])
        if user['role'] != 'admin':  # Check if the user is an admin
            logging.info("Access denied! Admins only.", "error")
            flash("Access denied! Admins only.", "error")
            return redirect(url_for('products'))  # Redirect to products page if not admin

        return f(*args, **kwargs)

    return decorated_function
