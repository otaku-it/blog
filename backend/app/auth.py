import base64
import hashlib
import hmac
import json
import os
import time

from fastapi import Depends, HTTPException, status
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer
from sqlalchemy import select
from sqlalchemy.orm import Session

from .database import get_db
from .models import AdminUser

ADMIN_USERNAME = os.getenv("ADMIN_USERNAME", "baize")
ADMIN_PASSWORD = os.getenv("ADMIN_PASSWORD", "change-me-now")
AUTH_SECRET = os.getenv("AUTH_SECRET", "baize-dev-local-secret-change-me")
TOKEN_TTL = 60 * 60 * 12
bearer = HTTPBearer(auto_error=False)


def _encode(value: dict) -> str:
    raw = json.dumps(value, ensure_ascii=False, separators=(",", ":")).encode()
    body = base64.urlsafe_b64encode(raw).decode().rstrip("=")
    signature = hmac.new(AUTH_SECRET.encode(), body.encode(), hashlib.sha256).hexdigest()
    return f"{body}.{signature}"


def _decode(token: str) -> dict | None:
    try:
        body, signature = token.split(".", 1)
        expected = hmac.new(AUTH_SECRET.encode(), body.encode(), hashlib.sha256).hexdigest()
        if not hmac.compare_digest(signature, expected):
            return None
        raw = base64.urlsafe_b64decode(body + "=" * (-len(body) % 4))
        payload = json.loads(raw)
        if payload.get("exp", 0) < time.time() or payload.get("role") != "admin" or payload.get("sub") != ADMIN_USERNAME:
            return None
        return payload
    except (ValueError, TypeError, json.JSONDecodeError):
        return None


def hash_password(password: str) -> str:
    salt = os.urandom(16)
    digest = hashlib.pbkdf2_hmac("sha256", password.encode(), salt, 180_000)
    return f"pbkdf2_sha256$180000${base64.urlsafe_b64encode(salt).decode()}${base64.urlsafe_b64encode(digest).decode()}"


def verify_password(password: str, encoded: str) -> bool:
    try:
        algorithm, rounds, salt, expected = encoded.split("$", 3)
        if algorithm != "pbkdf2_sha256":
            return False
        digest = hashlib.pbkdf2_hmac("sha256", password.encode(), base64.urlsafe_b64decode(salt), int(rounds))
        return hmac.compare_digest(base64.urlsafe_b64encode(digest).decode(), expected)
    except (ValueError, TypeError):
        return False


def authenticate(db: Session, username: str, password: str) -> str | None:
    user = db.scalar(select(AdminUser).where(AdminUser.username == username))
    if user and verify_password(password, user.password_hash):
        password_version = hashlib.sha256(user.password_hash.encode()).hexdigest()
        return _encode({"sub": username, "role": "admin", "pwd": password_version, "exp": int(time.time()) + TOKEN_TTL})
    return None


def require_admin(credentials: HTTPAuthorizationCredentials | None = Depends(bearer), db: Session = Depends(get_db)):
    payload = _decode(credentials.credentials) if credentials else None
    user = db.scalar(select(AdminUser).where(AdminUser.username == (payload or {}).get("sub"))) if payload else None
    password_version = hashlib.sha256(user.password_hash.encode()).hexdigest() if user else None
    if not payload or not user or password_version != payload.get("pwd"):
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="需要管理员登录", headers={"WWW-Authenticate": "Bearer"})
    return {**payload, "user": user}
