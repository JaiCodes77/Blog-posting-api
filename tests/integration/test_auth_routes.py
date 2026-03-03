import pytest


@pytest.mark.asyncio
async def test_register_returns_201(async_client):
    # Arrange
    payload = {
        "username": "register-user",
        "email": "register@example.com",
        "password": "strong-password",
    }

    # Act
    response = await async_client.post("/auth/register", json=payload)
    data = response.json()

    # Assert
    assert response.status_code == 201
    assert data["username"] == "register-user"
    assert data["email"] == "register@example.com"
    assert "id" in data


@pytest.mark.asyncio
async def test_register_returns_422_for_invalid_payload(async_client):
    # Arrange
    payload = {
        "username": "bad-user",
        "password": "missing-email",
    }

    # Act
    response = await async_client.post("/auth/register", json=payload)

    # Assert
    assert response.status_code == 422


@pytest.mark.asyncio
async def test_login_returns_200_and_token(async_client):
    # Arrange
    register_payload = {
        "username": "login-user",
        "email": "login@example.com",
        "password": "plain-password",
    }
    await async_client.post("/auth/register", json=register_payload)

    # Act
    response = await async_client.post(
        "/auth/login",
        data={"username": "login-user", "password": "plain-password"},
    )
    data = response.json()

    # Assert
    assert response.status_code == 200
    assert "access_token" in data
    assert data["token_type"] == "bearer"


@pytest.mark.asyncio
async def test_login_returns_401_for_invalid_credentials(async_client):
    # Arrange
    register_payload = {
        "username": "invalid-login-user",
        "email": "invalid-login@example.com",
        "password": "correct-password",
    }
    await async_client.post("/auth/register", json=register_payload)

    # Act
    response = await async_client.post(
        "/auth/login",
        data={"username": "invalid-login-user", "password": "wrong-password"},
    )

    # Assert
    assert response.status_code == 401
    assert response.json()["detail"] == "Invalid credentials"
