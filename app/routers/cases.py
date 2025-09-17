from typing import List
from fastapi import APIRouter, Depends, HTTPException, Request
from sqlmodel import Session, select
from app.db import get_session
from app.models.schemas import CaseCreateRequest, CaseResponse, CasesListResponse, CaseUpdateRequest
from app.models.models import Case


router = APIRouter()


@router.get("/", response_model=CasesListResponse)
async def list_cases(request: Request, session: Session = Depends(get_session)) -> CasesListResponse:
	user_id = getattr(request.state, "user_id", "")
	print(user_id)
	if not user_id:
		raise HTTPException(status_code=401, detail="Not authenticated")
	rows: List[Case] = list(session.exec(select(Case).where(Case.owner_user_id == user_id)))
	return CasesListResponse(cases=[CaseResponse(id=r.id, name=r.name, assigned_lawyer=r.assigned_lawyer, plaintiff=r.plaintiff) for r in rows])


@router.patch("/{case_id}", response_model=CaseResponse)
async def update_case(case_id: str, request: Request, payload: CaseUpdateRequest, session: Session = Depends(get_session)) -> CaseResponse:
	user_id = getattr(request.state, "user_id", "")
	if not user_id:
		raise HTTPException(status_code=401, detail="Not authenticated")
	c = session.exec(select(Case).where(Case.id == case_id, Case.owner_user_id == user_id)).first()
	if not c:
		raise HTTPException(status_code=404, detail="Case not found")
	if payload.name is not None: c.name = payload.name
	if payload.assigned_lawyer is not None: c.assigned_lawyer = payload.assigned_lawyer
	if payload.plaintiff is not None: c.plaintiff = payload.plaintiff
	session.add(c)
	session.commit()
	return CaseResponse(id=c.id, name=c.name, assigned_lawyer=c.assigned_lawyer, plaintiff=c.plaintiff)
