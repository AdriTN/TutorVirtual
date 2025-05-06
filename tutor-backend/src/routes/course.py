# src/routes/course.py
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy import select
from sqlalchemy.orm import Session, joinedload

from models.course import Course, user_subjects          # tabla de unión curso–subject
from models.subject import Subject
from models.user import User
from ..dependencies.database_dependencies import get_db
from ..dependencies.auth_dependencies import jwt_required, admin_required

router = APIRouter()

# ------------------------------------------------------------------ #
# ---------------------------- HELPERS ----------------------------- #
# ------------------------------------------------------------------ #

def _subject_row_to_dict(subject: Subject, enrolled: bool) -> dict:
    """Convierte un Subject + flag a diccionario JSON."""
    return {
        "id": subject.id,
        "name": subject.name,
        "description": subject.description,
        "enrolled": enrolled,
    }

def _subjects_rows_for(course: Course, user: User | None, db: Session):
    """
    Crea lista [(Subject, bool enrolled)] para un curso y, opcionalmente, un usuario.
    * Si user es None → todos enrolled=False (modo público/visitante).
    * Si user está presente → marca True sólo los subject.id que aparezcan
      en la tabla user_subjects para ese usuario.
    """
    if user is None:
        return [(s, False) for s in course.subjects]

    enrolled_ids = {
        row.subject_id
        for row in db.execute(
            select(user_subjects.c.subject_id).where(
                user_subjects.c.user_id == user.id
            )
        )
    }
    return [(s, s.id in enrolled_ids) for s in course.subjects]

def _course_to_dict(course: Course, subjects_rows) -> dict:
    """Devuelve la representación final de un curso con su lista de asignaturas."""
    return {
        "id": course.id,
        "title": course.title,
        "description": course.description,
        "subjects": [_subject_row_to_dict(s, en) for s, en in subjects_rows],
    }

# ------------------------------------------------------------------ #
# ---------------------------- ENDPOINTS --------------------------- #
# ------------------------------------------------------------------ #

@router.post(
    "/course/create",
    status_code=status.HTTP_201_CREATED,
    dependencies=[Depends(admin_required)],
)
def create_course(data: dict, db: Session = Depends(get_db)):
    if db.query(Course).filter(Course.title == data["title"]).first():
        raise HTTPException(409, detail="El curso ya existe")

    course = Course(title=data["title"], description=data.get("description"))

    if data.get("subject_ids"):
        subjects = db.query(Subject).filter(
            Subject.id.in_(data["subject_ids"])
        ).all()
        course.subjects.extend(subjects)

    db.add(course)
    db.commit()
    db.refresh(course)

    # modo admin: enrolled=False para todos
    rows = _subjects_rows_for(course, None, db)
    return _course_to_dict(course, rows)

@router.get("/course/my")
def my_courses(
    payload: dict = Depends(jwt_required),
    db: Session = Depends(get_db),
):
    user: User = (
        db.query(User)
        .options(
            joinedload(User.courses).joinedload(Course.subjects),
            joinedload(User.subjects),
        )
        .get(payload["user_id"])
    )
    return [
        _course_to_dict(c, _subjects_rows_for(c, user, db))
        for c in user.courses
    ]

@router.get("/course/courses")
def list_courses(
    payload: dict = Depends(jwt_required),
    db: Session = Depends(get_db),
):
    user: User = (
        db.query(User)
        .options(joinedload(User.subjects))
        .get(payload["user_id"])
    )
    courses = db.query(Course).options(joinedload(Course.subjects)).all()
    return [
        _course_to_dict(c, _subjects_rows_for(c, user, db))
        for c in courses
    ]

@router.get("/course/{course_id}")
def get_course(
    course_id: int,
    payload: dict = Depends(jwt_required),
    db: Session = Depends(get_db),
):
    user: User = (
        db.query(User)
        .options(joinedload(User.subjects))
        .get(payload["user_id"])
    )
    course: Course = (
        db.query(Course)
        .options(joinedload(Course.subjects))
        .get(course_id)
    )
    if not course:
        raise HTTPException(404, "Curso no encontrado")

    rows = _subjects_rows_for(course, user, db)
    return _course_to_dict(course, rows)

@router.delete(
    "/course/{course_id}/unenroll",
    status_code=status.HTTP_204_NO_CONTENT,
)
def unenroll(
    course_id: int,
    payload: dict = Depends(jwt_required),
    db: Session = Depends(get_db),
):
    user: User = db.query(User).get(payload["user_id"])
    course: Course = db.query(Course).get(course_id)
    if not course:
        raise HTTPException(404, "Curso no encontrado")

    if course in user.courses:
        user.courses.remove(course)
        db.commit()
