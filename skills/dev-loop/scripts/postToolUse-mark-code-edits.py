#!/usr/bin/env python3
"""PostToolUse hook: Mark that code files were edited in this session.

Fires after Edit/Write/MultiEdit. If the edited file is a code file
(not doc/config), creates a per-repo marker. The push blocker uses this
to distinguish code sessions from doc-only sessions.

Uses the same doc/code classification as stop-verify-pipeline.py.

Marker location: %TEMP%/claude-tdd-markers/code-edits-<cwd_hash>

Exit code: Always 0 (informational).
"""
import json
import sys
import os
import tempfile
import hashlib

try:
    data = json.load(sys.stdin)
except (json.JSONDecodeError, EOFError):
    sys.exit(0)

tool_name = data.get("tool_name", "")
if tool_name not in ("Edit", "Write", "MultiEdit"):
    sys.exit(0)

file_path = data.get("tool_input", {}).get("file_path", "")
if not file_path:
    sys.exit(0)

fp = file_path.replace("\\", "/").lower()

# Doc/config extensions (aligned with stop-verify-pipeline.py)
DOC_EXTENSIONS = (".md", ".txt", ".json", ".yaml", ".yml", ".toml")
DOC_PATHS = ("reference-data/", "references/", ".claude/skills/", ".claude/agents/",
             ".claude/commands/", ".vscode/")

if any(fp.endswith(ext) for ext in DOC_EXTENSIONS):
    sys.exit(0)
if any(seg in fp for seg in DOC_PATHS):
    sys.exit(0)

# This is a code file edit — create marker
cwd = os.getcwd()
cwd_hash = hashlib.md5(cwd.replace("\\", "/").lower().encode()).hexdigest()[:12]

marker_dir = os.path.join(tempfile.gettempdir(), "claude-tdd-markers")
os.makedirs(marker_dir, exist_ok=True)
marker_file = os.path.join(marker_dir, f"code-edits-{cwd_hash}")

with open(marker_file, "w") as f:
    f.write(file_path)

sys.exit(0)
