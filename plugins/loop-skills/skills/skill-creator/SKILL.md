---
name: skill-creator
description: >-
  Scaffold a new Claude Code skill in this repository following its conventions.
  Use when the user wants to create or add a new skill, start a SKILL.md, bootstrap
  a skill folder, or contribute a skill to this marketplace. Generates the skill
  directory and a SKILL.md from the template, helps write a trigger-optimized
  description, adds the catalog row in README, and validates the result.
---

# Skill Creator

Bootstraps a new skill inside this repo so it matches the project's conventions
and passes validation on the first try.

## When to use
The user says something like "add a skill that…", "create a new skill",
"scaffold a SKILL.md", or "I want to contribute a skill here".

## Steps

1. **Clarify the skill.** Ask for (or infer):
   - A short **kebab-case name** (`[a-z0-9-]+`, gerund form where natural, e.g.
     `reviewing-prs`). This becomes the folder name AND the `name` frontmatter.
   - The **purpose**: what it does and — crucially — **when it should trigger**
     (the concrete situations/phrases). This drives the `description`.
   - Whether it needs `references/` (long docs) and/or `scripts/` (helper code).

2. **Research prior art on the web (required).** Before writing anything, search
   the web for existing skills/tools/approaches that solve the same problem —
   Anthropic's official skills (`anthropics/skills`), community plugin
   marketplaces, `awesome-claude-*` lists, and comparable non-Claude tools. Use
   `WebSearch`/`WebFetch`. Then report to the user a short synthesis covering:
   - **Gaps** — capabilities the existing solutions miss that this skill should cover.
   - **Better approach** — proven patterns worth adopting instead of reinventing.
   - **Novelty / quality / rarity** — how common or valuable this idea is, and an
     honest recommendation: build it, build a differentiated version, or just point
     the user at an existing solution (and skip creating a near-duplicate).
   Let the user steer based on this before scaffolding. Capture the prior-art
   summary so it can go into the PR description (see [SCOPE.md](../../../../SCOPE.md)).

3. **Create the folder** under the plugin:
   `plugins/loop-skills/skills/<name>/`

4. **Generate `SKILL.md`** from the template at
   `${CLAUDE_SKILL_DIR}/assets/SKILL.template.md`. Replace the placeholders:
   - `{{SKILL_NAME}}` → the kebab-case name
   - `{{DESCRIPTION}}` → a description that states **what it does AND when to use
     it**, leading with the key use case and naming trigger phrases (this is the
     ONLY discovery signal — be specific, even "pushy").
   - `{{BODY}}` → the standing instructions (keep the whole file < 500 lines).
   Add `references/` and `scripts/` subfolders only if needed; reference bundled
   files with markdown links and `${CLAUDE_SKILL_DIR}/...`.

5. **Register it in the catalog.** Add a row to the **Skill catalog** table in
   the repo `README.md`: name, one-line description, and invoke command
   `/loop-skills:<name>`.

6. **Validate** before finishing:
   ```bash
   bash scripts/validate-skills.sh     # structure + manifests (no auth)
   claude plugin validate .            # official validator (if CLI available)
   ```
   Fix any error the linter reports (missing `name`/`description`, non-kebab-case
   folder, invalid manifest). Warnings (e.g. missing `version`) are acceptable.

7. **Tell the user how to load it**: from a local install, `/reload-plugins`
   picks up the new skill; from a GitHub install, push then
   `/plugin marketplace update`.

## Conventions to enforce
- kebab-case names; one folder per skill; folder name == `name`.
- Lean `SKILL.md`; detail in `references/`, code in `scripts/`.
- No `version` in manifests (ship by commit SHA).
- See [CONTRIBUTING.md](../../../../CONTRIBUTING.md) for the full contributor flow.
