"""
API Security

Handles API key authentication and authorization.
"""

import secrets
from typing import Optional, List
from fastapi import HTTPException, Security, status
from fastapi.security import APIKeyHeader
from .config import get_settings

settings = get_settings()

# API Key header
api_key_header = APIKeyHeader(name="X-API-Key", auto_error=False)


def generate_api_key() -> str:
    """Generate a secure random API key"""
    return secrets.token_urlsafe(32)


async def verify_api_key(api_key: Optional[str] = Security(api_key_header)) -> str:
    """
    Verify API key from request header.

    Args:
        api_key: API key from X-API-Key header

    Returns:
        Verified API key

    Raises:
        HTTPException: If API key is invalid or missing
    """
    if not api_key:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Missing API key. Provide X-API-Key header.",
            headers={"WWW-Authenticate": "ApiKey"},
        )

    # If no API keys configured, allow any key (development mode)
    if not settings.API_KEYS or len(settings.API_KEYS) == 0:
        return api_key

    # Verify against configured keys
    if api_key not in settings.API_KEYS:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid API key",
            headers={"WWW-Authenticate": "ApiKey"},
        )

    return api_key


def create_api_keys_file(num_keys: int = 3) -> List[str]:
    """
    Generate multiple API keys for distribution.

    Args:
        num_keys: Number of keys to generate

    Returns:
        List of generated API keys
    """
    keys = [generate_api_key() for _ in range(num_keys)]

    # Save to file for easy distribution
    with open("api_keys.txt", "w") as f:
        f.write("# WordPress SEO Publishing API Keys\n")
        f.write("# Add these to your .env file: API_KEYS=key1,key2,key3\n\n")
        for i, key in enumerate(keys, 1):
            f.write(f"Key {i}: {key}\n")

    return keys


if __name__ == "__main__":
    # Generate API keys for initial setup
    print("Generating 3 API keys...\n")
    keys = create_api_keys_file(3)
    print("API Keys generated and saved to api_keys.txt\n")
    print("Add to .env file:")
    print(f"API_KEYS={','.join(keys)}")
