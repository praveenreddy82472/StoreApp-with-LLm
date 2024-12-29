from flask import Flask, render_template, request, redirect, url_for, flash, session, send_from_directory, jsonify
from Store.db import DBConnection
from Store.productsDB import PDBConnection
from Store.cartDB import get_connection
from Store.orderDB import get_connection,get_user_by_id
from werkzeug.utils import secure_filename
from Store.blog import save_to_json, get_all_posts, save_image
import datetime
import os
import boto3
from Store.admin_utils import admin_only


app = Flask(__name__)
app.secret_key = 'your_secret_key_here'

# Initialize database connections
user_db_params = {'host': 'localhost', 'user': 'root', 'password': 'praveen987@', 'database': 'praveenstore_db'}
product_db_params = {'host': 'localhost', 'user': 'root', 'password': 'praveen987@', 'database': 'praveenstore_db'}
order_manage= {'host': 'localhost', 'user': 'root', 'password': 'praveen987@', 'database': 'praveenstore_db'}

user_db = DBConnection(user_db_params)
user_db.connect()

product_db = PDBConnection(product_db_params)
product_db.connect()


# Configuration
UPLOAD_FOLDER = 'static/uploads'
BLOGS_FOLDER = 'static/blogs/'
PRODUCTS_FOLDER = 'static/images'
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER
app.config['BLOGS_FOLDER'] = BLOGS_FOLDER
app.config['PRODUCTS_FOLDER'] = PRODUCTS_FOLDER

app.config['ALLOWED_EXTENSIONS'] = {'png', 'jpg', 'jpeg', 'gif'}



# Home page route
@app.route('/')
def home():
    return render_template('home.html')


from flask import request, redirect, url_for, flash, render_template
import os


# Assuming you have the `user_db` object (your DBConnection) set up
@app.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        name = request.form['name']
        dob = request.form['dob']
        email = request.form['email']
        pwd = request.form['pwd']

        # Check if email already exists
        if user_db.check_email_exists(email):
            flash("Email already registered! Please log in.", "error")
            return redirect(url_for('login'))

        # Handle profile picture upload if provided
        profile_picture = None
        if 'profile_picture' in request.files and request.files['profile_picture'].filename:
            picture = request.files['profile_picture']
            if allowed_file(picture.filename):  # Validate file type
                filename = secure_filename(picture.filename)
                # Save the picture in the specified folder
                picture.save(os.path.join(app.config['UPLOAD_FOLDER'], filename))
                profile_picture = filename

        # Insert the user into the database with the profile picture path (or None if no picture)
        user_db.insert_user(name, dob, email, pwd, profile_picture)

        flash("Registration successful! Please log in.", "success")
        return redirect(url_for('login'))

    return render_template('register.html')


# Login route
@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        email = request.form['email']
        pwd = request.form['pwd']

        # Authenticate user
        user = user_db.authenticate_user(email, pwd)

        if user:  # If authentication succeeds
            session['user_id'] = user['id']  # Save user ID in the session
            session['user_name'] = user['name']  # Optionally save the user's name
            flash("Login successful!", "success")
            return redirect(url_for('dashboard'))  # Redirect to the dashboard
        else:  # Authentication failed
            flash("Invalid email or password. Please try again.", "error")
            return render_template('login.html')

    return render_template('login.html')

# Dashboard route
@app.route('/dashboard')
def dashboard():
    if not session.get('user_id'):  # Ensure user is logged in
        flash("Please log in to access the dashboard.", "error")
        return redirect(url_for('login'))

    # Fetch user details from the database
    user = user_db.get_user_by_id(session['user_id'])

    return render_template('dashboard.html', user=user)


# Function to check allowed file extensions
def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in app.config['ALLOWED_EXTENSIONS']


# Ensure the 'uploads' folder exists
if not os.path.exists(app.config['UPLOAD_FOLDER']):
    os.makedirs(app.config['UPLOAD_FOLDER'])


# Route to serve uploaded files
@app.route('/uploads/user_images')
def uploaded_file(filename):
    return send_from_directory(app.config['UPLOAD_FOLDER'], filename)


# Profile Picture Update Route
@app.route('/update_profile_picture', methods=['POST'])
def update_profile_picture():
    if 'profile_picture' not in request.files:
        flash("No file part", "error")
        return redirect(url_for('profile'))

    file = request.files['profile_picture']
    if file.filename == '':
        flash("No selected file", "error")
        return redirect(url_for('profile'))

    if file and allowed_file(file.filename):
        filename = secure_filename(file.filename)
        filepath = os.path.join(app.config['UPLOAD_FOLDER'], filename)
        file.save(filepath)

        # Get current user ID
        user_id = session.get('user_id')

        # Update the user's profile picture in the database
        user_db.update_profile_picture(user_id, filename)

        flash("Profile picture updated successfully!", "success")
        return redirect(url_for('profile'))


