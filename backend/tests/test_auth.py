import pytest
from httpx import AsyncClient


@pytest.mark.asyncio
async def test_register(client: AsyncClient):
    response = await client.post("/api/v1/auth/register", json={
        "email": "test@example.com",
        "password": "sifre1234",
        "full_name": "Test Kullanici",
    })
    assert response.status_code == 201
    data = response.json()
    assert data["status"] == "success"
    assert data["data"]["email"] == "test@example.com"
    assert "id" in data["data"]


@pytest.mark.asyncio
async def test_register_duplicate_email(client: AsyncClient):
    payload = {"email": "ayni@example.com", "password": "sifre1234"}
    await client.post("/api/v1/auth/register", json=payload)
    response = await client.post("/api/v1/auth/register", json=payload)
    assert response.status_code == 409


@pytest.mark.asyncio
async def test_login(client: AsyncClient):
    await client.post("/api/v1/auth/register", json={
        "email": "login@example.com",
        "password": "sifre1234",
    })
    response = await client.post("/api/v1/auth/login", json={
        "email": "login@example.com",
        "password": "sifre1234",
    })
    assert response.status_code == 200
    data = response.json()
    assert "access_token" in data["data"]
    assert "refresh_token" in data["data"]


@pytest.mark.asyncio
async def test_login_wrong_password(client: AsyncClient):
    await client.post("/api/v1/auth/register", json={
        "email": "wrong@example.com",
        "password": "sifre1234",
    })
    response = await client.post("/api/v1/auth/login", json={
        "email": "wrong@example.com",
        "password": "yanlis_sifre",
    })
    assert response.status_code == 401


@pytest.mark.asyncio
async def test_me(client: AsyncClient):
    await client.post("/api/v1/auth/register", json={
        "email": "me@example.com",
        "password": "sifre1234",
        "full_name": "Ben",
    })
    login = await client.post("/api/v1/auth/login", json={
        "email": "me@example.com",
        "password": "sifre1234",
    })
    token = login.json()["data"]["access_token"]

    response = await client.get("/api/v1/auth/me", headers={"Authorization": f"Bearer {token}"})
    assert response.status_code == 200
    assert response.json()["data"]["email"] == "me@example.com"


@pytest.mark.asyncio
async def test_refresh_token(client: AsyncClient):
    await client.post("/api/v1/auth/register", json={
        "email": "refresh@example.com",
        "password": "sifre1234",
    })
    login = await client.post("/api/v1/auth/login", json={
        "email": "refresh@example.com",
        "password": "sifre1234",
    })
    refresh_token = login.json()["data"]["refresh_token"]

    response = await client.post("/api/v1/auth/refresh", json={"refresh_token": refresh_token})
    assert response.status_code == 200
    assert "access_token" in response.json()["data"]
