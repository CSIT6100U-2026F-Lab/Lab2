"""
Teaching auth helpers: deterministic password ciphertext.

ciphertext = SHA256(PUBLIC_KEY + password) as hex.
Not for production use.
"""

import hashlib

# Public constant used when hashing passwords (plain text by design for the lab).
PUBLIC_KEY = "OnlineCodeExplorer-LabPublicKey-v1"


def hash_password(password: str) -> str:
    """Return hex digest of SHA256(PUBLIC_KEY + password)."""
    material = "{}{}".format(PUBLIC_KEY, password).encode("utf-8")
    return hashlib.sha256(material).hexdigest()
