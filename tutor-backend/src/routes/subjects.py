from fastapi import APIRouter, Depends, HTTPException, status
from models.course import Course
from models.user import User
from sqlalchemy.orm import Session, joinedload
from ..dependencies.database_dependencies import get_db
from ..dependencies.auth_dependencies import admin_required, jwt_required
from models.subject import Subject

router = APIRouter()

@router.post("/subject/nueva", status_code=status.HTTP_201_CREATED,
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

@router.post("/subject/course/{course_id}/subjects", status_code=status.HTTP_201_CREATED,
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

@router.get("/subject/subjects", status_code=status.HTTP_200_OK)
def list_subjects(db: Session = Depends(get_db)):
    return [
        {
            "id": s.id,
            "name": s.name,
            "description": s.description,
        }
        for s in db.query(Subject).all()
    ]

@router.post("/subject/{subject_id}/enroll", status_code=status.HTTP_204_NO_CONTENT, dependencies=[Depends(jwt_required)],)
def enroll_subject(
    subject_id: int,
    payload: dict = Depends(jwt_required),
    db: Session = Depends(get_db),
):
    # 1) obtenemos usuario + asignaturas + cursos ya matriculados
    user: User = (
        db.query(User)
        .options(joinedload(User.subjects))
        .get(payload["user_id"])
    )
    subject: Subject = (
        db.query(Subject)
        .options(joinedload(Subject.courses).joinedload(Course.subjects))
        .get(subject_id)
    )
    if not subject:
        raise HTTPException(404, "Subject no encontrado")
    
    # 2) Si no la tiene, la añadimos
    if subject not in user.subjects:
        user.subjects.append(subject)
        
        # 3) Por cada curso asociado a la asignatura
        for course in subject.courses:
            # ya está en el curso → saltamos
            if course in user.courses:
                continue
            # ¿tiene todas las asignaturas?
            if all(sub in user.subjects for sub in course.subjects):
                user.courses.append(course)
        
        db.commit()
