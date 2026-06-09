---
name: {{SKILL_NAME}}
description: >-
  {{DESCRIPTION}}
  Use when the user wants to <X>, <Y>, or <Z>.
---

# {{SKILL_NAME}}

<!--
  Standing instructions for this skill (applied throughout the task, not a one-time
  script). Keep this file under ~500 lines. Move long reference docs into
  references/ (loaded on demand) and executable helpers into scripts/ (run, not
  loaded into context). Reference bundled files with markdown links and
  ${CLAUDE_SKILL_DIR}/...
-->

## Setup (run this FIRST, before any other step)
This skill needs the items below. On invocation, verify each and guide the user to
fix anything missing **before** doing the skill's real work. If the skill needs
none of these, delete this whole section.

- **Tools / CLIs:** {{REQUIRED_TOOLS}} — check with `command -v <tool>`; if missing,
  give the install command for the user's OS (winget / brew / apt).
- **Credentials / env vars (secrets):** {{REQUIRED_KEYS}} — read from the
  environment / Claude Code settings. If missing, guide the user to add them to
  **`.claude/settings.local.json`** (auto-gitignored — NEVER the shared
  `settings.json`):
  ```json
  { "env": { "{{ENV_KEY}}": "<value>" } }
  ```
  Then re-check (a new session picks them up). Do not continue until setup passes.

## When to use
Describe the concrete situations and user phrases that should trigger this skill.

## Steps
1. ...
2. ...
3. ...

## Notes / gotchas
- ...

{{BODY}}
