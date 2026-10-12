from httpx import AsyncClient

PASSWORD = "testpass123"
JOB = {
    "title": "Backend Developer",
    "company": "TestCo",
    "location": "Remote",
    "description": "Build things",
}


async def register_and_login(client: AsyncClient, email: str, role: str) -> dict[str, str]:
    await client.post(
        "/api/v1/users/",
        json={"name": "Test User", "email": email, "password": PASSWORD, "role": role},
    )
    response = await client.post(
        "/api/v1/auth/login", data={"username": email, "password": PASSWORD}
    )
    return {"Authorization": f"Bearer {response.json()['access_token']}"}


async def create_job(client: AsyncClient, headers: dict[str, str]) -> int:
    response = await client.post("/api/v1/jobs/", json=JOB, headers=headers)
    return response.json()["id"]


async def apply(client: AsyncClient, headers: dict[str, str], job_id: int):
    return await client.post(
        "/api/v1/applications/", json={"job_id": job_id}, headers=headers
    )


async def test_seeker_can_apply_and_response_includes_job(client: AsyncClient) -> None:
    employer = await register_and_login(client, "employer@example.com", "employer")
    seeker = await register_and_login(client, "seeker@example.com", "job_seeker")
    job_id = await create_job(client, employer)

    response = await apply(client, seeker, job_id)

    assert response.status_code == 201
    assert response.json()["job"]["title"] == "Backend Developer"


async def test_applying_twice_fails(client: AsyncClient) -> None:
    employer = await register_and_login(client, "employer@example.com", "employer")
    seeker = await register_and_login(client, "seeker@example.com", "job_seeker")
    job_id = await create_job(client, employer)

    await apply(client, seeker, job_id)
    response = await apply(client, seeker, job_id)

    assert response.status_code == 400


async def test_employer_cannot_apply(client: AsyncClient) -> None:
    employer = await register_and_login(client, "employer@example.com", "employer")
    job_id = await create_job(client, employer)

    response = await apply(client, employer, job_id)

    assert response.status_code == 403


async def test_owner_sees_applicants_without_password_data(client: AsyncClient) -> None:
    employer = await register_and_login(client, "employer@example.com", "employer")
    seeker = await register_and_login(client, "seeker@example.com", "job_seeker")
    job_id = await create_job(client, employer)
    await apply(client, seeker, job_id)

    response = await client.get(f"/api/v1/jobs/{job_id}/applications", headers=employer)

    assert response.status_code == 200
    data = response.json()
    assert len(data) == 1
    assert data[0]["applicant"]["email"] == "seeker@example.com"
    assert "hashed_password" not in response.text


async def test_non_owner_cannot_see_applicants(client: AsyncClient) -> None:
    employer = await register_and_login(client, "employer@example.com", "employer")
    other_employer = await register_and_login(client, "other@example.com", "employer")
    job_id = await create_job(client, employer)

    response = await client.get(f"/api/v1/jobs/{job_id}/applications", headers=other_employer)

    assert response.status_code == 403


async def test_owner_can_change_status_but_applicant_cannot(client: AsyncClient) -> None:
    employer = await register_and_login(client, "employer@example.com", "employer")
    seeker = await register_and_login(client, "seeker@example.com", "job_seeker")
    job_id = await create_job(client, employer)
    application_id = (await apply(client, seeker, job_id)).json()["id"]
    url = f"/api/v1/applications/{application_id}"

    by_applicant = await client.patch(url, json={"status": "accepted"}, headers=seeker)
    by_owner = await client.patch(url, json={"status": "accepted"}, headers=employer)

    assert by_applicant.status_code == 403
    assert by_owner.status_code == 200
    assert by_owner.json()["status"] == "accepted"


async def test_invalid_status_is_rejected(client: AsyncClient) -> None:
    employer = await register_and_login(client, "employer@example.com", "employer")
    seeker = await register_and_login(client, "seeker@example.com", "job_seeker")
    job_id = await create_job(client, employer)
    application_id = (await apply(client, seeker, job_id)).json()["id"]

    response = await client.patch(
        f"/api/v1/applications/{application_id}", json={"status": "banana"}, headers=employer
    )

    assert response.status_code == 422


async def test_stranger_cannot_read_application(client: AsyncClient) -> None:
    employer = await register_and_login(client, "employer@example.com", "employer")
    seeker = await register_and_login(client, "seeker@example.com", "job_seeker")
    stranger = await register_and_login(client, "stranger@example.com", "job_seeker")
    job_id = await create_job(client, employer)
    application_id = (await apply(client, seeker, job_id)).json()["id"]
    url = f"/api/v1/applications/{application_id}"

    assert (await client.get(url, headers=stranger)).status_code == 403
    assert (await client.get(url)).status_code == 401
    assert (await client.get(url, headers=seeker)).status_code == 200
    assert (await client.get(url, headers=employer)).status_code == 200


async def test_listing_all_applications_is_gone(client: AsyncClient) -> None:
    seeker = await register_and_login(client, "seeker@example.com", "job_seeker")

    response = await client.get("/api/v1/applications/", headers=seeker)

    assert response.status_code == 405


async def test_applicant_can_withdraw_but_owner_cannot_delete(client: AsyncClient) -> None:
    employer = await register_and_login(client, "employer@example.com", "employer")
    seeker = await register_and_login(client, "seeker@example.com", "job_seeker")
    job_id = await create_job(client, employer)
    application_id = (await apply(client, seeker, job_id)).json()["id"]
    url = f"/api/v1/applications/{application_id}"

    assert (await client.delete(url, headers=employer)).status_code == 403
    assert (await client.delete(url, headers=seeker)).status_code == 204