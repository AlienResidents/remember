#!/usr/bin/env bash
# detect-drift.bash — Check OKF knowledge bundle for drift against the codebase.
#
# Validates:
#   1. All `resource:` paths in OKF frontmatter point to existing files
#   2. All markdown link references in OKF files point to existing targets
#   3. All OKF files are listed in okf/index.md (no orphan docs)
#   4. All sections in okf/index.md reference existing files
#
# Exit codes:
#   0 — No drift detected
#   1 — Drift detected (broken references, orphan files, etc.)

set -euo pipefail

OKF_DIR="okf"
ROOT_DIR="$(git rev-parse --show-toplevel)"
ERRORS=0

# Colors
RED='\033[0;31m'
YELLOW='\033[0;33m'
GREEN='\033[0;32m'
NC='\033[0m'

log_error() {
    echo -e "${RED}ERROR:${NC} $*" >&2
    ERRORS=$((ERRORS + 1))
}

log_warn() {
    echo -e "${YELLOW}WARN:${NC} $*" >&2
}

log_ok() {
    echo -e "${GREEN}OK:${NC} $*"
}

# --- 1. Check resource: paths in frontmatter ---
echo "Checking resource: paths in OKF frontmatter..."

while IFS= read -r -d '' file; do
    # Extract resource: line from frontmatter (between --- markers)
    resource=$(sed -n '/^---$/,/^---$/p' "$file" | grep '^resource:' | head -1 | sed 's/^resource:[[:space:]]*//' || true)

    if [[ -z "$resource" ]]; then
        continue
    fi

    # Skip URLs (https://, http://, git@)
    if [[ "$resource" =~ ^(https?://|git@) ]]; then
        continue
    fi

    # Resolve relative to repo root (resource: paths are repo-relative)
    if [[ "$resource" == /* ]]; then
        target="$ROOT_DIR$resource"
    else
        target="$ROOT_DIR/$resource"
    fi

    if [[ ! -e "$target" ]]; then
        log_error "$file: resource '$resource' -> '$target' does not exist"
    fi
done < <(find "$ROOT_DIR/$OKF_DIR" -name "*.md" -print0)

# --- 2. Check markdown link references ---
echo "Checking markdown link references..."

while IFS= read -r -d '' file; do
    # Extract link targets from [text](path) — skip URLs and anchors
    link_targets=$(grep -oP '\]\([^)]+\)' "$file" 2>/dev/null | \
        grep -oP '(?<=\()[^)]+(?=\))' | \
        grep -v '^#' | \
        grep -v '^https\?://' | \
        grep -v '^mailto:' || true)

    if [[ -z "$link_targets" ]]; then
        continue
    fi

    while IFS= read -r target; do
        # Skip external/absolute paths
        if [[ "$target" =~ ^(https?://|git@|/|ftp://) ]]; then
            continue
        fi

        # Resolve relative to the file's directory
        file_dir=$(dirname "$file")
        resolved="$file_dir/$target"

        if [[ ! -e "$resolved" ]]; then
            log_error "$file: link target '$target' -> '$resolved' does not exist"
        fi
    done <<< "$link_targets"
done < <(find "$ROOT_DIR/$OKF_DIR" -name "*.md" -print0)

# --- 3. Check for orphan OKF files (not referenced in index) ---
echo "Checking for orphan OKF files..."

if [[ -f "$ROOT_DIR/$OKF_DIR/index.md" ]]; then
    # Get all .md files excluding index.md
    while IFS= read -r -d '' file; do
        file_basename=$(basename "$file")
        if [[ "$file_basename" == "index.md" ]]; then
            continue
        fi

        # Check if this file is referenced in index.md (by filename)
        if ! grep -q "$file_basename" "$ROOT_DIR/$OKF_DIR/index.md"; then
            rel_path="${file#"$ROOT_DIR"/}"
            log_warn "$rel_path is not referenced in okf/index.md"
        fi
    done < <(find "$ROOT_DIR/$OKF_DIR" -name "*.md" -print0)
fi

# --- 4. Check index.md links point to existing files ---
echo "Checking index.md references..."

if [[ -f "$ROOT_DIR/$OKF_DIR/index.md" ]]; then
    link_targets=$(grep -oP '\](?:\([^)]+\))' "$ROOT_DIR/$OKF_DIR/index.md" 2>/dev/null | \
        grep -oP '(?<=\()[^)]+(?=\))' | \
        grep -v '^#' | \
        grep -v '^https\?://' || true)

    if [[ -z "$link_targets" ]]; then
        : # No links to check
    else
        while IFS= read -r target; do
            if [[ "$target" =~ ^(\./|\.\\.\\.|\.\\.\/) ]]; then
                # Relative path from index.md location
                resolved="$ROOT_DIR/$OKF_DIR/$target"
            else
                resolved="$ROOT_DIR/$OKF_DIR/$target"
            fi

            if [[ ! -e "$resolved" ]]; then
                log_error "okf/index.md: reference '$target' -> '$resolved' does not exist"
            fi
        done <<< "$link_targets"
    fi
fi

# --- Summary ---
echo ""
if [[ $ERRORS -eq 0 ]]; then
    log_ok "No drift detected. OKF knowledge bundle is consistent."
    exit 0
else
    log_error "$ERRORS drift issue(s) found. Update OKF docs or fix references."
    exit 1
fi
