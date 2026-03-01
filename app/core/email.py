"""Email service for sending confirmation emails."""

import smtplib
import logging
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart

from app.core.config import get_settings

logger = logging.getLogger(__name__)

settings = get_settings()


def send_confirmation_email(to_email: str, confirmation_token: str) -> bool:
    """Send confirmation email to user."""
    try:
        # Create message
        msg = MIMEMultipart("alternative")
        msg["Subject"] = "Confirm Your Account - SemanticSearch API"
        msg["From"] = settings.EMAIL_FROM
        msg["To"] = to_email

        # Confirmation URL
        confirmation_url = f"{settings.BASE_URL}/confirm/{confirmation_token}"

        # Plain text version
        text = f"""
Welcome to SemanticSearch API!

Confirm your account by clicking the link below:
{confirmation_url}

This link is valid for 24 hours.

If you didn't create this account, please ignore this email.

---
SemanticSearch API
Powered by Arctic-768D ONNX INT8
"""

        # HTML version
        html = f"""
<!DOCTYPE html>
<html>
<head>
    <style>
        body {{ font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, sans-serif; line-height: 1.6; color: #333; }}
        .container {{ max-width: 600px; margin: 0 auto; padding: 20px; }}
        .header {{ background: linear-gradient(135deg, #667eea 0%, #764ba2 100%); color: white; padding: 30px; text-align: center; border-radius: 8px 8px 0 0; }}
        .content {{ background: #f9f9f9; padding: 30px; border-radius: 0 0 8px 8px; }}
        .button {{ display: inline-block; background: #667eea; color: white; padding: 12px 30px; text-decoration: none; border-radius: 5px; margin: 20px 0; }}
        .footer {{ text-align: center; margin-top: 30px; color: #666; font-size: 0.9em; }}
    </style>
</head>
<body>
    <div class="container">
        <div class="header">
            <h1>🎉 Welcome to SemanticSearch API!</h1>
        </div>
        <div class="content">
            <p>Hello,</p>
            <p>Thank you for signing up at <strong>SemanticSearch API</strong>. You're one step away from using our ultra-fast semantic search.</p>
            <p style="text-align: center;">
                <a href="{confirmation_url}" class="button">Confirm My Account</a>
            </p>
            <p style="color: #666; font-size: 0.9em;">Or copy this link in your browser:<br>
            <code style="background: #eee; padding: 5px 10px; border-radius: 3px; display: inline-block; margin-top: 5px;">{confirmation_url}</code></p>
            <p style="margin-top: 30px; color: #666;">This link is valid for <strong>24 hours</strong>.</p>
            <p style="color: #999; font-size: 0.85em; margin-top: 20px;">If you didn't create this account, you can ignore this email.</p>
        </div>
        <div class="footer">
            <p>SemanticSearch API<br>
            Powered by Arctic-768D ONNX INT8</p>
        </div>
    </div>
</body>
</html>
"""

        # Attach both versions
        part1 = MIMEText(text, "plain")
        part2 = MIMEText(html, "html")
        msg.attach(part1)
        msg.attach(part2)

        # Send email
        smtp_password = settings.SMTP_PASSWORD.strip()
        if not smtp_password or smtp_password.lower() == "your_password_here":
            logger.warning(
                f"SMTP not configured. Would send email to {to_email}: {confirmation_url}"
            )
            # In development, just log the URL
            print(f"\n{'='*60}")
            print(f"📧 CONFIRMATION EMAIL (dev mode)")
            print(f"To: {to_email}")
            print(f"URL: {confirmation_url}")
            print(f"{'='*60}\n")
            return True

        # Production: actually send email
        with smtplib.SMTP(settings.SMTP_HOST, settings.SMTP_PORT) as server:
            server.starttls()
            server.login(settings.SMTP_USER, smtp_password)
            server.send_message(msg)

        logger.info(f"Confirmation email sent to {to_email}")
        return True

    except Exception as e:
        logger.error(f"Failed to send email to {to_email}: {e}")
        return False


