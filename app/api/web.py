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
    regenerate_confirmation_token,
    request_password_reset,
    reset_password_with_token,
)
from app.core.email import (
    send_confirmation_email,
    send_api_key_email,
    send_password_reset_email,
)
from app.core.config import get_settings

logger = logging.getLogger(__name__)
settings = get_settings()

# Setup templates
TEMPLATE_DIR = os.path.join(os.path.dirname(__file__), "../templates")
templates = Jinja2Templates(directory=TEMPLATE_DIR)

router = APIRouter(tags=["Authentication"])

# Initialize search engines for different datasets
_search_engines = {}


def get_search_engine(dataset: str = "movies"):
    """Get or create search engine instance for specific dataset."""
    global _search_engines

    if dataset not in _search_engines:
        # Map datasets to their tenant IDs
        tenant_map = {
            "movies": "admin",  # Admin tenant has movies
            "clothing": "user_1",  # User 1 tenant has clothing
        }
        tenant_id = tenant_map.get(dataset, "admin")

        # Create vector store for specific tenant
        vector_store = VectorStore(tenant_id=tenant_id)
        _search_engines[dataset] = SearchEngine(vector_store=vector_store)

    return _search_engines[dataset]


def _extract_summary(content: str) -> str:
    """Extract clean summary from stored content text."""
    if not content:
        return ""

    # For clothing items (Title: X Content: Y Keywords: Z format)
    if "Content:" in content and "Keywords:" in content:
        # Extract only the Content part
        content_start = content.find("Content:") + len("Content:")
        content_end = content.find("Keywords:")
        if content_start > 0 and content_end > content_start:
            return content[content_start:content_end].strip()
    
    # For movies (Summary: format)
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


@router.get("/", response_class=HTMLResponse, include_in_schema=False)
async def home(request: Request):
    """Home page."""
    return templates.TemplateResponse("index.html", {"request": request})


@router.get("/api-docs", response_class=HTMLResponse, include_in_schema=False)
async def api_docs(request: Request):
    """Redirect to Swagger docs in a new tab."""
    return HTMLResponse(
        """
    <html>
    <head><title>Redirecting...</title></head>
    <body>
        <script>
            window.open('/api/docs', '_blank');
            window.location.href = '/';
        </script>
        <p>Opening API documentation in a new tab...</p>
    </body>
    </html>
    """
    )


@router.get("/simulator", response_class=HTMLResponse, include_in_schema=False)
async def simulator(request: Request):
    """Movie search simulator page."""
    return templates.TemplateResponse("simulator.html", {"request": request})


@router.get("/demos", response_class=HTMLResponse, include_in_schema=False)
async def demos(request: Request):
    """Live demos page with multiple datasets."""
    return templates.TemplateResponse("demos.html", {"request": request})


@router.post("/search-partial", response_class=HTMLResponse, include_in_schema=False)
async def search_partial(
    request: Request, query: str = Form(...), dataset: str = Form(default="movies")
):
    """HTMX endpoint that returns HTML partial with search results."""
    try:
        if not query or len(query.strip()) < 2:
            if dataset == "clothing":
                return templates.TemplateResponse(
                    "clothing_results.html",
                    {"request": request, "results": [], "timing": 0},
                )
            else:
                return templates.TemplateResponse(
                    "results_list.html",
                    {"request": request, "results": [], "timing": 0},
                )

        # Get search engine for the specific dataset
        search_engine = get_search_engine(dataset)
        results, timing = search_engine.search(query, top_k=5, include_content=True)

        for result in results:
            result["summary"] = _extract_summary(result.get("content", ""))

        if dataset == "clothing":
            return templates.TemplateResponse(
                "clothing_results.html",
                {"request": request, "results": results, "timing": timing},
            )
        else:
            return templates.TemplateResponse(
                "results_list.html",
                {"request": request, "results": results, "timing": timing},
            )
    except Exception as e:
        logger.error(f"Search error: {e}")
        template = (
            "clothing_results.html" if dataset == "clothing" else "results_list.html"
        )
        return templates.TemplateResponse(
            template,
            {"request": request, "results": [], "timing": 0, "error": str(e)},
        )


@router.get("/register", response_class=HTMLResponse, include_in_schema=False)
async def register_page(request: Request):
    """Registration form page."""
    return templates.TemplateResponse("register.html", {"request": request})


@router.get("/login", response_class=HTMLResponse, include_in_schema=False)
async def login_page(request: Request):
    """Login form page."""
    return templates.TemplateResponse("login.html", {"request": request})


@router.post("/login", response_class=HTMLResponse, include_in_schema=False)
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


