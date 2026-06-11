STUDENT_PAYLOAD = {
    "name": "Ali Hassan",
    "email": "ali@example.com",
    "course": "DevOps Fundamentals",
}


def test_create_student_returns_201(client):
    response = client.post("/students", json=STUDENT_PAYLOAD)
    assert response.status_code == 201


def test_create_student_returns_id(client):
    data = client.post("/students", json=STUDENT_PAYLOAD).json()
    assert "id" in data
    assert data["id"] > 0


def test_create_student_persists_to_get(client):
    client.post("/students", json=STUDENT_PAYLOAD)
    students = client.get("/students").json()
    assert len(students) == 1
    assert students[0]["email"] == STUDENT_PAYLOAD["email"]


def test_get_student_by_id(client):
    created = client.post("/students", json=STUDENT_PAYLOAD).json()
    student_id = created["id"]
    response = client.get(f"/students/{student_id}")
    assert response.status_code == 200
    assert response.json()["name"] == STUDENT_PAYLOAD["name"]


def test_get_student_not_found(client):
    response = client.get("/students/9999")
    assert response.status_code == 404


def test_list_students_empty(client):
    response = client.get("/students")
    assert response.status_code == 200
    assert response.json() == []


def test_create_multiple_students(client):
    for i in range(3):
        client.post(
            "/students",
            json={"name": f"Student {i}", "email": f"s{i}@test.com", "course": "CS"},
        )
    assert len(client.get("/students").json()) == 3
