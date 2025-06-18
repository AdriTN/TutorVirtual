from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from ...database.session import get_db
from ...api.dependencies.auth import admin_required
from ...models import Subject, Theme

router = APIRouter()


@router.post("", status_code=status.HTTP_201_CREATED, dependencies=[Depends(admin_required)])
def create_theme(body: dict, db: Session = Depends(get_db)):
    if db.query(Theme).filter(Theme.name == body["name"]).first():
        raise HTTPException(status.HTTP_409_CONFLICT, "Duplicado")

    subj = db.query(Subject).get(body["subject_id"])
    if not subj:
        raise HTTPException(status.HTTP_404_NOT_FOUND, "Subject no encontrado")

    tema = Theme(
        name=body["name"],
        description=body.get("descripcion"),
        subject_id=subj.id,
    )
    db.add(tema)
    db.commit()
    db.refresh(tema)
    return {"id": tema.id, "name": tema.name}


@router.get("", summary="Lista pública de temas")
def list_all(db: Session = Depends(get_db)):
    return [
        {"id": t.id, "name": t.name, "description": t.description}
        for t in db.query(Theme).all()
    ]
