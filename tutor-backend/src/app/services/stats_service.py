from sqlalchemy import func, case
from ..models import UserResponse, Exercise, Theme
from sqlalchemy.orm import Session

def _correct_expr():
    return func.sum(case((UserResponse.correcto, 1), else_=0)).label("correct")

def overview(db: Session, user_id: int):
    q = db.query(
        func.count().label("total"),
        _correct_expr()
    ).filter(UserResponse.user_id == user_id).first()

    total    = q.total or 0
    correct  = q.correct or 0
    return {
        "hechos"     : total,
        "correctos"  : correct,
        "porcentaje" : round(correct * 100 / total, 1) if total else 0.0,
        "trend24h"   : 0.0,
    }

def timeline(db: Session, user_id: int):
    rows = (
        db.query(
            func.date_trunc("day", UserResponse.respondida_en).label("date"),
            func.count().label("total"),
            _correct_expr(),
        )
        .filter(UserResponse.user_id == user_id)
        .group_by("date")
        .order_by("date")
        .all()
    )

    return [
        {
            "date"        : r.date.isoformat(),
            "correctRatio": round(r.correct * 100 / r.total, 1) if r.total else 0.0,
        }
        for r in rows
    ]

def by_theme(db: Session, user_id: int):
    rows = (
        db.query(
            Theme.id,
            Theme.nombre,
            func.count().label("done"),
            _correct_expr(),
        )
        .join(Exercise, Exercise.tema_id == Theme.id)
        .join(UserResponse, UserResponse.ejercicio_id == Exercise.id)
        .filter(UserResponse.user_id == user_id)
        .group_by(Theme.id)
        .all()
    )

    return [
        {
            "theme_id": r.id,
            "theme"   : r.nombre,
            "done"    : r.done,
            "correct" : r.correct,
            "ratio"   : round(r.correct * 100 / r.done, 1) if r.done else 0.0,
        }
        for r in rows
    ]