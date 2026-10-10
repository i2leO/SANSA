from fastapi import FastAPI, Depends
from app.participant_access import require_participant_access
from app.auth import get_current_staff_or_admin
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
    facilities,
    knowledge,
    scoring,
    dashboard,
    participant_auth,
    instruments,
    assessment_history,
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
    allow_origins=[settings.FRONTEND_URL] + ([] if settings.APP_MODE.lower() == "production" else [
        "http://localhost:5173",
        "http://localhost:5174",
        "http://127.0.0.1:5173",
        "http://127.0.0.1:5174",
    ]),
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
    expose_headers=["X-Total-Count"],
)

# Create uploads directory if it doesn't exist
os.makedirs(settings.UPLOAD_DIR, exist_ok=True)

# Mount static files for uploads
app.mount("/uploads", StaticFiles(directory=settings.UPLOAD_DIR), name="uploads")

# Include routers
app.include_router(auth.router)
app.include_router(instruments.router)
app.include_router(assessment_history.router)
app.include_router(respondents.router, dependencies=[Depends(require_participant_access)])
app.include_router(visits.router, dependencies=[Depends(require_participant_access)])
app.include_router(sansa.router, dependencies=[Depends(require_participant_access)])
app.include_router(satisfaction.router, dependencies=[Depends(require_participant_access)])
app.include_router(bia.router, dependencies=[Depends(require_participant_access)])
app.include_router(
    mna.router,
    dependencies=[Depends(require_participant_access), Depends(get_current_staff_or_admin)],
)
app.include_router(exports.router)
app.include_router(food_diary.router, dependencies=[Depends(require_participant_access)])
app.include_router(facilities.router)
app.include_router(knowledge.router)
app.include_router(scoring.router)
app.include_router(dashboard.router)
app.include_router(participant_auth.router)


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
