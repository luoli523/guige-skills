#!/usr/bin/env bash
# PreToolUse(Bash) hook — warn when a Bash command tries to rm -r/-rf a
# guige-skills runtime output directory. Warn-only: prints to stderr and
# always exits 0, letting Claude decide whether to proceed.
#
# Input on stdin (Claude Code hook protocol):
#   { "tool_name": "Bash", "tool_input": { "command": "..." }, ... }

set -u

input=$(cat)

command=$(printf '%s' "$input" | python3 -c '
import json, sys
try:
    data = json.load(sys.stdin)
    print(data.get("tool_input", {}).get("command", ""))
except Exception:
    pass
' 2>/dev/null)

if [ -z "$command" ]; then
    exit 0
fi

if ! printf '%s' "$command" | grep -Eq '(^|[^A-Za-z0-9_])rm[[:space:]]+-[A-Za-z]*[rR][A-Za-z]*'; then
    exit 0
fi

PROTECTED=(
    "infographic"
    "hand-write-pic"
    "imagen"
    "svg"
    "slide-deck"
    "x-to-markdown"
    "post-to-wechat"
    "wechat"
    "downloads"
    "generated"
    "guige-skill-imagen"
    "guige-skill-video"
)

matched=()
for dir in "${PROTECTED[@]}"; do
    if printf '%s' "$command" | grep -Eq "(^|[[:space:]]|/|=|~)${dir}(/|[[:space:]]|\$|'|\")"; then
        matched+=("$dir")
    fi
done

if [ ${#matched[@]} -gt 0 ]; then
    {
        echo "⚠️  guige-skills guard: 检测到 rm -r/-rf 指向受保护的运行时输出目录:"
        for d in "${matched[@]}"; do
            echo "    - ${d}/"
        done
        echo "    这些目录保存 skill 的生成产物 (见 CLAUDE.md → Runtime Output Directories)"
        echo "    如果不是有意清理，请取消该删除操作"
    } >&2
fi

exit 0
