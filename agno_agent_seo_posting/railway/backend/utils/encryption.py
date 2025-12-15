"""
Password encryption utilities using Fernet symmetric encryption.

Provides secure encryption/decryption for sensitive data like WordPress app passwords.
"""

import os
import base64
import hashlib
from cryptography.fernet import Fernet
from typing import Optional

# Get encryption key from environment, or generate a default one
# IMPORTANT: In production, always set ENCRYPTION_KEY environment variable
_ENCRYPTION_KEY = os.getenv("ENCRYPTION_KEY")


def _get_fernet() -> Fernet:
    """Get Fernet instance with the encryption key."""
    if not _ENCRYPTION_KEY:
        raise ValueError(
            "ENCRYPTION_KEY environment variable not set. "
            "Generate one with: python -c \"from cryptography.fernet import Fernet; print(Fernet.generate_key().decode())\""
        )

    # Ensure key is valid Fernet key (32 url-safe base64-encoded bytes)
    try:
        return Fernet(_ENCRYPTION_KEY.encode() if isinstance(_ENCRYPTION_KEY, str) else _ENCRYPTION_KEY)
    except Exception as e:
        raise ValueError(f"Invalid ENCRYPTION_KEY: {e}")


def encrypt_password(plain_password: str) -> str:
    """
    Encrypt a password using Fernet symmetric encryption.

    Args:
        plain_password: The plain text password to encrypt

    Returns:
        Base64-encoded encrypted password string (prefixed with 'enc:')
    """
    if not plain_password:
        return plain_password

    # If already encrypted, return as-is
    if plain_password.startswith("enc:"):
        return plain_password

    fernet = _get_fernet()
    encrypted = fernet.encrypt(plain_password.encode())
    return f"enc:{encrypted.decode()}"


def decrypt_password(encrypted_password: str) -> str:
    """
    Decrypt an encrypted password.

    Args:
        encrypted_password: The encrypted password (prefixed with 'enc:')

    Returns:
        The decrypted plain text password
    """
    if not encrypted_password:
        return encrypted_password

    # If not encrypted (legacy plain text), return as-is
    if not encrypted_password.startswith("enc:"):
        return encrypted_password

    fernet = _get_fernet()
    encrypted_data = encrypted_password[4:]  # Remove 'enc:' prefix
    decrypted = fernet.decrypt(encrypted_data.encode())
    return decrypted.decode()


def is_encrypted(password: str) -> bool:
    """Check if a password is already encrypted."""
    return password.startswith("enc:") if password else False


def generate_encryption_key() -> str:
    """Generate a new Fernet encryption key."""
    return Fernet.generate_key().decode()


if __name__ == "__main__":
    # Generate a new key for setup
    print("New encryption key:")
    print(generate_encryption_key())
    print("\nAdd this to your Railway environment variables as ENCRYPTION_KEY")
