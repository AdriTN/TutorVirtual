"""
Rutas de asignaturas
------------------------------------
Todas las URL empiezan ahora por un prefijo claro:

  • /subjects/…         → acciones sobre asignaturas
  • /courses/…          → acciones sobre cursos + asignaturas
"""
import structlog
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session, joinedload

from src.database.session import get_db
from sqlalchemy import select, and_

from sqlalchemy import delete
from sqlalchemy.orm import selectinload

from src.api.dependencies.auth import jwt_required, admin_required
from src.api.schemas.subjects import SubjectUpdate, ThemeDetach, SubjectEnrollData, SubjectUnenrollData
from src.models.user import User
from src.models.subject import Subject
from src.models.course import Course
from src.models.theme import Theme
from src.models.associations import user_enrollments

router = APIRouter()
logger = structlog.get_logger(__name__)


# ---------------------------------------------------------------------------
# 1. CRUD de asignaturas
# ---------------------------------------------------------------------------

@router.post(
    "/create",
    status_code=status.HTTP_201_CREATED,
    dependencies=[Depends(admin_required)],
)
def create_subject(data: dict, db: Session = Depends(get_db)):
    """Crear nueva asignatura."""
    name = data.get("name")
    description = data.get("description")
    logger.info("Intentando crear asignatura", name=name, description=description)
    if not name or not description:
        logger.warn("Datos insuficientes para crear asignatura", name=name, description=description)
        raise HTTPException(status.HTTP_422_UNPROCESSABLE_ENTITY, "El nombre y la descripción son obligatorios")

    if db.query(Subject).filter(
        (Subject.name == name) | (Subject.description == description) # TODO: Revisar si este OR es correcto, podría ser AND o dos queries.
    ).first():
        logger.warn("Conflicto: La asignatura ya existe", name=name, description=description)
        raise HTTPException(status.HTTP_409_CONFLICT, "La asignatura ya existe")

    subj = Subject(name=name, description=description)
    db.add(subj)
    db.commit()
    db.refresh(subj)
    logger.info("Asignatura creada exitosamente", subject_id=subj.id, name=subj.name)
    return {"id": subj.id, "name": subj.name, "description": subj.description}


@router.get("/all", status_code=status.HTTP_200_OK)
def list_subjects(db: Session = Depends(get_db)):
    """Lista completa de asignaturas + sus temas."""
    logger.info("Listando todas las asignaturas")
    subjects_with_themes = db.query(Subject).options(selectinload(Subject.themes)).all()
    logger.info("Asignaturas listadas", count=len(subjects_with_themes))
    return [
        {
            "id": s.id,
            "name": s.name,
            "description": s.description,
            "themes": [
                {"id": t.id, "title": t.name, "description": t.description}
                for t in s.themes
            ],
        }
        for s in subjects_with_themes
    ]


@router.put("/{subject_id}/update", response_model=dict, dependencies=[Depends(admin_required)])
def update_subject(
    subject_id: int, body: SubjectUpdate, db: Session = Depends(get_db)
):
    logger.info("Intentando actualizar asignatura", subject_id=subject_id, update_data=body.model_dump(exclude_none=True))
    subj: Subject | None = db.query(Subject).get(subject_id)
    if not subj:
        logger.warn("Asignatura no encontrada al intentar actualizar", subject_id=subject_id)
        raise HTTPException(status.HTTP_404_NOT_FOUND, "Asignatura no encontrada")

    if body.name:
        dup = (
            db.query(Subject)
            .filter(Subject.name == body.name, Subject.id != subject_id)
            .first()
        )
        if dup:
            logger.warn("Conflicto: Ya existe otra asignatura con el nuevo nombre", new_name=body.name, existing_subject_id=dup.id)
            raise HTTPException(status.HTTP_409_CONFLICT, "Ya existe otra asignatura con ese nombre")
        subj.name = body.name

    if body.description is not None:
        subj.description = body.description

    db.commit()
    db.refresh(subj)
    logger.info("Asignatura actualizada exitosamente", subject_id=subj.id, name=subj.name)
    return {"id": subj.id, "name": subj.name, "description": subj.description}


