# from fastapi.testclient import TestClient

from httpx import AsyncClient

async def test_register_user_success(client: AsyncClient)-> None:
    response = await client.post("/api/v1/users/",json={
        "name": "Test User",
        "email": "testuser@example.com",
        "password": "testpass123",
        "role": "job_seeker",

    },
    )

    assert response.status_code == 201
    data = response.json()
    assert data["email"] == "testuser@example.com"
    assert data["name"] == "Test User"
    assert "id" in data
    assert "hashed_password" not in data


async def test_register_duplicate_email_fails(client: AsyncClient)-> None:
    await client.post(
        "/api/v1/users/",
        json={
            "name": "First User",
            "email": "duplicate@example.com",
            "password": "testpass12345",
            "role": "job_seeker"
        },
    )

    response = await client.post(
        "/api/v1/users/",
        json={
            "name": "Second User",
            "email": "duplicate@example.com",
            "password": "testpass123",
            "role": "job_seeker"
        }

    )

    assert response.status_code == 400
    assert "already registered" in response.json()["detail"]