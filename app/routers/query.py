from fastapi import APIRouter, HTTPException, Request
from typing import List
from app.models.schemas import QueryRequest, QueryResponse, RetrievedChunk, GraphPath
from app.services.graph_store import graph_store
from app.services.llm import answer_question


router = APIRouter()


@router.post("/", response_model=QueryResponse)
async def ask(request: Request, payload: QueryRequest) -> QueryResponse:
	user_id = payload.user_id.strip() or getattr(request.state, "user_id", "")
	if not user_id:
		raise HTTPException(status_code=401, detail="Not authenticated")
	if not payload.question.strip():
		raise HTTPException(status_code=400, detail="question required")
	# Call GraphRAG query API
	result = await graph_store.query(payload.question)
	# Map response to QueryResponse
	answer = str(result.get("response", ""))
	# For demonstration, references/chunks/paths are empty or can be parsed from context if needed
	return QueryResponse(answer=answer, references=[], chunks=[], graph_paths=[])
