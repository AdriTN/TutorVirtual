from fastapi import APIRouter, Depends, HTTPException, status
from models.user import User
from sqlalchemy.orm import Session, joinedload
from ..dependencies.database_dependencies import get_db
from ..dependencies.auth_dependencies import admin_required, jwt_required
from ..models.course import Course
from ..models.subject import Subject

router = APIRouter(prefix="/courses", tags=["courses"])

def _course_to_dict(course: Course):
    return {
        "id": course.id,
        "title": course.title,
        "description": course.description,
        "subjects": [
            {"id": s.id, "name": s.name, "code": s.code} for s in course.subjects
        ],
    }

@router.post("", status_code=status.HTTP_201_CREATED,
             dependencies=[Depends(admin_required)])
def create_course(data: dict, db: Session = Depends(get_db)):
    if db.query(Course).filter(Course.title == data["title"]).first():
        raise HTTPException(409, detail="El curso ya existe")

    course = Course(title=data["title"], description=data.get("description"))
    if data.get("subject_ids"):
        subjects = db.query(Subject).filter(Subject.id.in_(data["subject_ids"])).all()
        course.subjects.extend(subjects)

    db.add(course)
    db.commit()
    db.refresh(course)
    return _course_to_dict(course)

@router.get("")
def list_courses(db: Session = Depends(get_db)):
    courses = db.query(Course).options(joinedload(Course.subjects)).all()
    return [_course_to_dict(c) for c in courses]

@router.get("/{course_id}")
def get_course(course_id: int, db: Session = Depends(get_db)):
    course = db.query(Course).options(joinedload(Course.subjects)).get(course_id)
    if not course:
        raise HTTPException(404, "Curso no encontrado")
    return _course_to_dict(course)

@router.post("/{course_id}/enroll", status_code=204,
             dependencies=[Depends(jwt_required)])
def enroll(course_id: int,
           payload: dict = Depends(jwt_required),
           db: Session = Depends(get_db)):
    user: User = db.query(User).get(payload["user_id"])
    course: Course = db.query(Course).get(course_id)
    if not course:
        raise HTTPException(404, "Curso no encontrado")

    if course not in user.courses:
        user.courses.append(course)
        db.commit()

@router.delete("/{course_id}/enroll", status_code=204,
               dependencies=[Depends(jwt_required)])
def unenroll(course_id: int,
             payload: dict = Depends(jwt_required),
             db: Session = Depends(get_db)):
    user: User = db.query(User).get(payload["user_id"])
    course: Course = db.query(Course).get(course_id)
    if not course:
        raise HTTPException(404, "Curso no encontrado")

    if course in user.courses:
        user.courses.remove(course)
        db.commit()

@router.get("/my", dependencies=[Depends(jwt_required)])
def my_courses(payload: dict = Depends(jwt_required),
               db: Session = Depends(get_db)):
    user: User = db.query(User).options(joinedload(User.courses)).get(payload["user_id"])
    return [_course_to_dict(c) for c in user.courses]
