from datetime import datetime, timedelta, timezone
import hashlib
import secrets

from fastapi import Depends, HTTPException, status
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer
from jose import JWTError, jwt
from passlib.context import CryptContext
from sqlalchemy import select

from QAWithPDF.config import settings
from QAWithPDF.db import get_session
from QAWithPDF.db_models import ApiKey, User
from QAWithPDF.schemas import LoginResponse

security = HTTPBearer(auto_error=True)
pwd_context = CryptContext(schemes=["pbkdf2_sha256"], deprecated="auto")


def _create_access_token(username: str) -> tuple[str, int]:
    expire_minutes = max(settings.auth_token_expire_minutes, 1)
    expires_at = datetime.now(timezone.utc) + timedelta(minutes=expire_minutes)
    payload = {
        "sub": username,
        "exp": expires_at,
        "iat": datetime.now(timezone.utc),
        "jti": secrets.token_hex(8),
    }
    token = jwt.encode(payload, settings.auth_secret_key, algorithm=settings.auth_algorithm)
    return token, expire_minutes * 60


def _create_login_response(username: str) -> LoginResponse:
    token, expires_in = _create_access_token(username=username)
    return LoginResponse(access_token=token, expires_in=expires_in, username=username)


def signup_user(username: str, password: str) -> LoginResponse:
    normalized_username = username.strip()
    if not normalized_username:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Username is required")

    with get_session() as session:
        existing = session.execute(select(User).where(User.username == normalized_username)).scalar_one_or_none()
        if existing is not None:
            raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail="Username already exists")

        new_user = User(username=normalized_username, password_hash=pwd_context.hash(password))
        session.add(new_user)

    return _create_login_response(username=normalized_username)


def login_user(username: str, password: str) -> LoginResponse:
    normalized_username = username.strip()

    with get_session() as session:
        user = session.execute(select(User).where(User.username == normalized_username)).scalar_one_or_none()
        if user is not None and pwd_context.verify(password, user.password_hash):
            return _create_login_response(username=normalized_username)

    # Backward-compatible fallback to env credentials for first-time bootstrapping.
    valid_user = secrets.compare_digest(normalized_username, settings.auth_username)
    valid_pass = secrets.compare_digest(password, settings.auth_password)
    if valid_user and valid_pass:
        return _create_login_response(username=normalized_username)

    raise HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Invalid username or password",
    )


def get_current_user(credentials: HTTPAuthorizationCredentials = Depends(security)) -> str:
    token = credentials.credentials
    try:
        payload = jwt.decode(token, settings.auth_secret_key, algorithms=[settings.auth_algorithm])
        username = payload.get("sub")
        if not isinstance(username, str) or not username.strip():
            raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid authentication token")
        return username
    except JWTError:
        # Fallback: support product API keys in Bearer header.
        hashed = hashlib.sha256(token.encode("utf-8")).hexdigest()
        with get_session() as session:
            key = (
                session.execute(
                    select(ApiKey).where(ApiKey.key_hash == hashed, ApiKey.is_active.is_(True))
                )
                .scalars()
                .first()
            )
            if key is not None:
                key.last_used_at = datetime.utcnow()
                return key.owner_username

        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid or expired token")
