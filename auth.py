"""
Mercury Dashboard Authentication Module
Provides session token generation, verification, and route protection.
"""

import os
import hmac
import hashlib
import time
from fastapi import Request, HTTPException, status
from fastapi.responses import JSONResponse

# Credentials loaded dynamically from SQLite settings or environment variables
DEFAULT_USERNAME = os.getenv("DASHBOARD_USERNAME", "admin").strip()
DEFAULT_PASSWORD = os.getenv("DASHBOARD_PASSWORD", "").strip()
COOKIE_NAME = "mercury_session"
SESSION_DURATION_SECONDS = 60 * 60 * 24 * 30  # 30 days


def get_target_username() -> str:
    try:
        import database
        val = database.get_setting("DASHBOARD_USERNAME")
        if val:
            return val
    except Exception:
        pass
    return os.getenv("DASHBOARD_USERNAME", DEFAULT_USERNAME).strip()


def get_target_password() -> str:
    try:
        import database
        val = database.get_setting("DASHBOARD_PASSWORD")
        if val:
            return val
    except Exception:
        pass
    return os.getenv("DASHBOARD_PASSWORD", DEFAULT_PASSWORD).strip()


def get_auth_secret() -> bytes:
    try:
        import database
        val = database.get_setting("AUTH_SECRET")
        if val:
            return val.encode("utf-8")
    except Exception:
        pass
    return os.getenv("AUTH_SECRET", "Mercury_Auth_Secret_Key_Secure_9988").encode("utf-8")


def verify_credentials(username: str, password: str) -> bool:
    """Verifies username and password against dynamic settings or environment variables."""
    target_user = get_target_username()
    target_pass = get_target_password()
    
    if not target_pass:
        print("[AUTH WARNING] DASHBOARD_PASSWORD is not set in settings or environment!")
        return False
    
    # Constant-time comparison to prevent timing attacks
    user_ok = hmac.compare_digest(username.strip(), target_user)
    pass_ok = hmac.compare_digest(password.strip(), target_pass)
    return user_ok and pass_ok


def create_session_token(username: str) -> str:
    """Creates a signed, tamper-proof session token."""
    expires_at = int(time.time()) + SESSION_DURATION_SECONDS
    payload = f"{username}:{expires_at}"
    secret = get_auth_secret()
    signature = hmac.new(secret, payload.encode("utf-8"), hashlib.sha256).hexdigest()
    return f"{payload}:{signature}"


def verify_session_token(token: str) -> bool:
    """Validates the session token signature and expiration."""
    if not token or ":" not in token:
        return False
    parts = token.split(":")
    if len(parts) != 3:
        return False
    username, expires_at_str, signature = parts
    try:
        expires_at = int(expires_at_str)
    except ValueError:
        return False

    if time.time() > expires_at:
        return False  # Expired

    payload = f"{username}:{expires_at_str}"
    secret = get_auth_secret()
    expected_sig = hmac.new(secret, payload.encode("utf-8"), hashlib.sha256).hexdigest()
    return hmac.compare_digest(signature, expected_sig)


def is_authenticated(request: Request) -> bool:
    """Checks if incoming HTTP request has a valid session cookie."""
    token = request.cookies.get(COOKIE_NAME)
    if not token:
        # Also check Authorization header as fallback: Bearer <token>
        auth_header = request.headers.get("Authorization", "")
        if auth_header.startswith("Bearer "):
            token = auth_header.split(" ", 1)[1].strip()
    return verify_session_token(token)


def require_auth(request: Request):
    """FastAPI dependency to protect sensitive API endpoints."""
    if not is_authenticated(request):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Unauthorized: Valid Mercury session required"
        )
