
import os
import shutil
import uuid
import glob
from typing import List, Optional
from fastapi import APIRouter, UploadFile, File, HTTPException, Request, Depends, Form
from sqlmodel import Session, select
from app.models.schemas import UploadResponse
from app.config import settings
from app.db import get_session
from app.models.models import Document, Case, User
from app.services.graph_store import graph_store
from app.services.vector_store import vector_store


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

	# Get firm info (user)
	from app.models.models import User
	user = session.exec(select(User).where(User.id == user_id)).first()
	if not user:
		raise HTTPException(status_code=404, detail="User not found")
	firm_name = user.username
	firm_id = user.id
	case_name = c.name
	case_id_val = c.id
	from app.services.extract_text import extract_text
	upload_ids: List[str] = []
	supported_exts = [".txt", ".md", ".pdf", ".docx", ".pptx"]
	for f in files:
		file_ext = os.path.splitext(f.filename or "")[1].lower()
		if file_ext not in supported_exts:
			raise HTTPException(status_code=400, detail="Unsupported file type. Use .txt, .md, .pdf, .docx, or .pptx")
		document_id = str(uuid.uuid4())
		document_name = os.path.splitext(f.filename)[0] if f.filename else f"document"
		# Build the directory path
		dir_path = os.path.join(
			settings.upload_dir,
			f"{firm_name}_{firm_id}",
			f"{case_name}_{case_id_val}",
			f"{document_name}_{document_id}"
		)
		os.makedirs(dir_path, exist_ok=True)
		file_path = os.path.join(dir_path, f.filename)
		with open(file_path, "wb") as out:
			shutil.copyfileobj(f.file, out)
		# Extract text and save as .txt
		extracted_text = extract_text(file_path)
		if extracted_text:
			text_path = os.path.join(dir_path, f"{document_name}_{document_id}.txt")
			with open(text_path, "w", encoding="utf-8") as txt_out:
				txt_out.write(extracted_text)
		else:
			raise HTTPException(status_code=400, detail=f"Could not extract text from {f.filename}")
		# Store document in DB with this document_id
		doc = Document(id=document_id, owner_user_id=firm_id, case_id=case_id_val, filename=f.filename)
		session.add(doc)
		session.commit()
		upload_ids.append(document_id)

	# Double-check files exist before indexing
	for doc_id in upload_ids:
		dir_path = os.path.join(
			settings.upload_dir,
			f"{firm_name}_{firm_id}",
			f"{case_name}_{case_id_val}",
			f"*{doc_id}"
		)
		# Check if any file exists in this directory
		import glob
		found = glob.glob(os.path.join(dir_path, "*"))
		if not found:
			raise HTTPException(status_code=500, detail=f"Document {doc_id} was not saved correctly.")

	# Trigger GraphRAG indexing after upload
	await graph_store.run_indexing()

	return UploadResponse(document_ids=upload_ids)

	
