from sqlalchemy import Column, Integer, String, Float, DateTime, Enum
from app.database import Base
from datetime import datetime
import enum

class GenreEnum(str, enum.Enum):
    FICTION = "fiction"
    NON_FICTION = "non_fiction"
    MYSTERY = "mystery"
    SCI_FI = "sci_fi"
    FANTASY = "fantasy"
    BIOGRAPHY = "biography"
    HISTORY = "history"
    SCIENCE = "science"
    OTHER = "other"

class Book(Base):
    __tablename__ = "books"
    
    id = Column(Integer, primary_key=True, index=True)
    
    title = Column(String(200), nullable=False)  
     
    author = Column(String(100), nullable=False)
    
    genre = Column(Enum(GenreEnum), nullable=False)
    
    rating = Column(Float, nullable=True)  
    
    notes = Column(String(1000), nullable=True)
    
    date_added = Column(DateTime, default=datetime.utcnow)