import logging
from fastapi import FastAPI, Request, Response

logger = logging.getLogger(__name__)


def setup_security_middlewares(app: FastAPI):
    """
    Aplica cabeceras de seguridad HTTP a todas las respuestas
    sin interferir con clientes de API (curl, Python, etc.).
    """

    @app.middleware("http")
    async def add_security_headers_middleware(request: Request, call_next):
        response: Response = await call_next(request)

        # Cabeceras de Seguridad Estándar (No afectan a cURL ni clientes de API)
        response.headers["X-Frame-Options"] = "DENY"
        response.headers["X-Content-Type-Options"] = "nosniff"
        response.headers["X-XSS-Protection"] = "1; mode=block"
        response.headers["Referrer-Policy"] = "strict-origin-when-cross-origin"

        return response
