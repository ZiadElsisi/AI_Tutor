import os
import httpx
import streamlit as st

class BackendError(RuntimeError):
    pass

def settings():
    try:
        base = st.secrets.get("BACKEND_URL", "")
        secret = st.secrets.get("BACKEND_SECRET", "")
    except Exception:
        base, secret = "", ""
    return str(base or os.getenv("BACKEND_URL", "")).rstrip("/"), str(secret or os.getenv("BACKEND_SECRET", ""))

def call(method: str, path: str, *, timeout: float = 90, **kwargs):
    base, secret = settings()
    if not base or not secret:
        raise BackendError("Backend URL or secret is not configured. Set BACKEND_URL and BACKEND_SECRET in app secrets.")
    headers = dict(kwargs.pop("headers", {}))
    headers["X-API-Key"] = secret
    try:
        response = httpx.request(method, f"{base}{path}", headers=headers, timeout=timeout, **kwargs)
    except httpx.TimeoutException as exc:
        raise BackendError("The AI backend timed out. The notebook may be loading or under heavy load.") from exc
    except httpx.HTTPError as exc:
        raise BackendError("The AI backend is offline or BACKEND_URL is stale. Start the configured backend service and update BACKEND_URL.") from exc
    if response.is_error:
        try:
            detail = response.json().get("detail", response.text)
        except Exception:
            detail = response.text
        raise BackendError(f"Backend returned {response.status_code}: {detail}")
    try:
        return response.json()
    except ValueError as exc:
        raise BackendError("Backend returned an unreadable response.") from exc

def health():
    base, _ = settings()
    if not base:
        return {"status": "unconfigured", "model_loaded": False}
    try:
        response = httpx.get(f"{base}/health", timeout=5)
        response.raise_for_status()
        return response.json()
    except httpx.HTTPError:
        return {"status": "offline", "model_loaded": False}
