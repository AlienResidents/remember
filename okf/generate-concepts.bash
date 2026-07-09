#!/usr/bin/env bash
#
# generate-concepts.bash — OKF concept generator for remember.
#
# Walks the entire repo via `git ls-files` and produces an OKF concept
# document for every tracked text file. Concepts are categorised by file
# type and written under okf/:
#
#   okf/docs/          — Markdown files (.md) — preserves directory structure
#   okf/code/          — Source files (.py, .js, .ts, .css, .html, .sh, .sql)
#   okf/infrastructure/ — YAML, Helm, K8s, Docker, Makefile
#   okf/config/        — TOML, INI, .env, gitignore, pre-commit config
#   okf/LICENSE.md     — The LICENSE file
#
# Binary files (images, fonts, binary locks) are skipped.
#
# Usage:
#   ./generate-concepts.bash               # generate all concepts
#   ./generate-concepts.bash --dry-run     # report what would be written
#   ./generate-concepts.bash --help
#
# Exit codes:
#   0  - Success
#   1  - Usage error
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

dry_run=false

case "${1:-}" in
  -h|--help)
    sed -n '3,30p' "${0}"
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
  printf '[generate-concepts] %s\n' "${1:-}"
}

# ---------------------------------------------------------------------------
# Binary file detection
# ---------------------------------------------------------------------------

is_binary() {
  local file="${1}"
  local ext="${file##*.}"
  [[ "${ext}" == "${file}" ]] && return 1

  case "${ext}" in
    png|jpg|jpeg|gif|bmp|ico|svg|webp|otf|ttf|woff|woff2|eot)
      return 0 ;;
    lock)
      # uv.lock, package-lock.json are large/structured — skip
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
# File classification — returns a category string
# ---------------------------------------------------------------------------

classify() {
  local file="${1}"
  local ext="${file##*.}"
  [[ "${ext}" == "${file}" ]] && ext=""

  case "${ext}" in
    md)       echo "docs" ;;
    py)       echo "code" ;;
    sh)       echo "code" ;;
    ps1)      echo "code" ;;
    sql)      echo "code" ;;
    mako)     echo "code" ;;
    js)       echo "code" ;;
    ts)       echo "code" ;;
    css)      echo "code" ;;
    html)     echo "code" ;;
    tpl)      echo "code" ;;
    yaml|yml) echo "infrastructure" ;;
    toml)     echo "config" ;;
    ini)      echo "config" ;;
    example)  echo "config" ;;
    env)      echo "config" ;;
    dockerignore) echo "config" ;;
    gitignore)    echo "config" ;;
    *)
      local base
      base=$(basename "${file}")
      case "${base}" in
        Makefile|Containerfile|Dockerfile) echo "infrastructure" ;;
        LICENSE|LICENSE.md|license)        echo "license" ;;
        *)                                echo "misc" ;;
      esac
      ;;
  esac
}

# ---------------------------------------------------------------------------
# Map a source path to its OKF concept path
# ---------------------------------------------------------------------------

concept_path() {
  local category="${1}"
  local source_path="${2}"

  case "${category}" in
    docs)
      # Markdown: place under okf/ preserving subdirectory structure
      # e.g. docs/deployment.md -> okf/docs/deployment.md
      printf '%s' "${bundle_root}/${source_path}"
      ;;
    code)
      # Flatten slashes to underscores
      local flat
      flat=$(printf '%s' "${source_path}" | tr '/' '_')
      printf '%s' "${bundle_root}/code/${flat}.md"
      ;;
    infrastructure)
      local flat
      flat=$(printf '%s' "${source_path}" | tr '/' '_')
      printf '%s' "${bundle_root}/infrastructure/${flat}.md"
      ;;
    config)
      local flat
      flat=$(printf '%s' "${source_path}" | tr '/' '_')
      printf '%s' "${bundle_root}/config/${flat}.md"
      ;;
    license)
      printf '%s' "${bundle_root}/LICENSE.md"
      ;;
    misc)
      local flat
      flat=$(printf '%s' "${source_path}" | tr '/' '_')
      printf '%s' "${bundle_root}/misc/${flat}.md"
      ;;
  esac
}

# ---------------------------------------------------------------------------
# Frontmatter type from category
# ---------------------------------------------------------------------------

concept_type() {
  local category="${1}"
  case "${category}" in
    docs)           echo "Documentation" ;;
    code)           echo "Source Code" ;;
    infrastructure) echo "Infrastructure" ;;
    config)         echo "Configuration" ;;
    license)        echo "License" ;;
    misc)           echo "Other" ;;
  esac
}

# ---------------------------------------------------------------------------
# Extract a one-line description from a file
# ---------------------------------------------------------------------------

