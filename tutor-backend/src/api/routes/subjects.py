"""
Rutas de asignaturas
------------------------------------
Todas las URL empiezan ahora por un prefijo claro:

  • /subjects/…         → acciones sobre asignaturas
  • /courses/…          → acciones sobre cursos + asignaturas
"""

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session, joinedload

from src.database.session import get_db
from sqlalchemy import select, and_

from sqlalchemy import delete

from src.api.dependencies.auth import jwt_required, admin_required
from src.api.schemas.subjects import SubjectUpdate, ThemeDetach, SubjectEnrollData, SubjectUnenrollData
from src.models.user import User
from src.models.subject import Subject
from src.models.course import Course
from src.models.theme import Theme
from src.models.associations import user_enrollments

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
    enroll_data: SubjectEnrollData,
    payload: dict = Depends(jwt_required),
    db: Session = Depends(get_db),
):
    user_id = payload["user_id"]
    user: User = (
        db.query(User)
        .options(joinedload(User.courses)) 
        .get(user_id)
    )
    if not user:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Usuario no encontrado")

    subject: Subject = db.query(Subject).get(subject_id)
    if not subject:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Asignatura no encontrada")

    course: Course = (
        db.query(Course)
        .options(joinedload(Course.subjects))
        .get(enroll_data.course_id)
    )
    if not course:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Curso no encontrado")

    if subject not in course.subjects:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="La asignatura no pertenece al curso especificado"
        )

    existing_enrollment = db.execute(
        select(user_enrollments).where(
            and_(
                user_enrollments.c.user_id == user_id,
                user_enrollments.c.subject_id == subject_id,
                user_enrollments.c.course_id == enroll_data.course_id,
            )
        )
    ).first()

    if existing_enrollment:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="Ya estás matriculado en esta asignatura para este curso."
        )

    try:
        db.execute(
            user_enrollments.insert().values(
                user_id=user_id,
                subject_id=subject_id,
                course_id=enroll_data.course_id,
            )
        )
    except Exception as e:
        db.rollback()
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error al crear la matrícula: {e}"
        )

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
    unenroll_data: SubjectUnenrollData,
    payload: dict = Depends(jwt_required),
    db: Session = Depends(get_db),
):
    user_id = payload["user_id"]
    course_id = unenroll_data.course_id

    user: User = (
        db.query(User)
        .options(joinedload(User.courses))
        .get(user_id)
    )
    if not user:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Usuario no encontrado")

    subject: Subject = db.query(Subject).get(subject_id)
    if not subject:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Asignatura no encontrada")
    
    course: Course = db.query(Course).get(course_id)
    if not course:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Curso no encontrado")

    delete_stmt = (
        delete(user_enrollments)
        .where(
            and_(
                user_enrollments.c.user_id == user_id,
                user_enrollments.c.subject_id == subject_id,
                user_enrollments.c.course_id == course_id,
            )
        )
    )
    result = db.execute(delete_stmt)

    if result.rowcount == 0:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Matrícula no encontrada para esta asignatura y curso."
        )
        
    remaining_enrollments_in_course = db.execute(
        select(user_enrollments.c.subject_id).where(
            and_(
                user_enrollments.c.user_id == user_id,
                user_enrollments.c.course_id == course_id,
            )
        )
    ).first()

    if not remaining_enrollments_in_course and course in user.courses:
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
    dependencies=[Depends(admin_required)],
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
