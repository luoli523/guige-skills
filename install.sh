#!/usr/bin/env bash
set -euo pipefail

# Installer for Gui Ge skills.
#
# Two modes:
#   marketplace (default) - drive `claude plugin` / `codex plugin` CLIs to add
#                           the Git marketplace and install the `guige` plugin.
#   symlink               - link ./skills/* into local skill dirs (local dev).

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
SKILLS_ROOT="$SCRIPT_DIR/skills"

MARKETPLACE_REPO="${GUIGE_MARKETPLACE_REPO:-luoli523/guige-skills}"
MARKETPLACE_REF="${GUIGE_MARKETPLACE_REF:-main}"
PLUGIN_NAME="guige"

MODE=marketplace
DRY_RUN=false
CLEANUP=false
LIST=false
PURGE_SYMLINKS=true
TARGET_ARGS=()

if [[ -t 1 ]]; then
    RED='\033[0;31m'; GREEN='\033[0;32m'; YELLOW='\033[1;33m'; BLUE='\033[0;34m'; NC='\033[0m'
else
    RED=''; GREEN=''; YELLOW=''; BLUE=''; NC=''
fi

usage() {
    cat <<EOF
Usage: $(basename "$0") [OPTIONS]

Install Gui Ge skills via plugin marketplace (default) or local symlinks.

Options:
  --mode MODE     marketplace (default) | symlink
  --target T      In marketplace mode: claude | codex | both (default: both).
                  In symlink mode: a directory to install into (repeatable).
  --dry-run       Show what would be done without making changes
  --cleanup       (symlink mode) Remove stale managed symlinks
  --no-purge-symlinks  (marketplace mode) Keep this repo's local symlinks
                  instead of removing them before installing the plugin
  --list          List install status for the selected mode
  --repo OWNER/REPO  Marketplace repo slug (default: $MARKETPLACE_REPO)
  -h, --help      Show this help message

Environment:
  GUIGE_MARKETPLACE_REPO  Override marketplace repo slug
  GUIGE_MARKETPLACE_REF   Override Codex marketplace branch/ref (default: main)
  GUIGE_SKILLS_TARGETS    (symlink mode) Colon-separated target directories
  CODEX_HOME              (symlink mode) Default Codex target root; defaults to ~/.codex

Examples:
  ./install.sh                      # marketplace install into claude + codex
  ./install.sh --target codex       # marketplace install into codex only
  ./install.sh --mode symlink       # local symlink install (dev)
  ./install.sh --list               # show current install status
EOF
    exit 0
}

expand_path() {
    local path="$1"
    case "$path" in
        "~") echo "$HOME" ;;
        "~/"*) echo "$HOME/${path#~/}" ;;
        *) echo "$path" ;;
    esac
}

while [[ $# -gt 0 ]]; do
    case "$1" in
        --mode) MODE="${2:-}"; shift 2 ;;
        --mode=*) MODE="${1#--mode=}"; shift ;;
        --dry-run) DRY_RUN=true; shift ;;
        --cleanup) CLEANUP=true; shift ;;
        --purge-symlinks) PURGE_SYMLINKS=true; shift ;;
        --no-purge-symlinks) PURGE_SYMLINKS=false; shift ;;
        --list) LIST=true; shift ;;
        --repo) MARKETPLACE_REPO="${2:-}"; shift 2 ;;
        --repo=*) MARKETPLACE_REPO="${1#--repo=}"; shift ;;
        --target)
            [[ $# -ge 2 ]] || { echo -e "${RED}Error: --target requires a value${NC}" >&2; exit 1; }
            TARGET_ARGS+=("$2"); shift 2 ;;
        --target=*) TARGET_ARGS+=("${1#--target=}"); shift ;;
        -h|--help) usage ;;
        *) echo -e "${RED}Unknown option: $1${NC}" >&2; usage ;;
    esac
done

case "$MODE" in
    marketplace|symlink) ;;
    *) echo -e "${RED}Invalid --mode: $MODE (must be marketplace|symlink)${NC}" >&2; exit 1 ;;
esac

MARKETPLACE_NAME="${MARKETPLACE_REPO##*/}"
PLUGIN_ID="${PLUGIN_NAME}@${MARKETPLACE_NAME}"

# ===========================================================================
# Marketplace mode
# ===========================================================================

run_cmd() {
    # run_cmd <label> <cmd...>
    local label="$1"; shift
    echo -e "  ${GREEN}${label}:${NC} $*"
    if $DRY_RUN; then
        return 0
    fi
    if ! "$@"; then
        echo -e "  ${RED}Command failed:${NC} $*" >&2
        return 1
    fi
}

