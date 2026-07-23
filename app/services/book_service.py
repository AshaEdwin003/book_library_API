from sqlalchemy.orm import Session
from sqlalchemy import desc
from app.models.book import Book as BookModel
from app.schemas.book import BookCreate, BookUpdate
from typing import List, Optional

class BookService:
    @staticmethod
    def get_books(
        db: Session, 
        skip: int = 0, 
        limit: int = 100,
        genre: Optional[str] = None,
        sort_by: Optional[str] = None
    ) -> List[BookModel]:
        query = db.query(BookModel)
    
        if genre:
            query = query.filter(BookModel.genre == genre)
        if sort_by == "rating":
            query = query.order_by(desc(BookModel.rating))
        elif sort_by == "date_added":
            query = query.order_by(desc(BookModel.date_added))
        else:
            query = query.order_by(desc(BookModel.date_added))
        return query.offset(skip).limit(limit).all()
    
    @staticmethod
    def get_book(db: Session, book_id: int) -> Optional[BookModel]:
        return db.query(BookModel).filter(BookModel.id == book_id).first()
    @staticmethod
    def create_book(db: Session, book: BookCreate) -> BookModel:
        db_book = BookModel(**book.dict())
        db.add(db_book)  
        db.commit()    
        db.refresh(db_book) 
        return db_book
    
    @staticmethod
    def update_book(
        db: Session, 
        book_id: int, 
        book_update: BookUpdate
    ) -> Optional[BookModel]:
        db_book = db.query(BookModel).filter(BookModel.id == book_id).first()
        if not db_book:
            return None
    
        update_data = book_update.dict(exclude_unset=True)
        
        for field, value in update_data.items():
            setattr(db_book, field, value)
        
        db.commit()
        db.refresh(db_book)
        return db_book
    
    @staticmethod
    def delete_book(db: Session, book_id: int) -> bool:
        db_book = db.query(BookModel).filter(BookModel.id == book_id).first()
        if not db_book:
            return False
        
        db.delete(db_book)
        db.commit()
        return True