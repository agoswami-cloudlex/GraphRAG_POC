from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.config import settings
from app.routers import auth, documents, query
from app.middleware.jwt_middleware import JWTAuthMiddleware
from app.db import init_db

from app.routers import cases
from app.services.graph_store import graph_store


app = FastAPI(title="GraphRAG Service", version="0.1.0")

app.add_middleware(
	CORSMiddleware,
	allow_origins=["*"],
	allow_credentials=True,
	allow_methods=["*"],
	allow_headers=["*"]
)
app.add_middleware(JWTAuthMiddleware, protected_prefixes=["/documents", "/query", "/cases"])



@app.on_event("startup")
async def on_startup() -> None:
	init_db()


@app.get("/health")
async def health_check() -> dict:
	return {"status": "ok"}


app.include_router(auth.router, prefix="/auth", tags=["auth"])
app.include_router(documents.router, prefix="/documents", tags=["documents"])
app.include_router(query.router, prefix="/query", tags=["query"])
app.include_router(cases.router, prefix="/cases", tags=["cases"])
