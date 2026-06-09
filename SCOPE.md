# Scope

## Mission
A curated, installable collection of **Claude Code skills, automations, and
per-project setups** that are genuinely reusable across many projects — not
throwaway snippets. Packaged as a plugin marketplace so anyone can install it
with one command.

## Goal
Be the **state of the art** for repositories of this kind: cleanly structured,
validated in CI, trigger-optimized, well-documented, and easy to contribute to.
Every addition should raise the bar, not just the count.

## Positioning
Where comparable tools optimize for **visibility/SEO**, this collection leads with
**safety**: e.g. `glow-up` does secret/PII scanning, CV-link
protection, history scrubbing, and credential-rotation guidance — the security
layer that SEO-style profile optimizers deliberately skip. Prior-art research
(required for every skill) keeps each addition genuinely differentiated.

## In scope
- **Skills** (`SKILL.md`) that encode reusable workflows or know-how.
- **Automations** (scripts/hooks) that remove repetitive manual work.
- **Project setups** — opinionated Claude Code bootstrap for common stacks
  (`.claude/` scaffolding, settings, agents, commands).
- Supporting **references** and **assets** that make the above work well.

## Out of scope
- One-off, project-specific code with no reuse value.
- Anything containing secrets, credentials, or personal/third-party data.
- Skills that duplicate an existing one here without a clear improvement.
- Vendor lock-in or content that only works in a single private context.

## Quality bar (every skill must…)
1. **Earn its place** — checked against prior art on the web first (see below);
   it should fill a gap, improve on what exists, or be meaningfully rarer/better.
2. **Trigger reliably** — a `description` stating what it does AND when to use it.
3. **Stay lean** — `SKILL.md` < 500 lines; detail in `references/`, code in `scripts/`.
4. **Be generic with safe defaults** — usable by anyone; destructive/outward-facing
   actions require confirmation.
5. **Pass validation** — `scripts/validate-skills.sh` and `claude plugin validate .`.
6. **Be documented** — a row in the README catalog.

## Prior-art research (required before creating any skill)
Before building a skill, **research what already exists on the web** (Anthropic's
official skills, community marketplaces, awesome-lists, comparable tools). Use the
findings to:
1. **Spot gaps** — capabilities you're missing or should add.
2. **Adopt a better approach** — proven patterns beat reinventing.
3. **Judge novelty & quality** — understand how rare/valuable the contribution is,
   and whether it's worth adding versus pointing at an existing solution.

The `the-forge` skill performs this step automatically; contributors should do
the same and summarize the prior art in their PR.

## Conventions
See [CONTRIBUTING.md](CONTRIBUTING.md) and the **Conventions** section of the
[README](README.md).
