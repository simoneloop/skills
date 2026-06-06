#!/usr/bin/env bash
# repo-inventory.sh — dump structured metadata for a GitHub account's repos.
# Usage: repo-inventory.sh [github-user]   (defaults to the authenticated user)
# Requires: gh (authenticated), jq.
set -euo pipefail

USER_ARG="${1:-}"
GH="${GH_BIN:-gh}"

command -v "$GH" >/dev/null 2>&1 || { echo "gh not found (set GH_BIN to its path)"; exit 1; }

FIELDS="name,description,visibility,isFork,isArchived,primaryLanguage,pushedAt,createdAt,stargazerCount,forkCount,diskUsage,homepageUrl"

if [ -n "$USER_ARG" ]; then
  json="$("$GH" repo list "$USER_ARG" --limit 200 --json "$FIELDS")"
else
  json="$("$GH" repo list --limit 200 --json "$FIELDS")"
fi

echo "$json" | jq -r '
  "Total: \(length) repos  |  public: \([.[]|select(.visibility=="PUBLIC")]|length)  private: \([.[]|select(.visibility=="PRIVATE")]|length)  forks: \([.[]|select(.isFork)]|length)  archived: \([.[]|select(.isArchived)]|length)\n",
  (["REPO","VIS","LANG","FORK","ARCH","STARS","PUSHED"] | @tsv),
  (.[] | [
     .name,
     (.visibility|ascii_downcase),
     (.primaryLanguage.name // "-"),
     (if .isFork then "fork" else "-" end),
     (if .isArchived then "arch" else "-" end),
     (.stargazerCount|tostring),
     (.pushedAt[0:10])
   ] | @tsv)
' | column -t -s $'\t'

# Emit raw JSON too (for programmatic classification)
echo
echo "----- raw json -----"
echo "$json"