@app.route('/profile')
def profile():
    if not session.get('user_id'):
        flash("Please log in to view your profile.", "error")
        return redirect(url_for('login'))

    user_id = session['user_id']  # Get the user ID from session
    # Fetch user profile details from the database
    user = user_db.get_user_by_id(user_id)
    # Fetch the orders for the logged-in user
    connection = get_connection()
    cursor = connection.cursor()

    # Fetch orders using the user_id
    cursor.execute("""
            SELECT order_id, user_id, total_price, shipping_address, payment_method, status, created_at 
            FROM orders 
            WHERE user_id = %s
        """, (user['id'],))

    orders = cursor.fetchall()  # List of tuples: (order_id, user_id, total_price, shipping_address, payment_method, status, created_at)

    # Close connection
    cursor.close()
    connection.close()
    # Debugging: Print the user data to check
    print(user)  # This should print the dictionary with user details

    return render_template('profile.html', user=user,orders=orders)



@app.route('/edit_profile', methods=['GET', 'POST'])
def edit_profile():
    if not session.get('user_id'):  # Ensure user is logged in
        flash("Please log in to edit your profile.", "error")
        return redirect(url_for('login'))

    # Fetch the current user details
    user = user_db.get_user_by_id(session['user_id'])

    if request.method == 'POST':
        # Fetch updated details from the form
        name = request.form['name'] or user['name']  # Use existing name if not changed
        dob = request.form['dob'] or user['dob']  # Use existing dob if not changed
        email = request.form['email'] or user['email']  # Use existing email if not changed

        # Handle profile picture upload if provided
        profile_picture = None
        if 'profile_picture' in request.files and request.files['profile_picture'].filename:
            picture = request.files['profile_picture']
            if allowed_file(picture.filename):  # Validate file type
                filename = secure_filename(picture.filename)

                # Sanitize username to create a valid folder name
                sanitized_name = user['name'].replace(" ", "_").replace("/", "_")  # Replace spaces and slashes with underscores
                username_folder = os.path.join(app.config['UPLOAD_FOLDER'], sanitized_name)

                # Create the folder if it doesn't exist
                os.makedirs(username_folder, exist_ok=True)

                # Save the profile picture in the user's folder
                picture_path = os.path.join(username_folder, filename)
                picture.save(picture_path)
                profile_picture = f"{sanitized_name}/{filename}"  # Save relative path in DB

        # Update the user details, including profile picture if provided
        user_db.update_user_details(session['user_id'], name, dob, email, profile_picture)

        flash("Profile updated successfully!", "success")
        return redirect(url_for('profile'))

    return render_template('edit_profile.html', user=user)



# Products route
@app.route('/products', methods=['GET', 'POST'])
def products():
    if not session.get('user_id'):  # Ensure user is logged in
        flash("Please log in to view products.", "error")
        return redirect(url_for('login'))

    # Fetch user data based on the session user_id
    user = user_db.get_user_by_id(session['user_id'])  # Implement this function to fetch user details

    # Fetch products from the product database
    products = product_db.fetch_all_products()

    # Check if user is an admin, and allow access to the "Add Product" form
    is_admin = user['role'] == 'admin'

    # Fetch the cart items for the user
    cart = session.get('cart', [])  # Use session to store cart, or replace with your DB logic
    cart_count = len(cart)  # Count the number of items in the cart

    return render_template('products.html', products=products, user=user, is_admin=is_admin,cart_count = cart_count)

