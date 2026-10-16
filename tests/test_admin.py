from httpx import AsyncClient
from sqlalchemy import update
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.user import User, UserRole

PASSWORD = "testpass123"
JOB = {
    "title": "Backend Developer",
    "company": "TestCo",
    "location": "Remote",
    "description": "Build things",
}


async def register(client: AsyncClient, email: str, role: str) -> int:
    response = await client.post(
        "/api/v1/users/",
        json={"name": "Test User", "email": email, "password": PASSWORD, "role": role},
    )
    return response.json()["id"]


async def login(client: AsyncClient, email: str) -> dict[str, str]:
    response = await client.post(
        "/api/v1/auth/login", data={"username": email, "password": PASSWORD}
    )
    return {"Authorization": f"Bearer {response.json()['access_token']}"}


async def create_admin(client: AsyncClient, db_session: AsyncSession) -> dict[str, str]:
    email = "admin@example.com"
    await register(client, email, "job_seeker")
    await db_session.execute(
        update(User).where(User.email == email).values(role=UserRole.ADMIN)
    )
    await db_session.commit()
    return await login(client, email)


async def test_non_admins_are_blocked(client: AsyncClient) -> None:
    await register(client, "seeker@example.com", "job_seeker")
    seeker = await login(client, "seeker@example.com")

    assert (await client.get("/api/v1/admin/stats", headers=seeker)).status_code == 403
    assert (await client.get("/api/v1/admin/stats")).status_code == 401


async def test_admin_sees_correct_stats(client: AsyncClient, db_session: AsyncSession) -> None:
    admin = await create_admin(client, db_session)
    await register(client, "employer@example.com", "employer")
    await register(client, "seeker@example.com", "job_seeker")
    employer = await login(client, "employer@example.com")
    await client.post("/api/v1/jobs/", json=JOB, headers=employer)

    response = await client.get("/api/v1/admin/stats", headers=admin)

    assert response.status_code == 200
    assert response.json() == {
        "total_users": 3,
        "employers": 1,
        "job_seekers": 1,
        "total_jobs": 1,
        "open_jobs": 1,
        "total_applications": 0,
    }


async def test_admin_can_list_users_and_jobs(client: AsyncClient, db_session: AsyncSession) -> None:
    admin = await create_admin(client, db_session)
    await register(client, "employer@example.com", "employer")
    employer = await login(client, "employer@example.com")
    await client.post("/api/v1/jobs/", json=JOB, headers=employer)

    users = await client.get("/api/v1/admin/users", headers=admin)
    jobs = await client.get("/api/v1/admin/jobs", headers=admin)

    assert {user["email"] for user in users.json()} == {"admin@example.com", "employer@example.com"}
    assert len(jobs.json()) == 1


async def test_deleting_a_user_removes_their_jobs(client: AsyncClient, db_session: AsyncSession) -> None:
    admin = await create_admin(client, db_session)
    employer_id = await register(client, "employer@example.com", "employer")
    employer = await login(client, "employer@example.com")
    job_id = (await client.post("/api/v1/jobs/", json=JOB, headers=employer)).json()["id"]

    response = await client.delete(f"/api/v1/admin/users/{employer_id}", headers=admin)

    assert response.status_code == 204
    assert (await client.get(f"/api/v1/jobs/{job_id}")).status_code == 404


async def test_admin_cannot_delete_themselves(client: AsyncClient, db_session: AsyncSession) -> None:
    admin = await create_admin(client, db_session)
    me = (await client.get("/api/v1/users/me", headers=admin)).json()

    response = await client.delete(f"/api/v1/admin/users/{me['id']}", headers=admin)

    assert response.status_code == 400


async def test_admin_can_delete_any_job(client: AsyncClient, db_session: AsyncSession) -> None:
    admin = await create_admin(client, db_session)
    await register(client, "employer@example.com", "employer")
    employer = await login(client, "employer@example.com")
    job_id = (await client.post("/api/v1/jobs/", json=JOB, headers=employer)).json()["id"]

    response = await client.delete(f"/api/v1/admin/jobs/{job_id}", headers=admin)

    assert response.status_code == 204
    assert (await client.get(f"/api/v1/jobs/{job_id}")).status_code == 404


async def test_public_user_listing_is_gone(client: AsyncClient) -> None:
    await register(client, "seeker@example.com", "job_seeker")

    assert (await client.get("/api/v1/users/")).status_code == 405
    assert (await client.get("/api/v1/users/1")).status_code == 404