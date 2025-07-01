from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session, selectinload, joinedload

from src.database.session import get_db
from src.api.dependencies.auth import jwt_required, admin_required
from src.models import Course, Subject, User
from src.api.schemas.courses import CourseIn, CourseOut, CourseUpdate, SubjectDetach, SubjectOut, ThemeOut
from src.models.associations import user_enrollments
from sqlalchemy import delete


router = APIRouter()

# ---------- Helpers ----------
def _subject_to_schema(subject: Subject, enrolled_subject_ids_for_user: set[int]) -> SubjectOut:
    return SubjectOut(
        id=subject.id,
        name=subject.name,
        description=subject.description,
        enrolled=subject.id in enrolled_subject_ids_for_user,
        themes=[ThemeOut(id=t.id, title=t.name) for t in subject.themes],
    )


def _course_to_schema(course: Course, user: User | None) -> CourseOut:
    user_specific_enrollments: set[tuple[int, int]] | None = getattr(user, '_loaded_enrollments', None)

    enrolled_subject_ids_for_this_course = set()
    if user and user_specific_enrollments:
        enrolled_subject_ids_for_this_course = {
            s_id for s_id, c_id in user_specific_enrollments if c_id == course.id
        }
    
    return CourseOut(
        id=course.id,
        title=course.title,
        description=course.description,
        subjects=[_subject_to_schema(s, enrolled_subject_ids_for_this_course) for s in course.subjects],
    )


# ---------- Endpoints ----------
def _load_user_with_enrollments(user_id: int, db: Session) -> User | None:
    """Carga el usuario y adjunta sus tuplas de matrícula (subject_id, course_id)."""
    user = db.query(User).get(user_id)
    if user:
        enrollments_query = db.query(
            user_enrollments.c.subject_id,
            user_enrollments.c.course_id
        ).filter(user_enrollments.c.user_id == user_id).all()
        user._loaded_enrollments = set(enrollments_query)
    return user


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
    user_id = payload["user_id"]
    user_with_enrollments = _load_user_with_enrollments(user_id, db)
    if not user_with_enrollments:
         raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Usuario no encontrado")
    
    user_for_courses_relation = db.query(User).options(
        selectinload(User.courses)
        .selectinload(Course.subjects)
        .selectinload(Subject.themes)
    ).get(user_id)

    if not user_for_courses_relation:
         raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Usuario no encontrado al cargar cursos.")

    return [_course_to_schema(c, user_with_enrollments) for c in user_for_courses_relation.courses]


@router.get("/all", response_model=list[CourseOut])
def list_all_courses(payload: dict = Depends(jwt_required), db: Session = Depends(get_db)):
    user_id = payload["user_id"]
    user_with_enrollments = _load_user_with_enrollments(user_id, db)

    courses = (
        db.query(Course)
        .options(
            selectinload(Course.subjects).selectinload(Subject.themes)
        )
        .all()
    )
    return [_course_to_schema(c, user_with_enrollments) for c in courses]

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
    user_id = payload["user_id"]
    user: User = db.query(User).options(joinedload(User.courses)).get(user_id)
    if not user:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Usuario no encontrado")

    course: Course = db.query(Course).get(course_id)
    if not course:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Curso no encontrado")

    db.execute(
        delete(user_enrollments).where(
            user_enrollments.c.user_id == user_id,
            user_enrollments.c.course_id == course_id,
        )
    )

    if course in user.courses:
        user.courses.remove(course)

    db.commit()

@router.get("/{course_id}", response_model=CourseOut)
def get_course(
    course_id: int, payload: dict = Depends(jwt_required), db: Session = Depends(get_db)
):
    user_id = payload["user_id"]
    user_with_enrollments = _load_user_with_enrollments(user_id, db)


    course: Course | None = (
        db.query(Course)
        .options(selectinload(Course.subjects).selectinload(Subject.themes))
        .get(course_id)
    )
    if not course:
        raise HTTPException(status.HTTP_404_NOT_FOUND)

    return _course_to_schema(course, user_with_enrollments)

@router.put("/{course_id}", response_model=dict)
def update_course(course_id: int, body: CourseUpdate, db: Session = Depends(get_db)):
    course: Course | None = (
        db.query(Course).options(joinedload(Course.subjects)).get(course_id)
    )
    if not course:
        raise HTTPException(404, "Curso no encontrado")

    # ── título/descr ─────────────────────────────────────────
    if body.title:
        dup = db.query(Course).filter(Course.title == body.title, Course.id != course_id).first()
        if dup:
            raise HTTPException(409, "Ya existe otro curso con ese título")
        course.title = body.title
    if body.description is not None:
        course.description = body.description

    # ── reemplazar asignaturas ───────────────────────────────
    if body.subject_ids is not None:
        subjects = db.query(Subject).filter(Subject.id.in_(body.subject_ids)).all()
        course.subjects = subjects

    db.commit()
    db.refresh(course)
    return {
        "id": course.id,
        "title": course.title,
        "description": course.description,
        "subject_ids": [s.id for s in course.subjects],
    }

@router.delete("/{course_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_course(course_id: int, db: Session = Depends(get_db)):
    course = db.query(Course).get(course_id)
    if not course:
        raise HTTPException(404, "Curso no encontrado")
    db.delete(course)
    db.commit()

@router.delete("/{course_id}/subjects", status_code=status.HTTP_204_NO_CONTENT)
def detach_subjects(
    course_id: int, body: SubjectDetach, db: Session = Depends(get_db)
):
    course: Course | None = (
        db.query(Course).options(joinedload(Course.subjects)).get(course_id)
    )
    if not course:
        raise HTTPException(404, "Curso no encontrado")

    for sid in body.subject_ids:
        subj = db.query(Subject).get(sid)
        if subj and subj in course.subjects:
            course.subjects.remove(subj)

    db.commit()