# Route for adding a product
@app.route('/add_product', methods=['GET', 'POST'])
def add_product():
    if not session.get('user_id'):  # Ensure the user is logged in
        flash("Please log in to add a product.", "error")
        return redirect(url_for('login'))  # Redirect to login page

    # Fetch the logged-in user
    user = user_db.get_user_by_id(session['user_id'])
    if user['role'] != 'admin':  # Ensure that only an admin can add products
        flash("Access denied! You must be an admin to add a product.", "error")
        return redirect(url_for('products'))  # Redirect to products page if not admin

    if request.method == 'POST':
        # Get product details from the form
        name = request.form['name']
        category = request.form['category']  # Get the selected category
        description = request.form['description']
        price = request.form['price']
        nutritional_info = request.form['nutritional_info']
        image = request.files['image']

        # Validate the input fields
        if not name or not category or not description or not price or not nutritional_info:
            flash("Please fill in all fields.", "error")
            return render_template('add_product.html')

        # Handle the image file upload
        if image and allowed_file(image.filename):
            # Create a folder path based on the category for local storage
            category_folder = os.path.join(app.config['PRODUCTS_FOLDER'], category)
            if not os.path.exists(category_folder):
                os.makedirs(category_folder)  # Create the folder if it doesn't exist

            # Save the image in the category-specific folder locally
            filename = secure_filename(image.filename)
            image_path = os.path.join(category_folder, filename)
            image.save(image_path)

            # Upload the image to S3
            s3_client = boto3.client(
                's3',
                aws_access_key_id='AKIAVRUVTHAIC4WA37MC',
                aws_secret_access_key='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'
            )
            s3_path = f"{category}/{filename}"
            try:
                s3_client.upload_file(
                    image_path,  # Local file path
                    'praveen-store-mini-appli',  # S3 bucket name
                    s3_path,
                    ExtraArgs={'ACL': 'public-read'}  # Make the file publicly accessible
                )
                # S3 URL
                s3_url = f"https://praveen-store-mini-appli.s3.amazonaws.com/{s3_path}"
            except Exception as e:
                flash(f"Failed to upload image to S3: {e}", "error")
                return render_template('add_product.html')

        else:
            s3_url = None  # If no image is provided, set the S3 URL as None

        # Insert the product into the database with the S3 URL
        product_db.insert_product(name, category, price, description, nutritional_info, s3_url)

        flash("Product added successfully!", "success")
        return redirect(url_for('products'))  # Redirect to products page after successful addition

    return render_template('add_product.html')




@app.route('/blog', methods=['GET', 'POST'])
def blog_page():
    if not session.get('user_id'):  # Ensure user is logged in
        flash("Please log in to create a blog post.", "error")
        return redirect(url_for('login'))

    # Fetch the current user details using the session user_id
    user = user_db.get_user_by_id(session['user_id'])
    author = user['name']  # Use the logged-in user's name as the author

    if request.method == 'POST':
        title = request.form['title']
        content = request.form['content']
        author = request.form['author'] or user['name']  # Use form author or default to logged-in user
        image = request.files['image']

        # Save the blog image to the author's folder
        image_filename = save_image(image, author)

        # Create the post data
        data = {
            'title': title,
            'content': content,
            'author': author,
            'image': image_filename,  # Save image relative path
            'timestamp': datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        }

        # Save the post data (you can customize this to save to a database or JSON)
        save_to_json(author, data)
        flash("Post Successfully Created!")
        return redirect('/blog')

    posts = get_all_posts()  # Fetch all posts from all users
    return render_template('blog.html', posts=posts, user=user)

# Add to Cart
@app.route('/add_to_cart/<int:product_id>', methods=['POST'])
def add_to_cart(product_id):
    if 'user_id' not in session:
        return redirect(url_for('login'))

    # Fetch user and product data
    user = user_db.get_user_by_id(session['user_id'])  # Fetch user using the existing method
    product = product_db.fetch_product_by_id(product_id)  # Fetch product using the existing method
    user = user_db.get_user_by_id(session['user_id'])

    # Handle cases where user or product is not found
    if not user:
        return "User not found!", 404
    if not product:
        return "Product not found!", 404

    # Extract required parameters
    user_id = user['id']
    product_id = product['id']
    quantity = int(request.form.get('quantity', 1))  # Default quantity 1

    conn = get_connection()
    cursor = conn.cursor()

    # Check if product already exists in cart
    cursor.execute(
        "SELECT cart_id, quantity FROM cart WHERE user_id = %s AND product_id = %s",
        (user_id, product_id)
    )
    cart_item = cursor.fetchone()
    print(cart_item)

    if cart_item:
        # If the product is already in the cart, update the quantity
        new_quantity = cart_item[1] + quantity
        cursor.execute(
            "UPDATE cart SET quantity = %s WHERE cart_id = %s",
            (new_quantity, cart_item[0])
        )
    else:
        # Otherwise, insert the new product into the cart
        cursor.execute(
            "INSERT INTO cart (user_id, product_id, quantity) VALUES (%s, %s, %s)",
            (user_id, product_id, quantity)
        )

    conn.commit()

    # Get updated cart count
    cursor.execute("SELECT SUM(quantity) FROM cart WHERE user_id = %s", (user_id,))
    cart_count = cursor.fetchone()[0] or 0

    cursor.close()
    conn.close()

    return jsonify({"cart_count": cart_count})  # Return the updated cart count in JSON format

