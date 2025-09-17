from datetime import datetime, timedelta, timezone
from jose import jwt
from app.config import settings


def create_access_token(subject: str) -> str:
	expires_delta = timedelta(minutes=settings.jwt_access_token_expires_minutes)
	to_encode = {"sub": subject, "exp": datetime.now(timezone.utc) + expires_delta}
	return jwt.encode(to_encode, settings.jwt_secret_key, algorithm=settings.jwt_algorithm)
