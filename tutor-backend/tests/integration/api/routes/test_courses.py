from datetime import datetime, timezone
from uuid import uuid4

import pytest
from starlette.testclient import TestClient
from sqlalchemy.orm import Session

import src.api.routes.courses as courses_module
from src.models import User, Course, Subject, Theme


# ───────────────── helpers ──────────────────────────────────────────────────
def insert_theme(*, title: str | None = None, subject: Subject | None = None) -> Theme:
    if title is None:
        title = f"Tema 1 – {uuid4().hex[:6]}"
    return Theme(name=title, subject=subject)


def insert_subject(
    db: Session,
    *,
    name: str | None = None,
    description: str = "Desc",
) -> Subject:
    if name is None:
        name = f"Álgebra – {uuid4().hex[:6]}"

    sub = Subject(name=name, description=description)

    # Creamos el theme ya enlazado
    sub.themes.append(insert_theme(subject=sub))

    db.add(sub)
    db.commit()
    db.refresh(sub)
    return sub

def insert_course(db: Session, *,
                  title="Curso A", description="Desc",
                  with_subject=True) -> Course:
    course = Course(title=title, description=description)
    if with_subject:
        course.subjects.append(insert_subject(db))
    db.add(course)
    db.commit()
    db.refresh(course)
    return course

def insert_user(db: Session, *, email="ada@example.com", username="ada") -> User:
    user = db.query(User).filter_by(email=email).first()
    if user:
        return user
    user = User(username=username, email=email, password="hashed", is_admin=False)
    db.add(user)
    db.commit()
    db.refresh(user)
    return user


# ───────────────── tests ────────────────────────────────────────────────────
def _as_user(monkeypatch, user: User):
    """
    Bypass JWT/auth dependencies so we can hit the endpoints
    sin necesidad de generar tokens reales.
    """
    monkeypatch.setattr(
        courses_module, "jwt_required", lambda: {"user_id": user.id, "is_admin": False}
    )


def _as_admin(monkeypatch):
    """
    Bypass la dependencia admin_required (sólo comprueba que la llames).
    """
    monkeypatch.setattr(courses_module, "admin_required", lambda: None)


# ---------- POST /api/courses ----------
def test_create_course(client: TestClient, db_session: Session, monkeypatch):
    _as_admin(monkeypatch)

    body = {"title": "Nuevo Curso", "description": "Intro"}
    r = client.post("/api/courses", json=body)

    assert r.status_code == 201
    data = r.json()
    assert data["title"] == "Nuevo Curso"
    # Se creó realmente en la BBDD
    assert db_session.query(Course).count() == 1


def test_create_course_duplicate(client, db_session, monkeypatch):
    _as_admin(monkeypatch)
    insert_course(db_session, title="Duplicado")

    r = client.post("/api/courses", json={"title": "Duplicado"})
    assert r.status_code == 409
    assert r.json()["detail"] == "Curso duplicado"


# ---------- GET /api/courses y /my ----------
@pytest.fixture
def sample_data(db_session: Session):
    """
    Crea:
    * user
    * course1 con subject1 (user matriculado)
    * course2 con subject2 (sin matricular)
    """
    user = insert_user(db_session)
    subject_A = insert_subject(db_session, name="Asignatura Común A")
    subject_B = insert_subject(db_session, name="Asignatura B Específica")

    # Crear cursos sin que auto-creen su propia asignatura, para poder asignarles subject_A y subject_B
    course1 = Course(title="C1 - Curso con A matriculada", description="Desc C1")
    course2 = Course(title="C2 - Curso con A NO matriculada", description="Desc C2")
    course3 = Course(title="C3 - Curso con B", description="Desc C3")
    
    db_session.add_all([course1, course2, course3])
    db_session.commit()

    # Vincular asignaturas a cursos (tabla course_subjects)
    from src.models.associations import course_subjects, user_enrollments, user_courses
    db_session.execute(course_subjects.insert().values(course_id=course1.id, subject_id=subject_A.id))
    db_session.execute(course_subjects.insert().values(course_id=course2.id, subject_id=subject_A.id))
    db_session.execute(course_subjects.insert().values(course_id=course3.id, subject_id=subject_B.id))
    
    db_session.commit()
    # Recargar las relaciones de los cursos después de añadirles asignaturas manualmente
    db_session.refresh(course1) # course1 ahora tiene subject_A
    db_session.refresh(course2) # course2 ahora tiene subject_A
    db_session.refresh(course3) # course3 ahora tiene subject_B
    
    return user, course1, course2, course3, subject_A, subject_B


