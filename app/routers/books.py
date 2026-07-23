from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy.orm import Session
from typing import List, Optional

from app.database import get_db
from app.schemas.book import Book, BookCreate, BookUpdate
from app.services.book_service import BookService


router = APIRouter(
    prefix="/api/v1/books",
    tags=["books"]
)

@router.get("/", response_model=List[Book])
def get_books(
    skip: int = Query(0, ge=0, description="Number of books to skip"),
    limit: int = Query(100, ge=1, le=100, description="Max books to return"),
    genre: Optional[str] = Query(None, description="Filter by genre"),
    sort_by: Optional[str] = Query(
        None, 
        regex="^(rating|date_added)$",
        description="Sort by field"
    ),
    db: Session = Depends(get_db)
):
    books = BookService.get_books(db, skip=skip, limit=limit, genre=genre, sort_by=sort_by)
    return books


@router.post("/", response_model=Book, status_code=status.HTTP_201_CREATED)
def create_book(
    book: BookCreate,
    db: Session = Depends(get_db)
):
    return BookService.create_book(db=db, book=book)


@router.get("/{book_id}", response_model=Book)
def get_book(
    book_id: int,  
    db: Session = Depends(get_db)
):
    db_book = BookService.get_book(db, book_id=book_id)
    if db_book is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Book with id {book_id} not found"
        )
    return db_book


@router.patch("/{book_id}", response_model=Book)
def update_book(
    book_id: int,
    book_update: BookUpdate,
    db: Session = Depends(get_db)
):
    db_book = BookService.update_book(db, book_id=book_id, book_update=book_update)
    if db_book is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Book with id {book_id} not found"
        )
    return db_book


@router.delete("/{book_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_book(
    book_id: int,
    db: Session = Depends(get_db)
):
    success = BookService.delete_book(db, book_id=book_id)
    if not success:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Book with id {book_id} not found"
        )
    return None 