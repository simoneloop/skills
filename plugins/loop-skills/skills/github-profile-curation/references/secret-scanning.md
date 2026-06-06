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

## 2. How to scan (this skill runs an on-demand audit)

This skill is invoked by command and performs a **one-time scan** of the target —
it does NOT install anything. Use the best scanner available; the others are pure
**fallbacks** for when it isn't installed. `scripts/scan-secrets.sh` already
applies this exact order automatically.

```bash
# PRIMARY — TruffleHog: scans the FULL git history AND verifies whether each
# secret is still live, so you know what to rotate first.
trufflehog git file://<path> --fail --no-update
# add --only-verified to list only credentials confirmed still active

# FALLBACK 1 (only if trufflehog is missing) — Gitleaks: fast regex scan.
gitleaks detect --source <path> --no-banner --redact

# FALLBACK 2 (last resort) — ripgrep / git grep over the WORKING TREE only
# (no history!): use only when neither scanner is installed.
rg -n -i '(api[_-]?key|secret|token\s*[=:]|password|AKIA[0-9A-Z]{16}|sk-[A-Za-z0-9]{20,}|\b\d{8,10}:[A-Za-z0-9_-]{30,})' <path>

# Hunt a known secret string across ALL commits (history)
git -C <repo> log -p -S '<secret-substring>' --all
```

> Why TruffleHog first: a `grep`/working-tree scan misses secrets that live only
> in old commits (the exact mistake that leaks tokens). TruffleHog walks the whole
> history; its verification tells you which leaked credentials are still active.
> Gitleaks/grep exist here only so the scan still works where TruffleHog isn't
> present — they add no capability over it.

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
- Enable GitHub **Secret Scanning** + **Push Protection** on the account.
- (Optional, and separate from this on-demand skill) set up a **pre-commit hook**
  so new secrets are blocked *before* they ever reach history — e.g.
  `gitleaks protect --staged` or the official `gitleaks` pre-commit hook. This is
  a one-time setup in the user's own repos, not something this skill performs.
