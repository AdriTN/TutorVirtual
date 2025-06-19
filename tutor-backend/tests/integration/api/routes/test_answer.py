import pytest

import src.api.routes.answer as answer_module

# ── helpers --------------------------------------------------------------------
def insert_exercise(db, **kwargs):
    """Crea un Exercise mínimo en la BBDD de pruebas."""
    from src.models import Exercise
    defaults = dict(
        statement="¿Cuánto es 2+2?",
        answer="4",
        difficulty="fácil",
        type="respuesta corta",
        theme_id=1,
    )
    defaults.update(kwargs)
    ej = Exercise(**defaults)
    db.add(ej)
    db.commit()
    db.refresh(ej)
    return ej

# ── casos ----------------------------------------------------------------------
def test_exercise_not_found(client):
    body = {"ejercicio_id": 999, "answer": "X"}
    resp = client.post("/api/answer", json=body)
    assert resp.status_code == 404
    assert resp.json()["detail"] == "Ejercicio no encontrado"


@pytest.mark.parametrize("service_return,expected", [
    (True,  True),
    (False, False),
])
def test_answer_created(client, db_session, monkeypatch,
                        service_return, expected):
    # 1) Creamos un ejercicio válido
    ej = insert_exercise(db_session)

    # 2) Mockeamos register_user_answer para controlar la lógica de negocio
    monkeypatch.setattr(
        answer_module,
        "register_user_answer",
        lambda *args, **kw: service_return,
    )

    body = {"ejercicio_id": ej.id, "answer": "4", "tiempo_seg": 8}
    resp = client.post("/api/answer", json=body)

    assert resp.status_code == 201
    assert resp.json() == {"correcto": expected}
