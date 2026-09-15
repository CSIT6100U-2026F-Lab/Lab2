"""
Lab 2 — RESTful API (auth + file list).

Login / register are provided so you can use the app after solving the puzzle.
GET /files lists data/ (requires Bearer token). File contents are not served.

Start from the Lab2 directory:
    python3 backend/rest_service.py
"""

import os
import secrets
import time
from typing import Dict, List

from fastapi import Depends, FastAPI, HTTPException, Request, Response
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from pydantic import BaseModel

import data_logic
from data_logic import MAX_FILE_SIZE, AuthConflictError

_BACKEND_DIR = os.path.dirname(os.path.abspath(__file__))

TOKEN_TTL_SECONDS = 600

_sessions_by_token: Dict[str, dict] = {}
_token_by_user: Dict[str, str] = {}


class FileInfo(BaseModel):
    name: str
    size: int
    last_modified: str


class LoginRequest(BaseModel):
    username: str
    password: str


class LoginResponse(BaseModel):
    token: str
    expires_in: int


class RegisterResponse(BaseModel):
    message: str


app = FastAPI(
    title="Online Code Explorer — Lab 2",
    description="Login / register + file list (no file body APIs in this lab)",
    version="1.0.0",
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "http://localhost:5500",
        "http://127.0.0.1:5500",
        "http://localhost:3000",
        "http://127.0.0.1:3000",
        "http://localhost:8080",
        "http://127.0.0.1:8080",
    ],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


def _looks_like_traversal(value: str) -> bool:
    lowered = value.lower()
    return ".." in value or "%2e%2e" in lowered or "%2f" in lowered or "%5c" in lowered


def _drop_session(token: str) -> None:
    session = _sessions_by_token.pop(token, None)
    if not session:
        return
    username = session.get("username")
    if username and _token_by_user.get(username) == token:
        _token_by_user.pop(username, None)


def _issue_token(username: str) -> str:
    old = _token_by_user.get(username)
    if old:
        _sessions_by_token.pop(old, None)
    token = secrets.token_urlsafe(32)
    _sessions_by_token[token] = {
        "username": username,
        "expires_at": time.time() + TOKEN_TTL_SECONDS,
    }
    _token_by_user[username] = token
    return token


def require_auth(request: Request) -> str:
    header = request.headers.get("Authorization") or ""
    if not header.startswith("Bearer "):
        raise HTTPException(
            status_code=401,
            detail="Missing or invalid Authorization header",
        )
    token = header[len("Bearer ") :].strip()
    if not token:
        raise HTTPException(
            status_code=401,
            detail="Missing or invalid Authorization header",
        )
    session = _sessions_by_token.get(token)
    if session is None:
        raise HTTPException(status_code=401, detail="Invalid or expired token")
    if time.time() >= session["expires_at"]:
        _drop_session(token)
        raise HTTPException(status_code=401, detail="Invalid or expired token")
    return session["username"]


@app.middleware("http")
async def security_and_size_limits(request: Request, call_next):
    raw_path = request.scope.get("raw_path", b"").decode("latin-1")
    if _looks_like_traversal(request.url.path) or _looks_like_traversal(raw_path):
        return JSONResponse(status_code=400, content={"detail": "Invalid filename"})

    content_length = request.headers.get("content-length")
    if content_length is not None:
        try:
            length = int(content_length)
        except ValueError:
            return JSONResponse(
                status_code=400,
                content={"detail": "Invalid Content-Length header"},
            )
        if length > MAX_FILE_SIZE:
            return JSONResponse(
                status_code=413,
                content={"detail": "File too large. Maximum size is 5MB."},
            )
    return await call_next(request)


@app.on_event("startup")
def ensure_data_dir() -> None:
    data_logic.ensure_data_dir()


def _to_http_file_info(info: data_logic.FileInfo) -> FileInfo:
    return FileInfo(**info._asdict())


@app.post("/login", response_model=LoginResponse)
def login(body: LoginRequest) -> LoginResponse:
    if not data_logic.verify_user(body.username, body.password):
        raise HTTPException(status_code=401, detail="Invalid username or password")
    token = _issue_token(body.username)
    return LoginResponse(token=token, expires_in=TOKEN_TTL_SECONDS)


@app.post("/register", response_model=RegisterResponse)
def register(body: LoginRequest, response: Response) -> RegisterResponse:
    try:
        result = data_logic.register_user(body.username, body.password)
    except ValueError as exc:
        raise HTTPException(status_code=400, detail=str(exc))
    except AuthConflictError as exc:
        raise HTTPException(status_code=409, detail=str(exc))
    if result == "created":
        response.status_code = 201
        return RegisterResponse(message="registered")
    return RegisterResponse(message="already registered")


@app.get("/files", response_model=List[FileInfo])
def list_files(_user: str = Depends(require_auth)) -> List[FileInfo]:
    return [_to_http_file_info(item) for item in data_logic.list_files()]


if __name__ == "__main__":
    import uvicorn

    uvicorn.run(
        "rest_service:app",
        host="127.0.0.1",
        port=8000,
        reload=True,
        app_dir=_BACKEND_DIR,
    )
