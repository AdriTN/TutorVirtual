from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session, joinedload

from ...database.session import get_db
from ...api.dependencies.auth import jwt_required, admin_required
from ...models import Subject, User

router = APIRouter()


@router.post("", status_code=status.HTTP_201_CREATED, dependencies=[Depends(admin_required)])
def create_subject(body: dict, db: Session = Depends(get_db)):
    if db.query(Subject).filter(Subject.name == body["name"]).first():
        raise HTTPException(status.HTTP_409_CONFLICT, "Duplicado")

    subj = Subject(name=body["name"], description=body.get("description"))
    db.add(subj)
    db.commit()
    db.refresh(subj)
    return {"id": subj.id, "name": subj.name, "description": subj.description}


@router.get("")
def list_subjects(db: Session = Depends(get_db)):
    return [
        {"id": s.id, "name": s.name, "description": s.description}
        for s in db.query(Subject).all()
    ]


@router.post("/{subject_id}/enroll", status_code=status.HTTP_204_NO_CONTENT)
def enroll(
    subject_id: int, payload: dict = Depends(jwt_required), db: Session = Depends(get_db)
):
    user: User = (
        db.query(User)
        .options(joinedload(User.subjects), joinedload(User.courses))
        .get(payload["user_id"])
    )
    subject: Subject | None = (
        db.query(Subject).options(joinedload(Subject.courses)).get(subject_id)
    )
    if not subject:
        raise HTTPException(status.HTTP_404_NOT_FOUND)

    if subject not in user.subjects:
        user.subjects.append(subject)
        for course in subject.courses:
            if course not in user.courses:
                user.courses.append(course)
        db.commit()


@router.delete("/{subject_id}/unenroll", status_code=status.HTTP_204_NO_CONTENT)
def unenroll(
    subject_id: int, payload: dict = Depends(jwt_required), db: Session = Depends(get_db)
):
    user: User = (
        db.query(User)
        .options(joinedload(User.subjects), joinedload(User.courses))
        .get(payload["user_id"])
    )
    subject: Subject | None = (
        db.query(Subject).options(joinedload(Subject.courses)).get(subject_id)
    )
    if not subject:
        raise HTTPException(status.HTTP_404_NOT_FOUND)

    if subject in user.subjects:
        user.subjects.remove(subject)
        # quitar cursos huérfanos
        for course in subject.courses:
            if all(sub not in user.subjects for sub in course.subjects):
                if course in user.courses:
                    user.courses.remove(course)
        db.commit()
