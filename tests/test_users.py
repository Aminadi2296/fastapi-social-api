import pytest
from jose import jwt
from config import settings

def test_create_user(client):
    response = client.post("/users", json={
        "email": "testuser@test.com",
        "password": "password123"
    })
    assert response.status_code == 201
    assert response.json()["email"] == "testuser@test.com"
    assert "password" not in response.json()  # never expose password

def test_login(client):
    # First create a user
    client.post("/users", json={
        "email": "testuser@test.com",
        "password": "password123"
    })
    # Then login
    response = client.post("/login", data={
        "username": "testuser@test.com",
        "password": "password123"
    })
    assert response.status_code == 200
    token_data = response.json()
    assert "access_token" in token_data
    assert token_data["token_type"] == "bearer"

def test_login_wrong_password(client):
    client.post("/users", json={
        "email": "testuser@test.com",
        "password": "password123"
    })
    response = client.post("/login", data={
        "username": "testuser@test.com",
        "password": "wrongpassword"
    })
    assert response.status_code == 403

def test_login_wrong_email(client):
    response = client.post("/login", data={
        "username": "nobody@test.com",
        "password": "password123"
    })
    assert response.status_code == 403