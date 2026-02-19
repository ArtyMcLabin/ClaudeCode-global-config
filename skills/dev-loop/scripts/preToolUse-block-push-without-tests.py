#!/usr/bin/env python3
"""PreToolUse hook: Block git push if tests haven't been run this session.

Fires before every Bash command. If the command contains 'git push',
checks for a per-repo session marker created by postToolUse-mark-tests-run.py.

Uses the same doc/code distinction as stop-verify-pipeline.py:
if only doc/config files were edited (no code edits), push is allowed.

Exclusions:
- Context-engineering repos (no test suites)
- Dry-run pushes
- Doc/config-only changes (no code files edited)

Exit codes:
  0 = allow (not a push, tests were run, excluded repo, or doc-only session)
  2 = block (push without tests when code was edited)
"""
import json
import sys
import os
import tempfile
import hashlib
import re

try:
    data = json.load(sys.stdin)
except (json.JSONDecodeError, EOFError):
    sys.exit(0)

tool_name = data.get("tool_name", "")
if tool_name != "Bash":
    sys.exit(0)

tool_input = data.get("tool_input", {})
command = tool_input.get("command", "")
command_lower = command.lower()

# Only care about git push commands
if not re.search(r'\bgit\s+push\b', command_lower):
    sys.exit(0)

# Allow dry-run pushes
if "--dry-run" in command_lower:
    sys.exit(0)

cwd = os.getcwd()
cwd_normalized = cwd.replace("\\", "/").lower()

# Exclude context-engineering repos (no tests to run)
EXCLUDED_REPO_PATTERNS = [
    "gh_coordinator",
    "personalassistant",
    "/.claude",
    "csv_to_gsheets",
]
if any(pattern in cwd_normalized for pattern in EXCLUDED_REPO_PATTERNS):
    sys.exit(0)

cwd_hash = hashlib.md5(cwd_normalized.encode()).hexdigest()[:12]

marker_dir = os.path.join(tempfile.gettempdir(), "claude-tdd-markers")
marker_file = os.path.join(marker_dir, f"tests-run-{cwd_hash}")

# If tests were run, allow
if os.path.exists(marker_file):
    sys.exit(0)

# Check if only doc/config files were edited (same logic as stop-verify-pipeline.py)
# If a code-edits marker exists, block. If not, allow (doc-only session).
code_marker = os.path.join(marker_dir, f"code-edits-{cwd_hash}")
if not os.path.exists(code_marker):
    # No code edits detected — doc/config-only session, push is fine
    sys.exit(0)

repo_name = os.path.basename(cwd)
content = (
    f"BLOCKED: git push attempted but no tests were run this session "
    f"for {repo_name}.\n\n"
    "Dev-loop SOP requires running the test suite BEFORE pushing code changes.\n"
    "Run the project's test command first (e.g., npm test, pytest).\n\n"
    "If this repo has no tests, add it to EXCLUDED_REPO_PATTERNS in\n"
    "~/.claude/skills/dev-loop/scripts/preToolUse-block-push-without-tests.py"
)

border = "=" * 70
boxed = "\n".join(f"| {line}" for line in content.split("\n"))
msg = f"\n+{border}\n| PRETOOLUSE HOOK OUTPUT\n+{border}\n{boxed}\n+{border}\n"
print(msg, file=sys.stderr)
sys.exit(2)