def send_api_key_email(to_email: str, api_key: str) -> bool:
    """Send API key to confirmed user."""
    try:
        msg = MIMEMultipart("alternative")
        msg["Subject"] = "Your API Key - SemanticSearch API"
        msg["From"] = settings.EMAIL_FROM
        msg["To"] = to_email

        text = f"""
Your Account Has Been Confirmed!

Your API Key:
{api_key}

Keep it safe and secure. You'll need it for all API requests.

Usage Example:
curl -X POST "https://api.readyapi.net/api/v1/search/query" \\
  -H "x-api-key: {api_key}" \\
  -H "Content-Type: application/json" \\
  -d '{{"query": "superhero saves the world", "top_k": 5}}'

Documentation: https://api.readyapi.net/api/docs

---
SemanticSearch API
"""

        html = f"""
<!DOCTYPE html>
<html>
<head>
    <style>
        body {{ font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, sans-serif; line-height: 1.6; color: #333; }}
        .container {{ max-width: 600px; margin: 0 auto; padding: 20px; }}
        .header {{ background: #4CAF50; color: white; padding: 30px; text-align: center; border-radius: 8px 8px 0 0; }}
        .content {{ background: #f9f9f9; padding: 30px; border-radius: 0 0 8px 8px; }}
        .api-key {{ background: #fff; border: 2px solid #4CAF50; padding: 15px; border-radius: 5px; font-family: monospace; font-size: 14px; word-break: break-all; margin: 20px 0; }}
        .code {{ background: #272822; color: #f8f8f2; padding: 15px; border-radius: 5px; overflow-x: auto; font-size: 12px; }}
        .footer {{ text-align: center; margin-top: 30px; color: #666; font-size: 0.9em; }}
    </style>
</head>
<body>
    <div class="container">
        <div class="header">
            <h1>✅ ¡Cuenta Confirmada!</h1>
        </div>
        <div class="content">
            <p>Tu cuenta ha sido activada con éxito.</p>
            <p><strong>Tu API Key:</strong></p>
            <div class="api-key">{api_key}</div>
            <p style="color: #d32f2f; font-weight: bold;">⚠️ Guárdala en un lugar seguro. No la compartas.</p>
            
            <p style="margin-top: 30px;"><strong>Ejemplo de uso:</strong></p>
            <pre class="code">curl -X POST "https://api.readyapi.net/api/v1/search/query" \\
  -H "x-api-key: {api_key}" \\
  -H "Content-Type: application/json" \\
  -d '{{"query": "superhero saves the world", "top_k": 5}}'</pre>
            
            <p style="margin-top: 20px;">📚 <a href="https://api.readyapi.net/api/docs" target="_blank">View Full Documentation</a></p>
        </div>
        <div class="footer">
            <p>SemanticSearch API</p>
        </div>
    </div>
</body>
</html>
"""

        part1 = MIMEText(text, "plain")
        part2 = MIMEText(html, "html")
        msg.attach(part1)
        msg.attach(part2)

        smtp_password = settings.SMTP_PASSWORD.strip()
        if not smtp_password or smtp_password.lower() == "your_password_here":
            logger.info(f"Would send API key email to {to_email}")
            print(f"\n{'='*60}")
            print(f"📧 API KEY EMAIL (dev mode)")
            print(f"To: {to_email}")
            print(f"API Key: {api_key}")
            print(f"{'='*60}\n")
            return True

        with smtplib.SMTP(settings.SMTP_HOST, settings.SMTP_PORT) as server:
            server.starttls()
            server.login(settings.SMTP_USER, smtp_password)
            server.send_message(msg)

        logger.info(f"API key email sent to {to_email}")
        return True

    except Exception as e:
        logger.error(f"Failed to send API key email to {to_email}: {e}")
        return False


def send_password_reset_email(to_email: str, reset_token: str) -> bool:
    """Send password reset email to user."""
    try:
        msg = MIMEMultipart("alternative")
        msg["Subject"] = "Reset your password - SemanticSearch API"
        msg["From"] = settings.EMAIL_FROM
        msg["To"] = to_email

        reset_url = f"{settings.BASE_URL}/reset-password/{reset_token}"

        text = f"""
Password Reset - SemanticSearch API

Click this link to reset your password:
{reset_url}

This link is valid for 24 hours.

If you didn't request this, ignore this email.

---
SemanticSearch API
"""

        html = f"""
<!DOCTYPE html>
<html>
<head>
    <style>
        body {{ font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, sans-serif; line-height: 1.6; color: #333; }}
        .container {{ max-width: 600px; margin: 0 auto; padding: 20px; }}
        .header {{ background: #ff9800; color: white; padding: 30px; text-align: center; border-radius: 8px 8px 0 0; }}
        .content {{ background: #f9f9f9; padding: 30px; border-radius: 0 0 8px 8px; }}
        .button {{ display: inline-block; background: #ff9800; color: white; padding: 12px 30px; text-decoration: none; border-radius: 5px; margin: 20px 0; }}
        .footer {{ text-align: center; margin-top: 30px; color: #666; font-size: 0.9em; }}
    </style>
</head>
<body>
    <div class="container">
        <div class="header">
            <h1>🔐 Reset Your Password</h1>
        </div>
        <div class="content">
            <p>Hi,</p>
            <p>You requested to reset your password for <strong>SemanticSearch API</strong>.</p>
            <p style="text-align: center;">
                <a href="{reset_url}" class="button">Reset Password</a>
            </p>
            <p style="color: #666; font-size: 0.9em;">Or copy this link in your browser:<br>
            <code style="background: #eee; padding: 5px 10px; border-radius: 3px; display: inline-block; margin-top: 5px;">{reset_url}</code></p>
            <p style="margin-top: 30px; color: #666;">This link is valid for <strong>24 hours</strong>.</p>
            <p style="color: #999; font-size: 0.85em; margin-top: 20px;">If you didn't request this, you can ignore this email.</p>
        </div>
        <div class="footer">
            <p>SemanticSearch API</p>
        </div>
    </div>
</body>
</html>
"""

        part1 = MIMEText(text, "plain")
        part2 = MIMEText(html, "html")
        msg.attach(part1)
        msg.attach(part2)

        smtp_password = settings.SMTP_PASSWORD.strip()
        if not smtp_password or smtp_password.lower() == "your_password_here":
            logger.info(f"Would send password reset email to {to_email}")
            print(f"\n{'='*60}")
            print(f"📧 PASSWORD RESET EMAIL (dev mode)")
            print(f"To: {to_email}")
            print(f"URL: {reset_url}")
            print(f"{'='*60}\n")
            return True

        with smtplib.SMTP(settings.SMTP_HOST, settings.SMTP_PORT) as server:
            server.starttls()
            server.login(settings.SMTP_USER, smtp_password)
            server.send_message(msg)

        logger.info(f"Password reset email sent to {to_email}")
        return True

    except Exception as e:
        logger.error(f"Failed to send password reset email to {to_email}: {e}")
        return False
