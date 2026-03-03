import pytest


@pytest.mark.asyncio
async def test_root_returns_200(async_client):
    # Arrange
    # No setup required.

    # Act
    response = await async_client.get("/")

    # Assert
    assert response.status_code == 200
    assert "message" in response.json()


@pytest.mark.asyncio
async def test_get_all_posts_returns_200(async_client):
    # Arrange
    # No setup required.

    # Act
    response = await async_client.get("/posts/")

    # Assert
    assert response.status_code == 200
    assert isinstance(response.json(), list)


@pytest.mark.asyncio
async def test_get_post_returns_404_when_missing(async_client):
    # Arrange
    missing_post_id = 9999

    # Act
    response = await async_client.get(f"/posts/{missing_post_id}")

    # Assert
    assert response.status_code == 404
    assert response.json()["detail"] == "Post not found"


@pytest.mark.asyncio
async def test_create_post_returns_201_with_auth(async_client, auth_headers):
    # Arrange
    payload = {"title": "First Post", "content": "Post body"}

    # Act
    response = await async_client.post("/posts/", json=payload, headers=auth_headers)
    data = response.json()

    # Assert
    assert response.status_code == 201
    assert data["title"] == "First Post"
    assert data["content"] == "Post body"
    assert data["author_id"] == 1


@pytest.mark.asyncio
async def test_create_post_returns_401_without_auth(async_client_no_auth_override):
    # Arrange
    payload = {"title": "Unauthorized Post", "content": "No token used"}

    # Act
    response = await async_client_no_auth_override.post("/posts/", json=payload)

    # Assert
    assert response.status_code == 401


@pytest.mark.asyncio
async def test_create_post_returns_422_for_invalid_payload(async_client, auth_headers):
    # Arrange
    payload = {"title": "Only title"}  # missing content

    # Act
    response = await async_client.post("/posts/", json=payload, headers=auth_headers)

    # Assert
    assert response.status_code == 422


@pytest.mark.asyncio
async def test_update_post_returns_200(async_client, auth_headers):
    # Arrange
    create_payload = {"title": "Before", "content": "Before content"}
    created = await async_client.post("/posts/", json=create_payload, headers=auth_headers)
    post_id = created.json()["id"]
    update_payload = {"title": "After", "content": "After content"}

    # Act
    response = await async_client.put(
        f"/posts/{post_id}",
        json=update_payload,
        headers=auth_headers,
    )
    data = response.json()

    # Assert
    assert response.status_code == 200
    assert data["title"] == "After"
    assert data["content"] == "After content"


@pytest.mark.asyncio
async def test_update_post_returns_404_when_missing(async_client, auth_headers):
    # Arrange
    payload = {"title": "Nope", "content": "Nope"}

    # Act
    response = await async_client.put("/posts/9999", json=payload, headers=auth_headers)

    # Assert
    assert response.status_code == 404


@pytest.mark.asyncio
async def test_delete_post_returns_204(async_client, auth_headers):
    # Arrange
    create_payload = {"title": "Delete me", "content": "Delete body"}
    created = await async_client.post("/posts/", json=create_payload, headers=auth_headers)
    post_id = created.json()["id"]

    # Act
    response = await async_client.delete(f"/posts/{post_id}", headers=auth_headers)

    # Assert
    assert response.status_code == 204
    assert response.text == ""