@router.delete("/{subject_id}/delete", status_code=status.HTTP_204_NO_CONTENT, dependencies=[Depends(admin_required)])
def delete_subject(subject_id: int, db: Session = Depends(get_db)):
    """Elimina una asignatura (y cascada según modelo)."""
    logger.info("Intentando eliminar asignatura", subject_id=subject_id)
    subj = db.query(Subject).get(subject_id)
    if not subj:
        logger.warn("Asignatura no encontrada al intentar eliminar", subject_id=subject_id)
        raise HTTPException(status.HTTP_404_NOT_FOUND, "Asignatura no encontrada")
    db.delete(subj)
    db.commit()
    logger.info("Asignatura eliminada exitosamente", subject_id=subject_id)


# ---------------------------------------------------------------------------
# 2. Matrícula de usuarios en asignaturas
# ---------------------------------------------------------------------------

@router.post(
    "/{subject_id}/enroll",
    status_code=status.HTTP_204_NO_CONTENT,
    dependencies=[Depends(jwt_required)],
)
def enroll_subject(
    subject_id: int,
    enroll_data: SubjectEnrollData,
    payload: dict = Depends(jwt_required),
    db: Session = Depends(get_db),
):
    user_id = payload["user_id"]
    course_id = enroll_data.course_id
    logger.info("Intentando matricular usuario en asignatura", user_id=user_id, subject_id=subject_id, course_id=course_id)

    user: User = (
        db.query(User)
        .options(joinedload(User.courses)) 
        .get(user_id)
    )
    if not user:
        logger.warn("Usuario no encontrado al intentar matricular", user_id=user_id, subject_id=subject_id, course_id=course_id)
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Usuario no encontrado")

    subject: Subject = db.query(Subject).get(subject_id)
    if not subject:
        logger.warn("Asignatura no encontrada al intentar matricular", user_id=user_id, subject_id=subject_id, course_id=course_id)
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Asignatura no encontrada")

    course: Course = (
        db.query(Course)
        .options(joinedload(Course.subjects))
        .get(enroll_data.course_id)
    )
    if not course:
        logger.warn("Curso no encontrado al intentar matricular", user_id=user_id, subject_id=subject_id, course_id=course_id)
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Curso no encontrado")

    if subject not in course.subjects:
        logger.warn("Intento de matricular en asignatura que no pertenece al curso", user_id=user_id, subject_id=subject_id, course_id=course_id, subject_name=subject.name, course_title=course.title)
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="La asignatura no pertenece al curso especificado"
        )

    existing_enrollment = db.execute(
        select(user_enrollments).where(
            and_(
                user_enrollments.c.user_id == user_id,
                user_enrollments.c.subject_id == subject_id,
                user_enrollments.c.course_id == enroll_data.course_id,
            )
        )
    ).first()

    if existing_enrollment:
        logger.warn("Conflicto: Usuario ya matriculado en esta asignatura para este curso", user_id=user_id, subject_id=subject_id, course_id=course_id)
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="Ya estás matriculado en esta asignatura para este curso."
        )

    try:
        db.execute(
            user_enrollments.insert().values(
                user_id=user_id,
                subject_id=subject_id,
                course_id=enroll_data.course_id,
            )
        )
        logger.info("Matrícula creada en tabla de asociación", user_id=user_id, subject_id=subject_id, course_id=course_id)
    except Exception as e:
        db.rollback()
        logger.error("Error al crear matrícula en tabla de asociación", exc_info=e, user_id=user_id, subject_id=subject_id, course_id=course_id)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error al crear la matrícula: {e}"
        )

    if course not in user.courses:
        user.courses.append(course)
        logger.info("Usuario añadido a la relación user.courses", user_id=user_id, course_id=course_id)
    
    db.commit()
    logger.info("Usuario matriculado en asignatura exitosamente", user_id=user_id, subject_id=subject_id, course_id=course_id)


