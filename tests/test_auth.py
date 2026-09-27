# from fastapi.testclient import TestClient
from httpx import AsyncClient


async def test_login_success(client: AsyncClient)-> None:
    await client.post("/api/v1/users/",
                json={
                    "name": "Auth Test",
                    "email": "authtest@example.com",
                    "password": "testpass123",
                    "role": "job_seeker",
                },
                )

    response =await client.post(
        "/api/v1/auth/login", data={"username": "authtest@example.com","password": "testpass123"},
    )

    assert response.status_code == 200
    data = response.json()
    assert "access_token" in data
    assert data["token_type"] == "bearer"



async def test_login_wrong_password_fails(client: AsyncClient)->None:
    await client.post(
        "/api/v1/users/",json={
            "name": "Auth Test",
            "email": "wrongpass@example.com",
            "password": "correctpassword",
            "role": "job_seeker",
        },
    )

    response = await client.post(
        "/api/v1/auth/login",
        data={"username": "wrongpass@example.com", "password": "incorrectpassword"},
    )

    assert response.status_code == 401


async def test_get_me_requires_token(client: AsyncClient)-> None:
        response = await client.get("/api/v1/users/me")
        assert response.status_code == 401


async def test_get_me_with_valid_token(client: AsyncClient)-> None:
     await client.post(
          "/api/v1/users/",
          json={
               "name": "Me Test",
               "email": "metest@example.com",
               "password": "testpass123",
               "role": "job_seeker",
          },
     )

     login_response =await client.post(
          "/api/v1/auth/login",
          data={"username": "metest@example.com", "password":"testpass123"},
     )
     token = login_response.json()["access_token"]

     response =await client.get(
          "/api/v1/users/me",
          headers={"Authorization": f"Bearer {token}"},
     )

     assert response.status_code == 200
     assert response.json()["email"] == "metest@example.com"
