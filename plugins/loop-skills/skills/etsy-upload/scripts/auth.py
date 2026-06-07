"""One-time OAuth 2.0 (PKCE) flow for Etsy Open API v3.

Run once:
    python3 auth.py

Opens the browser, captures the callback on http://localhost:3003/oauth/callback,
exchanges the code for tokens, and writes them to the data dir's .auth.json
(default ~/.claude/etsy-tools/.auth.json, override with ETSY_TOOLS_DIR).
"""
from __future__ import annotations

import base64
import hashlib
import http.server
import json
import secrets
import sys
import threading
import time
import urllib.parse
import urllib.request
import webbrowser
from pathlib import Path

ROOT = Path(__file__).resolve().parent
sys.path.insert(0, str(ROOT))
from etsy import AUTH_PATH, CONFIG_PATH, TOKEN_URL, load_config, save_auth  # noqa: E402

AUTHORIZE_URL = "https://www.etsy.com/oauth/connect"


def _pkce_pair() -> tuple[str, str]:
    verifier = base64.urlsafe_b64encode(secrets.token_bytes(48)).rstrip(b"=").decode()
    digest = hashlib.sha256(verifier.encode()).digest()
    challenge = base64.urlsafe_b64encode(digest).rstrip(b"=").decode()
    return verifier, challenge


class _CallbackHandler(http.server.BaseHTTPRequestHandler):
    captured: dict = {}

    def log_message(self, *_a, **_kw) -> None:  # silenzia stderr
        pass

    def do_GET(self) -> None:  # noqa: N802
        parsed = urllib.parse.urlparse(self.path)
        if parsed.path != "/oauth/callback":
            self.send_response(404)
            self.end_headers()
            return
        q = urllib.parse.parse_qs(parsed.query)
        _CallbackHandler.captured = {k: v[0] for k, v in q.items()}
        self.send_response(200)
        self.send_header("Content-Type", "text/html; charset=utf-8")
        self.end_headers()
        self.wfile.write(
            b"<html><body style='font-family:sans-serif;padding:2em'>"
            b"<h2>Autenticazione completata.</h2>"
            b"<p>Puoi chiudere questa scheda e tornare al terminale.</p>"
            b"</body></html>"
        )


def main() -> None:
    cfg = load_config()
    if cfg.get("client_secret", "").startswith("PASTE_"):
        sys.exit(
            f"Inserisci la shared secret in {CONFIG_PATH} (campo client_secret) prima di procedere."
        )

    redirect_uri = cfg["redirect_uri"]
    parsed_redirect = urllib.parse.urlparse(redirect_uri)
    port = parsed_redirect.port or 80

    verifier, challenge = _pkce_pair()
    state = secrets.token_urlsafe(16)

    params = {
        "response_type": "code",
        "client_id": cfg["client_id"],
        "redirect_uri": redirect_uri,
        "scope": cfg["scopes"],
        "state": state,
        "code_challenge": challenge,
        "code_challenge_method": "S256",
    }
    auth_url = AUTHORIZE_URL + "?" + urllib.parse.urlencode(params)

    server = http.server.HTTPServer(("127.0.0.1", port), _CallbackHandler)
    thread = threading.Thread(target=server.serve_forever, daemon=True)
    thread.start()

    print(f"Apro il browser per autorizzare l'app su Etsy ({redirect_uri})…")
    print(f"Se non si apre, vai a:\n  {auth_url}\n")
    webbrowser.open(auth_url)

    deadline = time.time() + 300
    while not _CallbackHandler.captured and time.time() < deadline:
        time.sleep(0.2)
    server.shutdown()

    cap = _CallbackHandler.captured
    if not cap:
        sys.exit("Timeout: nessuna callback ricevuta entro 5 minuti.")
    if cap.get("state") != state:
        sys.exit("Errore: state mismatch (possibile CSRF).")
    if "error" in cap:
        sys.exit(f"Etsy ha restituito errore: {cap}")
    code = cap.get("code")
    if not code:
        sys.exit(f"Nessun authorization code nella callback: {cap}")

    body = urllib.parse.urlencode({
        "grant_type": "authorization_code",
        "client_id": cfg["client_id"],
        "redirect_uri": redirect_uri,
        "code": code,
        "code_verifier": verifier,
    }).encode()
    req = urllib.request.Request(
        TOKEN_URL, data=body, method="POST",
        headers={"Content-Type": "application/x-www-form-urlencoded"},
    )
    with urllib.request.urlopen(req, timeout=30) as resp:
        tok = json.loads(resp.read())

    auth = {
        "access_token": tok["access_token"],
        "refresh_token": tok["refresh_token"],
        "expires_at": int(time.time()) + int(tok["expires_in"]) - 60,
        "scopes": cfg["scopes"],
        "user_id": tok["access_token"].split(".", 1)[0],
    }
    save_auth(auth)
    print(f"\n✓ Token salvati in {AUTH_PATH}")
    print(f"  user_id Etsy: {auth['user_id']}")
    print("  prossimo step: python3 get_shop_info.py")


if __name__ == "__main__":
    main()
