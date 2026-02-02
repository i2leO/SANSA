from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
import os
from app.config import get_settings
from app.routers import (
    auth,
    respondents,
    visits,
    sansa,
    satisfaction,
    bia,
    mna,
    exports,
    food_diary,
)

settings = get_settings()

app = FastAPI(
    title="SANSA Research System",
    description="Self-administered Nutrition Screening and Assessment Tool",
    version="1.0.0",
)

# CORS Configuration
app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        settings.FRONTEND_URL,
        "http://localhost:5173",
        "http://localhost:5174",
    ],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Create uploads directory if it doesn't exist
os.makedirs(settings.UPLOAD_DIR, exist_ok=True)

# Mount static files for uploads
app.mount("/uploads", StaticFiles(directory=settings.UPLOAD_DIR), name="uploads")

# Include routers
app.include_router(auth.router)
app.include_router(respondents.router)
app.include_router(visits.router)
app.include_router(sansa.router)
app.include_router(satisfaction.router)
app.include_router(bia.router)
app.include_router(mna.router)
app.include_router(exports.router)
app.include_router(food_diary.router)


@app.get("/")
def root():
    """API root endpoint"""
    return {
        "message": "SANSA Research System API",
        "version": "1.0.0",
        "docs": "/docs",
        "status": "operational",
    }


@app.get("/health")
def health_check():
    """Health check endpoint"""
    return {"status": "healthy"}
