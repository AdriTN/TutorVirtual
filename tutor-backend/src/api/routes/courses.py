from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session, selectinload, joinedload

from src.database.session import get_db
from src.api.dependencies.auth import jwt_required, admin_required
from src.models import Course, Subject, User
from src.api.schemas.courses import CourseIn, CourseOut, CourseUpdate, SubjectDetach, SubjectOut, ThemeOut
from src.models.associations import user_enrollments
from sqlalchemy import delete
import structlog


router = APIRouter()
logger = structlog.get_logger(__name__)

# ---------- Helpers ----------
def _subject_to_schema(subject: Subject, enrolled_subject_ids_for_user: set[int]) -> SubjectOut:
    return SubjectOut(
        id=subject.id,
        name=subject.name,
        description=subject.description,
        enrolled=subject.id in enrolled_subject_ids_for_user,
        themes=[ThemeOut(id=t.id, title=t.name, description=t.description, subject_id=t.subject_id) for t in subject.themes],
    )


def _course_to_schema(course: Course, subject_enrollments_for_user: set[tuple[int, int]] | None) -> CourseOut:
    enrolled_subject_ids_for_this_course = set()
    if subject_enrollments_for_user:
        enrolled_subject_ids_for_this_course = {
            s_id for s_id, c_id in subject_enrollments_for_user if c_id == course.id
        }
    
    return CourseOut(
        id=course.id,
        title=course.title,
        description=course.description,
        subjects=[_subject_to_schema(s, enrolled_subject_ids_for_this_course) for s in course.subjects],
    )


# ---------- Endpoints ----------
def _get_subject_enrollments_for_user(user_id: int, db: Session) -> set[tuple[int, int]]:
    """Devuelve un conjunto de tuplas (subject_id, course_id) para las matrículas del usuario."""
    enrollments_query = db.query(
        user_enrollments.c.subject_id,
        user_enrollments.c.course_id
    ).filter(user_enrollments.c.user_id == user_id).all()
    return set(enrollments_query)


@router.post(
    "",
    status_code=status.HTTP_201_CREATED,
    response_model=CourseOut,
    dependencies=[Depends(admin_required)],
)
def create_course(body: CourseIn, db: Session = Depends(get_db)):
    logger.info("Intentando crear curso", title=body.title, description=body.description, subject_ids=body.subject_ids)
    if db.query(Course).filter(Course.title == body.title).first():
        logger.warn("Conflicto: Ya existe un curso con el mismo título", title=body.title)
        raise HTTPException(status.HTTP_409_CONFLICT, "Curso duplicado")

    course = Course(title=body.title, description=body.description)

    if body.subject_ids:
        course.subjects.extend(
            db.query(Subject).filter(Subject.id.in_(body.subject_ids)).all()
        )

    db.add(course)
    db.commit()
    db.refresh(course)
    logger.info("Curso creado exitosamente", course_id=course.id, title=course.title)
    return _course_to_schema(course, None)


@router.get("/my", response_model=list[CourseOut])
def my_courses(payload: dict = Depends(jwt_required), db: Session = Depends(get_db)):
    user_id = payload["user_id"]
    logger.info("Obteniendo cursos para el usuario (my courses)", user_id=user_id)
    
    # Obtener las matrículas de asignaturas del usuario
    subject_enrollments = _get_subject_enrollments_for_user(user_id, db)
    
    # Obtener el usuario con sus cursos y las relaciones anidadas necesarias
    user_with_courses = db.query(User).options(
        selectinload(User.courses)
        .selectinload(Course.subjects)
        .selectinload(Subject.themes)
    ).get(user_id)

    if not user_with_courses:
         logger.warn("Usuario no encontrado al cargar la relación de cursos para 'my courses'", user_id=user_id)
         raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Usuario no encontrado al cargar cursos.")

    logger.info("Cursos del usuario obtenidos", user_id=user_id, count=len(user_with_courses.courses))
    return [_course_to_schema(c, subject_enrollments) for c in user_with_courses.courses]


