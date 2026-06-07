"""Etsy Open API v3 client (stdlib only).

Loads config + tokens, auto-refreshes the access token, exposes thin helpers
for the endpoints used by the etsy-upload skill.

Config and tokens live OUTSIDE this repo so secrets are never committed:
the data dir defaults to ~/.claude/etsy-tools/ and can be overridden with the
ETSY_TOOLS_DIR environment variable.
"""
from __future__ import annotations

import json
import mimetypes
import os
import time
import urllib.parse
import urllib.request
import uuid
from pathlib import Path
from typing import Any

DATA_DIR = Path(os.environ.get("ETSY_TOOLS_DIR", str(Path.home() / ".claude" / "etsy-tools"))).expanduser()
CONFIG_PATH = DATA_DIR / "config.json"
AUTH_PATH = DATA_DIR / ".auth.json"

API_BASE = "https://openapi.etsy.com/v3/application"
TOKEN_URL = "https://api.etsy.com/v3/public/oauth/token"


class EtsyError(RuntimeError):
    pass


def load_config() -> dict:
    if not CONFIG_PATH.exists():
        raise EtsyError(
            f"Config mancante: {CONFIG_PATH}. Copia config.example.json dello skill "
            f"in questa cartella e inserisci client_id/client_secret."
        )
    return json.loads(CONFIG_PATH.read_text())


def save_config(cfg: dict) -> None:
    DATA_DIR.mkdir(parents=True, exist_ok=True)
    CONFIG_PATH.write_text(json.dumps(cfg, indent=2) + "\n")


def load_auth() -> dict:
    if not AUTH_PATH.exists():
        raise EtsyError(
            f"File .auth.json mancante ({AUTH_PATH}). Esegui prima il flow OAuth: auth.py"
        )
    return json.loads(AUTH_PATH.read_text())


def save_auth(auth: dict) -> None:
    DATA_DIR.mkdir(parents=True, exist_ok=True)
    AUTH_PATH.write_text(json.dumps(auth, indent=2) + "\n")
    AUTH_PATH.chmod(0o600)


def _http(method: str, url: str, *, headers: dict | None = None,
          data: bytes | None = None, timeout: int = 30) -> tuple[int, bytes]:
    req = urllib.request.Request(url, data=data, method=method, headers=headers or {})
    try:
        with urllib.request.urlopen(req, timeout=timeout) as resp:
            return resp.status, resp.read()
    except urllib.error.HTTPError as e:
        return e.code, e.read()


def refresh_access_token() -> dict:
    cfg = load_config()
    auth = load_auth()
    body = urllib.parse.urlencode({
        "grant_type": "refresh_token",
        "client_id": cfg["client_id"],
        "refresh_token": auth["refresh_token"],
    }).encode()
    status, raw = _http("POST", TOKEN_URL,
                        headers={"Content-Type": "application/x-www-form-urlencoded"},
                        data=body)
    if status != 200:
        raise EtsyError(f"Refresh token fallito ({status}): {raw.decode(errors='replace')}")
    tok = json.loads(raw)
    auth.update({
        "access_token": tok["access_token"],
        "refresh_token": tok.get("refresh_token", auth["refresh_token"]),
        "expires_at": int(time.time()) + int(tok["expires_in"]) - 60,
    })
    save_auth(auth)
    return auth


def get_access_token() -> str:
    auth = load_auth()
    if auth.get("expires_at", 0) <= int(time.time()):
        auth = refresh_access_token()
    return auth["access_token"]


def _auth_headers() -> dict:
    cfg = load_config()
    return {
        "Authorization": f"Bearer {get_access_token()}",
        "x-api-key": f"{cfg['client_id']}:{cfg['client_secret']}",
    }


def api(method: str, path: str, *, params: dict | None = None,
        json_body: dict | None = None, form: dict | None = None) -> Any:
    """Call an Etsy API endpoint. Returns parsed JSON (or raises EtsyError)."""
    url = API_BASE + path
    if params:
        url += "?" + urllib.parse.urlencode({k: v for k, v in params.items() if v is not None})
    headers = _auth_headers()
    data: bytes | None = None
    if json_body is not None:
        data = json.dumps(json_body).encode()
        headers["Content-Type"] = "application/json"
    elif form is not None:
        data = urllib.parse.urlencode(form, doseq=True).encode()
        headers["Content-Type"] = "application/x-www-form-urlencoded"
    status, raw = _http(method, url, headers=headers, data=data)
    if status >= 400:
        raise EtsyError(f"{method} {path} → {status}: {raw.decode(errors='replace')}")
    if not raw:
        return None
    return json.loads(raw)


