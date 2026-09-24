import pytest
from fastapi.testclient import TestClient

from main import app


@pytest.fixture
def client():
    with TestClient(app) as test_client:
        yield test_client


def test_lost_and_found_workflow(client):
    created = client.post(
        "/items",
        json={
            "title": "Blue water bottle",
            "description": "Reusable bottle with a silver lid",
            "category": "Accessories",
            "location": "Library second floor",
            "reported_by": "Aisha Khan",
            "status": "Lost",
        },
    )
    assert created.status_code == 201
    item_id = created.json()["id"]

    assert client.get("/items").status_code == 200
    assert client.get(f"/items/{item_id}").json()["title"] == "Blue water bottle"
    assert client.get("/items/status/Lost").json()[0]["id"] == item_id
    assert client.get("/items/category/Accessories").json()[0]["id"] == item_id

    updated = client.put(f"/items/{item_id}", json={"status": "Found"})
    assert updated.status_code == 200
    assert updated.json()["status"] == "Found"

    assert client.get("/items/status/Found").json()[0]["id"] == item_id
    assert client.delete(f"/items/{item_id}").status_code == 204
    assert client.get(f"/items/{item_id}").status_code == 404


def test_validation_and_missing_item_errors(client):
    invalid = client.post(
        "/items",
        json={
            "title": "",
            "description": "short",
            "category": "Documents",
            "location": "Admin block",
            "reported_by": "Sam Lee",
            "status": "Missing",
        },
    )
    assert invalid.status_code == 422
    assert client.get("/items/999999").status_code == 404
