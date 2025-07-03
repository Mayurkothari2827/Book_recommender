import sqlite3
import pandas as pd

# Read the new CSV with correct dtypes
df = pd.read_csv("Books.csv", dtype=str).head(5000)  # Read all columns as strings

# Create or connect to SQLite DB
conn = sqlite3.connect("books.db")
cursor = conn.cursor()

# Drop old table if exists (optional)
cursor.execute("DROP TABLE IF EXISTS books")

# Create table with correct schema
cursor.execute("""
    CREATE TABLE books (
        Genre TEXT,
        ISBN TEXT PRIMARY KEY,
        `Book-Title` TEXT,
        `Book-Author` TEXT,
        Publisher TEXT,
        `Image-URL-M` TEXT
    )
""")

# Insert data
df.to_sql("books", conn, if_exists='replace', index=False)

print("✅ New data inserted into books.db successfully.")

conn.commit()
conn.close()
