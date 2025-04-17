from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from ..dependencies.database_dependencies import get_db
from ..dependencies.auth_dependencies import admin_required
from ..models.subject import Subject

router = APIRouter(prefix="/subjects", tags=["subjects"])

@router.post("", status_code=status.HTTP_201_CREATED,
             dependencies=[Depends(admin_required)])
def create_subject(
    data: dict,
    db: Session = Depends(get_db)
):
    if db.query(Subject).filter(
        (Subject.name == data["name"]) | (Subject.code == data["code"])
    ).first():
        raise HTTPException(409, detail="El subject ya existe")

    subj = Subject(
        name=data["name"],
        code=data["code"],
        description=data.get("description")
    )
    db.add(subj)
    db.commit()
    db.refresh(subj)
    return {
        "id": subj.id,
        "name": subj.name,
        "code": subj.code,
        "description": subj.description,
    }

@router.get("")
def list_subjects(db: Session = Depends(get_db)):
    return [
        {
            "id": s.id,
            "name": s.name,
            "code": s.code,
            "description": s.description,
        }
        for s in db.query(Subject).all()
    ]