marketplace_present() {
    # marketplace_present <cli> ; 0 if the marketplace is already known
    local cli="$1"
    # Do not use grep -q here: with pipefail, its early exit can turn a long
    # CLI listing into an upstream SIGPIPE and a false negative.
    "$cli" plugin marketplace list 2>/dev/null | grep -Fw "$MARKETPLACE_NAME" >/dev/null
}

plugin_present() {
    # plugin_present <cli> ; 0 if the plugin is already installed
    local cli="$1"
    "$cli" plugin list 2>/dev/null | grep -F "$PLUGIN_ID" >/dev/null
}

# Live CLI detection can be flaky (marketplace list may refresh/warn), so the
# add and update paths fall back to each other; nothing here aborts the script.
install_claude() {
    if ! command -v claude >/dev/null 2>&1; then
        echo -e "  ${YELLOW}Skip claude:${NC} \`claude\` CLI not found in PATH"
        return 0
    fi
    if marketplace_present claude; then
        run_cmd "Update marketplace" claude plugin marketplace update "$MARKETPLACE_NAME" || true
    else
        run_cmd "Add marketplace" claude plugin marketplace add "$MARKETPLACE_REPO" \
            || run_cmd "Update marketplace" claude plugin marketplace update "$MARKETPLACE_NAME" || true
    fi
    if plugin_present claude; then
        run_cmd "Update plugin" claude plugin update "$PLUGIN_ID" || true
    else
        run_cmd "Install plugin" claude plugin install "$PLUGIN_ID" \
            || run_cmd "Update plugin" claude plugin update "$PLUGIN_ID" || true
    fi
}

install_codex() {
    if ! command -v codex >/dev/null 2>&1; then
        echo -e "  ${YELLOW}Skip codex:${NC} \`codex\` CLI not found in PATH"
        return 0
    fi
    if marketplace_present codex; then
        run_cmd "Upgrade marketplace" codex plugin marketplace upgrade "$MARKETPLACE_NAME" || true
    else
        run_cmd "Add marketplace" codex plugin marketplace add "$MARKETPLACE_REPO" --ref "$MARKETPLACE_REF" \
            || run_cmd "Upgrade marketplace" codex plugin marketplace upgrade "$MARKETPLACE_NAME" || true
    fi
    # Codex has no in-place plugin update; re-add after removing (remove is
    # best-effort so a missing plugin does not abort).
    if plugin_present codex; then
        run_cmd "Remove plugin" codex plugin remove "$PLUGIN_ID" || true
    fi
    run_cmd "Add plugin" codex plugin add "$PLUGIN_ID" || true
}

resolve_cli_targets() {
    # Echo the CLI targets (claude/codex) from --target args; default both.
    if [[ ${#TARGET_ARGS[@]} -eq 0 ]]; then
        echo "claude codex"
        return
    fi
    local t
    for t in "${TARGET_ARGS[@]}"; do
        case "$t" in
            both) echo "claude codex" ;;
            claude|codex) echo "$t" ;;
            *) echo -e "${RED}Invalid --target for marketplace mode: $t (use claude|codex|both)${NC}" >&2; exit 1 ;;
        esac
    done
}

marketplace_status() {
    local cli
    echo -e "${BLUE}=== Marketplace Install Status ===${NC}"
    echo "Marketplace: $MARKETPLACE_NAME ($MARKETPLACE_REPO)   Plugin: $PLUGIN_ID"
    for cli in claude codex; do
        if ! command -v "$cli" >/dev/null 2>&1; then
            echo -e "  ${cli}: ${YELLOW}CLI not found${NC}"
            continue
        fi
        local mkt="missing" plg="missing"
        marketplace_present "$cli" && mkt="present"
        plugin_present "$cli" && plg="installed"
        echo -e "  ${cli}: marketplace=$mkt, plugin=$plg"
    done
}

cli_skills_dir() {
    case "$1" in
        claude) expand_path "$HOME/.claude/skills" ;;
        codex) expand_path "${CODEX_HOME:-$HOME/.codex}/skills" ;;
    esac
}

