import pytest
from fastapi import HTTPException
from fastapi.security import OAuth2PasswordRequestForm
from unittest.mock import MagicMock

import models
from routers.auth import login, register
from schemas import UserCreate


def test_register_creates_user_when_email_is_new(mocker):
    # Arrange
    db = MagicMock()
    db.query.return_value.filter.return_value.first.return_value = None
    user_data = UserCreate(username="alice", email="alice@example.com", password="plain")
    mocker.patch("routers.auth.hash_password", return_value="hashed-password")

    # Act
    created_user = register(user_data=user_data, db=db)

    # Assert
    assert created_user.username == "alice"
    assert created_user.email == "alice@example.com"
    assert created_user.hashed_password == "hashed-password"
    db.add.assert_called_once()
    db.commit.assert_called_once()
    db.refresh.assert_called_once()


def test_register_raises_400_when_email_exists():
    # Arrange
    db = MagicMock()
    db.query.return_value.filter.return_value.first.return_value = models.User(
        id=11, username="existing", email="existing@example.com", hashed_password="hashed"
    )
    user_data = UserCreate(
        username="new-user",
        email="existing@example.com",
        password="any-password",
    )

    # Act / Assert
    with pytest.raises(HTTPException) as exc:
        register(user_data=user_data, db=db)
    assert exc.value.status_code == 400
    assert exc.value.detail == "Email already registered"


def test_login_returns_token_for_valid_credentials(mocker):
    # Arrange
    db = MagicMock()
    db_user = models.User(
        id=1,
        username="alice",
        email="alice@example.com",
        hashed_password="stored-hash",
    )
    db.query.return_value.filter.return_value.first.return_value = db_user
    mocker.patch("routers.auth.verify_password", return_value=True)
    mocker.patch("routers.auth.create_access_token", return_value="signed-token")
    form_data = OAuth2PasswordRequestForm(
        username="alice",
        password="plain-password",
        scope="",
        client_id=None,
        client_secret=None,
    )

    # Act
    token = login(form_data=form_data, db=db)

    # Assert
    assert token == {"access_token": "signed-token", "token_type": "bearer"}


def test_login_raises_401_for_invalid_credentials(mocker):
    # Arrange
    db = MagicMock()
    db_user = models.User(
        id=1,
        username="alice",
        email="alice@example.com",
        hashed_password="stored-hash",
    )
    db.query.return_value.filter.return_value.first.return_value = db_user
    mocker.patch("routers.auth.verify_password", return_value=False)
    form_data = OAuth2PasswordRequestForm(
        username="alice",
        password="wrong-password",
        scope="",
        client_id=None,
        client_secret=None,
    )

    # Act / Assert
    with pytest.raises(HTTPException) as exc:
        login(form_data=form_data, db=db)
    assert exc.value.status_code == 401
    assert exc.value.detail == "Invalid credentials"
