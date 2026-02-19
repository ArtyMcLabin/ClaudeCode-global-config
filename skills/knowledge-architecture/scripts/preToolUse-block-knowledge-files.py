#!/usr/bin/env python3
"""
PreToolUse blocker: Blocks Edit/Write to CLAUDE.md and SKILL.md files.

Forces Claude to read the knowledge-architecture skill BEFORE modifying
these governed files. Regular .md files still get the softer PostToolUse reminder.

Behavior:
  1st edit attempt → BLOCK + create temp marker file (warns Claude to read skill)
  2nd edit attempt → marker exists (Claude was warned) → ALLOW + delete marker

This avoids the permanent-wall bug where edits were blocked unconditionally
even after Claude read the skill.

Exit code 2 = BLOCK the tool call + feed stderr to Claude.
Exit code 0 = allow through silently.
"""
import json
import sys
import os
import tempfile

try:
    input_data = json.load(sys.stdin)
except (json.JSONDecodeError, EOFError):
    sys.exit(0)

file_path = input_data.get("tool_input", {}).get("file_path", "")
if not file_path:
    sys.exit(0)

basename = os.path.basename(file_path).upper()

# Only block CLAUDE.md and SKILL.md — the files governed by knowledge-architecture
if basename not in ("CLAUDE.MD", "SKILL.MD"):
    sys.exit(0)

# Marker file: indicates Claude was already warned for this file type
marker_path = os.path.join(tempfile.gettempdir(), f"claude-knowledge-arch-warned-{basename}")

if os.path.exists(marker_path):
    # Claude was already warned — allow this edit through and clean up marker
    os.remove(marker_path)
    sys.exit(0)

# First attempt — create marker and block
with open(marker_path, "w") as f:
    f.write("warned")

content = (
    f"BLOCKED: You are trying to edit {basename}. "
    "This file is governed by the knowledge-architecture skill. "
    "You MUST read ~/.claude/skills/knowledge-architecture/SKILL.md FIRST, "
    "then retry the edit following its rules (one-liners in CLAUDE.md, proper skill structure for SKILL.md)."
)

border = "=" * 70
boxed = "\n".join(f"| {line}" for line in content.split("\n"))
msg = f"\n+{border}\n| PRETOOLUSE HOOK OUTPUT\n+{border}\n{boxed}\n+{border}\n"
print(msg, file=sys.stderr)
sys.exit(2)
