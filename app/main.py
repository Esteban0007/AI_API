"""
FastAPI application factory and middleware setup.
"""

from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse, HTMLResponse
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
import logging
import time
from typing import Callable
from pathlib import Path

from app.core.config import get_settings
from app.api import router

# Configure logging
logging.basicConfig(
    level=logging.INFO, format="%(asctime)s - %(name)s - %(levelname)s - %(message)s"
)
logger = logging.getLogger(__name__)


def create_app() -> FastAPI:
    """
    Create and configure the FastAPI application.

    Returns:
        Configured FastAPI application instance
    """
    settings = get_settings()

    # Create FastAPI app
    app = FastAPI(
        title=settings.API_TITLE,
        description=settings.API_DESCRIPTION,
        version=settings.API_VERSION,
        openapi_url="/api/openapi.json",
        docs_url="/api/docs",
        redoc_url="/api/redoc",
    )

    # Add CORS middleware
    app.add_middleware(
        CORSMiddleware,
        allow_origins=settings.ALLOWED_ORIGINS,
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )

    # Mount templates for Jinja2
    templates = Jinja2Templates(directory=str(Path(__file__).parent / "templates"))

    # Mount static files
    static_path = Path(__file__).parent / "static"
    if static_path.exists():
        app.mount("/static", StaticFiles(directory=str(static_path)), name="static")
        logger.info(f"Static files mounted at /static from {static_path}")

    # Add request logging middleware
    @app.middleware("http")
    async def log_requests(request: Request, call_next: Callable):
        """Log all HTTP requests and responses."""
        start_time = time.time()

        # Log request
        logger.info(
            f"Incoming request: {request.method} {request.url.path} "
            f"from {request.client.host if request.client else 'unknown'}"
        )

        try:
            response = await call_next(request)
        except Exception as e:
            logger.error(f"Request error: {str(e)}")
            return JSONResponse(
                status_code=500, content={"detail": "Internal server error"}
            )

        # Calculate processing time
        process_time = time.time() - start_time

        # Log response
        logger.info(
            f"Response: {response.status_code} - "
            f"Processing time: {process_time:.3f}s"
        )

        response.headers["X-Process-Time"] = str(process_time)
        return response

    # Include routers
    app.include_router(router)

    # Initialize database on startup
    @app.on_event("startup")
    async def startup_event():
        """Initialize database on application startup."""
        from app.db.session import init_db

        logger.info("Initializing database...")
        init_db()
        logger.info("Database initialized successfully")

    # Root endpoint
    @app.get("/", tags=["System"])
    async def root():
        """Root endpoint with API information."""
        return {
            "name": settings.API_TITLE,
            "version": settings.API_VERSION,
            "description": settings.API_DESCRIPTION,
            "docs": "/api/docs",
            "redoc": "/api/redoc",
        }

    # Health check endpoint
    @app.get("/health", tags=["System"])
    async def health():
        """Health check endpoint with model information."""
        from app.engine.embedder import Embedder

        try:
            # Get current embedder status
            embedder = Embedder()
            model_type = "INT8 ONNX" if embedder.is_int8_quantized() else "Standard"

            return {
                "status": "ok",
                "message": "Server is running",
                "embedding_model": model_type,
                "model_name": embedder.get_model_name(),
                "dimension": embedder.get_embedding_dimension(),
            }
        except Exception as e:
            return {
                "status": "ok",
                "message": "Server is running",
                "warning": f"Could not load embedder: {str(e)}",
            }

    # Error handlers
    @app.exception_handler(ValueError)
    async def value_error_handler(request: Request, exc: ValueError):
        """Handle ValueError exceptions."""
        logger.error(f"ValueError: {str(exc)}")
        return JSONResponse(status_code=400, content={"detail": str(exc)})

    @app.exception_handler(Exception)
    async def general_exception_handler(request: Request, exc: Exception):
        """Handle general exceptions."""
        logger.error(f"Unhandled exception: {str(exc)}")
        return JSONResponse(
            status_code=500, content={"detail": "Internal server error"}
        )

    logger.info(f"FastAPI application created successfully")
    return app


# Create application instance
app = create_app()


if __name__ == "__main__":
    import uvicorn

    settings = get_settings()
    uvicorn.run(app, host=settings.HOST, port=settings.PORT, log_level="info")
