"""Web UI endpoints (HTML templates with Jinja2)."""

from fastapi import APIRouter, Request, Form, HTTPException
from fastapi.responses import HTMLResponse, RedirectResponse, JSONResponse
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
    save_consent_record,
    get_consent_records,
    delete_user_account,
    get_user_deletion_summary,
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
            "spaceship": "user_1",  # User 1 tenant has spaceship parts
            "readyapi": "user_8",  # User 8 tenant has ReadyAPI documentation
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


def _extract_keywords(content: str) -> list[str]:
    """Extract keyword list from stored content text."""
    if not content or "Keywords:" not in content:
        return []

    keyword_text = content.split("Keywords:", 1)[1].strip()
    return [k.strip() for k in keyword_text.split(",") if k.strip()]


def _get_definition_image(title: str) -> str:
    """Get reference image for plant definition cards."""
    image_map = {
        "root": "https://images.unsplash.com/photo-1466692476868-aef1dfb1e735",
        "stem": "https://images.unsplash.com/photo-1464226184884-fa280b87c399",
        "leaf": "https://images.unsplash.com/photo-1472141521881-95d0e87e2e39",
        "flower": "https://images.unsplash.com/photo-1490750967868-88aa4486c946",
        "fruit": "https://images.unsplash.com/photo-1619566636858-adf3ef46400b",
    }
    return image_map.get((title or "").strip().lower(), image_map["leaf"])


@router.get("/", response_class=HTMLResponse, include_in_schema=False)
async def home(request: Request):
    """Home page."""
    return templates.TemplateResponse("index.html", {"request": request})


@router.get("/api-docs", response_class=HTMLResponse, include_in_schema=False)
async def api_docs(request: Request):
    """Redirect to Swagger docs in a new tab."""
    return HTMLResponse("""
    <html>
    <head><title>Redirecting...</title></head>
    <body>
        <script>
            window.location.href = '/api/docs';
        </script>
        <p>Redirecting to API documentation...</p>
    </body>
    </html>
    """)


@router.get("/demos", response_class=HTMLResponse, include_in_schema=False)
async def demos(request: Request):
    """Live demos page with multiple datasets."""
    return templates.TemplateResponse("demos.html", {"request": request})


@router.get("/privacy-policy", response_class=HTMLResponse, include_in_schema=False)
async def privacy_policy(request: Request):
    """Privacy policy page."""
    return templates.TemplateResponse("privacy_policy.html", {"request": request})


@router.get("/delete-account", response_class=HTMLResponse, include_in_schema=False)
async def delete_account_page(request: Request):
    """Account deletion page (GDPR Right to Erasure)."""
    return templates.TemplateResponse("delete_account.html", {"request": request})


@router.post("/api/consent", include_in_schema=False)
async def save_consent(request: Request):
    """
    API endpoint to save consent record (GDPR compliance).
    Called when user accepts privacy policy during registration.
    """
    try:
        data = await request.json()

        # Extract consent data
        user_email = data.get("email")
        privacy_version = data.get("privacy_version", "v1.0")
        consent_method = data.get("consent_method", "Web Form")

        # Get user IP from request headers
        client_host = request.client.host if request.client else None
        user_agent = request.headers.get("user-agent")

        # Validate email
        if not user_email:
            return JSONResponse(
                {"success": False, "message": "Email is required"}, status_code=400
            )

        # Save consent record
        result = save_consent_record(
            user_email=user_email,
            consent_status=True,
            consent_type="privacy_policy",
            privacy_version=privacy_version,
            consent_method=consent_method,
            consent_ip=client_host,
            user_agent=user_agent,
        )

        if result["success"]:
            return JSONResponse(
                {
                    "success": True,
                    "message": "Consent recorded successfully",
                    "timestamp": result["timestamp"],
                }
            )
        else:
            return JSONResponse(
                {"success": False, "message": result["message"]}, status_code=500
            )
    except Exception as e:
        logger.error(f"Consent save error: {e}")
        return JSONResponse(
            {"success": False, "message": f"Error: {str(e)}"}, status_code=500
        )


@router.post("/api/delete-account", include_in_schema=False)
async def delete_account_request(request: Request):
    """
    GDPR Right to Erasure: Delete user account and associated data.

    IMPORTANT:
    - Deleted: User data, files, embeddings, search logs
    - Preserved: Consent records (legal proof of consent - 3 years)
    """
    try:
        data = await request.json()
        email = data.get("email")
        password = data.get("password")

        if not email or not password:
            return JSONResponse(
                {"success": False, "message": "Email and password required"},
                status_code=400,
            )

        # Verify credentials (user must confirm password)
        user = get_user(email)
        if not user or not verify_password(email, password):
            return JSONResponse(
                {"success": False, "message": "Invalid email or password"},
                status_code=401,
            )

        # Get deletion summary before deleting
        summary = get_user_deletion_summary(email)

        # Delete account
        result = delete_user_account(email)

        if result["success"]:
            return JSONResponse(
                {
                    "success": True,
                    "message": "Account deleted successfully",
                    "summary": summary,
                    "note": "Consent records preserved for 3 years (legal compliance)",
                    "deleted_at": result["deleted_at"],
                }
            )
        else:
            return JSONResponse(
                {"success": False, "message": result["message"]}, status_code=500
            )
    except Exception as e:
        logger.error(f"Account deletion error: {e}")
        return JSONResponse(
            {"success": False, "message": f"Error: {str(e)}"}, status_code=500
        )


