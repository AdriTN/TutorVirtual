"""
Tests para el router de usuarios:   /api/users/*
"""
from starlette.status import (
    HTTP_200_OK,
    HTTP_204_NO_CONTENT,
    HTTP_404_NOT_FOUND,
)
from app.models import User
from app.core.security import hash_password


def _insert_user(db, *, uname, email, is_admin=False):
    u = User(username=uname, email=email, password=hash_password("x"), is_admin=is_admin)
    db.add(u)
    db.commit()
    db.refresh(u)
    return u.id


# ───────── GET /api/users/me ─────────────────────────────────────────
def test_me_ok(client, db_session):
    _insert_user(db_session, uname="alice", email="a@x.com")  # id=1 (fake_user)
    r = client.get("/api/users/me")

    assert r.status_code == HTTP_200_OK
    assert r.json()["username"] == "alice"


def test_me_not_found_returns_404(client):
    # No existe id=1
    r = client.get("/api/users/me")
    assert r.status_code == HTTP_404_NOT_FOUND


# ───────── GET /api/users/all ────────────────────────────────────────
def test_list_users(client, db_session):
    _insert_user(db_session, uname="user1", email="u1@x.com")
    _insert_user(db_session, uname="user2", email="u2@x.com", is_admin=True)

    r = client.get("/api/users/all")

    assert r.status_code == HTTP_200_OK
    assert {u["username"] for u in r.json()} == {"user1", "user2"}


# ───────── DELETE /api/users/{id} ────────────────────────────────────
def test_delete_user_ok(client, db_session):
    uid = _insert_user(db_session, uname="victim", email="v@x.com")

    r = client.delete(f"/api/users/{uid}")

    assert r.status_code == HTTP_204_NO_CONTENT
    assert db_session.query(User).get(uid) is None


def test_delete_user_404(client):
    r = client.delete("/api/users/999")
    assert r.status_code == HTTP_404_NOT_FOUND


# ───────── POST /api/users/{id}/promote ──────────────────────────────
def test_promote_user_ok(client, db_session):
    uid = _insert_user(db_session, uname="bob", email="b@x.com")

    r = client.post(f"/api/users/{uid}/promote")

    assert r.status_code == HTTP_200_OK
    assert db_session.query(User).get(uid).is_admin is True


def test_promote_user_404(client):
    r = client.post("/api/users/999/promote")
    assert r.status_code == HTTP_404_NOT_FOUND
