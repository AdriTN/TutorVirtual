"""
Rutas de asignaturas (sin colisiones)
------------------------------------
Todas las URL empiezan ahora por un prefijo claro:

  • /subjects/…         → acciones sobre asignaturas
  • /courses/…          → acciones sobre cursos + asignaturas
"""

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session, joinedload

from src.database.session import get_db
from src.api.dependencies.auth import jwt_required, admin_required
from src.api.schemas.subjects import SubjectUpdate, ThemeDetach
from src.models.user import User
from src.models.subject import Subject
from src.models.course import Course
from src.models.theme import Theme

router = APIRouter()


# ---------------------------------------------------------------------------
# 1. CRUD de asignaturas
# ---------------------------------------------------------------------------

@router.post(
    "/create",
    status_code=status.HTTP_201_CREATED,
    dependencies=[Depends(admin_required)],
)
def create_subject(data: dict, db: Session = Depends(get_db)):
    """Crear nueva asignatura."""
    name = data.get("name")
    description = data.get("description")
    if not name or not description:
        raise HTTPException(422, "El nombre y la descripción son obligatorios")

    if db.query(Subject).filter(
        (Subject.name == name) | (Subject.description == description)
    ).first():
        raise HTTPException(409, "La asignatura ya existe")

    subj = Subject(name=name, description=description)
    db.add(subj)
    db.commit()
    db.refresh(subj)
    return {"id": subj.id, "name": subj.name, "description": subj.description}


@router.get("/all", status_code=status.HTTP_200_OK)
def list_subjects(db: Session = Depends(get_db)):
    """Lista completa de asignaturas + sus temas."""
    return [
        {
            "id": s.id,
            "name": s.name,
            "description": s.description,
            "themes": [
                {"id": t.id, "title": t.name, "description": t.description}
                for t in s.themes
            ],
        }
        for s in db.query(Subject).all()
    ]


@router.put("/{subject_id}/update", response_model=dict)
def update_subject(
    subject_id: int, body: SubjectUpdate, db: Session = Depends(get_db)
):
    subj: Subject | None = db.query(Subject).get(subject_id)
    if not subj:
        raise HTTPException(404, "Asignatura no encontrada")

    if body.name:
        dup = (
            db.query(Subject)
            .filter(Subject.name == body.name, Subject.id != subject_id)
            .first()
        )
        if dup:
            raise HTTPException(409, "Ya existe otra asignatura con ese nombre")
        subj.name = body.name

    if body.description is not None:
        subj.description = body.description

    db.commit()
    db.refresh(subj)
    return {"id": subj.id, "name": subj.name, "description": subj.description}


@router.delete("/{subject_id}/delete", status_code=status.HTTP_204_NO_CONTENT)
def delete_subject(subject_id: int, db: Session = Depends(get_db)):
    """Elimina una asignatura (y cascada según modelo)."""
    subj = db.query(Subject).get(subject_id)
    if not subj:
        raise HTTPException(404, "Asignatura no encontrada")
    db.delete(subj)
    db.commit()


# ---------------------------------------------------------------------------
# 2. Matrícula de usuarios en asignaturas
# ---------------------------------------------------------------------------

@router.post(
    "/{subject_id}/enroll",
    status_code=status.HTTP_204_NO_CONTENT,
    dependencies=[Depends(jwt_required)],
)
def enroll_subject(
    subject_id: int,
    payload: dict = Depends(jwt_required),
    db: Session = Depends(get_db),
):
    user: User = (
        db.query(User)
        .options(joinedload(User.subjects), joinedload(User.courses))
        .get(payload["user_id"])
    )
    subject: Subject = (
        db.query(Subject)
        .options(joinedload(Subject.courses))
        .get(subject_id)
    )
    if not subject:
        raise HTTPException(404, "Asignatura no encontrada")

    if subject not in user.subjects:
        user.subjects.append(subject)
        for course in subject.courses:
            if course not in user.courses:
                user.courses.append(course)
        db.commit()


