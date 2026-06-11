def test_health_returns_200(client):
    response = client.get("/health")
    assert response.status_code == 200


def test_health_has_status_ok(client):
    data = client.get("/health").json()
    assert data["status"] == "ok"


def test_health_has_student_field(client):
    data = client.get("/health").json()
    assert "student" in data
    assert data["student"] != ""


def test_health_has_db_field(client):
    data = client.get("/health").json()
    assert "db" in data
