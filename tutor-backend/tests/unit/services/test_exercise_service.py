import pytest
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from src.database.base import Base
from src.models.subject import Subject
from src.models.theme import Theme
from src.models.exercise import Exercise
from src.models.user_response import UserResponse
from src.models.user_theme_progress import UserThemeProgress
from src.services.exercise_service import (
    create_exercise_from_ai,
    register_user_answer,
)


@pytest.fixture
def db_session():
    engine = create_engine("sqlite:///:memory:")
    Base.metadata.create_all(bind=engine)
    SessionLocal = sessionmaker(bind=engine)
    sess = SessionLocal()
    yield sess
    sess.close()


@pytest.fixture
def numeros_naturales_theme(db_session):
    # 1) Creamos la asignatura "Matemáticas"
    mat = Subject(name="Matemáticas 1º ESO", description="Curso 1º ESO")
    db_session.add(mat)
    db_session.commit()

    # 2) Creamos el tema "Números naturales" bajo esa asignatura
    tema = Theme(
        name="Números naturales",
        description="Tema de números naturales",
        subject_id=mat.id
    )
    db_session.add(tema)
    db_session.commit()
    return tema


def test_create_exercise_with_real_theme(numeros_naturales_theme, db_session):
    data = {
        "enunciado":   "¿Cuánto es 2 + 3?",
        "tipo":        "respuesta corta",
        "dificultad":  "fácil",
        "respuesta":   "5",
        "explicacion": "Suma básica de enteros.",
    }
    ej = create_exercise_from_ai(data, numeros_naturales_theme, db_session)

    assert isinstance(ej, Exercise)
    assert ej.theme_id == numeros_naturales_theme.id
    assert ej.answer == "5"


def test_register_answer_updates_progress(numeros_naturales_theme, db_session):
    # Creamos un ejercicio de ejemplo
    ej = create_exercise_from_ai({
        "enunciado": "¿Cuál es el siguiente número tras 7?",
        "tipo": "respuesta corta",
        "dificultad": "fácil",
        "respuesta": "8",
        "explicacion": "",
    }, numeros_naturales_theme, db_session)

    # No hay progreso inicial
    assert db_session.query(UserThemeProgress).get((99, numeros_naturales_theme.id)) is None

    # Registramos respuesta correcta
    ok = register_user_answer(
        user_id=99,
        ej=ej,
        answer="8",
        time_sec=3,
        db=db_session,
    )
    assert ok is True

    ur = (
        db_session.query(UserResponse)
        .filter_by(user_id=99, exercise_id=ej.id)
        .one()
    )
    assert ur.correct is True

    prog = db_session.query(UserThemeProgress).get((99, numeros_naturales_theme.id))
    assert prog.completed == 1
    assert prog.correct   == 1

    # Registramos segunda respuesta, esta vez incorrecta, para el mismo tema (otro ejercicio)
    ej2 = create_exercise_from_ai({
        "enunciado": "Otro ejercicio",
        "tipo": "respuesta corta",
        "dificultad": "media",
        "respuesta": "correcta2",
        "explicacion": "",
    }, numeros_naturales_theme, db_session)

    ok_incorrect = register_user_answer(
        user_id=99,
        ej=ej2,
        answer="incorrecta", # Respuesta incorrecta
        time_sec=5,
        db=db_session,
    )
    assert ok_incorrect is False

    prog_updated = db_session.query(UserThemeProgress).get((99, numeros_naturales_theme.id))
    assert prog_updated.completed == 2 # Se incrementa
    assert prog_updated.correct   == 1 # No se incrementa por respuesta incorrecta

    # Registramos tercera respuesta, correcta, para el mismo tema (otro ejercicio)
    ej3 = create_exercise_from_ai({
        "enunciado": "Tercer ejercicio",
        "tipo": "respuesta corta",
        "dificultad": "alta",
        "respuesta": "correcta3",
        "explicacion": "",
    }, numeros_naturales_theme, db_session)
    
    ok_correct_again = register_user_answer(
        user_id=99,
        ej=ej3,
        answer="correcta3", # Respuesta correcta
        time_sec=10,
        db=db_session,
    )
    assert ok_correct_again is True

    prog_final = db_session.query(UserThemeProgress).get((99, numeros_naturales_theme.id))
    assert prog_final.completed == 3 # Se incrementa
    assert prog_final.correct   == 2 # Se incrementa por respuesta correcta
