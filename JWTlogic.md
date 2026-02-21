# How JWT Authentication Works in This Project

## The Big Picture

JWT stands for **JSON Web Token**. It is a way to prove who you are to an API without sending your password on every request.

Think of it like a theme park wristband:

1. You show your ticket (username + password) at the gate — **login**
2. Staff verify it and snap a wristband on your wrist — **JWT token issued**
3. For the rest of the day you just flash the wristband — **protected routes**
4. The wristband expires at midnight — **token expiry**

The server never stores the token. It just signs it with a secret key, and verifies that signature whenever the token comes back.

---

## What a JWT Token Looks Like

A JWT is a string made of three parts separated by dots:

```
eyJhbGciOiJIUzI1NiJ9.eyJzdWIiOiJqb2huX2RvZSIsImV4cCI6MTcwODEyMzQ1Nn0.abc123signature
       ^                              ^                              ^
    Header                         Payload                       Signature
```

### Header
Contains the algorithm used to sign the token.
```json
{
  "alg": "HS256"
}
```

### Payload
Contains the actual data (called "claims"). In this project the payload holds the username and expiry time.
```json
{
  "sub": "john_doe",
  "exp": 1708123456
}
```
`"sub"` stands for "subject" — it identifies who the token belongs to.
`"exp"` is the Unix timestamp of when the token expires.

> Anyone can Base64-decode the header and payload and read them.
> That is fine — there is no sensitive data in there (no passwords).

### Signature
This is what makes the token trustworthy. It is created by running:
```
HMAC-SHA256(base64(header) + "." + base64(payload), SECRET_KEY)
```
Without knowing the `SECRET_KEY`, nobody can forge a valid signature.
If someone tampers with the payload, the signature will not match and the server rejects the token.

---

## The Full Flow in This Project

```
User                        FastAPI Server                    Database
 |                               |                               |
 |-- POST /auth/register ------->|                               |
 |   { username, email,          |-- hash password               |
 |     password }                |-- save new user ------------->|
 |<-- 201 { user info } ---------|                               |
 |                               |                               |
 |-- POST /auth/login ---------->|                               |
 |   { username, password }      |-- look up user -------------->|
 |                               |<-- user row ------------------|
 |                               |-- verify password             |
 |                               |-- create JWT token            |
 |<-- 200 { access_token } ------|                               |
 |                               |                               |
 |-- GET /posts ---------------->|                               |
 |   Authorization:              |-- decode JWT                  |
 |   Bearer <token>              |-- verify signature            |
 |                               |-- get username from payload   |
 |                               |-- look up user -------------->|
 |                               |<-- user row ------------------|
 |                               |-- run route logic             |
 |<-- 200 { posts } -------------|                               |
```

---

## Step-by-Step: What Happens at Each Stage

### Stage 1 — Registration (`POST /auth/register`)

- Client sends: `{ username, email, password }`
- Server takes the plain password and runs it through **bcrypt** to produce a hash
- The hash (never the plain password) is stored in the database
- bcrypt is a one-way function — you cannot reverse a hash to get the original password

```
"mypassword123"  -->  bcrypt  -->  "$2b$12$Ei3kLm..."
```

---

### Stage 2 — Login (`POST /auth/login`)

- Client sends: `{ username, password }`
- Server finds the user in the database by username
- Server runs `bcrypt.verify(plain_password, stored_hash)` — this re-hashes the input and compares
- If it matches, the server calls `create_access_token({"sub": user.username})`
- The token is returned to the client as `{ "access_token": "...", "token_type": "bearer" }`
- The client stores this token and sends it with every future request

---

### Stage 3 — Accessing a Protected Route (e.g. `POST /posts`)

- Client sends the token in the HTTP header:
  ```
  Authorization: Bearer eyJhbGci...
  ```
- FastAPI sees `Depends(get_current_user)` on the route
- `get_current_user` is called automatically with the token extracted from the header
- It decodes the token using `jwt.decode(token, SECRET_KEY, algorithms=["HS256"])`
  - This verifies the signature
  - This checks that the token has not expired
- The username is extracted from the payload (`payload.get("sub")`)
- The user is fetched from the database by username
- That user object is passed into the route function as `current_user`

If anything is wrong (bad signature, expired token, user not found), a `401 Unauthorized` error is raised automatically.

---

## Where Each Piece Lives in This Project

| File | What it does |
|---|---|
| `auth.py` | `hash_password`, `verify_password`, `create_access_token`, `get_current_user` |
| `routers/auth.py` | The actual `/register` and `/login` HTTP routes |
| `schemas.py` | `Token` (what login returns), `TokenData` (holds decoded username) |
| Any protected route | Uses `Depends(get_current_user)` to enforce authentication |

---

## Why Passwords Are Hashed (and Why bcrypt)

If your database is ever leaked, plain-text passwords are an instant disaster. Hashed passwords are useless to an attacker because:

- The hash is one-way — you cannot reverse it
- bcrypt is intentionally slow — brute-forcing millions of guesses takes years
- Every hash is salted (random data mixed in) — two users with the same password get different hashes

---

## Why Tokens Instead of Passwords on Every Request

- The client only sends the password once (at login)
- Tokens are short-lived (30 minutes by default here) — if stolen, the damage window is limited
- The server does not need to store sessions — it just verifies the signature mathematically
- You can instantly invalidate all tokens by changing `SECRET_KEY` in `auth.py`

---

## Common Errors You Will See

| Error | What it means |
|---|---|
| `401 Unauthorized` | Token is missing, expired, or has an invalid signature |
| `400 Bad Request` on register | Username or email already taken |
| `401` on login | Wrong username or password |
| `403 Forbidden` on update/delete | You are authenticated but you are not the owner of the post |
