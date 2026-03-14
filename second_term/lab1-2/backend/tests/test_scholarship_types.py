from tests.utils import auth_headers


def test_list_scholarship_types(client):
    response = client.get("/scholarship-types")
    assert response.status_code == 200
    assert isinstance(response.json(), list)


def test_list_scholarship_types_with_filter_and_sort(client):
    headers = auth_headers(client)

    client.post("/scholarship-types", json={"name": "Base", "base_amount": 1000}, headers=headers)
    client.post("/scholarship-types", json={"name": "Social", "base_amount": 1500}, headers=headers)

    response = client.get("/scholarship-types?name=Base&sort_by=name&sort_dir=asc&limit=10&offset=0")
    assert response.status_code == 200
    data = response.json()
    assert len(data) == 1
    assert data[0]["name"] == "Base"


def test_get_scholarship_type(client):
    headers = auth_headers(client)

    created = client.post(
        "/scholarship-types",
        json={"name": "Base", "base_amount": 1000},
        headers=headers,
    )
    st = created.json()

    response = client.get(f"/scholarship-types/{st['id']}")
    assert response.status_code == 200
    assert response.json()["id"] == st["id"]


def test_get_scholarship_type_not_found(client):
    response = client.get("/scholarship-types/999")
    assert response.status_code == 404


def test_create_scholarship_type_requires_auth(client):
    response = client.post(
        "/scholarship-types",
        json={"name": "Base", "base_amount": 1000},
    )
    assert response.status_code == 401


def test_create_scholarship_type(client):
    response = client.post(
        "/scholarship-types",
        json={"name": "Base", "base_amount": 1000},
        headers=auth_headers(client),
    )
    assert response.status_code == 201
    body = response.json()
    assert body["name"] == "Base"
    assert float(body["base_amount"]) == 1000.0


def test_create_scholarship_type_conflict(client):
    headers = auth_headers(client)

    client.post(
        "/scholarship-types",
        json={"name": "Base", "base_amount": 1000},
        headers=headers,
    )

    response = client.post(
        "/scholarship-types",
        json={"name": "Base", "base_amount": 2000},
        headers=headers,
    )
    assert response.status_code == 409


def test_update_scholarship_type(client):
    headers = auth_headers(client)

    obj = client.post(
        "/scholarship-types",
        json={"name": "Old", "base_amount": 1000},
        headers=headers,
    ).json()

    response = client.put(
        f"/scholarship-types/{obj['id']}",
        json={"name": "New", "base_amount": 2000},
        headers=headers,
    )

    assert response.status_code == 200
    assert response.json()["name"] == "New"
    assert float(response.json()["base_amount"]) == 2000.0


def test_update_scholarship_type_not_found(client):
    response = client.put(
        "/scholarship-types/999",
        json={"name": "New", "base_amount": 2000},
        headers=auth_headers(client),
    )
    assert response.status_code == 404


def test_delete_scholarship_type(client):
    headers = auth_headers(client)

    obj = client.post(
        "/scholarship-types",
        json={"name": "Temp", "base_amount": 1000},
        headers=headers,
    ).json()

    response = client.delete(
        f"/scholarship-types/{obj['id']}",
        headers=headers,
    )
    assert response.status_code == 204


def test_delete_scholarship_type_not_found(client):
    response = client.delete(
        "/scholarship-types/999",
        headers=auth_headers(client),
    )
    assert response.status_code == 404