def test_list_courses_enrolled_flag(client: TestClient, db_session: Session, sample_data, monkeypatch):
    user, course1, course2, course3, subject_A, subject_B = sample_data
    
    # Simular que el usuario 'user' (creado en sample_data) está haciendo la petición
    _as_user(monkeypatch, user)

    # Matricular al usuario en subject_A DENTRO de course1 usando el endpoint de subjects
    # Necesitamos que el client esté autenticado como el usuario que se matricula.
    # El fixture 'client' por defecto es admin, así que para este paso,
    # si _as_user no afecta al client globalmente, necesitaríamos un client específico o
    # asegurar que el user de sample_data es el user_id=1 que usa _as_user.
    # Asumamos que user.id es el que _as_user va a mockear.
    
    # Antes de matricular, el usuario no debería estar en user.courses directamente.
    # La matriculación en una asignatura de un curso debería añadirlo.
    
    # Crear un usuario específico para este test para evitar conflictos con el user_id=1 por defecto del client
    test_specific_user = insert_user(db_session, email="specific_user@example.com", username="specific_user_courses")
    _as_user(monkeypatch, test_specific_user) # Ahora el cliente opera como test_specific_user

    # Matricular test_specific_user en subject_A (del course1)
    enroll_resp = client.post(f"/api/subjects/{subject_A.id}/enroll", json={"course_id": course1.id})
    assert enroll_resp.status_code == 204 # 204 No Content para matriculación exitosa

    r = client.get("/api/courses/all")
    assert r.status_code == 200
    payload = r.json()
    
    course_titles_in_response = {c["title"] for c in payload}
    assert course_titles_in_response == {"C1 - Curso con A matriculada", "C2 - Curso con A NO matriculada", "C3 - Curso con B"}

    res_course1 = next(c for c in payload if c["id"] == course1.id)
    res_course2 = next(c for c in payload if c["id"] == course2.id)
    res_course3 = next(c for c in payload if c["id"] == course3.id)

    # En Course1, SubjectA debe estar enrolled: true
    subj_A_in_C1 = next(s for s in res_course1["subjects"] if s["id"] == subject_A.id)
    assert subj_A_in_C1["enrolled"] is True
    
    # En Course2, SubjectA debe estar enrolled: false
    subj_A_in_C2 = next(s for s in res_course2["subjects"] if s["id"] == subject_A.id)
    assert subj_A_in_C2["enrolled"] is False

    # En Course3, SubjectB debe estar enrolled: false
    subj_B_in_C3 = next(s for s in res_course3["subjects"] if s["id"] == subject_B.id)
    assert subj_B_in_C3["enrolled"] is False


def test_my_courses_returns_only_enrolled(client: TestClient, db_session: Session, sample_data, monkeypatch):
    user_from_fixture, course1, course2, course3, subject_A, subject_B = sample_data
    
    # Crear un usuario específico para este test
    test_user = insert_user(db_session, email="mycourses_user@example.com", username="mycourses_user")
    _as_user(monkeypatch, test_user) # Autenticar como este usuario

    # Matricular al test_user en subject_A (que está en course1)
    enroll_resp1 = client.post(f"/api/subjects/{subject_A.id}/enroll", json={"course_id": course1.id})
    assert enroll_resp1.status_code == 204

    # Matricular al test_user en subject_B (que está en course3)
    enroll_resp3 = client.post(f"/api/subjects/{subject_B.id}/enroll", json={"course_id": course3.id})
    assert enroll_resp3.status_code == 204
    
    # El usuario ahora debería estar matriculado en course1 y course3

    r = client.get("/api/courses/my")
    assert r.status_code == 200
    data = r.json()
    
    assert len(data) == 2
    course_ids_in_response = {c["id"] for c in data}
    assert course_ids_in_response == {course1.id, course3.id}

    # Verificar que course2 no está en la lista de "my courses"
    assert course2.id not in course_ids_in_response

    # Adicionalmente, verificar el estado 'enrolled' dentro de 'my courses'
    my_course1_data = next(c for c in data if c["id"] == course1.id)
    my_subject_A_in_course1 = next(s for s in my_course1_data["subjects"] if s["id"] == subject_A.id)
    assert my_subject_A_in_course1["enrolled"] is True
    
    my_course3_data = next(c for c in data if c["id"] == course3.id)
    my_subject_B_in_course3 = next(s for s in my_course3_data["subjects"] if s["id"] == subject_B.id)
    assert my_subject_B_in_course3["enrolled"] is True


