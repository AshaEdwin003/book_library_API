"""Streamlit user interface for the Book Library API."""

from __future__ import annotations

import os
from datetime import datetime
from typing import Any, Dict, List, Optional

import requests
import streamlit as st
from dotenv import load_dotenv

load_dotenv()

API_BASE_URL = os.getenv("API_BASE_URL", "http://127.0.0.1:8000/api/v1").rstrip("/")
BOOKS_ENDPOINT = f"{API_BASE_URL}/books/"
REQUEST_TIMEOUT_SECONDS = 10
GENRES = [
    "fiction", "non_fiction", "mystery", "sci_fi", "fantasy",
    "biography", "history", "science", "other",
]


def get_error_message(error: requests.RequestException) -> str:
    """Return a useful message from an API request failure."""
    if error.response is not None:
        try:
            detail = error.response.json().get("detail")
            if detail:
                return str(detail)
        except ValueError:
            pass
        return f"API request failed with status {error.response.status_code}."
    return f"Could not connect to the API: {error}"


def request_api(method: str, endpoint: str, **kwargs: Any) -> Optional[Any]:
    """Call the API and display a Streamlit error when it fails."""
    try:
        response = requests.request(
            method, endpoint, timeout=REQUEST_TIMEOUT_SECONDS, **kwargs
        )
        response.raise_for_status()
        if response.status_code == 204:
            return None
        return response.json()
    except requests.RequestException as error:
        st.error(get_error_message(error))
        return None


def fetch_books(
    genre: Optional[str], sort_by: Optional[str], limit: int
) -> Optional[List[Dict[str, Any]]]:
    """Retrieve books from the API using the selected filters."""
    params: Dict[str, Any] = {"limit": limit}
    if genre:
        params["genre"] = genre
    if sort_by:
        params["sort_by"] = sort_by
    return request_api("GET", BOOKS_ENDPOINT, params=params)


def create_book(book_data: Dict[str, Any]) -> Optional[Dict[str, Any]]:
    """Create a book through the API."""
    return request_api("POST", BOOKS_ENDPOINT, json=book_data)


def update_book(book_id: int, book_data: Dict[str, Any]) -> Optional[Dict[str, Any]]:
    """Partially update a book through the API."""
    return request_api("PATCH", f"{BOOKS_ENDPOINT}{book_id}", json=book_data)


def delete_book(book_id: int) -> bool:
    """Delete a book through the API."""
    try:
        response = requests.delete(
            f"{BOOKS_ENDPOINT}{book_id}", timeout=REQUEST_TIMEOUT_SECONDS
        )
        response.raise_for_status()
        return True
    except requests.RequestException as error:
        st.error(get_error_message(error))
        return False


def format_date(date_value: Optional[str]) -> str:
    """Format an API timestamp for display."""
    if not date_value:
        return "-"
    try:
        return datetime.fromisoformat(date_value.replace("Z", "+00:00")).strftime(
            "%Y-%m-%d %H:%M"
        )
    except ValueError:
        return date_value


def render_book_form(
    form_key: str,
    submit_label: str,
    existing_book: Optional[Dict[str, Any]] = None,
) -> None:
    """Render a create or update form and submit its values to the API."""
    existing_book = existing_book or {}
    with st.form(form_key):
        title = st.text_input("Title", value=existing_book.get("title", ""))
        author = st.text_input("Author", value=existing_book.get("author", ""))
        current_genre = existing_book.get("genre", GENRES[0])
        genre = st.selectbox(
            "Genre", GENRES,
            index=GENRES.index(current_genre) if current_genre in GENRES else 0,
        )
        rating = st.number_input(
            "Rating", min_value=0.0, max_value=5.0,
            value=float(existing_book.get("rating") or 0.0), step=0.1,
        )
        notes = st.text_area("Notes", value=existing_book.get("notes") or "")
        submitted = st.form_submit_button(submit_label, type="primary")

    if not submitted:
        return
    if not title.strip() or not author.strip():
        st.warning("Title and author are required.")
        return

    book_data = {
        "title": title.strip(), "author": author.strip(), "genre": genre,
        "rating": round(rating, 1), "notes": notes.strip() or None,
    }
    result = (
        update_book(existing_book["id"], book_data)
        if existing_book else create_book(book_data)
    )
    if result is not None:
        st.success("Book saved successfully.")
        st.session_state["refresh_books"] = True


def render_book_list(books: List[Dict[str, Any]]) -> None:
    """Render the book collection as readable cards."""
    if not books:
        st.info("No books found for the selected filters.")
        return

    st.subheader(f"{len(books)} book(s)")
    for book in books:
        with st.container(border=True):
            details_column, actions_column = st.columns([4, 1])
            with details_column:
                st.markdown(f"### {book['title']}")
                st.write(f"**Author:** {book['author']}")
                rating = book.get("rating")
                st.write(
                    f"**Genre:** {book['genre']}  |  **Rating:** "
                    f"{rating if rating is not None else 'Not rated'}"
                )
                st.write(f"**Added:** {format_date(book.get('date_added'))}")
                if book.get("notes"):
                    st.caption(book["notes"])
            with actions_column:
                if st.button("Delete", key=f"delete_{book['id']}"):
                    if delete_book(book["id"]):
                        st.success("Deleted.")
                        st.rerun()


def main() -> None:
    """Render the Streamlit application."""
    st.set_page_config(page_title="Book Library", page_icon="📚", layout="wide")
    st.title("📚 Personal Book Library")
    st.caption(f"Connected API: {API_BASE_URL}")

    with st.sidebar:
        st.header("Find books")
        selected_genre = st.selectbox("Genre", ["All genres", *GENRES])
        selected_sort = st.selectbox("Sort by", ["Recently added", "Rating"])
        result_limit = st.slider("Books to display", 1, 100, 20)

    genre_filter = None if selected_genre == "All genres" else selected_genre
    sort_filter = "date_added" if selected_sort == "Recently added" else "rating"
    books = fetch_books(genre_filter, sort_filter, result_limit)

    list_tab, add_tab, edit_tab = st.tabs(["Library", "Add a book", "Edit a book"])
    with list_tab:
        if books is not None:
            render_book_list(books)
    with add_tab:
        st.subheader("Add a new book")
        render_book_form("add_book_form", "Add book")
    with edit_tab:
        st.subheader("Edit a book")
        if books:
            book_options = {f"{book['id']}: {book['title']}": book for book in books}
            selected_book = st.selectbox("Book", list(book_options))
            render_book_form(
                "edit_book_form", "Save changes", book_options[selected_book]
            )
        else:
            st.info("Add a book or adjust the filters to edit a book.")


if __name__ == "__main__":
    main()
