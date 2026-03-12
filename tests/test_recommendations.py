def test_get_recommendations_empty_user(client):
    response = client.get("/v1/recommendations?user_id=999")
    assert response.status_code == 200
    data = response.json()
    assert "recommendations" in data

def test_post_recommendations_triggers_generation(client):
    response = client.post("/v1/recommendations?user_id=1")
    assert response.status_code == 200
    assert response.json()["source"] in ["cache", "stale", "scheduled"]