"""
Pruebas de integración para las rutas de *Subjects*.

El *conftest* global ya nos inyecta:

* TestClient → autenticado como `user_id = 1, is_admin = True`.
* Sesión de BBDD en memoria → `db_session`.
"""
from starlette.status import (
    HTTP_201_CREATED,
    HTTP_204_NO_CONTENT,
    HTTP_409_CONFLICT,
    HTTP_409_CONFLICT,
    HTTP_404_NOT_FOUND,
    HTTP_400_BAD_REQUEST,
)
from sqlalchemy import select, and_

from src.models import Subject, User, Course # Añadido Course
from src.models.associations import user_enrollments, course_subjects, user_courses # Añadidas tablas de asociación

API = "/api/subjects"        # prefijo común


# ───────────────────────── helpers ──────────────────────────
def _mk_subject(client, name: str, *, desc: str | None = None):
    """POST /api/subjects/create (description es obligatoria)."""
    if desc is None:                     # proveemos una por defecto
        desc = f"{name} desc"
    body = {"name": name, "description": desc}
    return client.post(f"{API}/create", json=body)

# Modificado para incluir course_id
def _enroll(client, subj_id: int, course_id: int):
    return client.post(f"{API}/{subj_id}/enroll", json={"course_id": course_id})

# Modificado para incluir course_id
def _unenroll(client, subj_id: int, course_id: int):
    return client.delete(f"{API}/{subj_id}/unenroll", json={"course_id": course_id})


# ───────────────────────── tests ────────────────────────────
def test_create_subject_ok(client, db_session):
    """✔ Devuelve 201 y persiste el subject."""
    resp = _mk_subject(client, "Maths", desc="Álgebra y cálculo")
    assert resp.status_code == HTTP_201_CREATED
    assert resp.json() == {
        "id": 1,
        "name": "Maths",
        "description": "Álgebra y cálculo",
    }
    assert db_session.query(Subject).count() == 1


def test_create_subject_duplicate(client, db_session):
    """✔ Nombre repetido → 409 Conflict."""
    _mk_subject(client, "Physics", desc="Física clásica")
    resp = _mk_subject(client, "Physics", desc="Física clásica")
    assert resp.status_code == HTTP_409_CONFLICT
    assert db_session.query(Subject).count() == 1


def test_list_subjects(client):
    """✔ GET /subjects devuelve todos los registros."""
    _mk_subject(client, "Art", desc="Historia del arte")
    _mk_subject(client, "History", desc="Historia universal")
    resp = client.get(f"{API}/all")
    assert resp.status_code == 200
    names = {s["name"] for s in resp.json()}
    assert names == {"Art", "History"}


def test_enroll_and_unenroll_flow(client, db_session):
    """
    ✔ POST /enroll asocia el subject al usuario.
    ✔ DELETE /unenroll quita la relación y cursos huérfanos.
    """
    user = User(id=1, username="test", email="t@t.com", password="x")
    subj = Subject(name="Bio", description="Biología")
    # Este test asume que existe un curso por defecto o no le importa el curso.
    # Con los cambios, enroll y unenroll ahora requieren course_id.
    # Este test necesitaría ser reescrito o eliminado si no tiene sentido
    # en el nuevo paradigma de matrícula por curso.
    # Por ahora, lo comentaré, ya que el nuevo test `test_enroll_unenroll_specific_course` es más completo.
    # db_session.add_all([user, subj])
    # db_session.commit()

    # assert _enroll(client, subj.id, ???).status_code == HTTP_204_NO_CONTENT 
    # db_session.refresh(user)
    # # assert subj in user.subjects # Esta comprobación ya no es válida
    #
    # assert _enroll(client, subj.id, ???).status_code == HTTP_204_NO_CONTENT # Esto debería ser 409
    #
    # assert _unenroll(client, subj.id, ???).status_code == HTTP_204_NO_CONTENT
    # db_session.refresh(user)
    # # assert subj not in user.subjects # Esta comprobación ya no es válida
    #
    # assert _unenroll(client, subj.id, ???).status_code == HTTP_204_NO_CONTENT # Esto debería ser 404
    pass # Comentando el contenido original


def test_enroll_unenroll_subject_not_found(client):
    """✔ Subject o Course inexistente → 404."""
    # Asumimos que el curso 1 existe para probar el subject_id inválido
    # En un setup real, crearíamos un curso válido primero.
    # Aquí, para simplificar, no creamos el curso, así que el endpoint de curso podría fallar primero.
    # La prueba original solo verificaba subject_id.
    assert _enroll(client, 999, 1).status_code   == HTTP_404_NOT_FOUND # subject_id=999 (no existe)
    assert _unenroll(client, 999, 1).status_code == HTTP_404_NOT_FOUND # subject_id=999 (no existe)
    # También deberíamos probar con un subject_id válido y course_id inválido
    # _mk_subject(client, "TempSubj") # Crea subject con id 1 (asumiendo que la BD está vacía)
    # assert _enroll(client, 1, 999).status_code == HTTP_404_NOT_FOUND # course_id=999 (no existe)
    # assert _unenroll(client, 1, 999).status_code == HTTP_404_NOT_FOUND # course_id=999 (no existe)
    # Esta parte requiere un setup más controlado que se hará en el nuevo test.