def upload_image(shop_id: int, listing_id: int, image_path: Path, rank: int = 1,
                 alt_text: str | None = None) -> dict:
    """Upload an image as multipart/form-data to a draft listing."""
    boundary = "----etsyboundary" + uuid.uuid4().hex
    mime = mimetypes.guess_type(image_path.name)[0] or "image/jpeg"
    parts: list[bytes] = []

    def add_field(name: str, value: str) -> None:
        parts.append(f"--{boundary}\r\n".encode())
        parts.append(f'Content-Disposition: form-data; name="{name}"\r\n\r\n'.encode())
        parts.append(value.encode() + b"\r\n")

    add_field("rank", str(rank))
    if alt_text:
        add_field("alt_text", alt_text[:250])

    parts.append(f"--{boundary}\r\n".encode())
    parts.append(
        f'Content-Disposition: form-data; name="image"; filename="{image_path.name}"\r\n'.encode()
    )
    parts.append(f"Content-Type: {mime}\r\n\r\n".encode())
    parts.append(image_path.read_bytes())
    parts.append(b"\r\n")
    parts.append(f"--{boundary}--\r\n".encode())
    body = b"".join(parts)

    url = f"{API_BASE}/shops/{shop_id}/listings/{listing_id}/images"
    headers = _auth_headers()
    headers["Content-Type"] = f"multipart/form-data; boundary={boundary}"
    status, raw = _http("POST", url, headers=headers, data=body, timeout=120)
    if status >= 400:
        raise EtsyError(f"Upload immagine fallito ({status}): {raw.decode(errors='replace')}")
    return json.loads(raw)


def upload_video(shop_id: int, listing_id: int, video_path: Path,
                 name: str | None = None) -> dict:
    """Upload a video (max 1 per listing) as multipart/form-data."""
    boundary = "----etsyboundary" + uuid.uuid4().hex
    mime = mimetypes.guess_type(video_path.name)[0] or "video/mp4"
    parts: list[bytes] = []

    def add_field(field_name: str, value: str) -> None:
        parts.append(f"--{boundary}\r\n".encode())
        parts.append(f'Content-Disposition: form-data; name="{field_name}"\r\n\r\n'.encode())
        parts.append(value.encode() + b"\r\n")

    if name:
        add_field("name", name[:200])

    parts.append(f"--{boundary}\r\n".encode())
    parts.append(
        f'Content-Disposition: form-data; name="video"; filename="{video_path.name}"\r\n'.encode()
    )
    parts.append(f"Content-Type: {mime}\r\n\r\n".encode())
    parts.append(video_path.read_bytes())
    parts.append(b"\r\n")
    parts.append(f"--{boundary}--\r\n".encode())
    body = b"".join(parts)

    url = f"{API_BASE}/shops/{shop_id}/listings/{listing_id}/videos"
    headers = _auth_headers()
    headers["Content-Type"] = f"multipart/form-data; boundary={boundary}"
    status, raw = _http("POST", url, headers=headers, data=body, timeout=300)
    if status >= 400:
        raise EtsyError(f"Upload video fallito ({status}): {raw.decode(errors='replace')}")
    return json.loads(raw)


def set_inventory(listing_id: int, *, variations: dict) -> dict:
    """Set listing variations as inventory.

    variations = {
        "property_name": "Size",
        "property_id": 513,   # optional, default 513 (custom property 1)
        "options": [
            {"name": "S", "price": 165.0, "quantity": 1, "sku": "..."},
            {"name": "M", "price": 165.0, "quantity": 1, "sku": "..."},
        ],
    }
    """
    prop_id = variations.get("property_id", 513)
    prop_name = variations["property_name"]
    options = variations["options"]
    cfg = load_config()
    readiness_state_id = variations.get("readiness_state_id") or cfg.get("default_readiness_state_id")

    products = []
    for opt in options:
        offering = {
            "price": float(opt["price"]),
            "quantity": int(opt.get("quantity", 1)),
            "is_enabled": True,
        }
        if readiness_state_id:
            offering["readiness_state_id"] = readiness_state_id
        products.append({
            "sku": opt.get("sku", ""),
            "property_values": [{
                "property_id": prop_id,
                "property_name": prop_name,
                "values": [opt["name"]],
                "value_ids": [],
                "scale_id": None,
            }],
            "offerings": [offering],
        })
    body = {
        "products": products,
        "price_on_property": [prop_id],
        "quantity_on_property": [prop_id],
        "sku_on_property": [prop_id],
    }
    return api("PUT", f"/listings/{listing_id}/inventory", json_body=body)


def set_variation_translation(shop_id: int, listing_id: int, property_id: int,
                              language: str, *, property_name: str,
                              values: list[str]) -> dict:
    """Translate a variation property (name + value labels) for a given language.

    Etsy expects `values` in the same order as the products' property_values
    when set_inventory was called.
    """
    form = {"property_name": property_name, "values": ",".join(values)}
    path = (f"/shops/{shop_id}/listings/{listing_id}/inventory/property/"
            f"{property_id}/translation/{language}")
    try:
        return api("POST", path, form=form)
    except EtsyError as e:
        if "already exists" in str(e).lower() or "409" in str(e):
            return api("PUT", path, form=form)
        raise


def set_translation(shop_id: int, listing_id: int, language: str, *,
                    title: str, description: str,
                    tags: list[str] | None = None) -> dict:
    """Create or update a translation for a listing in a given language."""
    form = {"title": title[:140], "description": description}
    if tags:
        form["tags"] = ",".join(tags)
    path = f"/shops/{shop_id}/listings/{listing_id}/translations/{language}"
    try:
        return api("POST", path, form=form)
    except EtsyError as e:
        if "already exists" in str(e).lower() or "409" in str(e):
            return api("PUT", path, form=form)
        raise
