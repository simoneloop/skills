---
name: next-quest
description: >-
  Given the project currently open in the working directory, pull its Jira
  issues via the Atlassian MCP server, rank them by priority while honoring
  blocker/blocked-by links, and hand back the single next task to develop
  (plus the ordered shortlist behind it). Use when the user asks "what should
  I work on next", "what's my next Jira task", "give me the next ticket",
  "cosa sviluppo adesso", "qual è il prossimo task", or wants their backlog
  triaged into one actionable pick for the current repo.
---

# next-quest

<!--
  Standing instructions. Keep lean. The whole flow is: resolve project key →
  query Jira via MCP → classify blocked/blocking from issue links → rank →
  return the next task. No bundled scripts or references needed.
-->

## Setup (run this FIRST, before any other step)
This skill talks to Jira through the **Atlassian MCP server** (Rovo). It needs no
CLI binaries and no secrets of its own — auth is handled by the MCP connection.

1. **Verify the Atlassian MCP is connected.** Use `ToolSearch` with query
   `atlassian jira` and confirm tools like `searchJiraIssuesUsingJql`,
   `getJiraIssue`, and `getAccessibleAtlassianResources` are available. If they
   don't appear, check whether the server merely needs auth vs. isn't added at
   all — run `claude mcp list`:
   - **Listed but "Needs authentication"** (common — the Atlassian connector
     ships with claude.ai): just run `/mcp`, pick **Atlassian**, and complete
     the browser login. Do **not** `claude mcp add` — it would duplicate it.
   - **Not listed at all:** add it, then `/mcp` to log in:
     ```bash
     claude mcp add --transport http atlassian https://mcp.atlassian.com/v1/mcp
     ```
   Auth is **OAuth via browser by default — no token to paste.** An API token
   is only needed for headless/non-interactive setups (passed to the MCP
   config, never committed to `settings.json`). Re-check before continuing.
2. **Load the tool schemas** you'll call via `ToolSearch`
   (`select:searchJiraIssuesUsingJql,getJiraIssue,getAccessibleAtlassianResources`).

Do not continue until setup passes.

## When to use
The user, while working inside a project repo, asks what to build next:
"what's my next task", "next Jira ticket", "what should I pick up",
"cosa faccio adesso", "dammi il prossimo task". The goal is **one** actionable
pick for the **current** project, not a raw issue dump.

## Steps

1. **Resolve the project key from the repo.** Read it from a `.jira-project`
   file at the repo root — a single line holding the Jira project key, e.g.:
   ```
   PROJ
   ```
   - If the file is missing, ask the user for the project key, then offer to
     create `.jira-project` so future runs are config-free. (Tip: add it to
     `.gitignore` if it shouldn't be shared.)
   - An optional second line may hold the site URL
     (`https://yoursite.atlassian.net`); if absent, resolve the cloudId via
     `getAccessibleAtlassianResources` (use the first/only site, or ask if
     there are several).

2. **Query the project's open issues** with `searchJiraIssuesUsingJql`. Default
   JQL (issues assigned to the user that aren't done, highest priority first):
   ```
   project = "<KEY>" AND assignee = currentUser() AND statusCategory != Done
   ORDER BY priority DESC, created ASC
   ```
   Request these fields: `summary, status, priority, issuetype, issuelinks,
   description, assignee`. If the user wants the whole team backlog, drop the
   `assignee` clause; if they want ready-to-pick unassigned work too, widen to
   `(assignee = currentUser() OR assignee IS EMPTY)`.

3. **Classify blocked vs. blocking** from each issue's `issuelinks`:
   - **Blocked** — has an inward `is blocked by` link to an issue whose status
     category is **not** Done. These are *not* startable now.
   - **Blocking** — has an outward `blocks` link to other open issues. Starting
     these unblocks downstream work → higher impact.
   - If a linked issue's status isn't in the payload, fetch it with
     `getJiraIssue` only when it's decisive for the pick (avoid over-fetching).

4. **Rank and pick the next task.** Order the *startable* (non-blocked) issues by:
   1. Jira **priority** (Highest → Lowest),
   2. then **blocking** issues first (they free up others),
   3. then oldest `created` as a tiebreaker.
   The **next task** is the top of this list. If every issue is blocked, say so
   explicitly and surface the blockers (so the user knows what to chase) rather
   than forcing a pick.

5. **Report.** Lead with the single pick, then the shortlist:
   ```
   ▶ Next: PROJ-142 — "Add OAuth token refresh"  [High · blocks PROJ-150]
     Why: highest startable priority and unblocks PROJ-150.
     <2–3 line summary of the description / acceptance criteria>

   Then:
     2. PROJ-138 — "..."  [High]
     3. PROJ-151 — "..."  [Medium · blocked by PROJ-149 ⛔ skipped]
   ```
   Use clickable issue keys/links when the site URL is known. Keep it short —
   the user wants a decision, not the full board.

## Notes / gotchas
- **Strictly read-only.** This skill only fetches, ranks, and reports. Use
  **only** read/search Jira tools (`searchJiraIssuesUsingJql`, `getJiraIssue`,
  `getAccessibleAtlassianResources`). **Never** call any write tool
  (`createJiraIssue`, `editJiraIssue`, `transitionJiraIssue`,
  `addCommentToJiraIssue`, `createIssueLink`, etc.) — it must not create,
  modify, assign, transition, or comment on anything in Jira.
- **Priority names vary** per Jira instance (Highest/High/… vs P1/P2/…).
  `ORDER BY priority DESC` respects the instance's own priority scheme, so trust
  it rather than hard-coding labels.
- **Blocked ≠ Done blocker.** A `blocked by` link to an issue already Done does
  **not** block — only count blockers whose statusCategory isn't Done.
- **cloudId format:** when the Atlassian MCP expects it as
  `https://yoursite.atlassian.net`, pass that and skip
  `getAccessibleAtlassianResources`; otherwise resolve the cloudId first.
- Keep the JQL deterministic — the value of this skill over a raw "list my
  issues" is the consistent ranking, so don't improvise the ordering.
