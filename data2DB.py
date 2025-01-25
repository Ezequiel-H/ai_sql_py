import pandas as pd
import sqlite3
from functions import table_name

# Load data from CSV
data = pd.read_csv('data.csv')

# Create SQLite database
conn = sqlite3.connect('database.db')
cursor = conn.cursor()

# Create table
data.to_sql(table_name, conn, if_exists='replace', index=False)

print(f"Data loaded into {table_name} database successfully.")
