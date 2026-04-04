# Tests for error handling (graceful failure)

def test_404_returns_json(client):
    """404 errors return JSON, not HTML"""
    response = client.get("/nonexistent/route/here")
    assert response.status_code == 404
    assert response.content_type == "application/json"
    assert "error" in response.json


def test_405_returns_json(client):
    """405 errors return JSON, not HTML"""
    response = client.delete("/health")  # health only supports GET
    assert response.status_code == 405
    assert response.content_type == "application/json"
    assert "error" in response.json


def test_bad_json_returns_error(client):
    """Invalid JSON returns proper error"""
    response = client.post("/users", data="not json", content_type="application/json")
    assert response.status_code == 400


def test_invalid_url_format(client, sample_user):
    """POST /urls with invalid URL returns 400"""
    response = client.post("/urls", json={
        "user_id": sample_user.id,
        "original_url": "not-a-valid-url"
    })
    assert response.status_code == 400
    assert "error" in response.json
