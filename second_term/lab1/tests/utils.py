def get_token(client):
    response = client.post(
        "/auth/token",
        data={"username": "admin", "password": "admin"},
    )
    assert response.status_code == 200, response.text
    return response.json()["access_token"]


def auth_headers(client):
    token = get_token(client)
    return {"Authorization": f"Bearer {token}"}