@router.delete(
    "/{subject_id}/unenroll",
    status_code=status.HTTP_204_NO_CONTENT,
    dependencies=[Depends(jwt_required)],
)
def unenroll_subject(
    subject_id: int,
    unenroll_data: SubjectUnenrollData,
    payload: dict = Depends(jwt_required),
    db: Session = Depends(get_db),
):
    user_id = payload["user_id"]
    course_id = unenroll_data.course_id
    logger.info("Intentando desmatricular usuario de asignatura", user_id=user_id, subject_id=subject_id, course_id=course_id)

    user: User = (
        db.query(User)
        .options(joinedload(User.courses))
        .get(user_id)
    )
    if not user:
        logger.warn("Usuario no encontrado al intentar desmatricular", user_id=user_id, subject_id=subject_id, course_id=course_id)
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Usuario no encontrado")

    subject: Subject = db.query(Subject).get(subject_id)
    if not subject:
        logger.warn("Asignatura no encontrada al intentar desmatricular", user_id=user_id, subject_id=subject_id, course_id=course_id)
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Asignatura no encontrada")
    
    course: Course = db.query(Course).get(course_id)
    if not course:
        logger.warn("Curso no encontrado al intentar desmatricular", user_id=user_id, subject_id=subject_id, course_id=course_id)
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Curso no encontrado")

    delete_stmt = (
        delete(user_enrollments)
        .where(
            and_(
                user_enrollments.c.user_id == user_id,
                user_enrollments.c.subject_id == subject_id,
                user_enrollments.c.course_id == course_id,
            )
        )
    )
    result = db.execute(delete_stmt)

    if result.rowcount == 0:
        logger.warn("Matrícula no encontrada para desmatricular", user_id=user_id, subject_id=subject_id, course_id=course_id)
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Matrícula no encontrada para esta asignatura y curso."
        )
    logger.info("Matrícula eliminada de la tabla de asociación", user_id=user_id, subject_id=subject_id, course_id=course_id, rowcount=result.rowcount)
        
    remaining_enrollments_in_course = db.execute(
        select(user_enrollments.c.subject_id).where(
            and_(
                user_enrollments.c.user_id == user_id,
                user_enrollments.c.course_id == course_id,
            )
        )
    ).first()

    if not remaining_enrollments_in_course and course in user.courses:
        user.courses.remove(course)
        logger.info("Usuario desvinculado del curso general ya que no quedan matrículas en asignaturas de ese curso", user_id=user_id, course_id=course_id)

    db.commit()
    logger.info("Usuario desmatriculado de asignatura exitosamente", user_id=user_id, subject_id=subject_id, course_id=course_id)


# ---------------------------------------------------------------------------
# 3. Temas de una asignatura
# ---------------------------------------------------------------------------

@router.get(
    "/{subject_id}/themes",
    status_code=status.HTTP_200_OK,
    dependencies=[Depends(jwt_required)],
)
def list_themes(subject_id: int, db: Session = Depends(get_db)):
    logger.info("Listando temas para la asignatura", subject_id=subject_id)
    subj: Subject = (
        db.query(Subject).options(joinedload(Subject.themes)).get(subject_id)
    )
    if not subj:
        logger.warn("Asignatura no encontrada al listar temas", subject_id=subject_id)
        raise HTTPException(status.HTTP_404_NOT_FOUND, "Asignatura no encontrada")

    logger.info("Temas listados para asignatura", subject_id=subject_id, count=len(subj.themes))
    return [
        {"id": t.id, "title": t.name, "description": t.description}
        for t in subj.themes
    ]


@router.delete(
    "/{subject_id}/themes/detach",
    status_code=status.HTTP_204_NO_CONTENT,
    dependencies=[Depends(admin_required)],
)
def detach_themes(
    subject_id: int,
    body: ThemeDetach,
    db: Session = Depends(get_db),
):
    logger.info("Intentando desvincular temas de asignatura", subject_id=subject_id, theme_ids_to_detach=body.theme_ids)
    subj: Subject = (
        db.query(Subject).options(joinedload(Subject.themes)).get(subject_id)
    )
    if not subj:
        logger.warn("Asignatura no encontrada al intentar desvincular temas", subject_id=subject_id)
        raise HTTPException(status.HTTP_404_NOT_FOUND, "Asignatura no encontrada")

    detached_count = 0
    for tid in body.theme_ids:
        theme = db.query(Theme).get(tid)
        if theme and theme.subject_id == subject_id:
            theme.subject_id = None
            detached_count +=1
            logger.debug("Tema preparado para desvincular", subject_id=subject_id, theme_id=tid)
        elif theme:
            logger.warn("Intento de desvincular tema que no pertenece a la asignatura", subject_id=subject_id, theme_id=tid, actual_subject_id=theme.subject_id)


    if detached_count > 0:
        db.commit()
        logger.info("Temas desvinculados exitosamente de la asignatura", subject_id=subject_id, count=detached_count, requested_count=len(body.theme_ids))
    else:
        logger.info("No se desvincularon temas (ninguno encontrado o no pertenecían a la asignatura)", subject_id=subject_id, requested_ids=body.theme_ids)