# Remove symlinks in <dir> that this repo created (point into SKILLS_ROOT or
# SCRIPT_DIR), so a marketplace install does not double-load skills already
# linked by a prior `--mode symlink` run. Other symlinks are left untouched.
purge_repo_symlinks() {
    local dir="$1" link current removed=0
    [[ -d "$dir" ]] || return 0
    shopt -s nullglob
    for link in "$dir"/*; do
        [[ -L "$link" ]] || continue
        current="$(readlink "$link")"
        case "$current" in
            "$SKILLS_ROOT"/*|"$SCRIPT_DIR"/*)
                echo -e "  ${YELLOW}Purge symlink:${NC} $(basename "$link") -> $current"
                $DRY_RUN || rm "$link"
                removed=$((removed + 1)) ;;
        esac
    done
    shopt -u nullglob
    [[ $removed -gt 0 ]] && echo "  Removed $removed managed symlink(s) from $dir"
    return 0
}

run_marketplace() {
    if $LIST; then
        marketplace_status
        exit 0
    fi
    echo -e "${BLUE}=== Install Gui Ge Skills (marketplace) ===${NC}"
    echo "Repo: $MARKETPLACE_REPO   Plugin: $PLUGIN_ID"
    local targets cli found_cli=false
    targets="$(resolve_cli_targets | tr ' ' '\n' | awk 'NF' | sort -u)"
    for cli in $targets; do
        command -v "$cli" >/dev/null 2>&1 && found_cli=true
    done
    if ! $found_cli; then
        echo -e "${RED}Error:${NC} none of the selected plugin CLIs ($(echo $targets | tr '\n' ' ')) are in PATH." >&2
        echo -e "Install Claude Code / Codex first, or run local symlink install: ${YELLOW}./install.sh --mode symlink${NC}" >&2
        exit 1
    fi
    if $PURGE_SYMLINKS; then
        echo -e "${BLUE}=== Purge local symlinks ===${NC}"
        for cli in $targets; do
            purge_repo_symlinks "$(cli_skills_dir "$cli")"
        done
    fi
    for cli in $targets; do
        echo -e "${BLUE}Target:${NC} $cli"
        "install_${cli}" || true
    done
    if $DRY_RUN; then
        echo -e "${YELLOW}(dry-run mode - no changes were made)${NC}"
    fi
    echo -e "${GREEN}Done!${NC}"
}

# ===========================================================================
# Symlink mode (legacy local-dev install)
# ===========================================================================

# A plugin install and local skill symlinks expose the same skills twice. Make
# local development deterministic by removing this marketplace plugin first.
# Missing CLIs and missing plugin installs are safe no-ops.
remove_plugin_for_symlink_mode() {
    local cli
    echo -e "${BLUE}=== Remove marketplace plugins for symlink mode ===${NC}"
    for cli in claude codex; do
        if ! command -v "$cli" >/dev/null 2>&1; then
            echo -e "  ${YELLOW}Skip $cli:${NC} CLI not found in PATH"
            continue
        fi
        if plugin_present "$cli"; then
            run_cmd "Remove plugin from $cli" "$cli" plugin remove "$PLUGIN_ID" || true
        else
            echo "  $cli: plugin not installed"
        fi
    done
}

has_valid_frontmatter() {
    local skill_dir="$1"
    local skill_md="$skill_dir/SKILL.md"
    local first_line
    [[ -f "$skill_md" ]] || return 1
    IFS= read -r first_line < "$skill_md" || return 1
    [[ "$first_line" == "---" ]] || return 1
    awk 'NR > 1 && $0 == "---" { found = 1; exit } END { exit(found ? 0 : 1) }' "$skill_md"
}

discover_skills() {
    local skill_dir
    if [[ ! -d "$SKILLS_ROOT" ]]; then
        echo -e "${RED}Error: skills directory not found: $SKILLS_ROOT${NC}" >&2
        exit 1
    fi
    shopt -s nullglob
    SKILL_NAMES=(); SKILL_SOURCES=()
    for skill_dir in "$SKILLS_ROOT"/*; do
        [[ -d "$skill_dir" ]] || continue
        if ! has_valid_frontmatter "$skill_dir"; then
            echo -e "${YELLOW}Warning: skipping $(basename "$skill_dir") (missing or invalid SKILL.md frontmatter)${NC}" >&2
            continue
        fi
        SKILL_NAMES+=("$(basename "$skill_dir")")
        SKILL_SOURCES+=("$skill_dir")
    done
    shopt -u nullglob
    if [[ ${#SKILL_NAMES[@]} -eq 0 ]]; then
        echo -e "${RED}Error: no valid skills found under $SKILLS_ROOT${NC}" >&2
        exit 1
    fi
}

link_status() {
    local link="$1" source="$2"
    if [[ -L "$link" ]]; then
        local current; current="$(readlink "$link")"
        [[ "$current" == "$source" ]] && echo "installed" || echo "points to $current"
    elif [[ -e "$link" ]]; then
        echo "blocked by non-symlink"
    else
        echo "missing"
    fi
}

list_skills() {
    local i target link status
    echo -e "${BLUE}=== Discovered Skills ===${NC}"
    for i in "${!SKILL_NAMES[@]}"; do
        echo -e "${GREEN}${SKILL_NAMES[$i]}${NC} -> ${SKILL_SOURCES[$i]}"
        for target in "${SYMLINK_DIRS[@]}"; do
            link="$target/${SKILL_NAMES[$i]}"
            status="$(link_status "$link" "${SKILL_SOURCES[$i]}")"
            echo "  $target: $status"
        done
    done
}

install_skills() {
    local target i name source link current created updated skipped
    echo -e "${BLUE}=== Install Gui Ge Skills (symlink) ===${NC}"
    echo "Source: $SKILLS_ROOT"
    for target in "${SYMLINK_DIRS[@]}"; do
        echo -e "${BLUE}Target:${NC} $target"
        $DRY_RUN || mkdir -p "$target"
        created=0; updated=0; skipped=0
        for i in "${!SKILL_NAMES[@]}"; do
            name="${SKILL_NAMES[$i]}"; source="${SKILL_SOURCES[$i]}"; link="$target/$name"
            if [[ -e "$link" && ! -L "$link" ]]; then
                echo -e "  ${YELLOW}Skip:${NC} $name (target exists and is not a symlink)"
                ((skipped+=1)); continue
            fi
            if [[ -L "$link" ]]; then
                current="$(readlink "$link")"
                if [[ "$current" == "$source" ]]; then ((skipped+=1)); continue; fi
                echo -e "  ${GREEN}Update:${NC} $name -> $source"
                if ! $DRY_RUN; then rm "$link"; ln -s "$source" "$link"; fi
                ((updated+=1))
            else
                echo -e "  ${GREEN}Link:${NC} $name -> $source"
                $DRY_RUN || ln -s "$source" "$link"
                ((created+=1))
            fi
        done
        echo "  Created: $created, Updated: $updated, Unchanged: $skipped"
    done
}

cleanup_stale_links() {
    local target entry link current removed
    echo -e "${BLUE}=== Cleanup Stale Managed Symlinks ===${NC}"
    for target in "${SYMLINK_DIRS[@]}"; do
        echo -e "${BLUE}Target:${NC} $target"
        removed=0
        [[ -d "$target" ]] || { echo "  Target directory does not exist"; continue; }
        shopt -s nullglob
        for link in "$target"/*; do
            [[ -L "$link" ]] || continue
            entry="$(basename "$link")"; current="$(readlink "$link")"
            case "$current" in
                "$SKILLS_ROOT"/*|"$SCRIPT_DIR"/*)
                    if [[ ! -d "$current" || ! -f "$current/SKILL.md" ]]; then
                        echo -e "  ${RED}Remove stale:${NC} $entry -> $current"
                        $DRY_RUN || rm "$link"
                        ((removed+=1))
                    fi ;;
            esac
        done
        shopt -u nullglob
        [[ $removed -eq 0 ]] && echo "  No stale symlinks found" || echo "  Removed: $removed"
    done
}

resolve_symlink_dirs() {
    SYMLINK_DIRS=()
    if [[ ${#TARGET_ARGS[@]} -gt 0 ]]; then
        local t
        for t in "${TARGET_ARGS[@]}"; do SYMLINK_DIRS+=("$(expand_path "$t")"); done
    elif [[ -n "${GUIGE_SKILLS_TARGETS:-}" ]]; then
        local IFS=':'; local parts; read -r -a parts <<< "$GUIGE_SKILLS_TARGETS"
        local t
        for t in "${parts[@]}"; do [[ -n "$t" ]] && SYMLINK_DIRS+=("$(expand_path "$t")"); done
    fi
    if [[ ${#SYMLINK_DIRS[@]} -eq 0 ]]; then
        SYMLINK_DIRS+=("$(expand_path "${CODEX_HOME:-$HOME/.codex}/skills")")
        SYMLINK_DIRS+=("$(expand_path "$HOME/.claude/skills")")
    fi
}

run_symlink() {
    resolve_symlink_dirs
    discover_skills
    if $LIST; then list_skills; exit 0; fi
    remove_plugin_for_symlink_mode
    install_skills
    $CLEANUP && cleanup_stale_links
    $DRY_RUN && echo -e "${YELLOW}(dry-run mode - no changes were made)${NC}"
    echo -e "${GREEN}Done!${NC}"
}

# ===========================================================================

if [[ "$MODE" == "marketplace" ]]; then
    run_marketplace
else
    run_symlink
fi
