import mysql.connector
from mysql.connector import Error


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


# Function to get the database connection
def get_db_connection():
    """Establishes and returns a connection to the database."""
    try:
        conn = mysql.connector.connect(
        host=db_host,
        user=db_user,
        password=db_password,
        database=db_name
    )

        if conn.is_connected():
            print("Connected to the database")
            return conn
        else:
            print("Failed to connect to the database")
            return None
    except Error as e:
        print(f"Error while connecting to MySQL: {e}")
        return None


# Function to list all tables in the database
def list_tables(conn):
    """Retrieve the names of all tables in the database."""
    if conn is None:
        return []

    print(' - DB CALL: list_tables')
    try:
        cursor = conn.cursor()
        cursor.execute("SHOW TABLES")
        tables = cursor.fetchall()
        return [t[0] for t in tables]
    except Error as e:
        print(f"Error while fetching tables: {e}")
        return []


# Function to describe the schema of a given table
def describe_table(conn, table_name):
    """Look up the table schema."""
    if conn is None:
        return []

    print(' - DB CALL: describe_table')
    try:
        cursor = conn.cursor()
        cursor.execute(f"DESCRIBE {table_name};")
        schema = cursor.fetchall()
        return [(col[0], col[1]) for col in schema]
    except Error as e:
        print(f"Error while describing the table {table_name}: {e}")
        return []


# Function to execute an SQL query and return the result
def execute_query(conn, sql):
    """Execute a SELECT statement, returning the results."""
    if conn is None:
        return []

    print(' - DB CALL: execute_query')
    try:
        cursor = conn.cursor()
        cursor.execute(sql)
        result = cursor.fetchall()
        return result
    except Error as e:
        print(f"Error while executing the query: {e}")
        return []


# Example usage of the functions
def main():
    conn = get_db_connection()

    if conn:
        # List tables
        tables = list_tables(conn)
        print("Tables:", tables)

        # Describe a table (example: 'products')
        if tables:
            schema = describe_table(conn, tables[0])  # Describe the first table
            print(f"Schema of {tables[0]}:", schema)

        # Execute a custom query
        query_result = execute_query(conn, "SELECT * FROM products LIMIT 5;")
        print("Query Result:", query_result)

        conn.close()



if __name__ == "__main__":
    main()
