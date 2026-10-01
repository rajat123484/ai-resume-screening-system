import os
import psycopg2
from dotenv import load_dotenv

load_dotenv()

database_url = os.getenv("DATABASE_URL")

if not database_url:
    print("DATABASE_URL not found.")
    exit()

try:
    connection = psycopg2.connect(database_url)

    cursor = connection.cursor()

    cursor.execute("SELECT version();")

    version = cursor.fetchone()

    print("Database connected successfully!")
    print(version[0])

    cursor.close()
    connection.close()

except Exception as error:
    print("Database connection failed!")
    print(error)