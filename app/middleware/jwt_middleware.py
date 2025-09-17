from typing import Callable, Awaitable
from fastapi import Request
from starlette.middleware.base import BaseHTTPMiddleware
from jose import jwt, JWTError
from app.config import settings


class JWTAuthMiddleware(BaseHTTPMiddleware):
	def __init__(self, app, protected_prefixes: list[str] | None = None):
		super().__init__(app)
		self.protected_prefixes = protected_prefixes or ["/documents", "/query"]

	async def dispatch(self, request: Request, call_next: Callable[[Request], Awaitable]):
		path = request.url.path
		if request.method == "OPTIONS":
			return await call_next(request)  # Allow preflight requests
		if not any(path.startswith(p) for p in self.protected_prefixes):
			return await call_next(request)

		auth_header = request.headers.get("Authorization", "")
		if not auth_header.lower().startswith("bearer "):
			return self._unauthorized()
		token = auth_header.split(" ", 1)[1].strip()
		try:
			payload = jwt.decode(token, settings.jwt_secret_key, algorithms=[settings.jwt_algorithm])
			print(f"JWT payload: {payload}")  # Debug log
			user_id = payload.get("sub")
			if not user_id:
				print("JWT missing 'sub' field")  # Debug log
				return self._unauthorized()
			request.state.user_id = user_id
		except JWTError as e:
			print(f"JWT decode error: {e}")  # Debug log
			return self._unauthorized()

		return await call_next(request)

	def _unauthorized(self):
		from starlette.responses import JSONResponse
		return JSONResponse({"detail": "Not authenticated"}, status_code=401)
