# Visibility curation with `gh`

## Commands

```bash
# Inventory (structured)
gh repo list --limit 200 --json name,visibility,isFork,isArchived,primaryLanguage,pushedAt,stargazerCount

# Make private (required flag avoids the interactive consequences prompt)
gh repo edit OWNER/REPO --visibility private --accept-visibility-change-consequences

# Make public (only after a clean secret scan!)
gh repo edit OWNER/REPO --visibility public --accept-visibility-change-consequences

# Archive (read-only)
gh repo archive OWNER/REPO --yes

# Delete (needs delete_repo scope)
gh repo delete OWNER/REPO --yes
```

## Gotchas (learned the hard way)

1. **Set visibility BEFORE archiving.** An archived repo is read-only — `gh repo
   edit` fails on it. So: `--visibility private` first, then `archive`.
2. **`delete` needs the `delete_repo` scope**, which the default `gh` token lacks.
   If you get `HTTP 403: Must have admin rights` / "needs the delete_repo scope",
   the user runs `gh auth refresh -h github.com -s delete_repo` (interactive),
   then retry. Until then, fall back to making the repo **private**.
3. **CV-linked repos are off-limits for privating.** If the user's CV/portfolio
   links `github.com/owner/repo`, making it private 404s that link. Keep public.
4. **Making a repo private loses** its stars, watchers, forks visibility, and
   traffic. Making one public exposes its **entire git history** — scan first.
5. **Forks add noise.** A bare fork of a popular library (no own commits) dilutes
   the profile; private/archive or delete it.
6. **Effects on the profile contribution graph**: private repo contributions only
   show if the user enables "Include private contributions" in profile settings.

## Batch pattern
Drive changes from the approved classification table. Echo each action's result
(OK/FAIL + reason) so failures (e.g. missing scope, archived-edit) are visible
rather than silently skipped. Retry transient GraphQL archive failures once.