@router.get("/api/account-deletion-preview", include_in_schema=False)
async def account_deletion_preview(request: Request, email: str = None):
    """
    Preview what will be deleted if user requests account deletion.
    Requires authentication via API key or session.
    """
    try:
        # Get user email from query param or session
        if not email:
            return JSONResponse(
                {"success": False, "message": "Email parameter required"},
                status_code=400,
            )

        summary = get_user_deletion_summary(email)

        if not summary.get("found"):
            return JSONResponse(
                {"success": False, "message": "User not found"}, status_code=404
            )

        return JSONResponse(summary)
    except Exception as e:
        logger.error(f"Error getting deletion preview: {e}")
        return JSONResponse(
            {"success": False, "message": f"Error: {str(e)}"}, status_code=500
        )


@router.post("/search-partial", response_class=HTMLResponse, include_in_schema=False)
async def search_partial(
    request: Request,
    query: str = Form(...),
    dataset: str = Form(default="movies"),
    include_content: str = Form(default="false"),
):
    """HTMX endpoint that returns HTML partial with search results."""
    try:
        include_content_bool = include_content.lower() == "true"

        if not query or len(query.strip()) < 2:
            if dataset == "spaceship":
                return templates.TemplateResponse(
                    "spaceship_results.html",
                    {
                        "request": request,
                        "results": [],
                        "timing": 0,
                        "include_content": include_content_bool,
                    },
                )
            elif dataset == "definitions":
                return templates.TemplateResponse(
                    "definitions_results.html",
                    {
                        "request": request,
                        "results": [],
                        "timing": 0,
                        "include_content": include_content_bool,
                    },
                )
            else:
                return templates.TemplateResponse(
                    "results_list.html",
                    {
                        "request": request,
                        "results": [],
                        "timing": 0,
                        "include_content": include_content_bool,
                    },
                )

        # Get search engine for the specific dataset
        search_engine = get_search_engine(dataset)
        results, timing = search_engine.search(query, top_k=5, include_content=True)

        # Only process special fields for spaceship/legacy datasets
        if dataset != "definitions":
            for result in results:
                result["summary"] = _extract_summary(result.get("content", ""))
                result["keywords_list"] = _extract_keywords(result.get("content", ""))
                result["reference_image"] = _get_definition_image(
                    result.get("title", "")
                )

        if dataset == "spaceship":
            return templates.TemplateResponse(
                "spaceship_results.html",
                {
                    "request": request,
                    "results": results,
                    "timing": timing,
                    "include_content": include_content_bool,
                },
            )
        elif dataset == "definitions":
            return templates.TemplateResponse(
                "definitions_results.html",
                {
                    "request": request,
                    "results": results,
                    "timing": timing,
                    "include_content": include_content_bool,
                },
            )
        else:
            return templates.TemplateResponse(
                "results_list.html",
                {
                    "request": request,
                    "results": results,
                    "timing": timing,
                    "include_content": include_content_bool,
                },
            )
    except Exception as e:
        logger.error(f"Search error: {e}")
        template = "results_list.html"
        if dataset == "spaceship":
            template = "spaceship_results.html"
        elif dataset == "definitions":
            template = "definitions_results.html"
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


@router.get("/dashboard", response_class=HTMLResponse, include_in_schema=False)
async def dashboard_page(request: Request):
    """User dashboard page."""
    return templates.TemplateResponse("dashboard.html", {"request": request})


@router.get("/profile", response_class=HTMLResponse, include_in_schema=False)
async def profile_page(request: Request):
    """Profile settings page."""
    return templates.TemplateResponse("profile.html", {"request": request})


@router.post("/change-password", response_class=HTMLResponse, include_in_schema=False)
async def change_password(
    request: Request,
    current_password: str = Form(...),
    new_password: str = Form(...),
    confirm_password: str = Form(...),
):
    """Change user password when logged in."""
    from app.db.users import verify_password, update_password

    # Get user email from localStorage via a hidden field or from form
    # Since we can't directly access localStorage in a form POST,
    # we'll use the API key sent in a hidden field (from localStorage via JS)

    # Get API key from form (hidden field set by JavaScript)
    form_data = await request.form()
    api_key = form_data.get("api_key")

    if not api_key:
        return templates.TemplateResponse(
            "profile.html",
            {"request": request, "error": "Not authenticated. Please log in first."},
        )

    # Get user by API key
    from app.db.users import get_user_by_api_key

    user = get_user_by_api_key(api_key)
    if not user:
        return templates.TemplateResponse(
            "profile.html",
            {"request": request, "error": "Invalid session. Please log in again."},
        )

    email = user.get("email")

    # Validate passwords match
    if new_password != confirm_password:
        return templates.TemplateResponse(
            "profile.html",
            {"request": request, "error": "New passwords do not match."},
        )

    # Validate new password length
    if len(new_password) < 8:
        return templates.TemplateResponse(
            "profile.html",
            {"request": request, "error": "Password must be at least 8 characters."},
        )

    # Verify current password
    if not verify_password(email, current_password):
        return templates.TemplateResponse(
            "profile.html",
            {"request": request, "error": "Current password is incorrect."},
        )

    # Change password
    try:
        update_password(email, new_password)
        return templates.TemplateResponse(
            "profile.html",
            {
                "request": request,
                "success": "Password changed successfully!",
            },
        )
    except Exception as e:
        logger.error(f"Password change error for {email}: {str(e)}")
        return templates.TemplateResponse(
            "profile.html",
            {
                "request": request,
                "error": "Failed to change password. Please try again.",
            },
        )


@router.api_route("/{path_name:path}", methods=["GET"], include_in_schema=False)
async def catch_all_404(request: Request, path_name: str):
    """Catch-all route for 404 errors."""
    return templates.TemplateResponse("404.html", {"request": request}, status_code=404)
