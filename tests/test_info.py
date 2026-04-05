def test_root_info(app_client):
    response = app_client.get("/")
    assert response.status_code == 200
    data = response.json()
    assert "created_by" in data
    assert "description" in data
    assert "version" in data