@router.delete(
    "/{subject_id}/unenroll",
    status_code=status.HTTP_204_NO_CONTENT,
    dependencies=[Depends(jwt_required)],
)
def unenroll_subject(
    subject_id: int,
    payload: dict = Depends(jwt_required),
    db: Session = Depends(get_db),
):
    user: User = (
        db.query(User)
        .options(joinedload(User.subjects), joinedload(User.courses))
        .get(payload["user_id"])
    )
    subject: Subject = (
        db.query(Subject)
        .options(joinedload(Subject.courses))
        .get(subject_id)
    )
    if not subject:
        raise HTTPException(404, "Asignatura no encontrada")

    if subject in user.subjects:
        user.subjects.remove(subject)

    for course in subject.courses:
        still_has = any(sub for sub in course.subjects if sub in user.subjects)
        if not still_has and course in user.courses:
            user.courses.remove(course)

    db.commit()


# ---------------------------------------------------------------------------
# 3. Temas de una asignatura
# ---------------------------------------------------------------------------

@router.get(
    "/{subject_id}/themes",
    status_code=status.HTTP_200_OK,
    dependencies=[Depends(jwt_required)],
)
def list_themes(subject_id: int, db: Session = Depends(get_db)):
    subj: Subject = (
        db.query(Subject).options(joinedload(Subject.themes)).get(subject_id)
    )
    if not subj:
        raise HTTPException(404, "Asignatura no encontrada")

    return [
        {"id": t.id, "title": t.name, "description": t.description}
        for t in subj.themes
    ]


@router.delete(
    "/{subject_id}/themes/detach",
    status_code=status.HTTP_204_NO_CONTENT,
    dependencies=[Depends(admin_required)],    # ← añade auth si procede
)
def detach_themes(
    subject_id: int,
    body: ThemeDetach,
    db: Session = Depends(get_db),
):
    subj: Subject = (
        db.query(Subject).options(joinedload(Subject.themes)).get(subject_id)
    )
    if not subj:
        raise HTTPException(404, "Asignatura no encontrada")

    for tid in body.theme_ids:
        theme = db.query(Theme).get(tid)
        if theme and theme.subject_id == subject_id:
            theme.subject_id = None

    db.commit()



# ---------------------------------------------------------------------------
# 4. Relación Curso ↔ Asignatura
# ---------------------------------------------------------------------------

@router.post(
    "/courses/{course_id}/subjects/add",
    status_code=status.HTTP_201_CREATED,
    dependencies=[Depends(admin_required)],
)
def add_subject_to_course(
    course_id: int,
    data: dict,
    db: Session = Depends(get_db),
):
    subject_id = data.get("subject_id")
    if not subject_id:
        raise HTTPException(422, "El id de la asignatura es obligatorio")

    subject = db.query(Subject).get(subject_id)
    if not subject:
        raise HTTPException(404, "Asignatura no encontrada")

    course = db.query(Course).get(course_id)
    if not course:
        raise HTTPException(404, "Curso no encontrado")

    if subject in course.subjects:
        raise HTTPException(409, "La asignatura ya está asociada al curso")

    course.subjects.append(subject)
    db.commit()
    return {"id": subject.id, "name": subject.name, "description": subject.description}


@router.delete(
    "/courses/{course_id}/subjects/{subject_id}/remove",
    status_code=status.HTTP_204_NO_CONTENT,
    dependencies=[Depends(admin_required)],
)
def remove_subject_from_course(
    course_id: int,
    subject_id: int,
    db: Session = Depends(get_db),
):
    course: Course = (
        db.query(Course).options(joinedload(Course.subjects)).get(course_id)
    )
    if not course:
        raise HTTPException(404, "Curso no encontrado")

    subject: Subject = db.query(Subject).get(subject_id)
    if not subject:
        raise HTTPException(404, "Asignatura no encontrada")

    if subject not in course.subjects:
        raise HTTPException(409, "La asignatura no está asociada al curso")

    course.subjects.remove(subject)
    db.commit()
