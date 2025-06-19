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
    course1 = insert_course(db_session, title="C1")
    course2 = insert_course(db_session, title="C2")

    # el usuario se apunta al primer subject del curso1
    subj_enrolled = course1.subjects[0]
    user.subjects.append(subj_enrolled)
    # y, para que course1 aparezca en /my, lo añadimos
    user.courses.append(course1)

    db_session.commit()
    return user, course1, course2, subj_enrolled


def test_list_courses_enrolled_flag(client, db_session, sample_data, monkeypatch):
    user, course1, course2, subj_enrolled = sample_data
    _as_user(monkeypatch, user)

    r = client.get("/api/courses/courses")
    assert r.status_code == 200
    payload = r.json()
    assert {c["title"] for c in payload} == {"C1", "C2"}

    # course1 → enrolled = True
    sub1 = next(s for s in payload[0]["subjects"] if s["id"] == subj_enrolled.id)
    assert sub1["enrolled"] is True
    # course2 → enrolled = False
    sub2 = next(
        s for s in payload[1]["subjects"] if s["id"] != subj_enrolled.id
    )
    assert sub2["enrolled"] is False


def test_my_courses_returns_only_enrolled(client, db_session, sample_data, monkeypatch):
    user, course1, *_ = sample_data
    _as_user(monkeypatch, user)

    r = client.get("/api/courses/my")
    assert r.status_code == 200
    data = r.json()
    assert len(data) == 1
    assert data[0]["id"] == course1.id


# ---------- GET /api/courses/{id} ----------
def test_get_course_ok(client, db_session, sample_data, monkeypatch):
    user, course1, *_ = sample_data
    _as_user(monkeypatch, user)

    r = client.get(f"/api/courses/{course1.id}")
    assert r.status_code == 200
    assert r.json()["title"] == "C1"


def test_get_course_not_found(client, db_session, sample_data, monkeypatch):
    user, *_ = sample_data
    _as_user(monkeypatch, user)

    r = client.get("/api/courses/9999")
    assert r.status_code == 404
