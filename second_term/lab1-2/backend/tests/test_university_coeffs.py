from tests.utils import auth_headers


def test_list_university_coeffs(client):
    response = client.get("/university-coeffs")
    assert response.status_code == 200
    assert isinstance(response.json(), list)


def test_get_university_coeff_not_found(client):
    response = client.get("/university-coeffs/999")
    assert response.status_code == 404


def test_create_university_coeff_requires_auth(client):
    response = client.post(
        "/university-coeffs",
        json={"university_id": 1, "scholarship_type_id": 1, "coeff": 1.5},
    )
    assert response.status_code == 401


def test_create_get_list_update_delete_coeff(client):
    headers = auth_headers(client)

    uni = client.post("/universities", json={"name": "Uni"}, headers=headers).json()
    st = client.post(
        "/scholarship-types",
        json={"name": "Base", "base_amount": 1000},
        headers=headers,
    ).json()

    create = client.post(
        "/university-coeffs",
        json={
            "university_id": uni["id"],
            "scholarship_type_id": st["id"],
            "coeff": 1.5,
        },
        headers=headers,
    )
    assert create.status_code == 201
    coeff = create.json()

    get_one = client.get(f"/university-coeffs/{coeff['id']}")
    assert get_one.status_code == 200
    assert get_one.json()["id"] == coeff["id"]

    list_filtered = client.get(f"/university-coeffs?university_id={uni['id']}")
    assert list_filtered.status_code == 200
    assert len(list_filtered.json()) == 1

    update = client.put(
        f"/university-coeffs/{coeff['id']}",
        json={"coeff": 2.0},
        headers=headers,
    )
    assert update.status_code == 200
    assert float(update.json()["coeff"]) == 2.0

    delete = client.delete(f"/university-coeffs/{coeff['id']}", headers=headers)
    assert delete.status_code == 204


def test_create_university_coeff_conflict(client):
    headers = auth_headers(client)

    uni = client.post("/universities", json={"name": "Uni"}, headers=headers).json()
    st = client.post(
        "/scholarship-types",
        json={"name": "Base", "base_amount": 1000},
        headers=headers,
    ).json()

    payload = {
        "university_id": uni["id"],
        "scholarship_type_id": st["id"],
        "coeff": 1.5,
    }

    client.post("/university-coeffs", json=payload, headers=headers)
    response = client.post("/university-coeffs", json=payload, headers=headers)

    assert response.status_code == 409


def test_create_university_coeff_fk_errors(client):
    headers = auth_headers(client)

    st = client.post(
        "/scholarship-types",
        json={"name": "Base", "base_amount": 1000},
        headers=headers,
    ).json()

    response_university = client.post(
        "/university-coeffs",
        json={"university_id": 999, "scholarship_type_id": st["id"], "coeff": 1.5},
        headers=headers,
    )
    assert response_university.status_code == 404

    uni = client.post("/universities", json={"name": "Uni"}, headers=headers).json()

    response_type = client.post(
        "/university-coeffs",
        json={"university_id": uni["id"], "scholarship_type_id": 999, "coeff": 1.5},
        headers=headers,
    )
    assert response_type.status_code == 404


def test_update_university_coeff_not_found(client):
    response = client.put(
        "/university-coeffs/999",
        json={"coeff": 2.0},
        headers=auth_headers(client),
    )
    assert response.status_code == 404


def test_delete_university_coeff_not_found(client):
    response = client.delete(
        "/university-coeffs/999",
        headers=auth_headers(client),
    )
    assert response.status_code == 404
