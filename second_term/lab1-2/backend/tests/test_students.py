from tests.utils import auth_headers


def test_students_requires_auth(client):
    assert client.get("/students").status_code == 401


def test_get_student_requires_auth(client):
    assert client.get("/students/1").status_code == 401


def test_list_create_get_update_delete_student(client):
    headers = auth_headers(client)

    uni = client.post("/universities", json={"name": "Uni"}, headers=headers).json()
    group = client.post(
        "/groups",
        json={
            "name": "IKBO",
            "course": 1,
            "admission_year": 2023,
            "university_id": uni["id"],
            "curator_full_name": "Ivanov Ivan",
            "curator_photo": None,
        },
        headers=headers,
    ).json()

    create = client.post(
        "/students",
        json={
            "full_name": "Ivan Ivanov",
            "group_id": group["id"],
            "address": "Moscow",
        },
        headers=headers,
    )
    assert create.status_code == 201
    student = create.json()

    list_resp = client.get("/students", headers=headers)
    assert list_resp.status_code == 200
    assert len(list_resp.json()) == 1

    list_filtered = client.get("/students?full_name=Ivan&group_id=1", headers=headers)
    assert list_filtered.status_code == 200
    assert len(list_filtered.json()) == 1

    get_one = client.get(f"/students/{student['id']}", headers=headers)
    assert get_one.status_code == 200
    assert get_one.json()["id"] == student["id"]

    update = client.put(
        f"/students/{student['id']}",
        json={
            "full_name": "Petr Petrov",
            "group_id": group["id"],
            "address": "SPB",
        },
        headers=headers,
    )
    assert update.status_code == 200
    assert update.json()["full_name"] == "Petr Petrov"

    delete = client.delete(f"/students/{student['id']}", headers=headers)
    assert delete.status_code == 204


def test_get_student_not_found(client):
    response = client.get("/students/999", headers=auth_headers(client))
    assert response.status_code == 404


def test_create_student_group_not_found(client):
    response = client.post(
        "/students",
        json={
            "full_name": "Ivan Ivanov",
            "group_id": 999,
            "address": "Moscow",
        },
        headers=auth_headers(client),
    )
    assert response.status_code == 404


def test_update_student_not_found(client):
    response = client.put(
        "/students/999",
        json={"full_name": "New Name"},
        headers=auth_headers(client),
    )
    assert response.status_code == 404


def test_delete_student_not_found(client):
    response = client.delete("/students/999", headers=auth_headers(client))
    assert response.status_code == 404
