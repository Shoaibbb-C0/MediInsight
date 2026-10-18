"""Explicit environment loading and fail-closed configuration validation."""
import base64
import json
import os
from pathlib import Path
from urllib.parse import urlsplit
from dotenv import load_dotenv

REPOSITORY_ROOT = Path(__file__).resolve().parents[3]
if os.getenv("SIMPLIFIER_LOAD_DOTENV", "1") != "0":
    load_dotenv(REPOSITORY_ROOT / ".env", override=False)
    load_dotenv(REPOSITORY_ROOT / "backend" / ".env", override=False)


def environment():
    value = os.getenv("ENVIRONMENT", "development").strip().lower()
    if value not in {"development", "test", "production"}:
        raise ValueError("ENVIRONMENT must be development, test, or production.")
    return value


def auth_configuration():
    mode = os.getenv("AUTH_MODE", "auto").strip().lower()
    if mode not in {"auto", "local", "supabase"}: raise ValueError("AUTH_MODE must be auto, local or supabase.")
    if mode == "local":
        if environment() == "production": raise ValueError("Production cannot use local authentication.")
        return None
    url = os.getenv("SUPABASE_URL", "").strip().rstrip("/")
    key = os.getenv("SUPABASE_PUBLISHABLE_KEY", "").strip()
    if not url and not key:
        if mode == "supabase": raise ValueError("Supabase authentication requires both connection settings.")
        return None
    if not url or not key:
        raise ValueError("Set both SUPABASE_URL and SUPABASE_PUBLISHABLE_KEY, or neither for development.")
    parts = urlsplit(url)
    local = environment() != "production" and parts.hostname in {"localhost", "127.0.0.1", "::1"}
    if (parts.scheme != "https" and not (local and parts.scheme == "http")) or not parts.hostname or parts.username or parts.password or parts.path or parts.query or parts.fragment:
        raise ValueError("SUPABASE_URL must be a valid HTTPS project origin.")
    if key.startswith("sb_secret_") or any(c.isspace() for c in key):
        raise ValueError("Use a Supabase publishable key, never a secret/service-role key.")
    if key.count(".") == 2:
        try:
            payload = json.loads(base64.urlsafe_b64decode(key.split(".")[1] + "=" * (-len(key.split(".")[1]) % 4)))
            if payload.get("role") != "anon": raise ValueError()
        except (ValueError, TypeError, AttributeError):
            raise ValueError("Legacy Supabase keys must have the anon role.") from None
    return url, key


def cors_origins():
    raw = os.getenv("CORS_ORIGINS", "")
    if not raw and environment() != "production":
        return [f"http://{host}:{port}" for host in ["localhost", "127.0.0.1"] for port in [3000, 3001]]
    origins = [item.strip() for item in raw.split(",") if item.strip()]
    if not origins: raise ValueError("Explicit HTTPS CORS_ORIGINS are required in production.")
    for origin in origins:
        parts = urlsplit(origin)
        if not parts.hostname or parts.username or parts.password or parts.path or parts.query or parts.fragment or "*" in origin or parts.scheme not in (["https"] if environment() == "production" else ["http", "https"]):
            raise ValueError("CORS_ORIGINS must contain exact allowed origins without paths or wildcards.")
    return origins


def data_directory():
    return Path(os.getenv("APP_DATA_DIR", str(REPOSITORY_ROOT / "backend" / "data")))


class Settings:
    PROJECT_NAME = "Simplifier 2.0"
    API_V1_STR = "/api/v1"
    ALLOWED_EXTENSIONS = ["pdf", "jpg", "jpeg", "png", "webp"]

    def __init__(self):
        self.ENVIRONMENT = environment()
        self.MAX_FILE_SIZE_MB = int(os.getenv("MAX_FILE_SIZE_MB", "15"))
        if not 1 <= self.MAX_FILE_SIZE_MB <= 50: raise ValueError("MAX_FILE_SIZE_MB must be between 1 and 50.")
        self.SUPABASE_URL = os.getenv("SUPABASE_URL")
        self.SUPABASE_PUBLISHABLE_KEY = os.getenv("SUPABASE_PUBLISHABLE_KEY")

    def validate_production(self):
        try:
            environment()
            cors_origins()
            if self.ENVIRONMENT == "production" and (not self.SUPABASE_URL or not self.SUPABASE_PUBLISHABLE_KEY):
                raise ValueError("SUPABASE_URL and SUPABASE_PUBLISHABLE_KEY are required.")
            if self.ENVIRONMENT == "production": auth_configuration()
        except ValueError as exc:
            raise RuntimeError(("PRODUCTION CONFIG ERROR: " if self.ENVIRONMENT == "production" else "CONFIG ERROR: ") + str(exc)) from None

settings = Settings()
