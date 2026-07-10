#!/usr/bin/env bash
#
# detect-drift.bash — OKF drift detector for the remember knowledge bundle.
#
# Compares the repo's tracked files (via `git ls-files`) against the OKF
# concept directory (okf/). Reports three classes of drift:
#
#   1. Missing concepts — a tracked file exists but has no matching OKF
#      concept under okf/.
#   2. Orphan concepts — a concept exists under okf/ but no corresponding
#      tracked file exists in the repo.
#   3. Broken cross-links — a markdown link inside okf/**/*.md points to
#      a local .md file that does not exist.
#
# Usage:
#   ./detect-drift.bash               # run all checks
#   ./detect-drift.bash --help
#
# Exit codes:
#   0  - No drift found
#   1  - Drift found (see report)
#   100 - Bash version requirement not met
#   101 - Missing required dependency (git)

set -euo pipefail

if [[ ${BASH_VERSINFO[0]:-0} -lt 5 ]] || { [[ ${BASH_VERSINFO[0]:-0} -eq 5 ]] && [[ ${BASH_VERSINFO[1]:-0} -lt 2 ]]; }; then
  echo "Error: Requires bash 5.2+. Current: ${BASH_VERSION}" >&2
  exit 100
fi

for dep in git; do
  if ! command -v "${dep}" >/dev/null 2>&1; then
    echo "Error: Required command not found: ${dep}" >&2
    exit 101
  fi
done

# ---------------------------------------------------------------------------
# Argument parsing
# ---------------------------------------------------------------------------

script_path=$(dirname "$(readlink -f "${0}")")
repo_root=$(cd "${script_path}/.." && pwd -P)
bundle_root="${repo_root}/okf"

while [[ $# -gt 0 ]]; do
  case "${1}" in
    -h|--help)
      sed -n '3,25p' "${0}"
      exit 0
      ;;
    *)
      echo "Error: unknown argument: ${1}" >&2
      exit 1
      ;;
  esac
done

# ---------------------------------------------------------------------------
# Working directory
# ---------------------------------------------------------------------------

if [[ ! -d "${bundle_root}" ]]; then
  echo "Error: okf/ not found at ${bundle_root} — run from the repo root." >&2
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
# Binary file detection (same logic as generator)
# ---------------------------------------------------------------------------

is_binary() {
  local file="${1}"
  local ext="${file##*.}"
  [[ "${ext}" == "${file}" ]] && return 1

  case "${ext}" in
    png|jpg|jpeg|gif|bmp|ico|svg|webp|otf|ttf|woff|woff2|eot)
      return 0 ;;
    lock)
      return 0 ;;
    *)
      if head -c 512 "${file}" 2>/dev/null | grep -qP '\x00'; then
        return 0
      fi
      return 1
      ;;
  esac
}

# ---------------------------------------------------------------------------
# Build the set of tracked files (excluding okf/ itself and binaries)
# ---------------------------------------------------------------------------

declare -A tracked_files=()

