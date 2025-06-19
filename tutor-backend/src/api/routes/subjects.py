from src.models.course import Course
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session, joinedload

from src.database.session import get_db
from src.api.dependencies.auth import jwt_required, admin_required
from src.models.user import User
from src.models.subject import Subject

router = APIRouter()


@router.post("/nueva", status_code=status.HTTP_201_CREATED,
             dependencies=[Depends(admin_required)])
def create_subject(
    data: dict,
    db: Session = Depends(get_db)
):
    name = data.get("name")
    description = data.get("description")
    if not name or not description:
        raise HTTPException(422, detail="El nombre y el código son obligatorios")
    
    if db.query(Subject).filter(
        (Subject.name == data["name"]) | (Subject.description == data["description"])
    ).first():
        raise HTTPException(409, detail="El subject ya existe")

    subj = Subject(
        name=data["name"],
        description=data["description"]
    )
    db.add(subj)
    db.commit()
    db.refresh(subj)
    return {
        "id": subj.id,
        "name": subj.name,
        "description": subj.description,
    }

@router.post("/{course_id}/subjects", status_code=status.HTTP_201_CREATED,
             dependencies=[Depends(admin_required)])
def add_subject_to_course(
    course_id: int,
    data: dict,
    db: Session = Depends(get_db)
):
    subject_id = data.get("subject_id")
    if not subject_id:
        raise HTTPException(422, detail="El id del subject es obligatorio")

    subject = db.query(Subject).get(subject_id)
    if not subject:
        raise HTTPException(404, detail="Subject no encontrado")

    course = db.query(Course).get(course_id)
    if not course:
        raise HTTPException(404, detail="Curso no encontrado")

    if subject in course.subjects:
        raise HTTPException(409, detail="El subject ya está asociado al curso")

    course.subjects.append(subject)
    db.commit()
    return {
        "id": subject.id,
        "name": subject.name,
        "description": subject.description,
    }

@router.get("/subjects", status_code=status.HTTP_200_OK)
def list_subjects(db: Session = Depends(get_db)):
    return [
        {
            "id": s.id,
            "name": s.name,
            "description": s.description,
        }
        for s in db.query(Subject).all()
    ]

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
    # 1) obtenemos usuario + asignaturas + cursos ya matriculados
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
        raise HTTPException(404, "Subject no encontrado")

    # 2) Si no tenía la asignatura, la añadimos
    if subject not in user.subjects:
        user.subjects.append(subject)

        # 3) Por cada curso al que pertenece la asignatura,
        #    añadimos el curso si aún no está matriculado
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
        raise HTTPException(404, "Subject no encontrado")

    # 1) quitar la asignatura, si la tenía
    if subject in user.subjects:
        user.subjects.remove(subject)

    # 2) Para cada curso asociado, si el usuario ya no tiene NINGUNA asignatura
    #    de ese curso, lo sacamos también del curso.
    for course in subject.courses:
        still_has = any(subj for subj in course.subjects if subj in user.subjects)
        if not still_has and course in user.courses:
            user.courses.remove(course)

    db.commit()

@router.get(
    "/{subject_id}/themes",
    status_code=status.HTTP_200_OK,
    dependencies=[Depends(jwt_required)]
)
def list_themes(subject_id: int, db: Session = Depends(get_db)):
    """
    Devuelve la lista de temas para una asignatura,
    o 404 si la asignatura no existe.
    """
    subj = (
        db.query(Subject)
        .options(joinedload(Subject.themes))
        .get(subject_id)
    )
    if not subj:
        raise HTTPException(status_code=404, detail="Asignatura no encontrada")

    return [
        {"id": t.id, "title": t.name, "description": t.description}
        for t in subj.themes
    ]

@router.delete(
    "/{course_id}/subjects/{subject_id}",
    status_code=status.HTTP_204_NO_CONTENT,
    dependencies=[Depends(admin_required)],
)
def remove_subject_from_course(
    course_id: int,
    subject_id: int,
    db: Session = Depends(get_db),
):
    course: Course | None = db.query(Course)\
        .options(joinedload(Course.subjects))\
        .get(course_id)
    if not course:
        raise HTTPException(404, "Curso no encontrado")

    subject: Subject | None = db.query(Subject).get(subject_id)
    if not subject:
        raise HTTPException(404, "Asignatura no encontrada")

    if subject not in course.subjects:
        raise HTTPException(409, "La asignatura no está asociada al curso")

    course.subjects.remove(subject)
    db.commit()
