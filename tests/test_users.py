# Tests for users endpoints

def test_list_users(client, sample_user):
    """GET /users returns list of users"""
    response = client.get("/users")
    assert response.status_code == 200
    assert isinstance(response.json, list)


def test_get_user(client, sample_user):
    """GET /users/<id> returns user"""
    response = client.get(f"/users/{sample_user.id}")
    assert response.status_code == 200
    assert response.json["username"] == sample_user.username


def test_get_user_not_found(client):
    """GET /users/<id> returns 404 for missing user"""
    response = client.get("/users/99999")
    assert response.status_code == 404


def test_create_user(client):
    """POST /users creates a user"""
    import uuid
    username = f"test_{uuid.uuid4().hex[:8]}"
    response = client.post("/users", json={"username": username, "email": f"{username}@test.com"})
    assert response.status_code == 201
    assert response.json["username"] == username


def test_create_user_missing_fields(client):
    """POST /users with missing fields returns 400"""
    response = client.post("/users", json={"username": "test"})
    assert response.status_code == 400


def test_update_user(client, sample_user):
    """PUT /users/<id> updates user"""
    response = client.put(f"/users/{sample_user.id}", json={"username": "updated_name"})
    assert response.status_code == 200
    assert response.json["username"] == "updated_name"


def test_update_user_not_found(client):
    """PUT /users/<id> returns 404 for missing user"""
    response = client.put("/users/99999", json={"username": "test"})
    assert response.status_code == 404
