from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
import sqlite3
import pandas as pd
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# ------------------------ GET ALL BOOKS ------------------------
@app.get("/books")
def get_books():
    try:
        conn = sqlite3.connect("backend/books.db")
        df = pd.read_sql("SELECT * FROM books LIMIT 5000", conn)
        conn.close()
        return df.to_dict(orient="records")
    except Exception as e:
        return {"error": str(e)}

# ------------------------ RECOMMEND BOOKS ------------------------
@app.get("/recommend")
def recommend(title: str):
    try:
        conn = sqlite3.connect("backend/books.db")
        df = pd.read_sql("SELECT * FROM books LIMIT 5000", conn)

        # Sanity check
        if df.empty or 'Book-Title' not in df.columns:
            print("No book data found.")
            return {"error": "Book data not available."}

        df.dropna(subset=["Book-Title", "Book-Author", "Publisher", "ISBN"], inplace=True)
        df['combined'] = df['Book-Title'] + ' ' + df['Book-Author'] + ' ' + df['Publisher']

        tfidf = TfidfVectorizer(stop_words='english')
        tfidf_matrix = tfidf.fit_transform(df['combined'])
        cosine_sim = cosine_similarity(tfidf_matrix, tfidf_matrix)

        df = df.reset_index(drop=True)
        title_lower = title.strip().lower()

        matched_indices = df[df['Book-Title'].str.strip().str.lower() == title_lower].index.tolist()
        if not matched_indices:
            return {"error": "Book not found."}

        idx = matched_indices[0]
        sim_scores = list(enumerate(cosine_sim[idx]))
        sim_scores = sorted(sim_scores, key=lambda x: x[1], reverse=True)[1:6]
        indices = [i[0] for i in sim_scores]

        results = df.loc[indices][['Book-Title', 'Book-Author', 'ISBN']].copy()
        results["Image-URL-M"] = results["ISBN"].apply(lambda x: f"https://covers.openlibrary.org/b/isbn/{x}-M.jpg")

        return results.to_dict(orient="records")

    except Exception as e:
        print("RECOMMENDATION ERROR:", e)
        return {"error": str(e)}

