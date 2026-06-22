# 🧩 simoneloop / skills

> A curated, installable collection of [Claude Code](https://code.claude.com)
> **skills & automations** — packaged as a plugin marketplace.

<p>
  <img src="https://img.shields.io/badge/Claude%20Code-plugin%20marketplace-1C3C3C?style=flat-square&logo=anthropic&logoColor=white" alt="claude code"/>
  <img src="https://img.shields.io/badge/license-MIT-blue?style=flat-square" alt="license"/>
</p>

This repo is both a **marketplace** (`.claude-plugin/marketplace.json`) and a
**plugin** (`loop-skills`) bundling reusable skills. The goal: a best-in-class
home for skills, project setups, and automations I reuse across Claude Code.

📄 **Scope & goals:** [SCOPE.md](SCOPE.md) · **Contributing:** [CONTRIBUTING.md](CONTRIBUTING.md)

## 🚀 Install

```text
/plugin marketplace add simoneloop/skills
/plugin install loop-skills@simoneloop-skills
```

Then invoke a skill (Claude also auto-triggers them from your request):

```text
/loop-skills:glow-up
```

Try locally before publishing changes:

```text
/plugin marketplace add ./        # from the repo root
/plugin validate .
```

## 📚 Skill catalog

| Skill | What it does | Invoke |
|---|---|---|
| **the-forge** | Scaffold a new skill in this repo from the template, with a trigger-optimized description, catalog row, and validation — so contributions pass on the first try. | `/loop-skills:the-forge` |
| **glow-up** | Audit & modernize a GitHub profile for a target professional positioning: repo inventory, secret/PII scanning, public/private/archive curation, git-history cleanup, and a CV-driven profile README + pins. | `/loop-skills:glow-up` |
| **grand-bazaar** | Turn a folder of product photos into a **draft** Etsy listing in one shot: infer style/price/category from the shop's existing listings, write SEO copy + tags, optional multilingual translations & variations, create via Etsy Open API v3. Generic & shop-agnostic — voice/languages come from a personal shop-profile file; drafts only, never auto-publishes. | `/loop-skills:grand-bazaar` |
| **hermes-tweet** | Install and safely operate Hermes Tweet for Hermes Agent X/Twitter workflows: plugin setup, XQUIK_API_KEY configuration, tweet_explore/read/action order, and action gating. | `/loop-skills:hermes-tweet` |
| **next-quest** | For the project open in the working dir, pull its Jira issues via the Atlassian MCP, rank by priority while honoring blocker/blocked-by links, and hand back the single next task to develop (plus the ordered shortlist). Read-only triage — "what should I work on next?". Project key comes from a `.jira-project` file in the repo. | `/loop-skills:next-quest` |

> **Why `glow-up` is different:** it's **safety-first** — secret/PII
> scanning, CV-link protection, git-history scrubbing, and credential-rotation
> guidance — the security layer that SEO/visibility optimizers (e.g.
> claudegithub.com) deliberately skip.

_More skills (project setups, automations) will be added here over time._

## 🗂️ Repo layout

```text
.
├── .claude-plugin/
│   └── marketplace.json              # marketplace manifest (name: simoneloop-skills)
├── plugins/
│   └── loop-skills/
│       ├── .claude-plugin/plugin.json
│       └── skills/
│           └── glow-up/
│               ├── SKILL.md          # entry point (lean; progressive disclosure)
│               ├── references/       # loaded on demand
│               └── scripts/          # executed, not loaded into context
├── scripts/validate-skills.sh        # frontmatter / structure linter (used by CI)
├── .github/                          # CI workflow + PR/issue templates
│   ├── workflows/validate.yml        # manifest + skill validation on every push/PR
│   ├── PULL_REQUEST_TEMPLATE.md
│   └── ISSUE_TEMPLATE/
├── SCOPE.md                          # mission, in/out of scope, quality bar
├── CONTRIBUTING.md
└── LICENSE
```

## 🧭 Conventions (state of the art)

- **One folder per skill**, folder name == skill name, **kebab-case**.
- `SKILL.md` frontmatter: `name` + `description` required; description states
  **what it does AND when to use it**, with concrete trigger phrases.
- Keep `SKILL.md` lean (< 500 lines); push detail to `references/`, code to `scripts/`.
- **Versioning**: no fixed `version` in the manifests — Claude Code uses the git
  commit SHA, so every push ships as a new version (no stale-version trap).
- CI runs structure + manifest validation on every change (see below).

## ✅ Validation

```bash
# Built-in validator (Claude Code CLI)
claude plugin validate .

# Repo's own linter (no auth required; also runs in CI)
bash scripts/validate-skills.sh
```

## 📄 License

[MIT](LICENSE) © Simonpaolo Lopez ([@simoneloop](https://github.com/simoneloop))
