#!/usr/bin/env python3
"""Stop hook: Verify retrospective skill was invoked when user asked for one.

Checks if user said "retrospective"/"retro"/"context audit"/"what went wrong"
but Claude did ad-hoc analysis instead of invoking Skill("retrospective").

Exit 0 = silent (no trigger, or skill was invoked)
Exit 2 = feedback to Claude (stderr) reminding to use the skill
"""
import json
import os
import re
import sys

try:
    data = json.load(sys.stdin)
except (json.JSONDecodeError, EOFError):
    sys.exit(0)

transcript_path = data.get("transcript_path", "")
if not transcript_path or not os.path.exists(transcript_path):
    sys.exit(0)

TRIGGERS = re.compile(
    r"\b(retrospective|retro|introspect|context audit|what went wrong)\b", re.IGNORECASE
)

user_triggered = False
skill_invoked = False

with open(transcript_path, "r", encoding="utf-8") as f:
    for line in f:
        try:
            entry = json.loads(line.strip())
        except (json.JSONDecodeError, ValueError):
            continue

        if entry.get("type") == "user":
            content = entry.get("message", {}).get("content", "")
            # content can be string or list of blocks
            if isinstance(content, str):
                if TRIGGERS.search(content):
                    user_triggered = True
            elif isinstance(content, list):
                for block in content:
                    if isinstance(block, dict) and block.get("type") == "text":
                        if TRIGGERS.search(block.get("text", "")):
                            user_triggered = True

        elif entry.get("type") == "assistant":
            for block in entry.get("message", {}).get("content", []):
                if block.get("type") == "tool_use" and block.get("name") == "Skill":
                    skill_arg = block.get("input", {}).get("skill", "")
                    if skill_arg == "retrospective":
                        skill_invoked = True

if user_triggered and not skill_invoked:
    content = (
        "RETROSPECTIVE SKILL NOT INVOKED. User asked for a retrospective but you "
        "did ad-hoc analysis instead of calling Skill('retrospective'). "
        "Invoke it now — the skill has a strict output template."
    )

    border = "=" * 70
    boxed = "\n".join(f"| {line}" for line in content.split("\n"))
    msg = f"\n+{border}\n| STOP HOOK OUTPUT\n+{border}\n{boxed}\n+{border}\n"
    print(msg, file=sys.stderr)
    sys.exit(2)

sys.exit(0)
