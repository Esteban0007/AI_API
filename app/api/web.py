"""Web UI endpoints (HTML templates with Jinja2)."""

from fastapi import APIRouter, Request, Form, HTTPException
from fastapi.responses import HTMLResponse, RedirectResponse
from fastapi.templating import Jinja2Templates
import os
import logging

from app.engine.searcher import SearchEngine
from app.engine.store import VectorStore
from app.db.users import register_user, confirm_user, get_user_by_api_key

logger = logging.getLogger(__name__)

# Setup templates
TEMPLATE_DIR = os.path.join(os.path.dirname(__file__), "../templates")
templates = Jinja2Templates(directory=TEMPLATE_DIR)

router = APIRouter(tags=["web"])

# Initialize search engine (lazy load)
_search_engine = None
_vector_store = None


def get_search_engine():
    """Get or create search engine instance."""
    global _search_engine, _vector_store
    if _search_engine is None:
        _vector_store = VectorStore()
        _search_engine = SearchEngine(vector_store=_vector_store)
    return _search_engine


@router.get("/", response_class=HTMLResponse)
async def home(request: Request):
    """Home page."""
    return templates.TemplateResponse("index.html", {"request": request})


@router.get("/api-docs", response_class=HTMLResponse)
async def api_docs(request: Request):
    """Redirect to Swagger docs."""
    return RedirectResponse(url="/api/docs")


@router.get("/simulator", response_class=HTMLResponse)
async def simulator(request: Request):
    """Movie search simulator page."""
    return templates.TemplateResponse("simulator.html", {"request": request})


@router.post("/search-partial", response_class=HTMLResponse)
async def search_partial(request: Request, query: str = Form(...)):
    """HTMX endpoint that returns HTML partial with search results."""
    try:
        if not query or len(query.strip()) < 2:
            return templates.TemplateResponse(
                "results_list.html", {"request": request, "results": [], "timing": 0}
            )

        search_engine = get_search_engine()
        results, timing = search_engine.search(query, top_k=5, include_content=False)

        return templates.TemplateResponse(
            "results_list.html",
            {"request": request, "results": results, "timing": timing},
        )
    except Exception as e:
        logger.error(f"Search error: {e}")
        return templates.TemplateResponse(
            "results_list.html",
            {"request": request, "results": [], "timing": 0, "error": str(e)},
        )


@router.get("/register", response_class=HTMLResponse)
async def register_page(request: Request):
    """Registration form page."""
    return templates.TemplateResponse("register.html", {"request": request})


@router.post("/register", response_class=HTMLResponse)
async def register(
    request: Request,
    email: str = Form(...),
    password: str = Form(...),
    password2: str = Form(...),
):
    """Process user registration."""
    # Validate inputs
    if not email or "@" not in email:
        return templates.TemplateResponse(
            "register.html", {"request": request, "error": "Email inválido"}
        )

    if len(password) < 8:
        return templates.TemplateResponse(
            "register.html",
            {"request": request, "error": "Contraseña mínimo 8 caracteres"},
        )

    if password != password2:
        return templates.TemplateResponse(
            "register.html",
            {"request": request, "error": "Las contraseñas no coinciden"},
        )

    # Register user
    result = register_user(email, password)

    if result["success"]:
        # In production, send confirmation email here
        logger.info(
            f"User registered: {email}, confirmation_token: {result['confirmation_token']}"
        )
        return templates.TemplateResponse(
            "register.html",
            {
                "request": request,
                "success": f"¡Bienvenido! Hemos creado tu API Key. Confirma tu email para activarla.",
            },
        )
    else:
        return templates.TemplateResponse(
            "register.html", {"request": request, "error": result["message"]}
        )


@router.get("/confirm/{token}", response_class=HTMLResponse)
async def confirm_email(request: Request, token: str):
    """Confirm user email with token."""
    result = confirm_user(token)

    if result["success"]:
        return templates.TemplateResponse(
            "index.html",
            {
                "request": request,
                "message": f"¡Email confirmado! Tu API Key está activa. Accede a tu dashboard para copiarla.",
            },
        )
    else:
        return templates.TemplateResponse(
            "index.html", {"request": request, "error": result["message"]}
        )