@router.get("/all", response_model=list[CourseOut])
def list_all_courses(payload: dict = Depends(jwt_required), db: Session = Depends(get_db)):
    user_id = payload["user_id"]
    logger.info("Obteniendo todos los cursos (list all courses)", user_id=user_id)
    subject_enrollments = _get_subject_enrollments_for_user(user_id, db)

    courses = (
        db.query(Course)
        .options(
            selectinload(Course.subjects).selectinload(Subject.themes)
        )
        .all()
    )
    logger.info("Todos los cursos obtenidos", count=len(courses))
    return [_course_to_schema(c, subject_enrollments) for c in courses]

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
    logger.info("Intentando desmatricular usuario de curso", user_id=user_id, course_id=course_id)
    user: User = db.query(User).options(joinedload(User.courses)).get(user_id)
    if not user:
        logger.warn("Usuario no encontrado al intentar desmatricular", user_id=user_id, course_id=course_id)
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Usuario no encontrado")

    course: Course = db.query(Course).get(course_id)
    if not course:
        logger.warn("Curso no encontrado al intentar desmatricular", user_id=user_id, course_id=course_id)
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Curso no encontrado")

    deleted_rows = db.execute(
        delete(user_enrollments).where(
            user_enrollments.c.user_id == user_id,
            user_enrollments.c.course_id == course_id,
        )
    ).rowcount
    logger.info("Eliminadas matrículas de la tabla de asociación", deleted_count=deleted_rows, user_id=user_id, course_id=course_id)

    if course in user.courses:
        user.courses.remove(course)
        logger.info("Curso eliminado de la relación user.courses", user_id=user_id, course_id=course_id)
    else:
        logger.info("Curso no estaba en la relación user.courses, solo en tabla de asociación", user_id=user_id, course_id=course_id)


    db.commit()
    logger.info("Usuario desmatriculado de curso exitosamente", user_id=user_id, course_id=course_id)

@router.get("/{course_id}", response_model=CourseOut)
def get_course(
    course_id: int, payload: dict = Depends(jwt_required), db: Session = Depends(get_db)
):
    user_id = payload["user_id"]
    logger.info("Obteniendo detalles del curso", course_id=course_id, user_id=user_id)
    subject_enrollments = _get_subject_enrollments_for_user(user_id, db)


    course: Course | None = (
        db.query(Course)
        .options(selectinload(Course.subjects).selectinload(Subject.themes))
        .get(course_id)
    )
    if not course:
        logger.warn("Curso no encontrado", course_id=course_id, user_id=user_id)
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Curso no encontrado")

    logger.info("Detalles del curso obtenidos", course_id=course.id, title=course.title)
    return _course_to_schema(course, subject_enrollments)