# ---------------------------------------------------------------------------
# 4. Relación Curso ↔ Asignatura
# ---------------------------------------------------------------------------

@router.post(
    "/courses/{course_id}/subjects/add",
    status_code=status.HTTP_201_CREATED,
    dependencies=[Depends(admin_required)],
)
def add_subject_to_course(
    course_id: int,
    data: dict,
    db: Session = Depends(get_db),
):
    subject_id = data.get("subject_id")
    logger.info("Intentando añadir asignatura a curso", course_id=course_id, subject_id=subject_id)
    if not subject_id:
        logger.warn("ID de asignatura no proporcionado para añadir a curso", course_id=course_id)
        raise HTTPException(status.HTTP_422_UNPROCESSABLE_ENTITY, "El id de la asignatura es obligatorio")

    subject = db.query(Subject).get(subject_id)
    if not subject:
        logger.warn("Asignatura no encontrada al intentar añadir a curso", course_id=course_id, subject_id=subject_id)
        raise HTTPException(status.HTTP_404_NOT_FOUND, "Asignatura no encontrada")

    course = db.query(Course).get(course_id)
    if not course:
        logger.warn("Curso no encontrado al intentar añadir asignatura", course_id=course_id, subject_id=subject_id)
        raise HTTPException(status.HTTP_404_NOT_FOUND, "Curso no encontrado")

    if subject in course.subjects:
        logger.warn("Conflicto: La asignatura ya está asociada al curso", course_id=course_id, subject_id=subject_id)
        raise HTTPException(status.HTTP_409_CONFLICT, "La asignatura ya está asociada al curso")

    course.subjects.append(subject)
    db.commit()
    logger.info("Asignatura añadida a curso exitosamente", course_id=course_id, subject_id=subject.id, subject_name=subject.name)
    return {"id": subject.id, "name": subject.name, "description": subject.description}


@router.delete(
    "/courses/{course_id}/subjects/{subject_id}/remove",
    status_code=status.HTTP_204_NO_CONTENT,
    dependencies=[Depends(admin_required)],
)
def remove_subject_from_course(
    course_id: int,
    subject_id: int,
    db: Session = Depends(get_db),
):
    logger.info("Intentando eliminar asignatura de curso", course_id=course_id, subject_id=subject_id)
    course: Course = (
        db.query(Course).options(joinedload(Course.subjects)).get(course_id)
    )
    if not course:
        logger.warn("Curso no encontrado al intentar eliminar asignatura", course_id=course_id, subject_id=subject_id)
        raise HTTPException(status.HTTP_404_NOT_FOUND, "Curso no encontrado")

    subject: Subject = db.query(Subject).get(subject_id)
    if not subject:
        logger.warn("Asignatura no encontrada al intentar eliminar de curso", course_id=course_id, subject_id=subject_id)
        raise HTTPException(status.HTTP_404_NOT_FOUND, "Asignatura no encontrada")

    if subject not in course.subjects:
        logger.warn("Conflicto: La asignatura no está asociada al curso para eliminar", course_id=course_id, subject_id=subject_id)
        raise HTTPException(status.HTTP_409_CONFLICT, "La asignatura no está asociada al curso")

    course.subjects.remove(subject)
    db.commit()
    logger.info("Asignatura eliminada de curso exitosamente", course_id=course_id, subject_id=subject_id)
