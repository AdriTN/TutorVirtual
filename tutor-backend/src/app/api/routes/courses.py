from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import joinedload, Session

from ...database.session import get_db
from ...api.dependencies.auth import jwt_required, admin_required
from ...models import Course, Subject, User

router = APIRouter(prefix="/courses", tags=["Courses"])


# ───────────── Helpers ─────────────
def _subject_dto(subject: Subject, enrolled: bool) -> dict:
    return {
        "id": subject.id,
        "name": subject.name,
        "description": subject.description,
        "enrolled": enrolled,
        "themes": [{"id": t.id, "title": t.nombre} for t in subject.themes],
    }


def _course_dto(course: Course, user: User | None) -> dict:
    enrolled_ids: set[int] = set()
    if user:
        enrolled_ids = {s.id for s in user.subjects}
    return {
        "id": course.id,
        "title": course.title,
        "description": course.description,
        "subjects": [
            _subject_dto(s, s.id in enrolled_ids) for s in course.subjects
        ],
    }


# ───────────── Endpoints ─────────────
@router.post(
    "",
    status_code=status.HTTP_201_CREATED,
    dependencies=[Depends(admin_required)],
)
def create_course(body: dict, db: Session = Depends(get_db)):
    if db.query(Course).filter(Course.title == body["title"]).first():
        raise HTTPException(status.HTTP_409_CONFLICT, "Curso duplicado")

    course = Course(title=body["title"], description=body.get("description"))
    if subject_ids := body.get("subject_ids"):
        course.subjects.extend(db.query(Subject).filter(Subject.id.in_(subject_ids)).all())
    db.add(course)
    db.commit()
    db.refresh(course)
    return _course_dto(course, None)


@router.get("/my")
def my_courses(payload: dict = Depends(jwt_required), db: Session = Depends(get_db)):
    user: User = (
        db.query(User)
        .options(
            joinedload(User.courses)
            .joinedload(Course.subjects)
            .joinedload(Subject.themes),
            joinedload(User.subjects),
        )
        .get(payload["user_id"])
    )
    return [_course_dto(c, user) for c in user.courses]


@router.get("")
def list_courses(payload: dict = Depends(jwt_required), db: Session = Depends(get_db)):
    user: User = (
        db.query(User).options(joinedload(User.subjects)).get(payload["user_id"])
    )
    courses = (
        db.query(Course)
        .options(joinedload(Course.subjects).joinedload(Subject.themes))
        .all()
    )
    return [_course_dto(c, user) for c in courses]


@router.get("/{course_id}")
def get_course(
    course_id: int, payload: dict = Depends(jwt_required), db: Session = Depends(get_db)
):
    user: User = (
        db.query(User).options(joinedload(User.subjects)).get(payload["user_id"])
    )
    course: Course | None = (
        db.query(Course)
        .options(joinedload(Course.subjects).joinedload(Subject.themes))
        .get(course_id)
    )
    if not course:
        raise HTTPException(status.HTTP_404_NOT_FOUND)
    return _course_dto(course, user)
