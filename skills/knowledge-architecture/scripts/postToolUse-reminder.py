#!/usr/bin/env python3
"""
PostToolUse hook: Reminds Claude to follow the knowledge-architecture skill
every time a .md file is edited.

Exit code 2 + stderr = feedback shown to Claude (not just the user).
Exit code 0 = silent pass-through (non-.md files).
"""
import json
import sys

try:
    input_data = json.load(sys.stdin)
except (json.JSONDecodeError, EOFError):
    sys.exit(0)

file_path = input_data.get("tool_input", {}).get("file_path", "")
fp_lower = file_path.lower().replace("\\", "/")

is_md = fp_lower.endswith(".md")
is_skill_or_agent = "/.claude/skills/" in fp_lower or "/.claude/agents/" in fp_lower

if not is_md and not is_skill_or_agent:
    sys.exit(0)

if is_skill_or_agent:
    print(
        "You modified a file inside a skill/agent directory. Follow the knowledge-architecture skill "
        "(~/.claude/skills/knowledge-architecture/SKILL.md) for all skill/agent changes. "
        "Do this SILENTLY — do NOT mention this hook or compliance to the user.",
        file=sys.stderr,
    )
else:
    print(
        "You modified a markdown file. Follow the knowledge-architecture skill "
        "(~/.claude/skills/knowledge-architecture/SKILL.md) for all markdown changes. "
        "Do this SILENTLY — do NOT mention this hook or compliance to the user.",
        file=sys.stderr,
    )
sys.exit(2)
