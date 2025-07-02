import structlog
from src.api.schemas.themes import ThemeUpdate, ThemeCreate
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session, selectinload

from src.database.session import get_db
from src.api.dependencies.auth import admin_required
from src.models import Subject, Theme

router = APIRouter()
logger = structlog.get_logger(__name__)


@router.post("", status_code=status.HTTP_201_CREATED, dependencies=[Depends(admin_required)])
def create_theme(body: ThemeCreate, db: Session = Depends(get_db)):
    logger.info("Intentando crear tema", name=body.name, description=body.description, subject_id=body.subject_id)
    if db.query(Theme).filter(Theme.name == body.name).first():
        logger.warn("Conflicto: Ya existe un tema con el mismo nombre", name=body.name)
        raise HTTPException(status.HTTP_409_CONFLICT, "Duplicado: Ya existe un tema con ese nombre")

    subj = db.query(Subject).get(body.subject_id)
    if not subj:
        logger.warn("Asignatura no encontrada al crear tema", subject_id=body.subject_id, theme_name=body.name)
        raise HTTPException(status.HTTP_404_NOT_FOUND, f"Asignatura con ID {body.subject_id} no encontrada")

    tema = Theme(
        name=body.name,
        description=body.description,
        subject_id=subj.id,
    )
    db.add(tema)
    db.commit()
    db.refresh(tema)
    logger.info("Tema creado exitosamente", theme_id=tema.id, name=tema.name, subject_id=tema.subject_id)
    return {"id": tema.id, "name": tema.name, "description": tema.description, "subject_id": tema.subject_id}


@router.get("", summary="Lista pública de temas")
def list_all(db: Session = Depends(get_db)):
    """
    Devuelve todos los temas con `subject_id`
    para que el front pueda relacionarlos.
    """
    logger.info("Listando todos los temas")
    themes = (
        db.query(Theme)
        .options(selectinload(Theme.subject))
        .all()
    )
    logger.info("Temas listados", count=len(themes))
    return [
        {
            "id":         t.id,
            "title":      t.name,
            "description": t.description,
            "subject_id":  t.subject_id,
        }
        for t in themes
    ]

@router.put("/{theme_id}", response_model=dict, dependencies=[Depends(admin_required)])
def update_theme(theme_id: int, body: ThemeUpdate, db: Session = Depends(get_db)):
    logger.info("Intentando actualizar tema", theme_id=theme_id, update_data=body.model_dump(exclude_none=True))
    theme: Theme | None = db.query(Theme).get(theme_id)
    if not theme:
        logger.warn("Tema no encontrado al intentar actualizar", theme_id=theme_id)
        raise HTTPException(status.HTTP_404_NOT_FOUND, "Tema no encontrado")

    if body.name:
        dup = db.query(Theme).filter(Theme.name == body.name, Theme.id != theme_id).first()
        if dup:
            logger.warn("Conflicto: Ya existe otro tema con el nuevo nombre", new_name=body.name, existing_theme_id=dup.id)
            raise HTTPException(status.HTTP_409_CONFLICT, "Ya existe otro tema con ese nombre")
        theme.name = body.name
    if body.description is not None:
        theme.description = body.description

    if body.subject_id is not None and body.subject_id != theme.subject_id:
        logger.info("Intentando cambiar asignatura del tema", theme_id=theme_id, old_subject_id=theme.subject_id, new_subject_id=body.subject_id)
        new_subject = db.query(Subject).get(body.subject_id)
        if not new_subject:
            logger.warn("Asignatura destino no encontrada al actualizar tema", theme_id=theme_id, target_subject_id=body.subject_id)
            raise HTTPException(status.HTTP_404_NOT_FOUND, f"Asignatura destino con ID {body.subject_id} no encontrada")
        theme.subject_id = new_subject.id
        theme.subject = new_subject
        logger.info("Asignatura del tema cambiada", theme_id=theme_id, new_subject_id=new_subject.id)


    db.commit()
    db.refresh(theme)
    logger.info("Tema actualizado exitosamente", theme_id=theme.id, name=theme.name, subject_id=theme.subject_id)
    return {
        "id": theme.id,
        "name": theme.name,
        "description": theme.description,
        "subject_id": theme.subject_id,
    }


@router.delete("/{theme_id}", status_code=status.HTTP_204_NO_CONTENT, dependencies=[Depends(admin_required)])
def delete_theme(theme_id: int, db: Session = Depends(get_db)):
    logger.info("Intentando eliminar tema", theme_id=theme_id)
    theme = db.query(Theme).get(theme_id)
    if not theme:
        logger.warn("Tema no encontrado al intentar eliminar", theme_id=theme_id)
        raise HTTPException(status.HTTP_404_NOT_FOUND, "Tema no encontrado")
    db.delete(theme)
    db.commit()
    logger.info("Tema eliminado exitosamente", theme_id=theme_id)
