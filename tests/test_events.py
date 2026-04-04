# Tests for events endpoints

def test_list_events(client):
    """GET /events returns list of events"""
    response = client.get("/events")
    assert response.status_code == 200
    assert isinstance(response.json, list)
