#!/usr/bin/env bash
# scan-secrets.sh — scan a repo (clone or local path) for secrets & PII.
# Usage:
#   scan-secrets.sh owner/repo      # clones to a temp dir, then scans (incl. history if gitleaks)
#   scan-secrets.sh /path/to/repo   # scans an existing checkout
# Requires: ripgrep (rg) or grep. Uses gitleaks and gh if available.
set -uo pipefail

TARGET="${1:-}"
[ -z "$TARGET" ] && { echo "usage: scan-secrets.sh <owner/repo | path>"; exit 2; }
GH="${GH_BIN:-gh}"

cleanup() { [ -n "${TMP:-}" ] && [ -d "${TMP:-}" ] && rm -rf "$TMP"; }
trap cleanup EXIT

if [ -d "$TARGET/.git" ] || [ -d "$TARGET" ]; then
  REPO_DIR="$TARGET"
else
  TMP="$(mktemp -d)"
  echo ">> cloning $TARGET ..."
  "$GH" repo clone "$TARGET" "$TMP" -- --quiet || { echo "clone failed"; exit 1; }
  REPO_DIR="$TMP"
fi

echo "== scanning: $REPO_DIR =="

PATTERN='(?i)(api[_-]?key|client_secret|secret\s*[=:]|password\s*[=:]|passwd|bearer |AKIA[0-9A-Z]{16}|sk-[A-Za-z0-9]{20,}|gh[pousr]_[A-Za-z0-9]{30,}|\b[0-9]{8,10}:[A-Za-z0-9_-]{30,}\b|-----BEGIN [A-Z ]*PRIVATE KEY-----|(mongodb(\+srv)?|postgres|mysql)://[^[:space:]]+)'

found=0

if command -v gitleaks >/dev/null 2>&1; then
  echo "-- gitleaks (full history) --"
  gitleaks detect --source "$REPO_DIR" --no-banner --redact -v && echo "gitleaks: clean" || found=1
else
  echo "-- gitleaks not installed; grepping working tree only (history NOT scanned) --"
fi

echo "-- pattern grep (working tree) --"
SCANNER="grep -REn"
command -v rg >/dev/null 2>&1 && SCANNER="rg -n --no-heading"
if $SCANNER -e "$PATTERN" "$REPO_DIR" --glob '!.git' 2>/dev/null | grep -v -E '\.(png|jpg|jpeg|wav|ogg)$'; then
  found=1
fi

echo "-- suspicious filenames (PII / secret stores) --"
find "$REPO_DIR" -path '*/.git' -prune -o -type f \
  \( -iname 'passwords' -o -iname '*.env' -o -iname '*.pem' -o -iname '*.pkl' \
     -o -iname '*.xlsx' -o -iname 'cookies*' -o -iname '*cellulari*' \) -print 2>/dev/null && found=1

echo
if [ "$found" -eq 0 ]; then
  echo "RESULT: clean (no obvious secrets/PII in working tree)."
else
  echo "RESULT: POTENTIAL SECRETS/PII FOUND — review above. Do NOT make this repo public until cleaned & credentials rotated."
fi
