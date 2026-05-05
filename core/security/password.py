import hashlib
import secrets
from base64 import b64decode, b64encode


class PasswordHandler:
    """Simple password hashing using PBKDF2 without external dependencies."""

    @staticmethod
    def hash_password(password: str) -> str:
        """
        Hash a password using PBKDF2.
        Returns format: algorithm$iterations$salt$hash
        """
        salt = secrets.token_bytes(32)
        iterations = 100000

        hash_obj = hashlib.pbkdf2_hmac(
            "sha256",
            password.encode("utf-8"),
            salt,
            iterations,
        )

        # Encode salt and hash in base64
        salt_b64 = b64encode(salt).decode("utf-8")
        hash_b64 = b64encode(hash_obj).decode("utf-8")

        return f"pbkdf2_sha256${iterations}${salt_b64}${hash_b64}"

    @staticmethod
    def verify_password(password: str, hashed_password: str) -> bool:
        """
        Verify a password against its hash.
        """
        try:
            parts = hashed_password.split("$")
            if len(parts) != 4 or parts[0] != "pbkdf2_sha256":
                return False

            iterations = int(parts[1])
            salt = b64decode(parts[2])
            stored_hash = b64decode(parts[3])

            hash_obj = hashlib.pbkdf2_hmac(
                "sha256",
                password.encode("utf-8"),
                salt,
                iterations,
            )

            return hash_obj == stored_hash
        except (ValueError, IndexError):
            return False
