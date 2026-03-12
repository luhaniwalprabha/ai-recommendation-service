def test_submit_feedback(client):
    response = client.post("/v1/feedback?user_id=1&product_id=1&action=like")
    assert response.status_code == 200
    assert response.json()["status"] == "feedback recorded"
    assert response.json()["cache_invalidated"] is True