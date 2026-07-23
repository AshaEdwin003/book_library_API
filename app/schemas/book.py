from pydantic import BaseModel, Field, validator
from typing import Optional
from datetime import datetime
from app.models.book import GenreEnum

class BookBase(BaseModel):
    title: str = Field(..., min_length=1, max_length=200, description="Book title")
    author: str = Field(..., min_length=1, max_length=100, description="Book author")
    genre: GenreEnum 
    rating: Optional[float] = Field(None, ge=0, le=5, description="Rating from 0 to 5")
    notes: Optional[str] = Field(None, max_length=1000, description="Personal notes")
   
    @validator('rating')
    def round_rating(cls, v):
        """Round rating to 1 decimal place"""
        if v is not None:
            return round(v, 1)
        return v
    
    class Config:
        schema_extra = {
            "example": {
                "title": "The Great Gatsby",
                "author": "F. Scott Fitzgerald",
                "genre": "fiction",
                "rating": 4.5,
                "notes": "A classic American novel"
            }
        }

class BookCreate(BookBase):
    pass  

class BookUpdate(BaseModel):
    title: Optional[str] = Field(None, min_length=1, max_length=200)
    author: Optional[str] = Field(None, min_length=1, max_length=100)
    genre: Optional[GenreEnum] = None
    rating: Optional[float] = Field(None, ge=0, le=5)
    notes: Optional[str] = Field(None, max_length=1000)

class Book(BookBase):
    id: int
    date_added: datetime
    
    class Config:
        orm_mode = True