# View Cart
@app.route('/cart')
def view_cart():
    if 'user_id' not in session:
        return redirect(url_for('login'))

    user_id = session['user_id']
    user = user_db.get_user_by_id(session['user_id'])

    conn = get_connection()
    cursor = conn.cursor(dictionary=True)

    cursor.execute("""
        SELECT c.cart_id AS cart_id, p.id AS product_id, p.name, p.price, c.quantity,
               (p.price * c.quantity) AS total
        FROM cart c
        INNER JOIN products p ON c.product_id = p.id
        WHERE c.user_id = %s
    """, (user_id,))
    cart_items = cursor.fetchall()

    total_price = sum(item['total'] for item in cart_items)

    cursor.close()
    conn.close()

    return render_template('cart.html', cart_items=cart_items, total_price=total_price,user = user)

@app.route('/cart/increase_quantity/<int:product_id>', methods=['POST'])
def increase_quantity(product_id):
    """Increase the quantity of a product in the cart."""
    if not session.get('user_id'):
        return jsonify({"error": "Unauthorized access"}), 401

    conn = get_connection()
    cursor = conn.cursor()

    # Fetch the cart item
    cursor.execute(
        "SELECT * FROM cart WHERE user_id = %s AND product_id = %s",
        (session['user_id'], product_id)
    )
    cart_item = cursor.fetchone()
    print(cart_item)

    if not cart_item:
        return jsonify({"error": "Product not found in cart"}), 404

    # Increase quantity by 1
    new_quantity = cart_item[3] + 1  # Assuming quantity is at index 2
    cursor.execute(
        "UPDATE cart SET quantity = %s WHERE user_id = %s AND product_id = %s",
        (new_quantity, session['user_id'], product_id)
    )
    conn.commit()

    return jsonify({"message": "Quantity increased", "new_quantity": new_quantity})


@app.route('/cart/decrease_quantity/<int:product_id>', methods=['POST'])
def decrease_quantity(product_id):
    """Decrease the quantity of a product in the cart."""
    if not session.get('user_id'):
        return jsonify({"error": "Unauthorized access"}), 401

    conn = get_connection()
    cursor = conn.cursor()

    # Fetch the cart item
    cursor.execute(
        "SELECT * FROM cart WHERE user_id = %s AND product_id = %s",
        (session['user_id'], product_id)
    )
    cart_item = cursor.fetchone()

    if not cart_item:
        return jsonify({"error": "Product not found in cart"}), 404

    # Decrease quantity by 1, but ensure it doesn't go below 1
    new_quantity = cart_item[3] - 1  # Ensure quantity doesn't go below 1
    if new_quantity <= 0:
        # Remove the product from the cart if the quantity is 0 or less
        cursor.execute(
            "DELETE FROM cart WHERE user_id = %s AND product_id = %s",
            (session['user_id'], product_id)
        )
        conn.commit()
        return jsonify({"message": "Product removed from cart", "new_quantity": 0})
    else:
        # Otherwise, update the quantity
        cursor.execute(
            "UPDATE cart SET quantity = %s WHERE user_id = %s AND product_id = %s",
            (new_quantity, session['user_id'], product_id)
        )
        conn.commit()
        return jsonify({"message": "Quantity decreased", "new_quantity": new_quantity})


# Remove from Cart
@app.route('/remove_from_cart/<int:cart_id>', methods=['POST'])
def remove_from_cart(cart_id):
    if 'user_id' not in session:
        return redirect(url_for('login'))

    conn = get_connection()
    cursor = conn.cursor()

    cursor.execute("DELETE FROM cart WHERE cart_id = %s", (cart_id,))

    conn.commit()
    cursor.close()
    conn.close()

    return redirect(url_for('view_cart'))


@app.route('/buy_now/<int:product_id>', methods=['POST'])
def buy_now(product_id):
    if 'user_id' not in session:
        print("User is not logged in!")
        return redirect(url_for('login'))

    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT id, name, price FROM products WHERE id = %s", (product_id,))
    product = cursor.fetchone()

    if product:
        print(f"Product found: {product}")
        cursor.execute("""
            INSERT INTO cart (user_id, product_id, quantity) 
            VALUES (%s, %s, %s)
            ON DUPLICATE KEY UPDATE quantity = quantity + 1
        """, (session['user_id'], product_id, 1))
        conn.commit()

        return redirect(url_for('checkout'))
    else:
        print("Product not found.")
        return redirect(url_for('error_page'))




