from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from ...database.session import get_db
from ...api.dependencies.auth import admin_required
from ...models import Subject, Theme

router = APIRouter(prefix="/themes", tags=["Themes"])


@router.post("", status_code=status.HTTP_201_CREATED, dependencies=[Depends(admin_required)])
def create_theme(body: dict, db: Session = Depends(get_db)):
    if db.query(Theme).filter(Theme.nombre == body["nombre"]).first():
        raise HTTPException(status.HTTP_409_CONFLICT, "Duplicado")

    subj = db.query(Subject).get(body["subject_id"])
    if not subj:
        raise HTTPException(status.HTTP_404_NOT_FOUND, "Subject no encontrado")

    tema = Theme(
        nombre=body["nombre"],
        descripcion=body.get("descripcion"),
        subject_id=subj.id,
    )
    db.add(tema)
    db.commit()
    db.refresh(tema)
    return {"id": tema.id, "nombre": tema.nombre}


@router.get("", summary="Lista pública de temas")
def list_all(db: Session = Depends(get_db)):
    return [
        {"id": t.id, "nombre": t.nombre, "description": t.descripcion}
        for t in db.query(Theme).all()
    ]
