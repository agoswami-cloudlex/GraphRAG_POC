import os
import shutil
import uuid
from typing import List, Optional
from fastapi import APIRouter, UploadFile, File, HTTPException, Request, Depends, Form
from sqlmodel import Session, select
from app.models.schemas import UploadResponse
from app.config import settings
from app.db import get_session
from app.models.models import Document, Case
from app.services.graph_store import graph_store


router = APIRouter()

@router.delete("/delete/{document_id}")
async def delete_document(document_id: str, request: Request, session: Session = Depends(get_session)):
	user_id = getattr(request.state, "user_id", "")
	if not user_id:
		raise HTTPException(status_code=401, detail="Not authenticated")
	# Delete from DB
	doc = session.exec(select(Document).where(Document.id == document_id, Document.owner_user_id == user_id)).first()
	if not doc:
		raise HTTPException(status_code=404, detail="Document not found")
	session.delete(doc)
	session.commit()
	# Delete embeddings
	from app.services.vector_store import vector_store
	vector_store.delete_document_chunks(user_id, document_id)
	return {"status": "deleted"}

@router.get("/case/{case_id}", response_model=List[dict])
async def list_documents_for_case(case_id: str, request: Request, session: Session = Depends(get_session)):
	user_id = getattr(request.state, "user_id", "")
	if not user_id:
		raise HTTPException(status_code=401, detail="Not authenticated")
	docs = list(session.exec(select(Document).where(Document.case_id == case_id, Document.owner_user_id == user_id)))
	return [
		{"id": d.id, "filename": d.filename, "uploaded_at": d.uploaded_at.isoformat()} for d in docs
	]

@router.post("/upload", response_model=UploadResponse)
async def upload_documents(
	request: Request,
	files: List[UploadFile] = File(...),
	case_id: str = Form(...),
	case_name: Optional[str] = Form(None),
	session: Session = Depends(get_session),
) -> UploadResponse:
	user_id = getattr(request.state, "user_id", "")
	if not user_id:
		raise HTTPException(status_code=401, detail="Not authenticated")

	# Ensure case exists for this user (create if not)
	c = session.exec(select(Case).where(Case.id == case_id, Case.owner_user_id == user_id)).first()
	if not c:
		if not case_name:
			raise HTTPException(status_code=400, detail="Unknown case_id; provide case_name to create")
		c = Case(id=case_id, owner_user_id=user_id, name=case_name)
		session.add(c)
		session.commit()

	# Save uploaded files to input directory
	os.makedirs(settings.upload_dir, exist_ok=True)
	upload_ids: List[str] = []
	for f in files:
		file_ext = os.path.splitext(f.filename or "")[1].lower()
		if file_ext not in [".txt", ".md"]:
			raise HTTPException(status_code=400, detail="Unsupported file type. Use .txt or .md")
		# Use original filename if possible, else generate a uuid
		safe_name = f.filename if f.filename else f"{uuid.uuid4()}{file_ext}"
		temp_path = os.path.join(settings.upload_dir, safe_name)
		with open(temp_path, "wb") as out:
			shutil.copyfileobj(f.file, out)
		upload_ids.append(safe_name)

	# Double-check files exist before indexing
	for fname in upload_ids:
		if not os.path.exists(os.path.join(settings.upload_dir, fname)):
			raise HTTPException(status_code=500, detail=f"File {fname} was not saved correctly.")

	# Trigger GraphRAG indexing after upload
	await graph_store.run_indexing()

	return UploadResponse(document_ids=upload_ids)

	