# ---------- GET /api/courses/{id} ----------
def test_get_course_ok(client: TestClient, db_session: Session, sample_data, monkeypatch):
    # El user_id de la autenticación no debería afectar qué curso se puede ver,
    # pero sí afecta el flag 'enrolled' dentro de la respuesta.
    user_generic, course1, course2, _, subject_A, _ = sample_data # user_generic no se usa para auth aquí
    
    test_specific_user_get = insert_user(db_session, email="specific_user_get@example.com", username="specific_user_get")
    _as_user(monkeypatch, test_specific_user_get) # Autenticar como este usuario

    # Matricular a este usuario en subject_A de course1 para probar el flag 'enrolled'
    enroll_resp = client.post(f"/api/subjects/{subject_A.id}/enroll", json={"course_id": course1.id})
    assert enroll_resp.status_code == 204

    r = client.get(f"/api/courses/{course1.id}")
    assert r.status_code == 200
    course_data = r.json()
    assert course_data["title"] == course1.title # El título original de sample_data

    # Verificar el flag 'enrolled' para subject_A dentro de course1
    subject_A_data = next(s for s in course_data["subjects"] if s["id"] == subject_A.id)
    assert subject_A_data["enrolled"] is True

    # Verificar que para course2 (donde no está matriculado), el flag es false
    r_course2 = client.get(f"/api/courses/{course2.id}") # course2 también tiene subject_A
    assert r_course2.status_code == 200
    course2_data = r_course2.json()
    subject_A_in_course2_data = next(s for s in course2_data["subjects"] if s["id"] == subject_A.id)
    assert subject_A_in_course2_data["enrolled"] is False


def test_get_course_not_found(client, db_session, sample_data, monkeypatch):
    user, *_ = sample_data
    _as_user(monkeypatch, user)

    r = client.get("/api/courses/9999")
    assert r.status_code == 404


# ---------- DELETE /api/courses/{course_id}/unenroll ----------
def test_unenroll_course(client: TestClient, db_session: Session, monkeypatch):
    # 1. Setup
    user = insert_user(db_session, email="test_unenroll@example.com", username="unenroll_user")
    course = insert_course(db_session, title="CourseToUnenroll")
    subject1_in_course = course.subjects[0] # Asumimos que insert_course crea al menos una asignatura
    
    # Matricular al usuario en el curso y en su asignatura
    from src.models.associations import user_enrollments, user_courses # Importar tablas
    from sqlalchemy import select, and_ # Para verificar

    db_session.execute(
        user_enrollments.insert().values(
            user_id=user.id,
            subject_id=subject1_in_course.id,
            course_id=course.id
        )
    )
    db_session.execute(
        user_courses.insert().values(user_id=user.id, course_id=course.id)
    )
    db_session.commit()

    # Verificar estado inicial
    assert db_session.execute(select(user_enrollments).where(and_(user_enrollments.c.user_id == user.id, user_enrollments.c.course_id == course.id))).first() is not None
    assert db_session.execute(select(user_courses).where(and_(user_courses.c.user_id == user.id, user_courses.c.course_id == course.id))).first() is not None

    _as_user(monkeypatch, user) # Autenticar como el usuario creado

    # 2. Llamar al endpoint de desmatriculación del curso
    r = client.delete(f"/api/courses/{course.id}/unenroll")
    assert r.status_code == 204

    # 3. Verificar estado final
    # No deben quedar matrículas para este usuario en este curso en user_enrollments
    assert db_session.execute(select(user_enrollments).where(and_(user_enrollments.c.user_id == user.id, user_enrollments.c.course_id == course.id))).first() is None
    # El usuario ya no debe estar en user_courses para este curso
    assert db_session.execute(select(user_courses).where(and_(user_courses.c.user_id == user.id, user_courses.c.course_id == course.id))).first() is None


def test_unenroll_course_not_found(client: TestClient, db_session: Session, sample_data, monkeypatch):
    user, *_ = sample_data
    _as_user(monkeypatch, user)

    r = client.delete("/api/courses/9999/unenroll") # Curso no existente
    assert r.status_code == 404 # Esperamos 404 si el curso no existe


def test_unenroll_course_user_not_enrolled_in_course_table(client: TestClient, db_session: Session, monkeypatch):
    # Caso: el usuario no está en user_courses, pero podría tener matrículas huérfanas (aunque no debería ocurrir)
    # o simplemente no está en user_courses y no tiene matrículas.
    # El endpoint debería funcionar igual (ser idempotente en cuanto a la no existencia previa).
    user = insert_user(db_session, email="test_unenroll_not_in_course@example.com", username="unenroll_user_not")
    course = insert_course(db_session, title="CourseNotReallyEnrolled")
    
    _as_user(monkeypatch, user)

    # Verificar que el usuario no está en user_courses para este curso
    from src.models.associations import user_courses
    from sqlalchemy import select, and_
    assert db_session.execute(select(user_courses).where(and_(user_courses.c.user_id == user.id, user_courses.c.course_id == course.id))).first() is None

    r = client.delete(f"/api/courses/{course.id}/unenroll")
    assert r.status_code == 204 # Debería ser exitoso (no hay nada que hacer o limpia huérfanos)
