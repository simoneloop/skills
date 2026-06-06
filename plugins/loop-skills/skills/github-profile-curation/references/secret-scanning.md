# Secret & PII scanning, history scrub, and rotation

## 1. What to look for

Credentials and personal data that must never sit in a public repo:

| Category | Examples / patterns |
|---|---|
| Generic tokens/keys | `api[_-]?key`, `secret`, `token\s*[=:]`, `bearer`, `client_secret` |
| Cloud | AWS `AKIA[0-9A-Z]{16}`, `aws_secret_access_key`, GCP `private_key`, `BEGIN RSA/PRIVATE KEY` |
| Provider keys | OpenAI `sk-[A-Za-z0-9]{20,}`, GitHub `gh[pousr]_[A-Za-z0-9]{36,}` |
| Telegram bot | `\d{8,10}:[A-Za-z0-9_-]{30,}` |
| DB URIs | `mongodb(\+srv)?://`, `postgres://`, `mysql://…:…@` |
| Passwords | `password\s*[=:]`, files literally named `passwords`, `.env`, `*.pkl` cookies |
| PII | emails, phone numbers, national IDs (e.g. Italian codice fiscale), name/number lists, spreadsheets |

## 2. How to scan

Prefer a dedicated scanner when available; fall back to grep.

```bash
# Best: gitleaks scans the FULL history, not just the working tree
gitleaks detect --source <path> --no-banner

# Fallback: ripgrep / git grep over the working tree
rg -n -i '(api[_-]?key|secret|token\s*[=:]|password|AKIA[0-9A-Z]{16}|sk-[A-Za-z0-9]{20,}|\b\d{8,10}:[A-Za-z0-9_-]{30,})' <path>

# Scan history for a known string across all commits
git -C <repo> log -p -S '<secret-substring>' --all
```

The bundled `scripts/scan-secrets.sh` clones (or takes a path) and runs the
above, preferring `gitleaks` if installed.

> When reporting findings, **redact the secret values** (show prefix + length),
> never paste full credentials back into chat.

## 3. Remediation order (important)

1. **Rotate / revoke the credential first.** A secret that was ever public is
   compromised; scrubbing the repo does not change that. Examples:
   - Telegram: @BotFather → `/revoke`
   - OpenAI/cloud: delete & recreate the key
   - Passwords: change them on the actual service
2. **Clean the working tree**: replace hardcoded values with
   `os.environ[...]` / config; delete files that are pure secrets or PII; commit.
3. **Scrub history** (only with explicit approval — it's a force-push):

```bash
# Option A — purge specific paths/strings across all history (preserves commits)
git filter-repo --invert-paths --path passwords --path secrets.env
git filter-repo --replace-text <(echo 'literalsecret==>REDACTED')

# Option B — nuke history entirely into one clean commit (simplest, total scrub)
git checkout --orphan _clean
git add -A
git commit -m "Initial commit"
git branch -D master 2>/dev/null; git branch -m master   # or main
git push --force origin master
```

4. **Note the residual risk**: even after a force-push, the host (GitHub) may keep
   unreachable commits accessible by direct SHA until garbage collection. Because
   the credential is already rotated, the leak is neutralized; for total certainty
   the user can ask GitHub Support to purge cached views.

## 4. Prevent recurrence
- Add a `.gitignore` for `.env`, `*.pkl`, key files, data dumps.
- Suggest enabling GitHub **Secret Scanning** + **Push Protection** on the account.
