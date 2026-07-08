#!/usr/bin/env bash
#
# generate-concepts.bash - OKF concept generator for remember.
#
# Walks the remember source tree and generates OKF concept files.
# Follows the convention: <relative-path>.md
#
# Usage:
#   ./generate-concepts.bash               # generate all concepts
#   ./generate-concepts.bash --dry-run     # report what would be written
#   ./generate-concepts.bash --help
#
# Error codes:
# 100 - Bash version requirement not met
# 101 - Missing required dependency (git)

set -euo pipefail

if [[ ${BASH_VERSINFO[0]} -lt 5 ]] || [[ ${BASH_VERSINFO[0]} -eq 5 && ${BASH_VERSINFO[1]} -lt 2 ]]; then
  echo "Error: Requires bash 5.2+. Current: ${BASH_VERSION}" >&2
  exit 100
fi

for dep in git; do
  if ! command -v "${dep}" >/dev/null 2>&1; then
    echo "Error: Required command not found: ${dep}" >&2
    exit 101
  fi
done

script_path=$(dirname "$(readlink -f "${0}")")
repo_root="${script_path}"
bundle_root="${repo_root}/okf"

dry_run=false
case "${1:-}" in
  -h|--help)
    sed -n '3,25p' "${0}"
    exit 0
    ;;
  -d|--dry-run)
    dry_run=true
    ;;
  "")
    ;;
  *)
    echo "Error: unknown argument: ${1}" >&2
    exit 1
    ;;
esac

log() {
  echo -e "[generate-concepts] ${1}"
}

# Write a file using the safe write-then-mv pattern. Honours --dry-run.
write_file() {
  local target="${1}"
  local content="${2}"
  if [[ "${dry_run}" == "true" ]]; then
    log "DRY: would write ${target} ($(echo -n "${content}" | wc -c) bytes)"
    return
  fi
  mkdir -p "$(dirname "${target}")"
  printf '%s' "${content}" > "${target}"
}

# Wipe a directory before regenerating. Honours --dry-run.
wipe_dir() {
  local target="${1}"
  if [[ "${dry_run}" == "true" ]]; then
    log "DRY: would wipe ${target}"
    return
  fi
  rm -rf "${target}"
  mkdir -p "${target}"
}

# Generate concept frontmatter for a Python file.
generate_python_concept() {
  local source_path="${1}"
  local concept_path="${2}"
  local basename
  basename=$(basename "${source_path}" .py)
  local dir
  dir=$(dirname "${source_path}")

  cat << EOF
---
type: Python Module
title: ${basename}
description: Source file for ${basename}.
resource: ${source_path}
tags: [python, source]
timestamp: $(date -u +"%Y-%m-%dT%H:%M:%SZ")
---

# ${basename}

Source file: \`${source_path}\`

## Purpose

$(grep -E "^\"\"\"" "${source_path}" 2>/dev/null | head -1 | sed 's/^"""//' | sed 's/"""$//' || echo "TODO: Add description.")

## API

\`\`\`python
# Import: from ${dir//\//.} import ${basename}
\`\`\`

## Related

- [Overview](./overview.md)
EOF
}

# Generate concept for server/remember/tools/*.py
generate_tool_concepts() {
  echo "  ### Tools"
  local count=0

  while read -r source_file; do
    [[ -z "${source_file}" ]] && continue
    local basename
    basename=$(basename "${source_file}" .py)
    local concept_name="${basename}.py.md"
    local concept_path="${bundle_root}/tools/${concept_name}"

    if [[ "${dry_run}" == "true" ]]; then
      log "DRY: would generate ${concept_path}"
    else
      local content
      content=$(generate_python_concept "${source_file}" "${concept_path}")
      write_file "${concept_path}" "${content}"
    fi
    ((++count)) || true
  done < <(git ls-files -- "server/remember/tools/*.py" 2>/dev/null)

  if [[ "${count}" -gt 0 ]]; then
    log "Generated ${count} tool concept(s)."
  else
    log "No tool concepts generated."
  fi
}

# Generate concept for server/remember/auth/*.py
generate_auth_concepts() {
  echo "  ### Auth Providers"
  local count=0

  while read -r source_file; do
    [[ -z "${source_file}" ]] && continue
    local basename
    basename=$(basename "${source_file}" .py)
    local concept_name="${basename}.py.md"
    local concept_path="${bundle_root}/auth/${concept_name}"

    if [[ "${dry_run}" == "true" ]]; then
      log "DRY: would generate ${concept_path}"
    else
      local content
      content=$(generate_python_concept "${source_file}" "${concept_path}")
      write_file "${concept_path}" "${content}"
    fi
    ((++count)) || true
  done < <(git ls-files -- "server/remember/auth/*.py" 2>/dev/null)

  if [[ "${count}" -gt 0 ]]; then
    log "Generated ${count} auth concept(s)."
  else
    log "No auth concepts generated."
  fi
}

# ---------------------------------------------------------------------------
# Main
# ---------------------------------------------------------------------------

echo "remember OKF concept generator"
echo "  bundle: ${bundle_root}"
echo "  repo:   ${repo_root}"
echo "  dry run: ${dry_run}"
echo

generate_tool_concepts
generate_auth_concepts

if [[ "${dry_run}" == "true" ]]; then
  echo
  echo "Dry run complete. No files written."
fi
