from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.database import engine, Base
from app.routers import books

Base.metadata.create_all(bind=engine)

app = FastAPI(
    title="Personal Book Library API",
    description="Track your books",
    version="1.0.0",
    docs_url="/api/docs",
    redoc_url="/api/redoc"
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(books.router)

@app.get("/")
def root():
    """API health check endpoint"""
    return {
        "message": "Welcome to Book Library API",
        "docs": "/api/docs",
        "status": "healthy"
    }