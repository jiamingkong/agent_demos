"""
Authentication skill: JWT token generation, validation, and basic auth utilities.
Requires PyJWT library (install via `pip install PyJWT`).
"""

import base64
import hashlib
import hmac
import json
import time
from typing import Any, Dict, Optional

from mcp.server.fastmcp import FastMCP

mcp = FastMCP("authentication", log_level="ERROR")

# Try to import PyJWT, provide fallback if not installed
try:
    import jwt

    _JWT_AVAILABLE = True
except ImportError:
    _JWT_AVAILABLE = False


@mcp.tool()
def generate_jwt(
    payload: str,
    secret: str,
    algorithm: str = "HS256",
    expires_in: Optional[int] = None,
) -> str:
    """
    Generate a JWT token.

    Args:
        payload: JSON string of claims (e.g., '{"user_id": 123, "role": "admin"}').
        secret: Secret key for signing.
        algorithm: Signing algorithm (HS256, HS384, HS512, RS256, etc.).
        expires_in: Token lifetime in seconds from now (optional). Adds an 'exp' claim.
    """
    if not _JWT_AVAILABLE:
        return "Error: PyJWT library not installed. Install with `pip install PyJWT`."
    try:
        claims = json.loads(payload)
        if expires_in is not None:
            claims["exp"] = int(time.time()) + expires_in
        token = jwt.encode(claims, secret, algorithm=algorithm)
        return token
    except Exception as e:
        return f"Error generating JWT: {e}"


@mcp.tool()
def validate_jwt(token: str, secret: str, algorithms: Optional[str] = None) -> str:
    """
    Validate a JWT token and return its payload.

    Args:
        token: JWT token string.
        secret: Secret key for verification (for HMAC) or public key for RSA.
        algorithms: Comma‑separated list of allowed algorithms (default depends on secret).
                   If not provided, defaults to ["HS256"].
    """
    if not _JWT_AVAILABLE:
        return "Error: PyJWT library not installed. Install with `pip install PyJWT`."
    try:
        if algorithms is None:
            algo_list = ["HS256"]
        else:
            algo_list = [alg.strip() for alg in algorithms.split(",")]
        payload = jwt.decode(token, secret, algorithms=algo_list)
        return json.dumps(payload, indent=2)
    except jwt.ExpiredSignatureError:
        return "Error: Token has expired."
    except jwt.InvalidTokenError as e:
        return f"Error: Invalid token: {e}"
    except Exception as e:
        return f"Error validating JWT: {e}"


@mcp.tool()
def hash_password(password: str, salt: Optional[str] = None) -> str:
    """
    Hash a password using SHA‑256 with an optional salt.

    Args:
        password: Plain‑text password.
        salt: Optional salt string. If not provided, a random salt is generated.
    """
    import secrets

    if salt is None:
        salt = secrets.token_hex(8)
    salted = salt + password
    hashed = hashlib.sha256(salted.encode()).hexdigest()
    return json.dumps({"hash": hashed, "salt": salt})


@mcp.tool()
def verify_password(password: str, stored_hash: str, salt: str) -> str:
    """
    Verify a password against a stored hash and salt.

    Args:
        password: Plain‑text password to verify.
        stored_hash: Previously stored hash.
        salt: Salt used when hashing.
    """
    salted = salt + password
    computed = hashlib.sha256(salted.encode()).hexdigest()
    if computed == stored_hash:
        return "Password matches."
    else:
        return "Password does NOT match."


@mcp.tool()
def basic_auth_header(username: str, password: str) -> str:
    """
    Generate a Basic Authentication header value.

    Args:
        username: Username.
        password: Password.
    """
    credentials = f"{username}:{password}"
    encoded = base64.b64encode(credentials.encode()).decode()
    return f"Basic {encoded}"


@mcp.tool()
def parse_basic_auth(header: str) -> str:
    """
    Parse a Basic Authentication header and return username/password.

    Args:
        header: Full header string (e.g., "Basic dXNlcjpwYXNz").
    """
    try:
        if not header.startswith("Basic "):
            return "Error: Not a Basic Auth header."
        encoded = header.split(" ", 1)[1]
        decoded = base64.b64decode(encoded).decode()
        username, password = decoded.split(":", 1)
        return json.dumps({"username": username, "password": password})
    except Exception as e:
        return f"Error parsing header: {e}"


if __name__ == "__main__":
    mcp.run()
