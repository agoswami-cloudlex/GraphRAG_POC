from fastapi import APIRouter, HTTPException, Depends
from sqlmodel import Session, select
from passlib.context import CryptContext
from app.models.schemas import LoginRequest, RegisterRequest, TokenResponse
from app.models.models import User
from app.services.auth import create_access_token
from app.db import get_session


router = APIRouter()
_pwd_ctx = CryptContext(schemes=["bcrypt"], deprecated="auto")


@router.post("/register", response_model=TokenResponse)
async def register(payload: RegisterRequest, session: Session = Depends(get_session)) -> TokenResponse:
	username = payload.username.strip()
	if not username or not payload.password:
		raise HTTPException(status_code=400, detail="username and password required")
	existing = session.exec(select(User).where(User.username == username)).first()
	if existing:
		raise HTTPException(status_code=409, detail="username already exists")
	user = User(username=username, password_hash=_pwd_ctx.hash(payload.password))
	session.add(user)
	session.commit()
	session.refresh(user)
	token = create_access_token(subject=str(user.id))
	return TokenResponse(access_token=token, user_id=str(user.id), username=user.username)


@router.post("/login", response_model=TokenResponse)
async def login(payload: LoginRequest, session: Session = Depends(get_session)) -> TokenResponse:
	username = payload.username.strip()
	if not username or not payload.password:
		raise HTTPException(status_code=400, detail="username and password required")
	user = session.exec(select(User).where(User.username == username)).first()
	if not user or not _pwd_ctx.verify(payload.password, user.password_hash):
		raise HTTPException(status_code=401, detail="invalid credentials")
	token = create_access_token(subject=str(user.id))
	return TokenResponse(access_token=token, user_id=str(user.id), username=user.username)
