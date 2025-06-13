# routes/theme_routes.py
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from models.subject import Subject
from models.thems import Tema
from ..dependencies.database_dependencies import get_db
from ..dependencies.auth_dependencies import admin_required, jwt_required

router = APIRouter(prefix="/theme")

# ─────────────────────────────────────────────────────────────
# 1. Crear un tema (ADMIN)
# POST /theme/new
# ─────────────────────────────────────────────────────────────
@router.post(
    "/new",
    status_code=status.HTTP_201_CREATED,
    dependencies=[Depends(admin_required)],
)
def create_theme(data: dict, db: Session = Depends(get_db)):
    nombre = data.get("nombre")
    descripcion = data.get("descripcion")
    subject_id = data.get("subject_id")

    if not (nombre and descripcion and subject_id):
        raise HTTPException(422, "nombre, descripcion y subject_id son obligatorios")

    # verificar duplicados
    if db.query(Tema).filter(Tema.nombre == nombre).first():
        raise HTTPException(409, "El tema ya existe")

    subject = db.query(Subject).get(subject_id)
    if not subject:
        raise HTTPException(404, "Asignatura no encontrada")

    tema = Tema(nombre=nombre, descripcion=descripcion, subject_id=subject_id)
    db.add(tema)
    db.commit()
    db.refresh(tema)

    return {"id": tema.id, "nombre": tema.nombre, "descripcion": tema.descripcion}


# ─────────────────────────────────────────────────────────────
# 2. Añadir un tema existente a una asignatura (ADMIN)
# POST /theme/subject/{subject_id}/add
# body: { "theme_id": 3 }
# ─────────────────────────────────────────────────────────────
@router.post(
    "/subject/{subject_id}/add",
    status_code=status.HTTP_201_CREATED,
    dependencies=[Depends(admin_required)],
)
def add_theme_to_subject(subject_id: int, data: dict, db: Session = Depends(get_db)):
    theme_id = data.get("theme_id")
    if not theme_id:
        raise HTTPException(422, "theme_id es obligatorio")

    tema = db.query(Tema).get(theme_id)
    if not tema:
        raise HTTPException(404, "Tema no encontrado")

    subject = db.query(Subject).get(subject_id)
    if not subject:
        raise HTTPException(404, "Asignatura no encontrada")

    if tema in subject.themes:
        raise HTTPException(409, "El tema ya está asociado a la asignatura")

    # Si el tema ya pertenece a otra asignatura, decide si permitirlo o no
    if tema.subject and tema.subject is not subject:
        raise HTTPException(409, "El tema pertenece a otra asignatura")

    tema.subject = subject
    db.commit()
    return {"id": tema.id, "nombre": tema.nombre, "descripcion": tema.descripcion}


# ─────────────────────────────────────────────────────────────
# 4. Listar todos los temas (opcional / público)
# GET /theme/all
# ─────────────────────────────────────────────────────────────
@router.get("/all", status_code=status.HTTP_200_OK)
def list_all_themes(db: Session = Depends(get_db)):
    return [
        {
            "id": t.id,
            "nombre": t.nombre,
            "descripcion": t.descripcion,
            "subject_id": t.subject_id,
        }
        for t in db.query(Tema).all()
    ]
