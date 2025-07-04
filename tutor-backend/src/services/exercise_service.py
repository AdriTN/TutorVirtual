from sqlalchemy.orm import Session

from src.models.exercise import Exercise
from src.models.user_response import UserResponse
from src.models.user_theme_progress import UserThemeProgress
from src.utils.utils import strip_and_lower


def create_exercise_from_ai(data: dict, tema, db: Session) -> Exercise:
    """
    Crea un Exercise a partir del dict que viene de la IA, asociándolo al tema dado.
    """
    ej = Exercise(
        statement   = data["enunciado"],
        type        = data["tipo"],
        difficulty  = data["dificultad"],
        answer      = data["respuesta"],
        explanation = data.get("explicacion", ""),
        theme_id    = tema.id,
    )
    db.add(ej)
    # db.commit()
    db.flush()
    db.refresh(ej)
    return ej


def register_user_answer(
    user_id: int,
    ej: Exercise,
    answer: str,
    time_sec: int | None,
    db: Session
) -> bool:
    """
    Registra la respuesta de un usuario a un ejercicio, actualiza su progreso
    y devuelve True/False según si fue correcta.
    """
    correcto = strip_and_lower(answer) == strip_and_lower(ej.answer)

    resp = UserResponse(
        user_id      = user_id,
        exercise_id  = ej.id,
        answer       = answer,
        correct      = correcto,
        time_sec     = time_sec,
    )
    db.add(resp)

    prog = db.get(UserThemeProgress, (user_id, ej.theme_id))
    if prog is None:
        prog = UserThemeProgress(
            user_id   = user_id,
            theme_id  = ej.theme_id,
            completed = 1,
            correct   = 1 if correcto else 0,
        )
        db.add(prog)
    else:
        prog.completed += 1
        prog.correct   += 1 if correcto else 0

    # db.commit()
    return correcto
