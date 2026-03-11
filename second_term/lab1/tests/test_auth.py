from tests.utils import get_token


def test_login_success(client):
    response = client.post(
        "/auth/token",
        data={"username": "admin", "password": "admin"},
    )

    assert response.status_code == 200
    body = response.json()
    assert "access_token" in body
    assert body["token_type"] == "bearer"


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
