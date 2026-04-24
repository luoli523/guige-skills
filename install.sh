#!/usr/bin/env bash
set -euo pipefail

# Local installer for Gui Ge skills.
# Discovers skills under ./skills and links them into local skill directories.

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
SKILLS_ROOT="$SCRIPT_DIR/skills"

DRY_RUN=false
CLEANUP=false
LIST=false
TARGET_DIRS=()

if [[ -t 1 ]]; then
    RED='\033[0;31m'
    GREEN='\033[0;32m'
    YELLOW='\033[1;33m'
    BLUE='\033[0;34m'
    NC='\033[0m'
else
    RED=''
    GREEN=''
    YELLOW=''
    BLUE=''
    NC=''
fi

usage() {
    cat <<EOF
Usage: $(basename "$0") [OPTIONS]

Install local Gui Ge skills by symlinking ./skills/* into local skill dirs.

Options:
  --dry-run       Show what would be done without making changes
  --cleanup       Remove stale managed symlinks
  --list          List discovered skills and install status
  --target DIR    Install into DIR; can be repeated
  -h, --help      Show this help message

Environment:
  GUIGE_SKILLS_TARGETS  Colon-separated target directories
  CODEX_HOME            Used for the default Codex target; defaults to ~/.codex

Default targets:
  \${CODEX_HOME:-~/.codex}/skills
  ~/.claude/skills
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

add_target() {
    local target
    target="$(expand_path "$1")"
    TARGET_DIRS+=("$target")
}

while [[ $# -gt 0 ]]; do
    case "$1" in
        --dry-run) DRY_RUN=true; shift ;;
        --cleanup) CLEANUP=true; shift ;;
        --list) LIST=true; shift ;;
        --target)
            if [[ $# -lt 2 ]]; then
                echo -e "${RED}Error: --target requires a directory${NC}" >&2
                exit 1
            fi
            add_target "$2"
            shift 2
            ;;
        -h|--help) usage ;;
        *) echo -e "${RED}Unknown option: $1${NC}" >&2; usage ;;
    esac
done

if [[ ${#TARGET_DIRS[@]} -eq 0 && -n "${GUIGE_SKILLS_TARGETS:-}" ]]; then
    IFS=':' read -r -a ENV_TARGETS <<< "$GUIGE_SKILLS_TARGETS"
    for target in "${ENV_TARGETS[@]}"; do
        [[ -n "$target" ]] && add_target "$target"
    done
fi

if [[ ${#TARGET_DIRS[@]} -eq 0 ]]; then
    add_target "${CODEX_HOME:-$HOME/.codex}/skills"
    add_target "$HOME/.claude/skills"
fi

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
    SKILL_NAMES=()
    SKILL_SOURCES=()
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
    local link="$1"
    local source="$2"

    if [[ -L "$link" ]]; then
        local current
        current="$(readlink "$link")"
        if [[ "$current" == "$source" ]]; then
            echo "installed"
        else
            echo "points to $current"
        fi
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
        for target in "${TARGET_DIRS[@]}"; do
            link="$target/${SKILL_NAMES[$i]}"
            status="$(link_status "$link" "${SKILL_SOURCES[$i]}")"
            echo "  $target: $status"
        done
    done
}

install_skills() {
    local target i name source link current created updated skipped

    echo -e "${BLUE}=== Install Gui Ge Skills ===${NC}"
    echo "Source: $SKILLS_ROOT"

    for target in "${TARGET_DIRS[@]}"; do
        echo -e "${BLUE}Target:${NC} $target"
        if ! $DRY_RUN; then
            mkdir -p "$target"
        fi

        created=0
        updated=0
        skipped=0

        for i in "${!SKILL_NAMES[@]}"; do
            name="${SKILL_NAMES[$i]}"
            source="${SKILL_SOURCES[$i]}"
            link="$target/$name"

            if [[ -e "$link" && ! -L "$link" ]]; then
                echo -e "  ${YELLOW}Skip:${NC} $name (target exists and is not a symlink)"
                ((skipped+=1))
                continue
            fi

            if [[ -L "$link" ]]; then
                current="$(readlink "$link")"
                if [[ "$current" == "$source" ]]; then
                    ((skipped+=1))
                    continue
                fi
                echo -e "  ${GREEN}Update:${NC} $name -> $source"
                if ! $DRY_RUN; then
                    rm "$link"
                    ln -s "$source" "$link"
                fi
                ((updated+=1))
            else
                echo -e "  ${GREEN}Link:${NC} $name -> $source"
                if ! $DRY_RUN; then
                    ln -s "$source" "$link"
                fi
                ((created+=1))
            fi
        done

        echo "  Created: $created, Updated: $updated, Unchanged: $skipped"
    done
}

cleanup_stale_links() {
    local target entry link current removed

    echo -e "${BLUE}=== Cleanup Stale Managed Symlinks ===${NC}"
    for target in "${TARGET_DIRS[@]}"; do
        echo -e "${BLUE}Target:${NC} $target"
        removed=0

        [[ -d "$target" ]] || {
            echo "  Target directory does not exist"
            continue
        }

        shopt -s nullglob
        for link in "$target"/*; do
            [[ -L "$link" ]] || continue
            entry="$(basename "$link")"
            current="$(readlink "$link")"
            case "$current" in
                "$SKILLS_ROOT"/*|"$SCRIPT_DIR"/*)
                    if [[ ! -d "$current" || ! -f "$current/SKILL.md" ]]; then
                        echo -e "  ${RED}Remove stale:${NC} $entry -> $current"
                        if ! $DRY_RUN; then
                            rm "$link"
                        fi
                        ((removed+=1))
                    fi
                    ;;
            esac
        done
        shopt -u nullglob

        if [[ $removed -eq 0 ]]; then
            echo "  No stale symlinks found"
        else
            echo "  Removed: $removed"
        fi
    done
}

discover_skills

if $LIST; then
    list_skills
    exit 0
fi

install_skills

if $CLEANUP; then
    cleanup_stale_links
fi

if $DRY_RUN; then
    echo -e "${YELLOW}(dry-run mode - no changes were made)${NC}"
fi

echo -e "${GREEN}Done!${NC}"
