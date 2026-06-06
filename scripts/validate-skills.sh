#!/usr/bin/env bash
# validate-skills.sh — structural linter for this marketplace/plugin/skills repo.
# No auth required. Exits non-zero on the first hard error. Runs in CI.
set -uo pipefail
cd "$(dirname "$0")/.."   # repo root

errors=0
err()  { echo "ERROR: $*"; errors=$((errors+1)); }
ok()   { echo "ok: $*"; }
KEBAB='^[a-z0-9]+(-[a-z0-9]+)*$'

need() { command -v "$1" >/dev/null 2>&1 || { echo "missing dependency: $1"; exit 3; }; }
need jq

# 1) marketplace.json
MP=".claude-plugin/marketplace.json"
[ -f "$MP" ] || err "$MP missing"
if [ -f "$MP" ]; then
  jq empty "$MP" 2>/dev/null || err "$MP is not valid JSON"
  jq -e '.name and .owner.name and (.plugins|type=="array")' "$MP" >/dev/null \
    || err "$MP must have name, owner.name, plugins[]"
  name=$(jq -r '.name' "$MP"); [[ "$name" =~ $KEBAB ]] || err "marketplace name '$name' not kebab-case"
  # no parent-dir traversal in sources
  if jq -r '.plugins[].source | if type=="string" then . else "" end' "$MP" | grep -q '\.\.'; then
    err "a plugin source contains '..' (path traversal)"
  fi
  ok "marketplace.json"
fi

# 2) each plugin.json
while IFS= read -r pj; do
  jq empty "$pj" 2>/dev/null || { err "$pj invalid JSON"; continue; }
  pn=$(jq -r '.name // empty' "$pj")
  [ -n "$pn" ] || err "$pj missing 'name'"
  [[ "$pn" =~ $KEBAB ]] || err "plugin name '$pn' not kebab-case ($pj)"
  ok "plugin.json: $pn"
done < <(find plugins -name plugin.json -path '*/.claude-plugin/*' 2>/dev/null)

# 3) each SKILL.md
shopt -s globstar nullglob
found_skill=0
for sk in plugins/**/skills/*/SKILL.md; do
  found_skill=1
  dir=$(basename "$(dirname "$sk")")
  [[ "$dir" =~ $KEBAB ]] || err "skill dir '$dir' not kebab-case"
  # extract frontmatter (between first two '---' lines)
  fm=$(awk 'NR==1&&/^---/{f=1;next} f&&/^---/{exit} f{print}' "$sk")
  echo "$fm" | grep -qE '^description:' || err "$sk: frontmatter missing 'description'"
  echo "$fm" | grep -qE '^name:'        || err "$sk: frontmatter missing 'name' (recommended)"
  ok "SKILL.md: $dir"
done
[ "$found_skill" -eq 1 ] || err "no SKILL.md found under plugins/**/skills/*/"

echo
if [ "$errors" -eq 0 ]; then echo "PASS — repo structure valid."; else echo "FAIL — $errors error(s)."; exit 1; fi
