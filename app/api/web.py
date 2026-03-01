"""Web UI endpoints (HTML templates with Jinja2)."""

from fastapi import APIRouter, Request, Form, HTTPException
from fastapi.responses import HTMLResponse, RedirectResponse
from fastapi.templating import Jinja2Templates
import os
import logging

from app.engine.searcher import SearchEngine
from app.engine.store import VectorStore
from app.db.users import (
    register_user,
    confirm_user,
    get_user_by_api_key,
    get_user,
    verify_password,
    update_last_login,
)
from app.core.email import send_confirmation_email, send_api_key_email
from app.core.config import get_settings

logger = logging.getLogger(__name__)
settings = get_settings()

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


def _extract_summary(content: str) -> str:
    """Extract clean summary from stored content text."""
    if not content:
        return ""

    if "Summary:" not in content:
        return content.strip()

    lines = [line.strip() for line in content.splitlines() if line.strip()]
    summary_started = False
    summary_parts = []
    stop_prefixes = ("Category:", "Director:", "Cast:", "Year Released:")

    for line in lines:
        if line.startswith("Summary:"):
            summary_started = True
            summary_parts.append(line.replace("Summary:", "", 1).strip())
            continue

        if summary_started:
            if any(line.startswith(prefix) for prefix in stop_prefixes):
                break
            summary_parts.append(line)

    return " ".join(part for part in summary_parts if part).strip() or content.strip()


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
        results, timing = search_engine.search(query, top_k=5, include_content=True)

        for result in results:
            result["summary"] = _extract_summary(result.get("content", ""))

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


@router.get("/login", response_class=HTMLResponse)
async def login_page(request: Request):
    """Login form page."""
    return templates.TemplateResponse("login.html", {"request": request})


@router.post("/login", response_class=HTMLResponse)
async def login(request: Request, email: str = Form(...), password: str = Form(...)):
    """Process user login and show API key."""
    user = get_user(email)

    if not user or not verify_password(email, password):
        return templates.TemplateResponse(
            "login.html",
            {"request": request, "error": "Invalid email or password."},
        )

    if not user.get("is_confirmed"):
        return templates.TemplateResponse(
            "login.html",
            {
                "request": request,
                "error": "Please confirm your email before logging in.",
            },
        )

    update_last_login(email)
    return templates.TemplateResponse(
        "login.html",
        {
            "request": request,
            "success": "Login successful.",
            "user_email": email,
            "api_key": user.get("api_key", ""),
        },
    )


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
            "register.html", {"request": request, "error": "Invalid email."}
        )

    if len(password) < 8:
        return templates.TemplateResponse(
            "register.html",
            {"request": request, "error": "Password must be at least 8 characters."},
        )

    if password != password2:
        return templates.TemplateResponse(
            "register.html",
            {"request": request, "error": "Passwords do not match."},
        )

    # Register user
    result = register_user(email, password)

    if result["success"]:
        confirmation_url = f"{settings.BASE_URL}/confirm/{result['confirmation_token']}"

        # Send confirmation email
        email_sent = send_confirmation_email(email, result["confirmation_token"])
        smtp_password = os.getenv("SMTP_PASSWORD", "").strip()
        smtp_configured = bool(
            smtp_password and smtp_password.lower() != "your_password_here"
        )

        if email_sent and smtp_configured:
            logger.info(f"User registered and confirmation email sent: {email}")
            return templates.TemplateResponse(
                "register.html",
                {
                    "request": request,
                    "success": f"Registration successful! Check your email ({email}) to confirm your account.",
                },
            )
        else:
            logger.warning(
                f"User registered without SMTP delivery. Confirmation URL: {confirmation_url}"
            )
            return templates.TemplateResponse(
                "register.html",
                {
                    "request": request,
                    "success": f"Account created, but email is not configured yet. Confirm manually with this link: {confirmation_url}",
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
        # Get user and send API key email
        user = get_user(result["email"])
        if user and user.get("api_key"):
            send_api_key_email(result["email"], user["api_key"])

        return templates.TemplateResponse(
            "index.html",
            {
                "request": request,
                "message": "Email confirmed! Your API Key is active. Log in to view and copy it.",
            },
        )
    else:
        return templates.TemplateResponse(
            "index.html", {"request": request, "error": result["message"]}
        )