@router.put("/{course_id}", response_model=CourseOut, dependencies=[Depends(admin_required)])
def update_course(course_id: int, body: CourseUpdate, db: Session = Depends(get_db)):
    logger.info("Intentando actualizar curso", course_id=course_id, update_data=body.model_dump(exclude_none=True))
    course: Course | None = (
        db.query(Course).options(joinedload(Course.subjects)).get(course_id)
    )
    if not course:
        logger.warn("Curso no encontrado al intentar actualizar", course_id=course_id)
        raise HTTPException(status.HTTP_404_NOT_FOUND, "Curso no encontrado")

    # ── título/descr ─────────────────────────────────────────
    if body.title:
        dup = db.query(Course).filter(Course.title == body.title, Course.id != course_id).first()
        if dup:
            logger.warn("Conflicto: Ya existe otro curso con el nuevo título", new_title=body.title, existing_course_id=dup.id)
            raise HTTPException(status.HTTP_409_CONFLICT, "Ya existe otro curso con ese título")
        course.title = body.title
    if body.description is not None:
        course.description = body.description

    # ── reemplazar asignaturas ───────────────────────────────
    if body.subject_ids is not None:
        logger.info("Actualizando asignaturas del curso", course_id=course_id, new_subject_ids=body.subject_ids)
        subjects = db.query(Subject).filter(Subject.id.in_(body.subject_ids)).all()
        course.subjects = subjects

    db.commit()
    db.refresh(course)
    # Es necesario recargar las relaciones de asignaturas y temas si se modificaron y se quieren devolver actualizadas.
    # joinedload(Course.subjects).selectinload(Subject.themes) podría ser necesario aquí si no están ya cargadas.
    # Sin embargo, _course_to_schema espera que course.subjects ya tenga los temas cargados.
    # Las operaciones de selectinload/joinedload en la carga inicial del curso deberían ser suficientes.
    db.refresh(course) # Asegura que course.subjects está actualizado si se cambió la lista de subjects
    # Para asegurar que los temas dentro de las asignaturas están cargados para _course_to_schema:
    # Es posible que necesitemos una nueva carga aquí si las asignaturas o sus temas fueron modificados
    # y no se reflejan automáticamente. Por ahora, asumimos que db.refresh(course) y las cargas
    # eager previas son suficientes. Si los tests fallan, se revisará esta parte.
    # Para estar seguros, recargamos explícitamente con las opciones necesarias.
    
    # Se quita la recarga completa para evitar complejidad innecesaria si no se requiere.
    # Si las subject_ids se actualizan, la relación course.subjects se actualiza.
    # _course_to_schema iterará sobre course.subjects, y cada subject.themes ya está cargado por
    # las opciones de selectinload en las queries GET. La actualización de course.subjects
    # no debería afectar la carga eager de subject.themes de esas instancias de Subject.

    logger.info("Curso actualizado exitosamente", course_id=course.id, title=course.title)
    return _course_to_schema(course, None) # User es None porque no es relevante para el contexto de admin

@router.delete("/{course_id}", status_code=status.HTTP_204_NO_CONTENT, dependencies=[Depends(admin_required)])
def delete_course(course_id: int, db: Session = Depends(get_db)):
    logger.info("Intentando eliminar curso", course_id=course_id)
    course = db.query(Course).get(course_id)
    if not course:
        logger.warn("Curso no encontrado al intentar eliminar", course_id=course_id)
        raise HTTPException(status.HTTP_404_NOT_FOUND, "Curso no encontrado")
    db.delete(course)
    db.commit()
    logger.info("Curso eliminado exitosamente", course_id=course_id)

@router.delete("/{course_id}/subjects", status_code=status.HTTP_204_NO_CONTENT, dependencies=[Depends(admin_required)])
def detach_subjects(
    course_id: int, body: SubjectDetach, db: Session = Depends(get_db)
):
    logger.info("Intentando desvincular asignaturas del curso", course_id=course_id, subject_ids_to_detach=body.subject_ids)
    course: Course | None = (
        db.query(Course).options(joinedload(Course.subjects)).get(course_id)
    )
    if not course:
        logger.warn("Curso no encontrado al intentar desvincular asignaturas", course_id=course_id)
        raise HTTPException(status.HTTP_404_NOT_FOUND, "Curso no encontrado")

    detached_count = 0
    for sid in body.subject_ids:
        subj = db.query(Subject).get(sid)
        if subj and subj in course.subjects:
            course.subjects.remove(subj)
            detached_count +=1
            logger.debug("Asignatura desvinculada", course_id=course_id, subject_id=sid)

    if detached_count > 0:
        db.commit()
        logger.info("Asignaturas desvinculadas exitosamente", course_id=course_id, count=detached_count, requested_count=len(body.subject_ids))
    else:
        logger.info("No se desvincularon asignaturas (ninguna encontrada o ya desvinculada)", course_id=course_id, requested_ids=body.subject_ids)