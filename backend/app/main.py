from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
import logging
from contextlib import asynccontextmanager

from .core.config import settings
from .core.database import test_database_connection, close_database

# Configure logging
logging.basicConfig(
    level=logging.INFO if not settings.DEBUG else logging.DEBUG,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s"
)
logger = logging.getLogger(__name__)


@asynccontextmanager
async def lifespan(app: FastAPI):
    """
    Application lifespan manager
    """
    # Startup
    logger.info("Starting up application...")
    try:
        await test_database_connection()
        logger.info("Application startup completed")
    except Exception as e:
        logger.error(f"Failed to start application: {e}")
        raise
    
    yield
    
    # Shutdown
    logger.info("Shutting down application...")
    try:
        await close_database()
        logger.info("Application shutdown completed")
    except Exception as e:
        logger.error(f"Error during shutdown: {e}")


# Create FastAPI application
app = FastAPI(
    description="Supvx2 API",
    lifespan=lifespan,
    docs_url="/docs" if settings.DEBUG else None,
    redoc_url="/redoc" if settings.DEBUG else None,
)


# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.BACKEND_CORS_ORIGINS,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


# Health check endpoint
@app.get("/")
async def health_check():
    """
    Health check endpoint
    """
    return {"status": "ok"}