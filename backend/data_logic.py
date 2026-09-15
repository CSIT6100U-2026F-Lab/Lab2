"""
Shared data layer for Lab 2 (auth + file list only).

Protocol-agnostic helpers over Lab2/data/ and backend/users.xml.
REST must not touch the disk itself.
"""

import os
from datetime import datetime, timezone
from typing import List, NamedTuple
from xml.etree import ElementTree

_BACKEND_DIR = os.path.dirname(os.path.abspath(__file__))
_PROJECT_ROOT = os.path.dirname(_BACKEND_DIR)
DATA_DIR = os.path.join(_PROJECT_ROOT, "data")
USERS_XML = os.path.join(_BACKEND_DIR, "users.xml")

MAX_FILE_SIZE = 5 * 1024 * 1024
UNSAFE_FILENAME_CHARS = ("..", "/", "\\")


class FileInfo(NamedTuple):
    name: str
    size: int
    last_modified: str


class InvalidFilenameError(Exception):
    def __init__(self, message: str = "Invalid filename") -> None:
        super().__init__(message)


class AuthConflictError(Exception):
    def __init__(self, message: str = "User already exists") -> None:
        super().__init__(message)


def _load_users_root():
    if not os.path.isfile(USERS_XML):
        return ElementTree.Element("users")
    try:
        return ElementTree.parse(USERS_XML).getroot()
    except ElementTree.ParseError:
        return ElementTree.Element("users")


def _write_users_root(root) -> None:
    tree = ElementTree.ElementTree(root)
    try:
        ElementTree.indent(tree, space="  ")
    except AttributeError:
        pass
    tree.write(USERS_XML, encoding="utf-8", xml_declaration=True)


def _find_user_node(root, username: str):
    for node in root.findall("user"):
        if node.get("username") == username:
            return node
    return None


def verify_user(username: str, password: str) -> bool:
    """Return True if password hashes to the ciphertext stored for username."""
    if not username or password is None:
        return False
    import auth_crypto

    root = _load_users_root()
    node = _find_user_node(root, username)
    if node is None:
        return False
    stored = node.get("password") or ""
    return stored == auth_crypto.hash_password(password)


def register_user(username: str, password: str) -> str:
    """Create or confirm a user. Returns 'created' or 'unchanged'.

    Raises AuthConflictError if the username exists with a different password hash.
    """
    if not username or password is None or password == "":
        raise ValueError("username and password are required")

    import auth_crypto

    digest = auth_crypto.hash_password(password)
    root = _load_users_root()
    if root.tag != "users":
        root = ElementTree.Element("users")

    node = _find_user_node(root, username)
    if node is None:
        ElementTree.SubElement(
            root, "user", {"username": username, "password": digest}
        )
        _write_users_root(root)
        return "created"

    stored = node.get("password") or ""
    if stored == digest:
        return "unchanged"
    raise AuthConflictError("User already exists")


def ensure_data_dir() -> None:
    os.makedirs(DATA_DIR, exist_ok=True)


def _build_file_info(filename: str, path: str) -> FileInfo:
    mtime = os.path.getmtime(path)
    last_modified = datetime.fromtimestamp(mtime, tz=timezone.utc).isoformat()
    return FileInfo(
        name=filename,
        size=os.path.getsize(path),
        last_modified=last_modified,
    )


def list_files() -> List[FileInfo]:
    """Scan data/ for regular files and return them sorted by name."""
    ensure_data_dir()
    result: List[FileInfo] = []
    for name in sorted(os.listdir(DATA_DIR)):
        path = os.path.join(DATA_DIR, name)
        if os.path.isfile(path):
            result.append(_build_file_info(name, path))
    return result
