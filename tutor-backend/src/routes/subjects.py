from fastapi import APIRouter, Depends, HTTPException, status
from models.course import Course
from sqlalchemy.orm import Session
from ..dependencies.database_dependencies import get_db
from ..dependencies.auth_dependencies import admin_required
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
