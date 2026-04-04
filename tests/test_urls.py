# Unit tests for URL shortener

def test_health(client):
    """Health endpoint returns 200 OK"""
    response = client.get("/health")
    assert response.status_code == 200
    assert response.json["status"] == "ok"


def test_shorten_missing_url(client):
    """POST /shorten without url returns 400"""
    response = client.post("/shorten", json={"user_id": 1})
    assert response.status_code == 400
    assert "url" in response.json["error"]


def test_shorten_missing_user_id(client):
    """POST /shorten without user_id returns 400"""
    response = client.post("/shorten", json={"url": "https://example.com"})
    assert response.status_code == 400
    assert "user_id" in response.json["error"]


def test_shorten_invalid_user(client):
    """POST /shorten with non-existent user returns 404"""
    response = client.post("/shorten", json={"url": "https://example.com", "user_id": 99999})
    assert response.status_code == 404


def test_shorten_success(client, sample_user):
    """POST /shorten creates a short URL"""
    response = client.post("/shorten", json={"url": "https://example.com", "user_id": sample_user.id})
    assert response.status_code == 201
    assert "short_code" in response.json
    assert "short_url" in response.json


def test_redirect_not_found(client):
    """GET /<invalid_code> returns 404"""
    response = client.get("/nonexistent123")
    assert response.status_code == 404


def test_redirect_success(client, sample_user):
    """GET /<short_code> redirects to original URL"""
    # Create a URL first
    create_resp = client.post("/shorten", json={"url": "https://example.com", "user_id": sample_user.id})
    short_code = create_resp.json["short_code"]
    
    response = client.get(f"/{short_code}")
    assert response.status_code == 302
    assert response.headers["Location"] == "https://example.com"


def test_get_url_details(client, sample_user):
    """GET /urls/<id> returns URL details"""
    create_resp = client.post("/shorten", json={"url": "https://example.com", "user_id": sample_user.id})
    short_code = create_resp.json["short_code"]
    
    # Get the URL id by looking it up
    from app.models import Url
    url = Url.get(Url.short_code == short_code)
    
    response = client.get(f"/urls/{url.id}")
    assert response.status_code == 200
    assert response.json["original_url"] == "https://example.com"


def test_get_url_stats(client, sample_user):
    """GET /urls/<short_code>/stats returns click count"""
    create_resp = client.post("/shorten", json={"url": "https://example.com", "user_id": sample_user.id})
    short_code = create_resp.json["short_code"]
    
    response = client.get(f"/urls/{short_code}/stats")
    assert response.status_code == 200
    assert response.json["clicks"] == 0
    
    # Click the link
    client.get(f"/{short_code}")
    
    response = client.get(f"/urls/{short_code}/stats")
    assert response.json["clicks"] == 1
