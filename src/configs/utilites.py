import os
import re
import psycopg2
from passlib.context import CryptContext
from datetime import datetime, timedelta
from jose import jwt
from src.configs.settings import settings
from src.configs.config import DATABASE_URL
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from jose.exceptions import JWTError
from fastapi import HTTPException, Depends , Request, status
import random
from fastapi.security import OAuth2PasswordBearer
from src.common.app_response import AppResponse
from src.common.app_constants import AppConstants
from src.common.messages import Messages
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from sqlalchemy.orm import Session
from src.configs.config import get_db
from src.services.tables import Tables

tables = Tables()

token_auth_scheme = HTTPBearer()
app_response = AppResponse()
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")



def table_exists(cursor, table_name):
    cursor.execute("SELECT EXISTS (SELECT FROM information_schema.tables WHERE table_name = %s);", (table_name,))
    return cursor.fetchone()[0]

def extract_version(filename):
    # Use regex to find the numeric part of the filename
    match = re.search(r'V(\d+)', filename)
    return int(match.group(1)) if match else float('inf')  # Return a large number if no match





def execute_sql_files():
    # Connect to the database
    conn = psycopg2.connect(DATABASE_URL)
    cursor = conn.cursor()

    # Ensure the migrations table exists
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS migrations (
        id SERIAL PRIMARY KEY,
        file_name VARCHAR(255) NOT NULL UNIQUE,
        executed_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
    );
    """)
    conn.commit()

    # Get the list of already executed files
    cursor.execute("SELECT file_name FROM migrations;")
    executed_files = {row[0] for row in cursor.fetchall()}

    # Get absolute path for the database directory
    BASE_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), '..'))
    DATABASE_DIR = os.path.join(BASE_DIR, "database")  # Correct path

    # Ensure the directory exists
    if not os.path.exists(DATABASE_DIR):
        raise FileNotFoundError(f"Database directory not found: {DATABASE_DIR}")

    sql_files = sorted(os.listdir(DATABASE_DIR), key=extract_version)
    
    for file_name in sql_files:
        if file_name not in executed_files:
            file_path = os.path.join(DATABASE_DIR, file_name)  # Correct path

            # Ensure the file exists
            if not os.path.isfile(file_path):
                raise FileNotFoundError(f"SQL file not found: {file_path}")

            with open(file_path, "r") as file:
                sql = file.read()

                # Extract table name (assuming one table per file)
                first_line = sql.strip().split("\n")[0].strip().lower()
                if first_line.startswith("create table"):
                    table_name = first_line.split(" ")[2]
                    table_name = table_name.replace("if not exists", "").strip("();")

                    # Check if the table already exists
                    if table_exists(cursor, table_name):
                        print(f"Skipping {file_name}: Table {table_name} already exists.")
                        continue

                # Execute the SQL script
                print(f"Executing: {file_name}")
                cursor.execute(sql)
                cursor.execute("INSERT INTO migrations (file_name) VALUES (%s);", (file_name,))
                conn.commit()
                print(f"Executed: {file_name}")

    cursor.close()
    conn.close()








