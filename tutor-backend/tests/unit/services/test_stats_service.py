import pytest
from datetime import datetime, timedelta, timezone

from sqlalchemy import create_engine, event
from sqlalchemy.orm import sessionmaker

from src.database.base import Base
from src.services.stats_service import overview, timeline, by_theme

from src.models.subject import Subject
from src.models.theme import Theme
from src.models.exercise import Exercise
from src.models.user_response import UserResponse

# Alias para que timeline() encuentre el atributo que usa el servicio
UserResponse.respondida_en = UserResponse.created_at  # mapea respondida_en a created_at

@pytest.fixture
def db_session():
    # Creamos el engine y registramos date_trunc para SQLite
    engine = create_engine("sqlite:///:memory:")
    @event.listens_for(engine, "connect")
    def _register_date_trunc(dbapi_conn, conn_record):
        # date_trunc('day', 'YYYY-MM-DD HH:MM:SS') -> 'YYYY-MM-DD'
        dbapi_conn.create_function(
            "date_trunc", 2, lambda part, ts: ts.split(" ")[0]
        )

    # Creamos todas las tablas
    Base.metadata.create_all(bind=engine)

    Session = sessionmaker(bind=engine)
    session = Session()
    yield session
    session.close()


def seed_data(session):
    # 1) Creamos una asignatura para referenciar en subjects/themes
    subj = Subject(name="Matemáticas", description="Materia de prueba")
    session.add(subj)
    session.flush()  # subj.id disponible

    # 2) Dos temas bajo esa asignatura
    t1 = Theme(name="T1", description="Tema 1", subject_id=subj.id)
    t2 = Theme(name="T2", description="Tema 2", subject_id=subj.id)
    session.add_all([t1, t2])
    session.flush()  # t1.id, t2.id disponibles

    # 3) Tres ejercicios: dos en t1, uno en t2
    e1 = Exercise(
        statement="Enunciado 1",
        type="tipo1",
        difficulty="fácil",
        answer="resp1",
        explanation="",
        theme_id=t1.id,
    )
    e2 = Exercise(
        statement="Enunciado 2",
        type="tipo2",
        difficulty="difícil",
        answer="resp2",
        explanation="",
        theme_id=t1.id,
    )
    e3 = Exercise(
        statement="Enunciado 3",
        type="tipo3",
        difficulty="medio",
        answer="resp3",
        explanation="",
        theme_id=t2.id,
    )
    session.add_all([e1, e2, e3])
    session.flush()  # e1.id, e2.id, e3.id disponibles

    # 4) Tres respuestas únicas (cumplen UNIQUE(user_id, exercise_id)):
    now = datetime.now(timezone.utc)
    yesterday = now - timedelta(days=1)

    r1 = UserResponse(
        user_id=1,
        exercise_id=e1.id,
        answer="resp1",
        correct=True,
        time_sec=5,
        created_at=yesterday,
    )
    r2 = UserResponse(
        user_id=1,
        exercise_id=e2.id,
        answer="mal",
        correct=False,
        time_sec=7,
        created_at=now,
    )
    r3 = UserResponse(
        user_id=1,
        exercise_id=e3.id,
        answer="resp3",
        correct=True,
        time_sec=4,
        created_at=now,
    )
    session.add_all([r1, r2, r3])
    session.commit()

    return t1, t2, now


def test_overview_empty(db_session):
    """Usuario sin respuestas → todo a 0."""
    out = overview(db_session, user_id=1)
    assert out == {
        "hechos": 0,
        "correctos": 0,
        "porcentaje": 0.0,
        "trend24h": 0.0,
    }


def test_overview_with_data(db_session):
    """Total, correctos y porcentaje correctos."""
    t1, t2, now = seed_data(db_session)
    out = overview(db_session, user_id=1)

    assert out["hechos"] == 3
    assert out["correctos"] == 2
    assert out["porcentaje"] == round(2 * 100 / 3, 1)
    assert out["trend24h"] == 0.0


def test_timeline(db_session):
    """Agrupación diaria y ratio correcta."""
    t1, t2, now = seed_data(db_session)
    rows = timeline(db_session, user_id=1)

    expected = [
        {
            "date": (now - timedelta(days=1)).date().isoformat(),
            "correctRatio": 100.0,  # 1 de 1 correctas ayer
        },
        {
            "date": now.date().isoformat(),
            "correctRatio": round(1 * 100 / 2, 1),  # 1 de 2 correctas hoy
        },
    ]
    assert rows == expected


def test_by_theme(db_session):
    """Conteo y ratio por tema."""
    t1, t2, now = seed_data(db_session)
    out = by_theme(db_session, user_id=1)

    assert out == [
        {
            "theme_id": t1.id,
            "theme": t1.name,
            "done": 2,
            "correct": 1,
            "ratio": round(1 * 100 / 2, 1),
        },
        {
            "theme_id": t2.id,
            "theme": t2.name,
            "done": 1,
            "correct": 1,
            "ratio": 100.0,
        },
    ]
