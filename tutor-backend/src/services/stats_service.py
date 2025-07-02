from sqlalchemy import func, case
from sqlalchemy.orm import Session
from datetime import datetime, timedelta, timezone

from src.models import UserResponse, Exercise, Theme


def _correct_expr():
    return func.sum(case((UserResponse.correct, 1), else_=0)).label("correct")


import structlog
logger = structlog.get_logger(__name__)

def _calculate_precision_for_period(db: Session, user_id: int, end_time: datetime, start_time: datetime):
    """Calcula el total de respuestas y las correctas para un período dado."""
    logger.debug("Calculando precisión para período", user_id=user_id, start_time=start_time.isoformat(), end_time=end_time.isoformat())
    query = (
        db.query(
            func.count().label("total"),
            _correct_expr(),
        )
        .filter(UserResponse.user_id == user_id)
        .filter(UserResponse.created_at >= start_time)
        .filter(UserResponse.created_at < end_time)
        .first()
    )
    total = query.total or 0
    correct = query.correct or 0
    logger.debug("Resultados del período", total=total, correct=correct, user_id=user_id, start_time=start_time.isoformat(), end_time=end_time.isoformat())
    if total == 0:
        logger.debug("Período sin datos", user_id=user_id, start_time=start_time.isoformat(), end_time=end_time.isoformat())
        return None
    precision = (correct * 100.0 / total)
    logger.debug("Precisión calculada para el período", precision=precision, user_id=user_id, start_time=start_time.isoformat(), end_time=end_time.isoformat())
    return {"total": total, "correct": correct, "precision": precision}


def overview(db: Session, user_id: int):
    """
    Retorna un resumen global:
      - hechos: número total de respuestas (global)
      - correctos: número de respuestas correctas (global)
      - porcentaje: ratio correctos/hechos en % (global)
      - trend24h: diferencia de precisión entre las últimas 24h y las 24h anteriores.
    """
    logger.info("Iniciando overview para usuario", user_id=user_id)
    # Cálculo global
    q_global = (
        db.query(
            func.count().label("total"),
            _correct_expr(),
        )
        .filter(UserResponse.user_id == user_id)
        .first()
    )
    total_global = q_global.total or 0
    correct_global = q_global.correct or 0
    porcentaje_global = round(correct_global * 100.0 / total_global, 1) if total_global else 0.0
    logger.debug("Estadísticas globales calculadas", user_id=user_id, total_global=total_global, correct_global=correct_global, porcentaje_global=porcentaje_global)

    # Cálculo de tendencia 24h
    now = datetime.now(timezone.utc)
    end_P1 = now
    start_P1 = now - timedelta(days=1)
    end_P0 = start_P1
    start_P0 = start_P1 - timedelta(days=1)

    logger.debug("Calculando estadísticas P1 (últimas 24h)", user_id=user_id, start_time=start_P1.isoformat(), end_time=end_P1.isoformat())
    stats_P1 = _calculate_precision_for_period(db, user_id, end_P1, start_P1)
    logger.debug("Calculando estadísticas P0 (24h anteriores a P1)", user_id=user_id, start_time=start_P0.isoformat(), end_time=end_P0.isoformat())
    stats_P0 = _calculate_precision_for_period(db, user_id, end_P0, start_P0)

    trend24h = 0.0

    if stats_P1 is not None:
        precision_P1_val = stats_P1["precision"]
        logger.debug("Precisión P1", precision=precision_P1_val, user_id=user_id)
        if stats_P0 is not None:
            precision_P0_val = stats_P0["precision"]
            logger.debug("Precisión P0", precision=precision_P0_val, user_id=user_id)
            trend24h = round(precision_P1_val - precision_P0_val, 1)
        else:
            logger.debug("No hay datos en P0 para comparar tendencia", user_id=user_id)
            pass 
    else:
        logger.debug("No hay datos en P1 para calcular tendencia", user_id=user_id)
        pass 

    logger.info("Trend24h calculado", trend24h=trend24h, user_id=user_id)
    return {
        "hechos": total_global,
        "correctos": correct_global,
        "porcentaje": porcentaje_global,
        "trend24h": trend24h,
    }


def timeline(db: Session, user_id: int):
    """
    Retorna una lista de días con:
      - date: fecha (YYYY-MM-DD)
      - correctRatio: porcentaje de respuestas correctas en ese día
    """
    logger.info("Generando timeline para usuario", user_id=user_id)
    rows = (
        db.query(
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
    logger.info("Generando estadísticas por tema para usuario", user_id=user_id)
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
