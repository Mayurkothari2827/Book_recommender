import streamlit as st
import pandas as pd
import requests

# ------------------- Helper Function -------------------
def get_cover_url(isbn):
    return f"https://covers.openlibrary.org/b/isbn/{isbn}-M.jpg"

# ------------------- Page Config -------------------
st.set_page_config(page_title="Book Recommender", layout="wide")

# ------------------- Title -------------------
st.title("BOOK RECOMMENDATION SYSTEM")
st.markdown("A book recommender system app to recommend books based on your favourite book")

# ------------------- Load Book Data -------------------
try:
    response = requests.post("/api/recommend/", json=preference_data)
    response.raise_for_status()
    books = pd.DataFrame(response.json()).head(5000)  # Limit to 5000 for performance
except Exception as e:
    st.error(f"Could not connect to backend: {e}")
    st.stop()

# ------------------- Filters -------------------
col1, col2, _ = st.columns([3, 3, 1])

if "author_filter" not in st.session_state:
    st.session_state.author_filter = "All"
if "publisher_filter" not in st.session_state:
    st.session_state.publisher_filter = "All"

with col1:
    authors = ["All"] + sorted(a for a in books["Book-Author"].dropna().unique())
    st.session_state.author_filter = st.selectbox("Filter by Author", authors, index=0)

with col2:
    publishers = ["All"] + sorted(p for p in books["Publisher"].dropna().unique())
    st.session_state.publisher_filter = st.selectbox("Filter by Publisher", publishers, index=0)

# ------------------- Filter Book Titles -------------------
filtered_books = books.copy()

if st.session_state.author_filter != "All":
    filtered_books = filtered_books[filtered_books["Book-Author"] == st.session_state.author_filter]

if st.session_state.publisher_filter != "All":
    filtered_books = filtered_books[filtered_books["Publisher"] == st.session_state.publisher_filter]

book_titles = filtered_books["Book-Title"].drop_duplicates().sort_values().tolist()
book_input = st.selectbox("Select a book title", ["All"] + book_titles)

# ------------------- Get Recommendations Button -------------------
col_btn, _, _ = st.columns([1.1, 0.4, 3])
with col_btn:
    get_clicked = st.button("Get Recommendations")

# ------------------- Recommendations -------------------
if get_clicked:
    if book_input == "All":
        st.warning("Please select a specific book title to get recommendations.")
    else:
        try:
            url = f"http://127.0.0.1:8000/recommend?title={book_input}"
            res = requests.get(url)
            res.raise_for_status()
            recommendations = res.json()
        except Exception as e:
            st.error(f"Error fetching recommendations: {e}")
            st.stop()

        if not recommendations or "error" in recommendations:
            st.error(f"{recommendations.get('error', 'No recommendations found.')}")
        else:
            st.subheader("Top 5 Recommended Books:")
            for row in recommendations:
                with st.container():
                    colA, colB = st.columns([1, 5])
                    with colA:
                        isbn = row.get("ISBN", "")
                        image_url = get_cover_url(isbn) if isbn else ""
                        st.image(image_url, width=100)
                    with colB:
                        st.markdown(
                            f"""
                            <h5>{row['Book-Title']}</h5>
                            <p><i>{row['Book-Author']}</i></p>
                            """,
                            unsafe_allow_html=True
                        )
