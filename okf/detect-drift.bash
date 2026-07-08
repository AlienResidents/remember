#!/usr/bin/env bash
#
# detect-drift.bash — OKF drift detector for the remember knowledge bundle.
#
# Runs three classes of check and exits non-zero if any drift is found:
#
#   1. Orphan / missing concepts
#      For each source artefact, asserts a matching OKF concept exists:
#        - server/remember/tools/*.py  -> okf/tools/<name>.md
#        - server/remember/auth/*.py   -> okf/auth/<name>.md
#        - server/remember/webui/*     -> okf/webui.md (single concept)
#        - extension/<name>/           -> okf/extension/<name>.md
#      Catches "you added a tool/auth/webui/extension file and forgot to
#      author the concept."
#
#   2. Cross-link integrity
#      For every markdown link inside okf/**/*.md that points to a local
#      .md file (relative path, not http(s)), asserts the target file
#      exists. Catches "the concept links to a file you haven't authored
#      yet" + "you deleted a file but forgot to fix the links pointing at
#      it."
#
# This script does NOT fix drift. It only reports it. The fix is always one
# of: author the missing concept, or fix the broken link.
#
# Usage:
#   ./detect-drift.bash               # run all checks
#   ./detect-drift.bash --help
#
# Exit codes:
#   0  - No drift found
#   1  - Drift found (see report above)
#   100 - Bash version requirement not met
#   101 - Missing required dependency (git)

set -euo pipefail

if [[ ${BASH_VERSINFO[0]} -lt 5 ]] || [[ ${BASH_VERSINFO[0]} -eq 5 && ${BASH_VERSINFO[1]} -lt 2 ]]; then
  echo "Error: Requires bash 5.2+. Current: ${BASH_VERSION}" >&2
  exit 100
fi

script_path=$(dirname "$(readlink -f "${0}")")
repo_root=$(cd "${script_path}/.." && pwd -P)
bundle_root="${repo_root}/okf"

# ---------------------------------------------------------------------------
# Argument parsing
# ---------------------------------------------------------------------------

while [[ $# -gt 0 ]]; do
  case "${1}" in
    -h|--help)
      sed -n '3,30p' "${0}"
      exit 0
      ;;
    *)
      echo "Error: Unknown argument: ${1}" >&2
      exit 1
      ;;
  esac
done

# ---------------------------------------------------------------------------
# Dependencies + working directory
# ---------------------------------------------------------------------------

for dep in git; do
  if ! command -v "${dep}" >/dev/null 2>&1; then
    echo "Error: Required command not found: ${dep}" >&2
    exit 101
  fi
done

if [[ ! -d "${repo_root}/okf" ]]; then
  echo "Error: okf/ not found at ${repo_root}/okf — run from the repo root." >&2
  exit 1
fi

cd "${repo_root}"

# ---------------------------------------------------------------------------
# Accumulators
# ---------------------------------------------------------------------------

declare -a drift_findings=()

add_drift() {
  drift_findings+=("${1}")
}

# ---------------------------------------------------------------------------
# Check 1: Orphan / missing concepts
# ---------------------------------------------------------------------------

