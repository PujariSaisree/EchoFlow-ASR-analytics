from fastapi.testclient import TestClient

from app.main import app

client = TestClient(app)


def test_health():
    response = client.get("/api/health")
    assert response.status_code == 200
    body = response.json()
    assert body["status"] == "ok"
    assert body["service"] == "EchoFlow"


def test_models():
    response = client.get("/api/models")
    assert response.status_code == 200
    body = response.json()
    assert "tiny" in body["models"]
    assert body["default"] == "tiny"


def test_dashboard_overview_structure():
    response = client.get("/api/dashboard/overview")
    assert response.status_code == 200
    body = response.json()
    assert "totals" in body
    assert "recent" in body
    assert "series" in body


def test_upload_rejects_invalid_type():
    response = client.post(
        "/api/recordings/upload",
        files={"file": ("notes.txt", b"not audio", "text/plain")},
    )
    assert response.status_code == 400
    assert "error" in response.json()


def test_evaluation_requires_reference():
    response = client.post("/api/evaluation/999999", json={"reference_transcript": ""})
    assert response.status_code in {404, 200}
    if response.status_code == 200:
        assert response.json()["message"] == "Reference transcript required for accuracy evaluation."
