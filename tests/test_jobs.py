# from fastapi.testclient import TestClient
from httpx import AsyncClient

async def register_and_login(client: AsyncClient,email: str,password: str, role: str)-> str:
    await client.post("/api/v1/users/",
                json={"name": "Test User", "email": email, "password": password, "role": role},)
    login_response =await client.post(
        "/api/v1/auth/login",
        data={"username": email,"password": password},
    )
    return login_response.json()["access_token"]


async def test_employer_can_create_job(client: AsyncClient)->None:
    token =await register_and_login(client,"employer1@example.com","testpass123","employer")

    response = await client.post(
        "/api/v1/jobs/",
        json={
            "title": "Backend Developer",
            "company": "Testco",
            "location": "remote",
            "description": "Build things",
        },
        headers={"Authorization": f"Bearer {token}"},
    )

    assert response.status_code == 201
    assert response.json()["title"] == "Backend Developer"


async def test_job_seeker_cannot_create_job(client: AsyncClient)-> None:
    token = await register_and_login(client,"seeker1@example.com","testpass123","job_seeker")

    response = await client.post("/api/v1/jobs/",
                    json={
                        "title": "Backend developer",
                        "company": "Testco",
                        "location": "remote",
                        "description": "Build things",
                           },
                           headers={"Authorization": f"Bearer {token}"},
                           )
    assert response.status_code == 403


async def test_non_owner_cannot_delete_job(client: AsyncClient)-> None:
    owner_token =await register_and_login(client,"owner@example.com","testpass123","employer")
    create_response =await client.post(
        "/api/v1/jobs/",
        json={
            "title": "Frontend Developer",
            "company": "TestCo",
            "location": "Remote",
            "description": "Build UI",
        },
        headers={
            "Authorization": f"Bearer {owner_token}"
        },
    )

    job_id = create_response.json()["id"]

    other_token = await register_and_login(client, "other@example.com", "testpass123", "employer")
    delete_response =await client.delete(
        f"/api/v1/jobs/{job_id}",
        headers={"Authorization": f"Bearer {other_token}"},
    )

    assert delete_response.status_code == 403


async def test_owner_can_delete_job(client: AsyncClient)->None:
    token = await register_and_login(client,"realowner@example.com","testpass123","employer")
    create_response = await client.post(
        "/api/v1/jobs/",
        json={
            "title": "Full Stack Developer",
            "company": "TestCo",
            "location": "Remote",
            "description": "Build everything",

        },
        headers={"Authorization": f"Bearer {token}"},
    )
    job_id = create_response.json()["id"]

    delete_response =await client.delete(
        f"/api/v1/jobs/{job_id}",
        headers={"Authorization": f"Bearer {token}"},
    )

    assert delete_response.status_code == 204


