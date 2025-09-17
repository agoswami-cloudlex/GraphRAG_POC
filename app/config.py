import os
from pydantic import BaseModel
from dotenv import load_dotenv


load_dotenv()


class Settings(BaseModel):
	port: int = int(os.getenv("PORT", "8001"))
	chroma_persist_dir: str = os.getenv("CHROMA_PERSIST_DIR", ".chroma")
	# Azure OpenAI
	azure_api_base: str = os.getenv("AZURE_OPENAI_API_BASE")
	azure_api_version: str = os.getenv("AZURE_OPENAI_API_VERSION", "2025-01-01-preview")
	azure_embedding_api_version: str = os.getenv("AZURE_OPENAI_EMBEDDING_API_VERSION")
	azure_api_key: str = os.getenv("AZURE_OPENAI_API_KEY")
	azure_chat_deployment: str = os.getenv("AZURE_OPENAI_CHAT_DEPLOYMENT")
	azure_embedding_deployment: str = os.getenv("AZURE_OPENAI_EMBEDDING_DEPLOYMENT")
	upload_dir: str = os.getenv("UPLOAD_DIR", "input")
	demo_users: list[str] = os.getenv("DEMO_USERS", "alice,bob").split(",")
	# JWT
	jwt_secret_key: str = os.getenv("JWT_SECRET_KEY", "change_me")
	jwt_algorithm: str = os.getenv("JWT_ALGORITHM", "HS256")
	jwt_access_token_expires_minutes: int = int(os.getenv("JWT_ACCESS_TOKEN_EXPIRES_MINUTES", "60"))
	# CORS
	frontend_origins: list[str] = os.getenv("FRONTEND_ORIGINS", "http://localhost:5173,http://localhost:5174").split(",")


settings = Settings()
