from datetime import timedelta

import pytest
from fastapi import HTTPException
from jose import jwt
from unittest.mock import MagicMock

import auth
import models


def test_hash_and_verify_password_success():
    # Arrange
    plain_password = "super-secret"

    # Act
    hashed_password = auth.hash_password(plain_password)
    is_valid = auth.verify_password(plain_password, hashed_password)

    # Assert
    assert hashed_password != plain_password
    assert is_valid is True


def test_create_access_token_contains_subject_claim():
    # Arrange
    payload = {"sub": "alice"}
    expires_delta = timedelta(minutes=10)

    # Act
    token = auth.create_access_token(data=payload, expires_delta=expires_delta)
    decoded = jwt.decode(token, auth.SECRET_KEY, algorithms=[auth.ALGORITHM])

    # Assert
    assert decoded["sub"] == "alice"
    assert "exp" in decoded


def test_get_current_user_returns_user_for_valid_token():
    # Arrange
    db = MagicMock()
    expected_user = models.User(
        id=1,
        username="alice",
        email="alice@example.com",
        hashed_password="hashed",
    )
    db.query.return_value.filter.return_value.first.return_value = expected_user
    token = auth.create_access_token(data={"sub": "alice"})

    # Act
    user = auth.get_current_user(token=token, db=db)

    # Assert
    assert user == expected_user
    db.query.assert_called_once_with(models.User)


def test_get_current_user_raises_401_when_user_not_found():
    # Arrange
    db = MagicMock()
    db.query.return_value.filter.return_value.first.return_value = None
    token = auth.create_access_token(data={"sub": "missing-user"})

    # Act / Assert
    with pytest.raises(HTTPException) as exc:
        auth.get_current_user(token=token, db=db)
    assert exc.value.status_code == 401
    assert exc.value.detail == "Could not validate credentials"
