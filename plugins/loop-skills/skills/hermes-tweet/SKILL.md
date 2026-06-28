---
name: hermes-tweet
description: >-
  Install, configure, and safely use Hermes Tweet, the Hermes Agent X/Twitter
  plugin powered by Xquik. Use when the user asks to set up Hermes Tweet,
  connect Hermes Agent to X/Twitter, run tweet_explore, tweet_read, or
  tweet_action, validate XQUIK_API_KEY setup, troubleshoot plugin loading, or
  plan guarded social media automation through Hermes Agent.
---

# Hermes Tweet

Use this skill to install and operate Hermes Tweet as a Hermes Agent plugin for
X/Twitter workflows. Keep setup local, keep secrets out of chat, and require
explicit approval before any outward-facing action.

## Setup (run first)

1. Check the local prerequisites before editing files or running the plugin:

   ```bash
   command -v hermes >/dev/null || echo "Install Hermes Agent first."
   command -v python3 >/dev/null || echo "Python 3 is required for pip fallback."
   ```

2. Install and enable Hermes Tweet:

   ```bash
   hermes plugins install Xquik-dev/hermes-tweet --enable
   ```

3. If the Hermes Agent virtual environment needs the package explicitly, install
   the PyPI distribution into that environment:

   ```bash
   ~/.hermes/hermes-agent/venv/bin/python -m pip install hermes-tweet
   ```

4. Store runtime settings in a local ignored file or shell environment. Do not
   paste the real API key into chat, commits, issue text, or logs:

   ```json
   {
     "env": {
       "XQUIK_API_KEY": "xq_...",
       "HERMES_TWEET_ENABLE_ACTIONS": "false"
     }
   }
   ```

## Operating flow

1. Start with `tweet_explore`. It is ungated and does not require network access,
   so use it to inspect the plugin surface and expected parameters.
2. Use `tweet_read` only after `XQUIK_API_KEY` is configured. Parse the JSON
   string result before summarizing it for the user.
3. Use `tweet_action` only when `HERMES_TWEET_ENABLE_ACTIONS=true` and the user
   has approved the exact outward-facing action. Leave actions disabled by
   default.
4. For copied URLs or catalog examples, stay on documented public `/api/v1/...`
   paths. Do not use account connection, reauth, API key management, billing,
   credit top-up, or support-ticket endpoints.
5. If Hermes Agent runs on a remote host or gateway, configure the environment on
   that runtime host. A local shell variable will not automatically propagate.

## Diagnostics

- Run `hermes plugins` to confirm the plugin is installed and enabled.
- Re-run `tweet_explore` after installation to verify Hermes can load the tool
  definitions.
- If `tweet_read` reports missing credentials, check only whether
  `XQUIK_API_KEY` exists. Do not print the value.
- If an action is blocked, check `HERMES_TWEET_ENABLE_ACTIONS` and ask for
  explicit user approval before retrying.

## References

- Hermes Tweet: https://github.com/Xquik-dev/hermes-tweet
- PyPI package: https://pypi.org/project/hermes-tweet/
