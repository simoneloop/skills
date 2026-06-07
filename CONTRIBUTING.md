# Contributing

Thanks for improving this skills collection. Keep it lean, validated, and
trigger-optimized.

## Add a new skill

0. **Research prior art first (required).** Search the web for existing
   skills/tools that already do this (Anthropic's `anthropics/skills`, community
   marketplaces, `awesome-claude-*`, comparable tools). Summarize in your PR: what
   gaps you fill, what better approach you adopt, and how novel/valuable this is.
   If a near-duplicate already exists, improve it or link to it instead of adding
   one. (The `skill-creator` skill does this step for you.) See
   [SCOPE.md](SCOPE.md).
1. Create a folder under the plugin:
   `plugins/loop-skills/skills/<kebab-case-name>/SKILL.md`
2. Frontmatter — `name` + `description` are required:
   ```yaml
   ---
   name: my-skill
   description: >-
     What it does AND when to use it, with concrete trigger phrases. Use when
     the user asks to <X>, <Y>, or <Z>.
   ---
   ```
   - Lead the description with the key use case; name the situations that should
     trigger it. The description is the **only** discovery signal.
   - Keep `SKILL.md` under ~500 lines. Put long docs in `references/` (loaded on
     demand) and code in `scripts/` (executed, not loaded into context).
   - Reference bundled files with markdown links and `${CLAUDE_SKILL_DIR}/...`.
3. Add a row to the **Skill catalog** table in `README.md`.

## Conventions

- **kebab-case** for skill/plugin/marketplace names (`[a-z0-9-]+`). The validator
  and the Claude.ai marketplace sync reject other casing.
- **One folder per skill**; folder name == skill name.
- **Self-contained setup** — if a skill needs a CLI or a credential, it must include
  a `## Setup (run first)` section that, as its first action, checks prerequisites
  and guides the user (tokens → `.claude/settings.local.json`, auto-gitignored).
  Don't make users configure something a *different* skill needs (no plugin-wide
  token prompts).
- **No `version`** in `plugin.json` / marketplace entry — we ship by commit SHA so
  every push is a new version. (If you ever add `version`, you must bump it on
  every release or users get no updates, and never set it in both places.)
- **No `..`** in plugin `source` paths.

## Validate before pushing

```bash
bash scripts/validate-skills.sh     # structure + manifests (no auth)
claude plugin validate .            # built-in validator (Claude Code CLI)
```

CI (`.github/workflows/validate.yml`) runs the same checks on every push/PR.

## Test locally

```text
/plugin marketplace add ./
/plugin install loop-skills@simoneloop-skills
/reload-plugins        # picks up SKILL.md edits during a session
```
