---
name: authentication
description: JWT token generation, validation, and basic authentication utilities.
allowed-tools:
  - generate_jwt
  - validate_jwt
  - hash_password
  - verify_password
  - basic_auth_header
  - parse_basic_auth
---

# Authentication Skill

This skill provides tools for authentication tasks: JWT token handling, password hashing, and Basic Authentication.

## Prerequisites

- **PyJWT** library (optional, only required for JWT tools). Install with:
  ```bash
  pip install PyJWT
  ```
- The `cryptography` library (already installed via project requirements) is NOT required for the included JWT algorithms (HS256, HS384, HS512, RS256, etc.) but may be needed for certain advanced algorithms.

## Tools

### generate_jwt
Generate a JSON Web Token (JWT) with the given claims.
- `payload`: JSON string of claims (e.g., `{"user_id": 123, "role": "admin"}`).
- `secret`: Secret key for signing (for HMAC algorithms) or private key (for RSA).
- `algorithm`: Signing algorithm (default `HS256`). Common values: `HS256`, `HS384`, `HS512`, `RS256`, `ES256`.
- `expires_in`: Optional token lifetime in seconds from now. Adds an `exp` claim.

### validate_jwt
Validate a JWT token and return its decoded payload.
- `token`: JWT token string.
- `secret`: Secret key (HMAC) or public key (RSA) for verification.
- `algorithms`: Comma‑separated list of allowed algorithms (default `HS256`). Example: `HS256,RS256`.

### hash_password
Hash a password using SHA‑256 with a salt.
- `password`: Plain‑text password.
- `salt`: Optional salt string. If omitted, a random salt is generated.
Returns a JSON object with `hash` and `salt`.

### verify_password
Verify a password against a stored hash and salt.
- `password`: Plain‑text password to verify.
- `stored_hash`: Previously stored hash (as returned by `hash_password`).
- `salt`: Salt used when hashing.
Returns a message indicating whether the password matches.

### basic_auth_header
Generate a Basic Authentication header value (Base64‑encoded `username:password`).
- `username`: Username.
- `password`: Password.
Returns the full `Basic ...` header string.

### parse_basic_auth
Parse a Basic Authentication header and extract the username and password.
- `header`: Full header string (e.g., `Basic dXNlcjpwYXNz`).
Returns a JSON object with `username` and `password`.

## Usage Example

1. **Create a JWT token**:
   ```
   generate_jwt(payload='{"user": "alice", "role": "editor"}', secret="mysecret", expires_in=3600)
   ```
2. **Validate a token**:
   ```
   validate_jwt(token="...", secret="mysecret")
   ```
3. **Hash a password**:
   ```
   hash_password("mypassword")
   ```
4. **Verify a password**:
   ```
   verify_password("mypassword", "stored_hash", "salt")
   ```
5. **Generate a Basic Auth header**:
   ```
   basic_auth_header("admin", "secret")
   ```
6. **Parse a Basic Auth header**:
   ```
   parse_basic_auth("Basic YWRtaW46c2VjcmV0")
   ```
