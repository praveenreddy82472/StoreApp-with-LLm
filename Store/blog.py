from PraveenStore.utils.log import logging
import os
import json
from werkzeug.utils import secure_filename
from flask import Flask, render_template, request, redirect, flash, url_for


BLOG_FOLDER = 'static/blogs/'  # Directory for storing blog content and images

# Ensure the blog folder exists
if not os.path.exists(BLOG_FOLDER):
    os.makedirs(BLOG_FOLDER)
    logging.info(f"Created blog folder: {BLOG_FOLDER}")

def save_to_json(username, data):
    user_folder = os.path.join(BLOG_FOLDER, username)

    # Create user folder if it doesn't exist
    if not os.path.exists(user_folder):
        os.makedirs(user_folder)
        logging.info(f"Created user folder for {username} at {user_folder}")

    content_file = os.path.join(user_folder, 'content.json')

    # Read existing blog posts from JSON file
    if os.path.exists(content_file):
        with open(content_file, 'r') as file:
            posts = json.load(file)
        logging.info(f"Loaded existing posts for {username} from {content_file}")
    else:
        posts = []
        logging.info(f"No existing posts found for {username}. Starting new post file.")

    # Append new post to the list
    posts.append(data)

    # Save the updated list back to the JSON file
    with open(content_file, 'w') as file:
        json.dump(posts, file, indent=4)
    logging.info(f"Saved new post for {username} to {content_file}")

def get_all_posts():
    all_posts = []

    # Loop through each user folder in the blog directory
    for username in os.listdir(BLOG_FOLDER):
        user_folder = os.path.join(BLOG_FOLDER, username)
        content_file = os.path.join(user_folder, 'content.json')

        if os.path.exists(content_file):
            with open(content_file, 'r') as file:
                posts = json.load(file)

            # Add username to each post to identify the author
            for post in posts:
                post['username'] = username
                all_posts.append(post)

            logging.info(f"Loaded {len(posts)} posts from {username}")
        else:
            logging.warning(f"No content.json file found for user {username}")

    # Sort posts by timestamp (newest first)
    all_posts.sort(key=lambda post: post['timestamp'], reverse=True)
    logging.info(f"Sorted {len(all_posts)} total posts by timestamp.")
    return all_posts

def save_image(image, author):
    if image and image.filename:
        sanitized_author = author.replace(" ", "_")  # Sanitize the author's name
        user_folder = os.path.join('static', 'blogs', sanitized_author, 'images')

        if not os.path.exists(user_folder):
            os.makedirs(user_folder)
            logging.info(f"Created image folder for {sanitized_author} at {user_folder}")

        filename = secure_filename(image.filename)
        image_path = os.path.join(user_folder, filename)

        image.save(image_path)

        # Log image save
        logging.info(f"Image saved to: {image_path}")
        return filename
    else:
        logging.warning("No image provided or invalid image filename.")
    return None