@router.post("/register", response_class=HTMLResponse, include_in_schema=False)
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
        smtp_password = settings.SMTP_PASSWORD.strip()
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


@router.get("/confirm/{token}", response_class=HTMLResponse, include_in_schema=False)
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


@router.get(
    "/resend-confirmation", response_class=HTMLResponse, include_in_schema=False
)
async def resend_confirmation_page(request: Request):
    """Resend confirmation email page."""
    return templates.TemplateResponse("resend_confirmation.html", {"request": request})


@router.post(
    "/resend-confirmation", response_class=HTMLResponse, include_in_schema=False
)
async def resend_confirmation(request: Request, email: str = Form(...)):
    """Resend confirmation email to user."""
    # Regenerate token
    result = regenerate_confirmation_token(email)

    if not result["success"]:
        return templates.TemplateResponse(
            "resend_confirmation.html", {"request": request, "error": result["message"]}
        )

    # Send new confirmation email
    email_sent = send_confirmation_email(email, result["confirmation_token"])
    smtp_password = settings.SMTP_PASSWORD.strip()
    smtp_configured = bool(
        smtp_password and smtp_password.lower() != "your_password_here"
    )

    if email_sent and smtp_configured:
        logger.info(f"Confirmation email resent to {email}")
        return templates.TemplateResponse(
            "resend_confirmation.html",
            {
                "request": request,
                "success": f"Confirmation email sent to {email}. Please check your inbox.",
            },
        )
    else:
        confirmation_url = f"{settings.BASE_URL}/confirm/{result['confirmation_token']}"
        logger.warning(f"Resend without SMTP delivery. URL: {confirmation_url}")
        return templates.TemplateResponse(
            "resend_confirmation.html",
            {
                "request": request,
                "success": f"Use this link to confirm: {confirmation_url}",
            },
        )


@router.get("/forgot-password", response_class=HTMLResponse, include_in_schema=False)
async def forgot_password_page(request: Request):
    """Forgot password form page."""
    return templates.TemplateResponse("forgot_password.html", {"request": request})


@router.post("/forgot-password", response_class=HTMLResponse, include_in_schema=False)
async def forgot_password(request: Request, email: str = Form(...)):
    """Process forgot password request."""
    result = request_password_reset(email)

    if not result["success"]:
        return templates.TemplateResponse(
            "forgot_password.html", {"request": request, "error": result["message"]}
        )

    # Send password reset email
    email_sent = send_password_reset_email(email, result["reset_token"])
    smtp_password = settings.SMTP_PASSWORD.strip()
    smtp_configured = bool(
        smtp_password and smtp_password.lower() != "your_password_here"
    )

    if email_sent and smtp_configured:
        logger.info(f"Password reset email sent to {email}")
        return templates.TemplateResponse(
            "forgot_password.html",
            {
                "request": request,
                "success": f"Password reset email sent to {email}. Check your inbox for instructions.",
            },
        )
    else:
        reset_url = f"{settings.BASE_URL}/reset-password/{result['reset_token']}"
        logger.warning(f"Password reset without SMTP. URL: {reset_url}")
        return templates.TemplateResponse(
            "forgot_password.html",
            {
                "request": request,
                "success": f"Use this link to reset password: {reset_url}",
            },
        )


@router.get(
    "/reset-password/{token}", response_class=HTMLResponse, include_in_schema=False
)
async def reset_password_page(request: Request, token: str):
    """Reset password form page with token."""
    return templates.TemplateResponse(
        "reset_password.html", {"request": request, "token": token}
    )


@router.post(
    "/reset-password/{token}", response_class=HTMLResponse, include_in_schema=False
)
async def reset_password(
    request: Request,
    token: str,
    password: str = Form(...),
    password2: str = Form(...),
):
    """Process password reset with token."""
    # Validate inputs
    if len(password) < 8:
        return templates.TemplateResponse(
            "reset_password.html",
            {
                "request": request,
                "token": token,
                "error": "Password must be at least 8 characters.",
            },
        )

    if password != password2:
        return templates.TemplateResponse(
            "reset_password.html",
            {
                "request": request,
                "token": token,
                "error": "Passwords do not match.",
            },
        )

    # Reset password
    result = reset_password_with_token(token, password)

    if not result["success"]:
        return templates.TemplateResponse(
            "reset_password.html",
            {"request": request, "token": token, "error": result["message"]},
        )

    # Success
    return templates.TemplateResponse(
        "index.html",
        {
            "request": request,
            "message": "Password reset successfully! You can now log in with your new password.",
        },
    )
