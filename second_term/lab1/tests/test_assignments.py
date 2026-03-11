from tests.utils import auth_headers


def prepare_assignment_data(client):
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

    student = client.post(
        "/students",
        json={
            "full_name": "Ivan Ivanov",
            "group_id": group["id"],
            "address": "Moscow",
        },
        headers=headers,
    ).json()

    st = client.post(
        "/scholarship-types",
        json={"name": "Base", "base_amount": 1000},
        headers=headers,
    ).json()

    client.post(
        "/university-coeffs",
        json={
            "university_id": uni["id"],
            "scholarship_type_id": st["id"],
            "coeff": 1.5,
        },
        headers=headers,
    )

    return headers, uni, group, student, st


def test_assignments_requires_auth(client):
    assert client.get("/scholarship-assignments").status_code == 401


def test_get_assignment_requires_auth(client):
    assert client.get("/scholarship-assignments/1").status_code == 401


def test_list_create_get_update_delete_assignment(client):
    headers, uni, group, student, st = prepare_assignment_data(client)

    create = client.post(
        "/scholarship-assignments",
        json={
            "student_id": student["id"],
            "semester": 1,
            "scholarship_type_id": st["id"],
        },
        headers=headers,
    )
    assert create.status_code == 201
    assignment = create.json()
    assert float(assignment["amount"]) == 1500.0

    list_resp = client.get("/scholarship-assignments", headers=headers)
    assert list_resp.status_code == 200
    assert len(list_resp.json()) == 1

    list_filtered = client.get(
        f"/scholarship-assignments?student_id={student['id']}&semester=1&scholarship_type_id={st['id']}",
        headers=headers,
    )
    assert list_filtered.status_code == 200
    assert len(list_filtered.json()) == 1

    get_one = client.get(f"/scholarship-assignments/{assignment['id']}", headers=headers)
    assert get_one.status_code == 200
    assert get_one.json()["id"] == assignment["id"]

    update = client.put(
        f"/scholarship-assignments/{assignment['id']}",
        json={
            "semester": 2,
            "scholarship_type_id": st["id"],
        },
        headers=headers,
    )
    assert update.status_code == 200
    assert update.json()["semester"] == 2

    delete = client.delete(f"/scholarship-assignments/{assignment['id']}", headers=headers)
    assert delete.status_code == 204


def test_get_assignment_not_found(client):
    response = client.get("/scholarship-assignments/999", headers=auth_headers(client))
    assert response.status_code == 404


def test_create_assignment_student_not_found(client):
    headers = auth_headers(client)

    st = client.post(
        "/scholarship-types",
        json={"name": "Base", "base_amount": 1000},
        headers=headers,
    ).json()

    response = client.post(
        "/scholarship-assignments",
        json={
            "student_id": 999,
            "semester": 1,
            "scholarship_type_id": st["id"],
        },
        headers=headers,
    )
    assert response.status_code == 404


def test_create_assignment_scholarship_type_not_found(client):
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
    student = client.post(
        "/students",
        json={
            "full_name": "Ivan Ivanov",
            "group_id": group["id"],
            "address": "Moscow",
        },
        headers=headers,
    ).json()

    response = client.post(
        "/scholarship-assignments",
        json={
            "student_id": student["id"],
            "semester": 1,
            "scholarship_type_id": 999,
        },
        headers=headers,
    )
    assert response.status_code == 404


def test_create_assignment_coeff_not_found(client):
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
    student = client.post(
        "/students",
        json={
            "full_name": "Ivan Ivanov",
            "group_id": group["id"],
            "address": "Moscow",
        },
        headers=headers,
    ).json()
    st = client.post(
        "/scholarship-types",
        json={"name": "Base", "base_amount": 1000},
        headers=headers,
    ).json()

    response = client.post(
        "/scholarship-assignments",
        json={
            "student_id": student["id"],
            "semester": 1,
            "scholarship_type_id": st["id"],
        },
        headers=headers,
    )
    assert response.status_code == 409


def test_create_assignment_conflict(client):
    headers, uni, group, student, st = prepare_assignment_data(client)

    payload = {
        "student_id": student["id"],
        "semester": 1,
        "scholarship_type_id": st["id"],
    }

    client.post("/scholarship-assignments", json=payload, headers=headers)
    response = client.post("/scholarship-assignments", json=payload, headers=headers)

    assert response.status_code == 409


def test_update_assignment_not_found(client):
    response = client.put(
        "/scholarship-assignments/999",
        json={"semester": 2},
        headers=auth_headers(client),
    )
    assert response.status_code == 404


def test_delete_assignment_not_found(client):
    response = client.delete(
        "/scholarship-assignments/999",
        headers=auth_headers(client),
    )
    assert response.status_code == 404
