import json
import csv
import os
from PraveenStore.utils.logger import logging

class FileHandling:
    def __init__(self, data):
        self.data = data  # data should be a dictionary of product or user details
        logging.info("--- FileHandling ----")

    def create_directory(self, path):
        """Create the directory if it doesn't already exist."""
        if not os.path.exists(path):
            os.makedirs(path)
            logging.info(f"Directory created at: {path}")
        else:
            logging.info(f"Directory already exists at: {path}")

    def save_to_txt(self, filename):
        try:
            directory = os.path.dirname(filename)  # Get the directory from the filename
            self.create_directory(directory)  # Create the directory if it doesn't exist

            with open(f"{filename}.txt", "a") as file:  # Using 'a' to append new data
                for key, value in self.data.items():
                    file.write(f"{key}: {value}\n")
            logging.info('Data saved into the .txt file')
        except Exception as e:
            logging.error(f"Error saving to txt: {e}")

    def save_to_json(self, filename):
        try:
            directory = os.path.dirname(filename)  # Get the directory from the filename
            self.create_directory(directory)  # Create the directory if it doesn't exist

            # Read existing data and append the new product or user data
            try:
                with open(f"{filename}.json", "r") as file:
                    items = json.load(file)
            except (FileNotFoundError, json.JSONDecodeError):
                items = []  # If file is empty or does not exist, start with an empty list

            items.append(self.data)  # Append the new data

            # Write the updated list of data back to the file (overwrite the file)
            with open(f"{filename}.json", "w") as file:
                json.dump(items, file, indent=4)
            logging.info('Data saved into the json file')
        except Exception as e:
            logging.error(f"Error saving to json: {e}")

    def save_to_csv(self, filename):
        try:
            directory = os.path.dirname(filename)  # Get the directory from the filename
            self.create_directory(directory)  # Create the directory if it doesn't exist

            with open(f"{filename}.csv", "a", newline="") as file:
                writer = csv.DictWriter(file, fieldnames=self.data.keys())
                # Write header only if the file is empty (for the first entry)
                file_empty = file.tell() == 0
                if file_empty:
                    writer.writeheader()
                writer.writerow(self.data)
            logging.info('Data saved into the csv file')
        except Exception as e:
            logging.error(f"Error saving to csv: {e}")
