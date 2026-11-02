#!/usr/bin/env bash
# Installs the global Claude Code instructions (user/CLAUDE.md) into
# ~/.claude/CLAUDE.md. Skills and agents are installed by the plugin system,
# not by this script, because a plugin cannot ship a user-level CLAUDE.md.
set -euo pipefail

kit_dir="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
source_file="${kit_dir}/user/CLAUDE.md"
target_dir="${CLAUDE_CONFIG_DIR:-${HOME}/.claude}"
target_file="${target_dir}/CLAUDE.md"

if [[ ! -f "${source_file}" ]]; then
  echo "error: ${source_file} not found" >&2
  exit 1
fi

mkdir -p "${target_dir}"

if [[ -f "${target_file}" ]]; then
  if cmp -s "${source_file}" "${target_file}"; then
    echo "${target_file} is already up to date."
    exit 0
  fi
  backup_file="${target_file}.bak.$(date +%Y%m%d-%H%M%S)"
  cp "${target_file}" "${backup_file}"
  echo "Backed up existing file to ${backup_file}"
fi

cp "${source_file}" "${target_file}"
echo "Installed ${target_file}"

cat <<'EOF'

Next step, inside Claude Code:
  /plugin marketplace add vinivaliati/vinivaliati-ai-template
  /plugin install vini-ai-kit@vinivaliati
EOF
