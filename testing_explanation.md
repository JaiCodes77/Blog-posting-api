# Testing Guide for `blog-posting-api`

This document explains:

1. Which stack we used for testing
2. Why we wrote both unit and integration tests
3. How the test setup works (`conftest.py`)
4. Every test case in every test file (beginner-friendly)
5. How to run tests and coverage

---

## 1) Testing Stack Used

Your app stack and test stack are:

- **Python**
- **FastAPI**
- **SQLite** (test DB URL: `sqlite:///./test.db`)
- **JWT Bearer auth** (`get_current_user` dependency)

Testing tools:

- **pytest**: main test runner
- **pytest-asyncio**: async test support (`async def` tests)
- **httpx**: `AsyncClient` to call FastAPI routes as if they were real HTTP requests
- **pytest-mock**: clean mocking with `mocker.patch(...)`
- **pytest-cov**: code coverage report

Configured in:

- `requirements.txt`
- `pytest.ini`

---

## 2) Why We Need Unit Tests and Integration Tests

### Unit tests (fast, isolated)

Unit tests check small pieces of logic in isolation.

- They run very fast.
- They fail only when a specific function's logic breaks.
- They use mocks instead of real DB/network/auth flows.
- Great for catching logic bugs early.

Example in this project: testing `auth.create_access_token(...)` and `auth.get_current_user(...)` directly with mocked DB behavior.

### Integration tests (real app flow)

Integration tests check that components work together:

- FastAPI routing + validation + dependencies + DB actions
- Real request/response behavior and status codes
- Auth-protected route behavior (`401` when missing auth, `201` when valid auth, etc.)

Example in this project: `POST /posts/` using `AsyncClient`, real test DB, and auth headers.

### Why both together?

- Unit tests give confidence in core logic and edge cases quickly.
- Integration tests confirm that your real API behavior is correct end-to-end.
- Together, they reduce regressions and improve refactor safety.

---

## 3) Project Test Structure

```text
tests/
├── conftest.py
├── unit/
│   ├── test_auth_service.py
│   └── test_auth_router_unit.py
└── integration/
    ├── test_auth_routes.py
    └── test_posts_routes.py
```

---

## 4) How `conftest.py` Works

File: `tests/conftest.py`

`conftest.py` is the shared setup for all tests. Pytest auto-loads it.

### Key parts

- **Import path setup**
  - Adds project root to `sys.path` so tests can import modules like `models`, `auth`, `routers`.

- **Test database**
  - `TEST_DATABASE_URL = "sqlite:///./test.db"`
  - Creates a dedicated SQLAlchemy engine/session for tests.

- **`db_session` fixture**
  - Drops + recreates tables before each test function.
  - Yields a clean session.
  - Ensures each test starts with a clean DB state.

- **`fake_current_user` fixture**
  - Creates a fake logged-in user object with `id=1`.

- **Dependency override fixtures**
  - `app_with_overrides`:
    - overrides `get_db` to use test DB session
    - overrides `get_current_user` to return fake user
  - `app_without_auth_override`:
    - overrides only `get_db` (used to test real `401` behavior when auth is missing)

- **`auth_headers` fixture**
  - Returns `{"Authorization": "Bearer fake-jwt-token"}` for protected routes.

- **Async HTTP clients**
  - `async_client`: with DB + auth overrides
  - `async_client_no_auth_override`: DB override only

---

## 5) Unit Tests Explained (File by File)

## `tests/unit/test_auth_service.py`

These test auth/service-level helper functions directly.

### 1. `test_hash_and_verify_password_success`

- **Arrange:** plain password
- **Act:** hash password, verify it
- **Assert:** hash is different from plain text, verification returns `True`

Why: confirms secure hashing + verification behavior.

### 2. `test_create_access_token_contains_subject_claim`

- **Arrange:** payload with `"sub": "alice"`
- **Act:** create token, decode token
- **Assert:** decoded token contains `sub="alice"` and has `exp`

Why: ensures JWT token includes required claims and expiry.

### 3. `test_get_current_user_returns_user_for_valid_token`

- **Arrange:** mocked DB returns a user, valid token with `sub`
- **Act:** call `get_current_user(...)`
- **Assert:** returned user is expected user; DB query was called

Why: validates happy path for auth dependency.

### 4. `test_get_current_user_raises_401_when_user_not_found`

- **Arrange:** mocked DB returns `None`, valid token
- **Act:** call `get_current_user(...)`
- **Assert:** raises `HTTPException` with `401` and correct message

Why: validates auth error path when token is valid but user no longer exists.

---

## `tests/unit/test_auth_router_unit.py`

These test auth router functions (`register`, `login`) with mocked DB and mocked auth utilities.

### 1. `test_register_creates_user_when_email_is_new`

- **Arrange:** mocked DB has no existing user with email; mock `hash_password`
- **Act:** call `register(...)`
- **Assert:** user fields match expected values; `db.add`, `db.commit`, `db.refresh` called once

Why: verifies user registration success flow.

### 2. `test_register_raises_400_when_email_exists`

- **Arrange:** mocked DB returns existing user for same email
- **Act:** call `register(...)`
- **Assert:** raises `400` with `"Email already registered"`

