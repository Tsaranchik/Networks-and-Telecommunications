from datetime import datetime, timedelta, timezone

from jose import jwt

from app.core.auth import JWT_ALGORITHM, JWT_SECRET_KEY
from tests.utils import get_token


def test_login_success(client):
    response = client.post(
        "/auth/token",
        data={"username": "admin", "password": "admin"},
    )

    assert response.status_code == 200
    body = response.json()
    assert "access_token" in body
    assert "refresh_token" in body
    assert body["token_type"] == "bearer"
    assert body["user"]["username"] == "admin"


def test_register_and_profile_flow(client):
    register_response = client.post(
        "/auth/register",
        json={
            "username": "student1",
            "email": "student1@example.com",
            "last_name": "Иванов",
            "first_name": "Иван",
            "middle_name": "Иванович",
            "password": "password123",
        },
    )
    assert register_response.status_code == 201
    register_body = register_response.json()
    assert register_body["user"]["email"] == "student1@example.com"

    headers = {"Authorization": f"Bearer {register_body['access_token']}"}
    me_response = client.get("/auth/me", headers=headers)
    assert me_response.status_code == 200
    assert me_response.json()["full_name"] == "Иванов Иван Иванович"

    update_response = client.put(
        "/auth/me",
        json={
            "default_page_size": 50,
            "auto_refresh_seconds": 30,
            "default_language": "en",
        },
        headers=headers,
    )
    assert update_response.status_code == 200
    updated = update_response.json()
    assert updated["default_page_size"] == 50
    assert updated["auto_refresh_seconds"] == 30
    assert updated["default_language"] == "en"


def test_refresh_token_flow(client):
    login_response = client.post(
        "/auth/token",
        data={"username": "admin", "password": "admin"},
    )
    refresh_token = login_response.json()["refresh_token"]

    refresh_response = client.post("/auth/refresh", json={"refresh_token": refresh_token})
    assert refresh_response.status_code == 200
    assert "access_token" in refresh_response.json()
    assert "refresh_token" in refresh_response.json()


def test_change_password_invalidates_old_tokens(client):
    login_response = client.post(
        "/auth/token",
        data={"username": "admin", "password": "admin"},
    )
    old_access_token = login_response.json()["access_token"]
    headers = {"Authorization": f"Bearer {old_access_token}"}

    change_response = client.post(
        "/auth/change-password",
        json={"current_password": "admin", "new_password": "new-admin-password"},
        headers=headers,
    )
    assert change_response.status_code == 204

    me_response = client.get("/auth/me", headers=headers)
    assert me_response.status_code == 401
    assert me_response.json()["detail"]["code"] == "tokenRevoked"

    relogin_response = client.post(
        "/auth/token",
        data={"username": "admin", "password": "new-admin-password"},
    )
    assert relogin_response.status_code == 200


def test_expired_access_token_returns_token_expired_exception(client):
    expired_token = jwt.encode(
        {
            "sub": "admin",
            "type": "access",
            "ver": 0,
            "iat": datetime.now(timezone.utc) - timedelta(minutes=2),
            "exp": datetime.now(timezone.utc) - timedelta(minutes=1),
        },
        JWT_SECRET_KEY,
        algorithm=JWT_ALGORITHM,
    )

    response = client.get(
        "/students",
        headers={"Authorization": f"Bearer {expired_token}"},
    )

    assert response.status_code == 401
    assert response.json()["detail"]["code"] == "tokenExpiredException"


def test_students_requires_auth(client):
    response = client.get("/students")
    assert response.status_code == 401


def test_students_with_auth(client):
    token = get_token(client)

    response = client.get(
        "/students",
        headers={"Authorization": f"Bearer {token}"}
    )

    assert response.status_code == 200