while IFS= read -r file; do
  [[ -z "${file}" ]] && continue
  [[ "${file}" == okf/* ]] && continue
  is_binary "${file}" && continue
  tracked_files["${file}"]=1
done < <(git ls-files 2>/dev/null)

# ---------------------------------------------------------------------------
# Build the set of concept files (okf/**/*.md)
# ---------------------------------------------------------------------------

declare -A concept_files=()

while IFS= read -r cfile; do
  [[ -z "${cfile}" ]] && continue
  # Store relative to repo root for consistent lookup
  cfile_rel="${cfile#${repo_root}/}"
  concept_files["${cfile_rel}"]=1
done < <(find "${bundle_root}" -name '*.md' -type f 2>/dev/null | sort)

# ---------------------------------------------------------------------------
# Path mapping: tracked source -> expected concept path
# ---------------------------------------------------------------------------

map_to_concept() {
  local src="${1}"

  # Inside okf/ — no concept to map to
  [[ "${src}" == okf/* ]] && return 0

  local base
  base=$(basename "${src}")
  local ext="${base##*.}"
  [[ "${ext}" == "${base}" ]] && ext=""

  case "${ext}" in
    md)
      # Markdown: okf/<source_path> (preserves subdirs)
      printf 'okf/%s' "${src}"
      ;;
    py|sh|ps1|sql|mako|js|ts|css|html|tpl)
      local flat
      flat=$(printf '%s' "${src}" | tr '/' '_')
      printf 'okf/code/%s.md' "${flat}"
      ;;
    yaml|yml)
      local flat
      flat=$(printf '%s' "${src}" | tr '/' '_')
      printf 'okf/infrastructure/%s.md' "${flat}"
      ;;
    toml|ini|env|example|dockerignore|gitignore)
      local flat
      flat=$(printf '%s' "${src}" | tr '/' '_')
      printf 'okf/config/%s.md' "${flat}"
      ;;
    *)
      # Match the generator's fallback classification
      local base
      base=$(basename "${src}")
      case "${base}" in
        LICENSE|LICENSE.md|license)
          printf 'okf/LICENSE.md'
          return 0
          ;;
        Makefile|Containerfile|Dockerfile)
          local flat
          flat=$(printf '%s' "${src}" | tr '/' '_')
          printf 'okf/infrastructure/%s.md' "${flat}"
          return 0
          ;;
      esac
      local flat
      flat=$(printf '%s' "${src}" | tr '/' '_')
      printf 'okf/misc/%s.md' "${flat}"
      ;;
  esac
}

# ---------------------------------------------------------------------------
# Path mapping: concept path -> expected source file (via resource: frontmatter)
# ---------------------------------------------------------------------------

map_to_source() {
  local concept="${1}"

  # Root-level okf files (index.md, LICENSE.md) — not backed by a source
  local dir
  dir=$(dirname "${concept}")
  [[ "${dir}" == "${bundle_root}" ]] && return 0

  # Try to read the resource: field from the concept's frontmatter
  local resource
  resource=$(grep -m1 '^resource:' "${concept}" 2>/dev/null | sed -E 's/^resource:[[:space:]]*//' || true)
  if [[ -n "${resource}" ]]; then
    printf '%s' "${resource}"
    return 0
  fi

  # Fallback for docs: path-preserving mapping
  local parent
  parent=$(basename "${dir}")
  case "${parent}" in
    docs)
      local rel="${concept#${bundle_root}/docs/}"
      printf '%s' "${rel}"
      return 0
      ;;
  esac

  return 0
}

# ---------------------------------------------------------------------------
# Check 1: Missing concepts
# ---------------------------------------------------------------------------

check_missing() {
  echo "## Check 1: Missing concepts (tracked file has no OKF concept)"
  echo

  local found_issues=false
  local missing_count=0

  for file in "${!tracked_files[@]}"; do
    local concept
    concept=$(map_to_concept "${file}")
    [[ -z "${concept}" ]] && continue

    if [[ -z "${concept_files[${concept}]:-}" ]]; then
      add_drift "missing concept: ${file} -> ${concept}"
      echo "  MISSING: ${concept}"
      ((++missing_count)) || true
      found_issues=true
    fi
  done

  if [[ "${found_issues}" == false ]]; then
    echo "  OK: every tracked file has an OKF concept."
  else
    echo
    echo "  Total missing concepts: ${missing_count}"
  fi
  echo
}

# ---------------------------------------------------------------------------
# Check 2: Orphan concepts
# ---------------------------------------------------------------------------

check_orphans() {
  echo "## Check 2: Orphan concepts (concept with no tracked source file)"
  echo

  local found_issues=false
  local orphan_count=0

  for concept in "${!concept_files[@]}"; do
    # Skip index.md and log.md (conventional, not source-backed)
    [[ "${concept##*/}" == "index.md" ]] && continue
    [[ "${concept##*/}" == "log.md" ]] && continue

    local source
    source=$(map_to_source "${concept}")
    [[ -z "${source}" ]] && continue

    if [[ -z "${tracked_files[${source}]:-}" ]]; then
      add_drift "orphan concept: ${concept} (no ${source})"
      echo "  ORPHAN: ${concept} (no ${source})"
      ((++orphan_count)) || true
      found_issues=true
    fi
  done

  if [[ "${found_issues}" == false ]]; then
    echo "  OK: every concept maps back to a tracked file."
  else
    echo
    echo "  Total orphan concepts: ${orphan_count}"
  fi
  echo
}

# ---------------------------------------------------------------------------
# Check 3: Cross-link integrity
# ---------------------------------------------------------------------------

check_cross_links() {
  echo "## Check 3: Cross-link integrity"
  echo

  local found_issues=false
  local broken_count=0

  while IFS= read -r md_file; do
    [[ -z "${md_file}" ]] && continue
    # Normalize to relative path
    md_file="${md_file#${repo_root}/}"
    local md_dir
    md_dir=$(dirname "${md_file}")
    while IFS= read -r link; do
      [[ -z "${link}" ]] && continue
      local path="${link%%#*}"
      [[ -z "${path}" ]] && continue
      # Skip external links
      [[ "${path}" == http://* ]] && continue
      [[ "${path}" == https://* ]] && continue
      [[ "${path}" == mailto:* ]] && continue
      [[ "${path}" == \#* ]] && continue
      # Links referencing okf/ directory structure are repo-external
      # (the generator copies original content with original paths)
      [[ "${path}" == okf/* ]] && continue
      # Only check links that look like they should resolve within the bundle
      # (markdown links or absolute paths starting with /)
      case "${path}" in
        *.md|*.md\#*) ;;  # markdown cross-links — check these
        /*) ;;              # absolute bundle paths — check these
        *) continue ;;      # images, yaml refs, etc. — skip
      esac

      local resolved="${md_dir}/${path}"
      local normalised
      normalised=$(realpath -m "${resolved}" 2>/dev/null || printf '%s' "${resolved}")
      # Only flag as broken if the resolved path is within the bundle
      # (i.e. this was meant to be a bundle-internal link)
      if [[ "${normalised}" == "${bundle_root}"* ]]; then
        # Absolute paths (/...) are bundle-internal by definition — flag
        # if the target doesn't exist.
        # Relative paths from subdirectories are likely repo-external refs —
        # only flag if the file doesn't exist (if it exists, it's fine).
        if [[ "${path}" == /* ]] && [[ ! -e "${normalised}" ]]; then
          add_drift "broken link in ${md_file}: ${link} -> ${normalised#${repo_root}/}"
          echo "  BROKEN: ${md_file}: ${link} -> ${normalised#${repo_root}/}"
          found_issues=true
          ((++broken_count)) || true
        fi
      fi
    done < <(
      grep -oE '\]\([^)]+\)' "${md_file}" 2>/dev/null \
        | sed -E 's/^\]\(([^)]+)\)$/\1/' \
        || true
    )
  done < <(find "${bundle_root}" -name '*.md' -type f 2>/dev/null | sort)

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
  echo "  Tracked files:     ${#tracked_files[@]}"
  echo "  Concept files:     ${#concept_files[@]}"
  echo "  Drift findings:    ${#drift_findings[@]}"
  echo

  if [[ ${#drift_findings[@]} -gt 0 ]]; then
    echo "Drift findings (must fix):"
    for f in "${drift_findings[@]}"; do
      echo "  - ${f}"
    done
    echo
    echo "To generate missing concepts, run:"
    echo "  bash okf/generate-concepts.bash"
    echo "Then re-run this check:"
    echo "  bash okf/detect-drift.bash"
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

check_missing
check_orphans
check_cross_links
print_summary

if [[ ${#drift_findings[@]} -gt 0 ]]; then
  exit 1
fi
exit 0