Why: verifies duplicate email protection.

### 3. `test_login_returns_token_for_valid_credentials`

- **Arrange:** mocked DB returns user; mock `verify_password=True`; mock token creation
- **Act:** call `login(...)`
- **Assert:** response contains token and `token_type="bearer"`

Why: verifies login success behavior.

### 4. `test_login_raises_401_for_invalid_credentials`

- **Arrange:** mocked DB returns user; mock `verify_password=False`
- **Act:** call `login(...)`
- **Assert:** raises `401` with `"Invalid credentials"`

Why: verifies login failure behavior.

---

## 6) Integration Tests Explained (File by File)

Integration tests call actual routes through `httpx.AsyncClient`.

## `tests/integration/test_auth_routes.py`

### 1. `test_register_returns_201`

- Calls `POST /auth/register` with valid JSON
- Expects `201` and response user fields

### 2. `test_register_returns_422_for_invalid_payload`

- Missing required `email`
- Expects `422` (FastAPI validation error)

### 3. `test_login_returns_200_and_token`

- Registers a user first
- Calls `POST /auth/login` with correct form credentials
- Expects `200`, `access_token`, and `token_type="bearer"`

### 4. `test_login_returns_401_for_invalid_credentials`

- Registers user first
- Logs in with wrong password
- Expects `401` and `"Invalid credentials"`

---

## `tests/integration/test_posts_routes.py`

### 1. `test_root_returns_200`

- Calls `GET /`
- Expects `200` with `message`

### 2. `test_get_all_posts_returns_200`

- Calls `GET /posts/`
- Expects `200` and list response

### 3. `test_get_post_returns_404_when_missing`

- Calls `GET /posts/9999`
- Expects `404` + `"Post not found"`

### 4. `test_create_post_returns_201_with_auth`

- Calls `POST /posts/` with `auth_headers`
- Expects `201`, returned post fields, and `author_id=1`

### 5. `test_create_post_returns_401_without_auth`

- Uses client without auth override
- Calls `POST /posts/` without header
- Expects `401`

### 6. `test_create_post_returns_422_for_invalid_payload`

- Missing `content`
- Expects `422`

### 7. `test_update_post_returns_200`

- Creates a post first
- Updates same post via `PUT /posts/{id}`
- Expects `200` and updated values

### 8. `test_update_post_returns_404_when_missing`

- Updates non-existent ID
- Expects `404`

### 9. `test_delete_post_returns_204`

- Creates a post first
- Deletes it via `DELETE /posts/{id}`
- Expects `204` and empty body

---

## 7) Arrange / Act / Assert Pattern

All tests follow AAA:

- **Arrange:** setup data, mocks, and prerequisites
- **Act:** perform one action (function call or API request)
- **Assert:** verify expected result/status/message

Why this helps beginners:

- clean structure
- easier debugging
- easier maintenance

---

## 8) Setup Instructions (Beginner-Friendly)

Run from project root: `blog-posting-api`

### 1. Create and activate virtual environment

macOS/Linux:

```bash
python3 -m venv .venv
source .venv/bin/activate
```

### 2. Install dependencies

```bash
pip install -r requirements.txt
```

### 3. Confirm pytest is installed

```bash
pytest --version
```

---

## 9) Test Run Commands

### Run all tests

```bash
pytest -q
```

Because `pytest.ini` has:

- `asyncio_mode = auto`
- `addopts = --cov=. --cov-report=term-missing`

...the command above also prints coverage automatically.

### Run with verbose output

```bash
pytest -v
```

### Run only unit tests

```bash
pytest -q tests/unit
```

### Run only integration tests

```bash
pytest -q tests/integration
```

### Run one specific test file

```bash
pytest -q tests/integration/test_posts_routes.py
```

### Run one specific test function

```bash
pytest -q tests/integration/test_posts_routes.py::test_create_post_returns_201_with_auth
```

---

## 10) Coverage Commands

Default coverage already runs via `pytest.ini`, but these are useful:

### Terminal coverage report

```bash
pytest --cov=. --cov-report=term-missing
```

### HTML coverage report

```bash
pytest --cov=. --cov-report=html
```

Open report:

```bash
open htmlcov/index.html
```

### Enforce minimum coverage (example: 80%)

```bash
pytest --cov=. --cov-report=term-missing --cov-fail-under=80
```

---

## 11) Quick Troubleshooting

- **`ModuleNotFoundError` during tests**
  - Ensure you run from project root.
  - Ensure virtualenv is activated.

- **`pytest: command not found`**
  - Use `python3 -m pytest -q` or install dependencies again.

- **Auth-protected route failing unexpectedly**
  - Use `auth_headers` with `async_client` in integration tests.
  - For explicit `401` checks, use `async_client_no_auth_override`.

---

## 12) Final Takeaway

This test setup gives you:

- isolated and fast **unit tests**
- real end-to-end API behavior checks via **integration tests**
- shared fixtures that keep test code clean and reusable
- built-in coverage reporting so quality is visible every run

This is a strong baseline for safely adding new features to your FastAPI app.
