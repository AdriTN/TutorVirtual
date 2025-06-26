from src.api.schemas.themes import ThemeUpdate
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session, selectinload

from src.database.session import get_db
from src.api.dependencies.auth import admin_required
from src.models import Subject, Theme

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
    """
    Devuelve todos los temas con `subject_id`
    para que el front pueda relacionarlos.
    """
    themes = (
        db.query(Theme)
        .options(selectinload(Theme.subject))
        .all()
    )
    return [
        {
            "id":         t.id,
            "title":      t.name,
            "description": t.description,
            "subject_id":  t.subject_id,
        }
        for t in themes
    ]

@router.put("/{theme_id}", response_model=dict)
def update_theme(theme_id: int, body: ThemeUpdate, db: Session = Depends(get_db)):
    theme: Theme | None = db.query(Theme).get(theme_id)
    if not theme:
        raise HTTPException(404, "Tema no encontrado")

    if body.name:
        dup = db.query(Theme).filter(Theme.name == body.name, Theme.id != theme_id).first()
        if dup:
            raise HTTPException(409, "Ya existe otro tema con ese nombre")
        theme.name = body.name
    if body.description is not None:
        theme.description = body.description

    if body.subject_id is not None and body.subject_id != theme.subject_id:
        new_subject = db.query(Subject).get(body.subject_id)
        if not new_subject:
            raise HTTPException(404, "Asignatura destino no encontrada")
        theme.subject_id = new_subject.id

    db.commit()
    db.refresh(theme)
    return {
        "id": theme.id,
        "name": theme.name,
        "description": theme.description,
        "subject_id": theme.subject_id,
    }


@router.delete("/{theme_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_theme(theme_id: int, db: Session = Depends(get_db)):
    theme = db.query(Theme).get(theme_id)
    if not theme:
        raise HTTPException(404, "Tema no encontrado")
    db.delete(theme)
    db.commit()
