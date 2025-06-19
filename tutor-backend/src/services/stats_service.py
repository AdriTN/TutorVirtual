from sqlalchemy import func, case
from sqlalchemy.orm import Session

from src.models import UserResponse, Exercise, Theme


def _correct_expr():
    # Suma 1 por cada respuesta correcta, 0 en caso contrario
    return func.sum(case((UserResponse.correct, 1), else_=0)).label("correct")


def overview(db: Session, user_id: int):
    """
    Retorna un resumen global:
      - hechos: número total de respuestas
      - correctos: número de respuestas correctas
      - porcentaje: ratio correctos/hechos en %
      - trend24h: placeholder (aún no implementado)
    """
    q = (
        db.query(
            func.count().label("total"),
            _correct_expr(),
        )
        .filter(UserResponse.user_id == user_id)
        .first()
    )

    total = q.total or 0
    correct = q.correct or 0

    return {
        "hechos": total,
        "correctos": correct,
        "porcentaje": round(correct * 100 / total, 1) if total else 0.0,
        "trend24h": 0.0,
    }


def timeline(db: Session, user_id: int):
    """
    Retorna una lista de días con:
      - date: fecha (YYYY-MM-DD)
      - correctRatio: porcentaje de respuestas correctas en ese día
    """
    rows = (
        db.query(
            # En SQLite func.date() agrupa por día; en Postgres func.date() también funciona.
            func.date(UserResponse.created_at).label("date"),
            func.count().label("total"),
            _correct_expr(),
        )
        .filter(UserResponse.user_id == user_id)
        .group_by("date")
        .order_by("date")
        .all()
    )

    result = []
    for r in rows:
        # r.date viene como string "YYYY-MM-DD" en SQLite,
        # o como date en otros dialectos; unificamos a string.
        date_str = r.date.isoformat() if hasattr(r.date, "isoformat") else str(r.date)
        result.append(
            {
                "date": date_str,
                "correctRatio": round(r.correct * 100 / r.total, 1) if r.total else 0.0,
            }
        )

    return result


def by_theme(db: Session, user_id: int):
    """
    Para cada tema en el que el usuario ha respondido:
      - theme_id
      - theme: nombre del tema
      - done: total de ejercicios resueltos
      - correct: total de ejercicios correctos
      - ratio: porcentaje correctos/done
    """
    rows = (
        db.query(
            Theme.id,
            Theme.name.label("nombre"),
            func.count().label("done"),
            _correct_expr(),
        )
        .join(Exercise, Exercise.theme_id == Theme.id)
        .join(UserResponse, UserResponse.exercise_id == Exercise.id)
        .filter(UserResponse.user_id == user_id)
        .group_by(Theme.id, Theme.name)
        .all()
    )

    return [
        {
            "theme_id": r.id,
            "theme": r.nombre,
            "done": r.done,
            "correct": r.correct,
            "ratio": round(r.correct * 100 / r.done, 1) if r.done else 0.0,
        }
        for r in rows
    ]
