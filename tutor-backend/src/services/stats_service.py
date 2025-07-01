from sqlalchemy import func, case
from sqlalchemy.orm import Session
from datetime import datetime, timedelta, timezone

from src.models import UserResponse, Exercise, Theme


def _correct_expr():
    # Suma 1 por cada respuesta correcta, 0 en caso contrario
    return func.sum(case((UserResponse.correct, 1), else_=0)).label("correct")


def _calculate_precision_for_period(db: Session, user_id: int, end_time: datetime, start_time: datetime):
    """Calcula el total de respuestas y las correctas para un período dado."""
    print(f"STATS_DEBUG: Calculando precisión para User ID: {user_id}, Start: {start_time}, End: {end_time}")
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
    print(f"STATS_DEBUG: Período ({start_time.strftime('%Y-%m-%d %H:%M')} a {end_time.strftime('%Y-%m-%d %H:%M')}): Total={total}, Correct={correct}")
    if total == 0:
        print(f"STATS_DEBUG: Período ({start_time.strftime('%Y-%m-%d %H:%M')} a {end_time.strftime('%Y-%m-%d %H:%M')}): No hay datos, retornando None.")
        return None
    precision = (correct * 100.0 / total)
    print(f"STATS_DEBUG: Período ({start_time.strftime('%Y-%m-%d %H:%M')} a {end_time.strftime('%Y-%m-%d %H:%M')}): Precision={precision:.2f}%")
    return {"total": total, "correct": correct, "precision": precision}


def overview(db: Session, user_id: int):
    """
    Retorna un resumen global:
      - hechos: número total de respuestas (global)
      - correctos: número de respuestas correctas (global)
      - porcentaje: ratio correctos/hechos en % (global)
      - trend24h: diferencia de precisión entre las últimas 24h y las 24h anteriores.
    """
    print(f"STATS_DEBUG: Iniciando overview para User ID: {user_id}")
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
    print(f"STATS_DEBUG: Global stats: Total={total_global}, Correct={correct_global}, Precision={porcentaje_global}%")

    # Cálculo de tendencia 24h
    now = datetime.now(timezone.utc)
    end_P1 = now
    start_P1 = now - timedelta(days=1)
    end_P0 = start_P1
    start_P0 = start_P1 - timedelta(days=1)

    print(f"STATS_DEBUG: --- Calculando stats P1 (últimas 24h) ---")
    stats_P1 = _calculate_precision_for_period(db, user_id, end_P1, start_P1)
    print(f"STATS_DEBUG: --- Calculando stats P0 (24h anteriores a P1) ---")
    stats_P0 = _calculate_precision_for_period(db, user_id, end_P0, start_P0)

    trend24h = 0.0
    precision_P1_val = None
    # precision_P0_val = None # No es necesario inicializar aquí

    if stats_P1 is not None:
        precision_P1_val = stats_P1["precision"]
        print(f"STATS_DEBUG: Precisión P1 (últimas 24h): {precision_P1_val:.2f}%")
        if stats_P0 is not None:
            precision_P0_val = stats_P0["precision"]
            print(f"STATS_DEBUG: Precisión P0 (anteriores 24h): {precision_P0_val:.2f}%")
            trend24h = round(precision_P1_val - precision_P0_val, 1)
        else:
            print("STATS_DEBUG: No hay datos en P0 para comparar tendencia. Trend se queda en 0.0.")
            # trend24h se queda en 0.0
    else:
        print("STATS_DEBUG: No hay datos en P1 (últimas 24h) para calcular tendencia. Trend se queda en 0.0.")
        # trend24h se queda en 0.0

    print(f"STATS_DEBUG: Trend24h calculado final: {trend24h}")
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
