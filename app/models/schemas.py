
from pydantic import BaseModel, Field
from typing import List, Optional, Dict, Any


class LoginRequest(BaseModel):
	username: str
	password: Optional[str] = None


class RegisterRequest(BaseModel):
	username: str
	password: str


class TokenResponse(BaseModel):
	access_token: str
	token_type: str = "bearer"
	user_id: str
	username: str


class CaseCreateRequest(BaseModel):
	name: str
	assigned_lawyer: Optional[str] = None
	plaintiff: Optional[str] = None


class CaseUpdateRequest(BaseModel):
	name: Optional[str] = None
	assigned_lawyer: Optional[str] = None
	plaintiff: Optional[str] = None


class CaseResponse(BaseModel):
	id: str
	name: str
	assigned_lawyer: Optional[str] = None
	plaintiff: Optional[str] = None


class CasesListResponse(BaseModel):
	cases: List[CaseResponse]


class UploadResponse(BaseModel):
	document_ids: List[str]


class QueryRequest(BaseModel):
	user_id: str
	question: str
	k: int = 5
	case_id: Optional[str] = None
	document_ids: Optional[List[str]] = None


class RetrievedChunk(BaseModel):
	text: str
	score: float
	metadata: Dict[str, Any] = Field(default_factory=dict)


class GraphPath(BaseModel):
	nodes: List[str]
	relationships: List[str]


class QueryResponse(BaseModel):
	answer: str
	references: List[str] = Field(default_factory=list)
	chunks: List[RetrievedChunk] = Field(default_factory=list)
	graph_paths: List[GraphPath] = Field(default_factory=list)
