# admin_utils.py
from flask import session, flash, redirect, url_for
from PraveenStore.utils .logger import logging
from PraveenStore.Store.db import DBConnection

from functools import wraps


user_db_params = {'host': 'localhost', 'user': 'root', 'password': 'praveen987@', 'database': 'praveenstore_db'}
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
