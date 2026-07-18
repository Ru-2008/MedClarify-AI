from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app.routes.upload import router as upload_router
from app.config import settings
import logging

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)

app = FastAPI(
    title=settings.APP_NAME,
    version=settings.APP_VERSION,
    description="Medical report analysis platform backend",
)

# CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.allowed_origins_list,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include routers
app.include_router(upload_router, prefix="/api")


@app.get("/", tags=["health"])
async def health_check():
    """
    Health check endpoint.
    """
    return {
        "status": "online",
        "service": settings.APP_NAME,
        "version": settings.APP_VERSION,
    }