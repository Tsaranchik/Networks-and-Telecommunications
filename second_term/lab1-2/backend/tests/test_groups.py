from tests.utils import auth_headers


def test_groups_requires_auth(client):
    assert client.get("/groups").status_code == 401


def test_get_group_requires_auth(client):
    assert client.get("/groups/1").status_code == 401


def test_list_create_get_update_delete_group(client):
    headers = auth_headers(client)

    uni = client.post("/universities", json={"name": "Uni"}, headers=headers).json()

    create = client.post(
        "/groups",
        json={
            "name": "IKBO-01-23",
            "course": 1,
            "admission_year": 2023,
            "university_id": uni["id"],
            "curator_full_name": "Ivanov Ivan",
            "curator_photo": None,
        },
        headers=headers,
    )
    assert create.status_code == 201
    group = create.json()

    list_resp = client.get("/groups", headers=headers)
    assert list_resp.status_code == 200
    assert len(list_resp.json()) == 1

    list_filtered = client.get(f"/groups?university_id={uni['id']}", headers=headers)
    assert list_filtered.status_code == 200
    assert len(list_filtered.json()) == 1

    get_one = client.get(f"/groups/{group['id']}", headers=headers)
    assert get_one.status_code == 200
    assert get_one.json()["id"] == group["id"]

    update = client.put(
        f"/groups/{group['id']}",
        json={
            "name": "IKBO-02-23",
            "course": 2,
            "admission_year": 2023,
            "university_id": uni["id"],
            "curator_full_name": "Petrov Petr",
            "curator_photo": "photo.jpg",
        },
        headers=headers,
    )
    assert update.status_code == 200
    assert update.json()["name"] == "IKBO-02-23"

    delete = client.delete(f"/groups/{group['id']}", headers=headers)
    assert delete.status_code == 204


def test_get_group_not_found(client):
    response = client.get("/groups/999", headers=auth_headers(client))
    assert response.status_code == 404


def test_create_group_university_not_found(client):
    response = client.post(
        "/groups",
        json={
            "name": "IKBO",
            "course": 1,
            "admission_year": 2023,
            "university_id": 999,
            "curator_full_name": "Ivanov Ivan",
            "curator_photo": None,
        },
        headers=auth_headers(client),
    )
    assert response.status_code == 404


def test_create_group_conflict(client):
    headers = auth_headers(client)

    uni = client.post("/universities", json={"name": "Uni"}, headers=headers).json()

    payload = {
        "name": "IKBO",
        "course": 1,
        "admission_year": 2023,
        "university_id": uni["id"],
        "curator_full_name": "Ivanov Ivan",
        "curator_photo": None,
    }

    client.post("/groups", json=payload, headers=headers)
    response = client.post("/groups", json=payload, headers=headers)

    assert response.status_code == 409


def test_update_group_not_found(client):
    response = client.put(
        "/groups/999",
        json={"name": "IKBO-NEW"},
        headers=auth_headers(client),
    )
    assert response.status_code == 404


def test_delete_group_not_found(client):
    response = client.delete("/groups/999", headers=auth_headers(client))
    assert response.status_code == 404