@app.route('/checkout', methods=['GET', 'POST'])
def checkout():
    if 'user_id' not in session:
        return redirect(url_for('login'))

    user = user_db.get_user_by_id(session['user_id'])

    # Get product_id from query parameters (if available)
    product_id = request.args.get('product_id', None)

    cart_items = []

    # If there's a product_id, add it directly to the checkout
    if product_id:
        conn = get_connection()
        cursor = conn.cursor()
        cursor.execute("SELECT id, name, price FROM products WHERE id = %s", (product_id,))
        product = cursor.fetchone()

        if product:
            cart_items.append({
                'id': product[0],
                'name': product[1],
                'quantity': 1,  # Direct buy, so quantity is 1
                'price': product[2],
                'total': product[2]  # Total is price * quantity
            })
        cursor.close()
        conn.close()

    # If no direct product is being bought, fetch the cart items
    if not product_id:
        conn = get_connection()
        cursor = conn.cursor()
        cursor.execute("""
            SELECT p.id, p.name, c.quantity, p.price 
            FROM cart c 
            JOIN products p ON c.product_id = p.id 
            WHERE c.user_id = %s
        """, (session['user_id'],))
        cart_items = cursor.fetchall()
        cursor.close()
        conn.close()
        print(cart_items)

    # Calculate the total price
    total_price = sum(int(item[2]) * float(item[3]) for item in cart_items)

    if request.method == 'POST':
        # Handle form submission (shipping details, payment method)
        shipping_address = request.form['shipping_address']
        payment_method = request.form['payment_method']

        # Save the order to the database
        conn = get_connection()
        cursor = conn.cursor()
        cursor.execute("""
            INSERT INTO orders (user_id, total_price, shipping_address, payment_method) 
            VALUES (%s, %s, %s, %s)
        """, (session['user_id'], total_price, shipping_address, payment_method))
        conn.commit()

        # Get the last inserted order_id
        order_id = cursor.lastrowid
        # Insert data into order_items for each item in the cart
        for item in cart_items:
            cursor.execute("""
                INSERT INTO order_items (order_id, product_id, quantity, price)
                VALUES (%s, %s, %s, %s)
            """, (order_id, item[0], item[2], item[3]))
        conn.commit()

        # Clear the cart after the order is placed
        cursor.execute("DELETE FROM cart WHERE user_id = %s", (session['user_id'],))
        conn.commit()

        cursor.close()
        conn.close()

        # Redirect to the order confirmation page
        return redirect(url_for('order_confirmation'))

    return render_template('checkout.html', cart_items=cart_items, total_price=total_price, user=user)


@app.route('/orders')
def view_orders():
    if 'user_id' not in session:
        return redirect(url_for('login'))

    # Fetch orders placed by the user
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("""
        SELECT * FROM orders 
        WHERE user_id = %s 
        ORDER BY created_at DESC
    """, (session['user_id'],))
    orders = cursor.fetchall()

    cursor.close()
    conn.close()

    return render_template('orders.html', orders=orders)


# Route: Order Confirmation
@app.route('/order_confirmation')
@admin_only
def order_confirmation():
    return render_template('order_confirmation.html')

@app.route('/update_order_status/<int:order_id>', methods=['GET', 'POST'])
@admin_only
def update_order_status(order_id):
    # Fetch the order details from the database
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM orders WHERE order_id = %s", (order_id,))
    order = cursor.fetchone()

    if request.method == 'POST':
        new_status = request.form['status']
        valid_statuses = ['Pending', 'Completed', 'Cancelled']  # Valid statuses

        # Check if the new status is valid
        if new_status not in valid_statuses:
            flash('Invalid status value!', 'error')
            return redirect(url_for('update_order_status', order_id=order_id))  # Redirect back to the same page with an error

        # Update the order status in the database
        cursor.execute("""
            UPDATE orders SET status = %s WHERE order_id = %s
        """, (new_status, order_id))
        conn.commit()

        flash("Order status updated successfully!", "success")
        return redirect(url_for('dashboard'))  # Redirect to the admin dashboard after updating the status

    cursor.close()
    conn.close()

    # Pass both `order` and `order_id` to the template
    return render_template('update_order_status.html', order=order, order_id=order_id)


# Logout route
@app.route('/logout')
def logout():
    session.clear()  # Clear all session data
    flash("You have been logged out.", "success")
    return redirect(url_for('home'))


if __name__ == '__main__':
    app.run(debug=True)
