from tests.utils import auth_headers


def test_list_universities(client):
    response = client.get("/universities")
    assert response.status_code == 200
    assert isinstance(response.json(), list)


def test_list_universities_with_filter(client):
    headers = auth_headers(client)

    client.post("/universities", json={"name": "MIT"}, headers=headers)
    client.post("/universities", json={"name": "MSU"}, headers=headers)

    response = client.get("/universities?name=MIT")
    assert response.status_code == 200
    data = response.json()
    assert len(data) == 1
    assert data[0]["name"] == "MIT"


def test_get_university(client):
    headers = auth_headers(client)

    created = client.post("/universities", json={"name": "Uni"}, headers=headers)
    uni = created.json()

    response = client.get(f"/universities/{uni['id']}")
    assert response.status_code == 200
    assert response.json()["id"] == uni["id"]


def test_get_university_not_found(client):
    assert client.get("/universities/999").status_code == 404


def test_create_university_requires_auth(client):
    response = client.post("/universities", json={"name": "Uni"})
    assert response.status_code == 401


def test_create_university(client):
    response = client.post(
        "/universities",
        json={"name": "Uni1"},
        headers=auth_headers(client),
    )
    assert response.status_code == 201
    assert response.json()["name"] == "Uni1"


def test_create_university_conflict(client):
    headers = auth_headers(client)

    client.post("/universities", json={"name": "Uni1"}, headers=headers)
    response = client.post("/universities", json={"name": "Uni1"}, headers=headers)

    assert response.status_code == 409


def test_update_university(client):
    headers = auth_headers(client)

    uni = client.post("/universities", json={"name": "Uni1"}, headers=headers).json()

    response = client.put(
        f"/universities/{uni['id']}",
        json={"name": "Uni2"},
        headers=headers,
    )
    assert response.status_code == 200
    assert response.json()["name"] == "Uni2"


def test_update_university_not_found(client):
    response = client.put(
        "/universities/999",
        json={"name": "Uni2"},
        headers=auth_headers(client),
    )
    assert response.status_code == 404


def test_delete_university(client):
    headers = auth_headers(client)

    uni = client.post("/universities", json={"name": "Uni1"}, headers=headers).json()

    response = client.delete(f"/universities/{uni['id']}", headers=headers)
    assert response.status_code == 204


def test_delete_university_not_found(client):
    response = client.delete("/universities/999", headers=auth_headers(client))
    assert response.status_code == 404
