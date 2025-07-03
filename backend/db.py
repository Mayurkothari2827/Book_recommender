import sqlite3
import pandas as pd

def get_books():
    conn = sqlite3.connect("backend/books.db")
    df = pd.read_sql_query("SELECT * FROM books", conn)
    conn.close()
    return df