check_tools() {
  echo "  ### Tools"
  local found_issues=false

  # Missing: tool file exists but no concept.
  while read -r name; do
    # Skip __init__.py (package markers, not concepts).
    [[ "${name}" == "__init__.py" ]] && continue
    local slug="${name%.py}"
    if [[ ! -f "okf/tools/${slug}.md" ]]; then
      add_drift "missing Tool concept: server/remember/tools/${name} exists but okf/tools/${slug}.md does not"
      echo "  MISSING: okf/tools/${slug}.md (server/remember/tools/${name} exists)"
      found_issues=true
    fi
  done < <(git ls-files -- server/remember/tools/*.py 2>/dev/null | xargs -n1 basename 2>/dev/null || true)

  # Orphan: concept exists but no tool file.
  for f in okf/tools/*.md; do
    [[ -f "${f}" ]] || continue
    local slug
    slug=$(basename "${f}" .md)
    [[ "${slug}" == "index" || "${slug}" == "overview" ]] && continue
    if [[ ! -f "server/remember/tools/${slug}.py" ]]; then
      add_drift "orphan Tool concept: okf/tools/${slug}.md exists but server/remember/tools/${slug}.py does not"
      echo "  ORPHAN: okf/tools/${slug}.md (no server/remember/tools/${slug}.py)"
      found_issues=true
    fi
  done

  if [[ "${found_issues}" == false ]]; then
    echo "  OK: all tools have concepts and vice versa."
  fi
}

check_auth() {
  echo "  ### Auth Providers"
  local found_issues=false

  # Missing: auth file exists but no concept.
  while read -r name; do
    # Skip __init__.py (package markers, not concepts).
    [[ "${name}" == "__init__.py" ]] && continue
    # Skip base.py (internal base class, not a standalone concept).
    [[ "${name}" == "base.py" ]] && continue
    local slug="${name%.py}"
    if [[ ! -f "okf/auth/${slug}.md" ]]; then
      add_drift "missing Auth concept: server/remember/auth/${name} exists but okf/auth/${slug}.md does not"
      echo "  MISSING: okf/auth/${slug}.md (server/remember/auth/${name} exists)"
      found_issues=true
    fi
  done < <(git ls-files -- server/remember/auth/*.py 2>/dev/null | xargs -n1 basename 2>/dev/null || true)

  # Orphan: concept exists but no auth file.
  for f in okf/auth/*.md; do
    [[ -f "${f}" ]] || continue
    local slug
    slug=$(basename "${f}" .md)
    [[ "${slug}" == "index" || "${slug}" == "middleware" ]] && continue
    if [[ ! -f "server/remember/auth/${slug}.py" ]]; then
      add_drift "orphan Auth concept: okf/auth/${slug}.md exists but server/remember/auth/${slug}.py does not"
      echo "  ORPHAN: okf/auth/${slug}.md (no server/remember/auth/${slug}.py)"
      found_issues=true
    fi
  done

  if [[ "${found_issues}" == false ]]; then
    echo "  OK: all auth providers have concepts and vice versa."
  fi
}

check_webui() {
  echo "  ### Web UI"
  local found_issues=false

  # Web UI has a single concept: okf/webui.md.
  # Missing: server/webui/ exists but no concept.
  if [[ -d "server/webui" ]] && [[ ! -f "okf/webui.md" ]]; then
    add_drift "missing Web UI concept: server/webui/ exists but okf/webui.md does not"
    echo "  MISSING: okf/webui.md (server/webui/ exists)"
    found_issues=true
  fi

  # Orphan: concept exists but no webui dir.
  if [[ -f "okf/webui.md" ]] && [[ ! -d "server/webui" ]]; then
    add_drift "orphan Web UI concept: okf/webui.md exists but server/webui/ does not"
    echo "  ORPHAN: okf/webui.md (no server/webui/)"
    found_issues=true
  fi

  if [[ "${found_issues}" == false ]]; then
    echo "  OK: web UI has concept and vice versa."
  fi
}

check_extension() {
  echo "  ### Extensions"
  local found_issues=false

  # Extensions: each subdirectory under extension/ gets a concept.
  while read -r ext_name; do
    [[ -d "extension/${ext_name}" ]] || continue
    if [[ ! -f "okf/extension/${ext_name}.md" ]]; then
      add_drift "missing Extension concept: extension/${ext_name}/ exists but okf/extension/${ext_name}.md does not"
      echo "  MISSING: okf/extension/${ext_name}.md (extension/${ext_name}/ exists)"
      found_issues=true
    fi
  done < <(git ls-files -- extension/ 2>/dev/null | xargs -n1 dirname 2>/dev/null | xargs -n1 basename 2>/dev/null | sort -u || true)

  # Orphan: concept exists but no extension dir.
  for f in okf/extension/*.md; do
    [[ -f "${f}" ]] || continue
    local slug
    slug=$(basename "${f}" .md)
    [[ "${slug}" == "index" ]] && continue
    if [[ ! -d "extension/${slug}" ]]; then
      add_drift "orphan Extension concept: okf/extension/${slug}.md exists but extension/${slug}/ does not"
      echo "  ORPHAN: okf/extension/${slug}.md (no extension/${slug}/)"
      found_issues=true
    fi
  done

  if [[ "${found_issues}" == false ]]; then
    echo "  OK: all extensions have concepts and vice versa."
  fi
}

check_hand_curated() {
  echo "## Check 1: Orphan / missing concepts"
  echo
  check_tools
  check_auth
  check_webui
  check_extension
  echo
}

# ---------------------------------------------------------------------------
# Check 2: Cross-link integrity
# ---------------------------------------------------------------------------

check_cross_links() {
  echo "## Check 2: Cross-link integrity"
  echo
  local found_issues=false
  local broken_count=0

  while read -r md_file; do
    local md_dir
    md_dir=$(dirname "${md_file}")
    while read -r link; do
      local path="${link%%#*}"
      [[ -z "${path}" ]] && continue
      local resolved="${md_dir}/${path}"
      local normalised
      normalised=$(realpath -m "${resolved}" 2>/dev/null || echo "${resolved}")
      if [[ ! -e "${normalised}" ]]; then
        add_drift "broken cross-link in ${md_file#./}: ${link} -> ${normalised#./} (path not found)"
        echo "  BROKEN: ${md_file#./}: ${link} -> ${normalised#./}"
        found_issues=true
        ((++broken_count)) || true
      fi
    done < <(
      grep -oE '\]\([^)]+\)' "${md_file}" 2>/dev/null \
        | sed -E 's/^\]\(([^)]+)\)$/\1/' \
        | grep -vE '^(https?://|mailto:|#)' \
        || true
    )
  done < <(find okf -name '*.md' -type f | sort)

  if [[ "${found_issues}" == false ]]; then
    echo "  OK: all local markdown cross-links resolve."
  else
    echo
    echo "  Total broken cross-links: ${broken_count}"
  fi
  echo
}

# ---------------------------------------------------------------------------
# Summary
# ---------------------------------------------------------------------------

print_summary() {
  echo "========================================"
  echo "OKF drift summary"
  echo "========================================"
  echo "  Drift findings:  ${#drift_findings[@]}"
  echo
  if [[ ${#drift_findings[@]} -gt 0 ]]; then
    echo "Drift findings (must fix):"
    for f in "${drift_findings[@]}"; do
      echo "  - ${f}"
    done
    echo
  fi
}

# ---------------------------------------------------------------------------
# Main
# ---------------------------------------------------------------------------

echo "remember OKF drift check"
echo "  bundle: ${bundle_root}"
echo "  repo:   ${repo_root}"
echo

check_hand_curated
check_cross_links
print_summary

if [[ ${#drift_findings[@]} -gt 0 ]]; then
  exit 1
fi
exit 0