extract_description() {
  local file="${1}"

  # For markdown: grab the first non-empty line, strip # headers
  if [[ "${file}" == *.md ]]; then
    local line
    line=$(grep -m1 -E '[^[:space:]]' "${file}" 2>/dev/null || true)
    line=$(printf '%s' "${line}" | sed -E 's/^#+[[:space:]]*//')
    printf '%s' "${line}" | head -c 120
    return
  fi

  # For code: grab first comment or docstring line
  local ext="${file##*.}"
  case "${ext}" in
    py)
      local line
      line=$(grep -m1 -E '^\s*(#|""")' "${file}" 2>/dev/null || true)
      line=$(printf '%s' "${line}" | sed -E 's/^\s*#?\s*//' | sed -E 's/^"""\s*//' | sed 's/"""//')
      printf '%s' "${line}" | head -c 120
      return
      ;;
    yaml|yml|toml|ini|env)
      local line
      line=$(grep -m1 -E '^\s*[^#\s]' "${file}" 2>/dev/null || true)
      printf '%s' "${line}" | head -c 120
      return
      ;;
  esac

  # Fallback: first non-empty line
  local line
  line=$(grep -m1 -E '[^[:space:]]' "${file}" 2>/dev/null || true)
  printf '%s' "${line}" | head -c 120
}

# ---------------------------------------------------------------------------
# Get the language tag for fenced code blocks
# ---------------------------------------------------------------------------

get_lang() {
  local file="${1}"
  local ext="${file##*.}"
  case "${ext}" in
    py)         echo "python" ;;
    sh)         echo "bash" ;;
    ps1)        echo "powershell" ;;
    sql)        echo "sql" ;;
    mako)       echo "mako" ;;
    js)         echo "javascript" ;;
    ts)         echo "typescript" ;;
    css)        echo "css" ;;
    html)       echo "html" ;;
    tpl)        echo "yaml" ;;
    yaml|yml)   echo "yaml" ;;
    toml)       echo "toml" ;;
    ini)        echo "ini" ;;
    env|example) echo "bash" ;;
    dockerignore|gitignore) echo "text" ;;
    md)         echo "markdown" ;;
    *)          echo "text" ;;
  esac
}

# ---------------------------------------------------------------------------
# Write a single concept file
# ---------------------------------------------------------------------------

write_concept() {
  local source_path="${1}"
  local category="${2}"
  local description="${3}"
  local cpath
  cpath=$(concept_path "${category}" "${source_path}")

  if [[ "${dry_run}" == "true" ]]; then
    log "DRY: would write ${cpath}"
    return
  fi

  mkdir -p "$(dirname "${cpath}")"

  # Build frontmatter
  {
    printf -- '---\n'
    printf 'type: %s\n' "$(concept_type "${category}")"
    printf 'description: "%s"\n' "${description}"
    printf 'resource: %s\n' "${source_path}"
    printf 'timestamp: %s\n' "$(date -u +"%Y-%m-%dT%H:%M:%SZ")"
    printf -- '---\n\n'
  } > "${cpath}"

  # Build body
  {
    local title
    title=$(basename "${source_path}" | sed 's/\.[^.]*$//' | tr '_' ' ')
    printf '# %s\n\n' "${title}"
    printf 'Source path: `%s`\n\n' "${source_path}"
    printf '## Content\n\n'

    case "${category}" in
      docs)
        # Include full markdown body, stripping YAML frontmatter if present
        if head -1 "${source_path}" 2>/dev/null | grep -q '^---$'; then
          local in_frontmatter=true line_count=0
          while IFS= read -r line || [[ -n "${line}" ]]; do
            if ${in_frontmatter}; then
              ((++line_count)) || true
              if [[ "${line}" == "---" ]] && [[ ${line_count} -gt 1 ]]; then
                in_frontmatter=false
              fi
              continue
            fi
            printf '%s\n' "${line}"
          done < "${source_path}"
        else
          cat "${source_path}"
        fi
        ;;
      code)
        printf '```%s\n' "$(get_lang "${source_path}")"
        head -40 "${source_path}" 2>/dev/null
        printf '```\n\n'
        printf '*…truncated — full source at `%s`*\n' "${source_path}"
        ;;
      infrastructure|config)
        printf '```%s\n' "$(get_lang "${source_path}")"
        cat "${source_path}"
        printf '\n```\n'
        ;;
      license)
        cat "${source_path}"
        ;;
      misc)
        if file "${source_path}" 2>/dev/null | grep -q 'text'; then
          cat "${source_path}"
        else
          printf '*(binary file — not displayed)*\n'
        fi
        ;;
    esac
  } >> "${cpath}"

  log "wrote ${cpath}"
}

# ---------------------------------------------------------------------------
# Main
# ---------------------------------------------------------------------------

log "remember OKF concept generator"
log "  bundle: ${bundle_root}"
log "  repo:   ${repo_root}"
log "  dry run: ${dry_run}"
log ""

# Collect all tracked files
mapfile -t all_files < <(git ls-files 2>/dev/null)

gen_count=0

for file in "${all_files[@]}"; do
  [[ -z "${file}" ]] && continue

  # Skip the okf/ output directory itself
  [[ "${file}" == okf/* ]] && continue

  # Skip binary files
  if is_binary "${file}"; then
    log "skip binary: ${file}"
    continue
  fi

  file_cat=$(classify "${file}")
  file_desc=$(extract_description "${file}")

  write_concept "${file}" "${file_cat}" "${file_desc}"
  ((++gen_count)) || true
done

log ""
log "Generated ${gen_count} concept(s)."

if [[ "${dry_run}" == "true" ]]; then
  log ""
  log "Dry run complete. No files written."
fi