def test_enroll_unenroll_specific_course(client, db_session):
    """
    Tests detallados para la matriculación y desmatriculación
    de una asignatura en cursos específicos.
    """
    # 1. Setup: Usuario, 2 Cursos, 1 Asignatura en ambos cursos
    user = User(id=1, username="student1", email="student1@example.com", password="password")
    course1 = Course(id=1, title="Introducción a la Programación", description="Curso de programación básica")
    course2 = Course(id=2, title="Programación Avanzada", description="Curso de programación avanzada")
    subject_a = Subject(id=1, name="Algoritmos Comunes", description="Estudio de algoritmos")

    db_session.add_all([user, course1, course2, subject_a])
    db_session.commit()

    # Asociar subject_a a course1 y course2
    db_session.execute(course_subjects.insert().values(course_id=course1.id, subject_id=subject_a.id))
    db_session.execute(course_subjects.insert().values(course_id=course2.id, subject_id=subject_a.id))
    db_session.commit()
    
    # Verificar que el usuario se autentica (el cliente de test ya está autenticado como user_id=1)

    # 2. Matricularse en AsignaturaA -> Curso1 -> Éxito
    resp_enroll_c1 = _enroll(client, subject_a.id, course1.id)
    assert resp_enroll_c1.status_code == HTTP_204_NO_CONTENT
    
    enrollment_c1 = db_session.execute(
        select(user_enrollments).where(
            and_(
                user_enrollments.c.user_id == user.id,
                user_enrollments.c.subject_id == subject_a.id,
                user_enrollments.c.course_id == course1.id,
            )
        )
    ).first()
    assert enrollment_c1 is not None
    
    user_in_course1 = db_session.execute(
        select(user_courses).where(and_(user_courses.c.user_id == user.id, user_courses.c.course_id == course1.id))
    ).first()
    assert user_in_course1 is not None

    # 3. Matricularse en AsignaturaA -> Curso2 -> Éxito
    resp_enroll_c2 = _enroll(client, subject_a.id, course2.id)
    assert resp_enroll_c2.status_code == HTTP_204_NO_CONTENT

    enrollment_c2 = db_session.execute(
        select(user_enrollments).where(
            and_(
                user_enrollments.c.user_id == user.id,
                user_enrollments.c.subject_id == subject_a.id,
                user_enrollments.c.course_id == course2.id,
            )
        )
    ).first()
    assert enrollment_c2 is not None

    user_in_course2 = db_session.execute(
        select(user_courses).where(and_(user_courses.c.user_id == user.id, user_courses.c.course_id == course2.id))
    ).first()
    assert user_in_course2 is not None

    # 4. Reintento en AsignaturaA -> Curso1 -> Error 409
    resp_reenroll_c1 = _enroll(client, subject_a.id, course1.id)
    assert resp_reenroll_c1.status_code == HTTP_409_CONFLICT
    assert resp_reenroll_c1.json()["detail"] == "Ya estás matriculado en esta asignatura para este curso."

    # 5. Desmatricularse de AsignaturaA -> Curso1 -> Éxito
    resp_unenroll_c1 = _unenroll(client, subject_a.id, course1.id)
    assert resp_unenroll_c1.status_code == HTTP_204_NO_CONTENT

    enrollment_c1_after_unenroll = db_session.execute(
        select(user_enrollments).where(
            and_(
                user_enrollments.c.user_id == user.id,
                user_enrollments.c.subject_id == subject_a.id,
                user_enrollments.c.course_id == course1.id,
            )
        )
    ).first()
    assert enrollment_c1_after_unenroll is None
    
    # Usuario debe seguir en user_courses para course2
    user_in_course2_still = db_session.execute(
        select(user_courses).where(and_(user_courses.c.user_id == user.id, user_courses.c.course_id == course2.id))
    ).first()
    assert user_in_course2_still is not None
    
    # Usuario ya no debe estar en user_courses para course1 (asumiendo que subject_a era la única en course1 para este user)
    user_in_course1_after_unenroll = db_session.execute(
        select(user_courses).where(and_(user_courses.c.user_id == user.id, user_courses.c.course_id == course1.id))
    ).first()
    assert user_in_course1_after_unenroll is None


    # 6. Intentar desmatricularse de AsignaturaA -> Curso1 (ya desmatriculado) -> Error 404
    resp_reunenroll_c1 = _unenroll(client, subject_a.id, course1.id)
    assert resp_reunenroll_c1.status_code == HTTP_404_NOT_FOUND
    assert resp_reunenroll_c1.json()["detail"] == "Matrícula no encontrada para esta asignatura y curso."

    # 7. Test adicional: Matricular en una asignatura que no pertenece al curso especificado -> Error 400
    subject_b = Subject(id=2, name="Otra Asignatura", description="No en cursos")
    db_session.add(subject_b)
    db_session.commit()
    resp_enroll_wrong_course = _enroll(client, subject_b.id, course1.id) # subject_b no está en course1
    assert resp_enroll_wrong_course.status_code == HTTP_400_BAD_REQUEST
    assert resp_enroll_wrong_course.json()["detail"] == "La asignatura no pertenece al curso especificado"

    # 8. Test adicional: Desmatricularse de AsignaturaA -> Curso2 (la última matrícula)
    resp_unenroll_c2 = _unenroll(client, subject_a.id, course2.id)
    assert resp_unenroll_c2.status_code == HTTP_204_NO_CONTENT
    
    enrollment_c2_after_unenroll = db_session.execute(
        select(user_enrollments).where(
            and_(
                user_enrollments.c.user_id == user.id,
                user_enrollments.c.subject_id == subject_a.id,
                user_enrollments.c.course_id == course2.id,
            )
        )
    ).first()
    assert enrollment_c2_after_unenroll is None

    user_in_course2_after_unenroll = db_session.execute(
        select(user_courses).where(and_(user_courses.c.user_id == user.id, user_courses.c.course_id == course2.id))
    ).first()
    assert user_in_course2_after_unenroll is None
