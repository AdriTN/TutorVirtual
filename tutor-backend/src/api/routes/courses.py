from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session, selectinload, joinedload

from src.database.session import get_db
from src.api.dependencies.auth import jwt_required, admin_required
from src.models import Course, Subject, User
from src.api.schemas.courses import CourseIn, CourseOut, SubjectOut, ThemeOut

router = APIRouter()


# ---------- Helpers ----------
def _subject_to_schema(subject: Subject, enrolled_ids: set[int]) -> SubjectOut:
    return SubjectOut(
        id=subject.id,
        name=subject.name,
        description=subject.description,
        enrolled=subject.id in enrolled_ids,
        themes=[ThemeOut(id=t.id, title=t.name) for t in subject.themes],
    )


def _course_to_schema(course: Course, user: User | None) -> CourseOut:
    enrolled = {s.id for s in user.subjects} if user else set()
    return CourseOut(
        id=course.id,
        title=course.title,
        description=course.description,
        subjects=[_subject_to_schema(s, enrolled) for s in course.subjects],
    )


# ---------- Endpoints ----------
@router.post(
    "",
    status_code=status.HTTP_201_CREATED,
    response_model=CourseOut,
    dependencies=[Depends(admin_required)],
)
def create_course(body: CourseIn, db: Session = Depends(get_db)):
    if db.query(Course).filter(Course.title == body.title).first():
        raise HTTPException(status.HTTP_409_CONFLICT, "Curso duplicado")

    course = Course(title=body.title, description=body.description)

    if body.subject_ids:
        course.subjects.extend(
            db.query(Subject).filter(Subject.id.in_(body.subject_ids)).all()
        )

    db.add(course)
    db.commit()
    db.refresh(course)
    return _course_to_schema(course, None)


@router.get("/my", response_model=list[CourseOut])
def my_courses(payload: dict = Depends(jwt_required), db: Session = Depends(get_db)):
    user: User = (
        db.query(User)
        .options(
            selectinload(User.courses)
            .selectinload(Course.subjects)
            .selectinload(Subject.themes),
            selectinload(User.subjects),
        )
        .get(payload["user_id"])
    )
    return [_course_to_schema(c, user) for c in user.courses]


@router.get("/courses", response_model=list[CourseOut])
def list_courses(payload: dict = Depends(jwt_required), db: Session = Depends(get_db)):
    user: User = (
        db.query(User).options(selectinload(User.subjects)).get(payload["user_id"])
    )

    courses = (
        db.query(Course)
        .options(
            selectinload(Course.subjects).selectinload(Subject.themes)
        )
        .all()
    )
    return [_course_to_schema(c, user) for c in courses]

@router.delete(
    "/{course_id}/unenroll",
    status_code=status.HTTP_204_NO_CONTENT,
    dependencies=[Depends(jwt_required)],
)
def unenroll_course(
    course_id: int,
    payload: dict = Depends(jwt_required),
    db: Session = Depends(get_db),
):
    user: User   = db.query(User).options(joinedload(User.subjects)).get(payload["user_id"])
    course: Course = db.query(Course).options(joinedload(Course.subjects)).get(course_id)
    if not course:
        raise HTTPException(404, "Curso no encontrado")

    # 1) Quitar todas las asignaturas del curso
    for subj in course.subjects:
        if subj in user.subjects:
            user.subjects.remove(subj)

    # 2) Quitar el curso
    if course in user.courses:
        user.courses.remove(course)

    db.commit()

@router.get("/{course_id}", response_model=CourseOut)
def get_course(
    course_id: int, payload: dict = Depends(jwt_required), db: Session = Depends(get_db)
):
    user: User = (
        db.query(User).options(selectinload(User.subjects)).get(payload["user_id"])
    )

    course: Course | None = (
        db.query(Course)
        .options(selectinload(Course.subjects).selectinload(Subject.themes))
        .get(course_id)
    )
    if not course:
        raise HTTPException(status.HTTP_404_NOT_FOUND)

    return _course_to_schema(course, user)
