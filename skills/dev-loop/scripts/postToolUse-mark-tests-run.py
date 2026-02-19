#!/usr/bin/env python3
"""PostToolUse hook: Mark that tests were run for the current repo.

Fires after every Bash command. If the command matches known test patterns,
creates a session marker file keyed to the repo's CWD. This marker is
checked by preToolUse-block-push-without-tests.py before allowing git push.

Marker location: %TEMP%/claude-tdd-markers/tests-run-<cwd_hash>

Exit code: Always 0 (PostToolUse hooks are informational, never block).
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
if tool_name != "Bash":
    sys.exit(0)

tool_input = data.get("tool_input", {})
command = tool_input.get("command", "").lower()

# Test command patterns (aligned with stop-verify-pipeline.py)
TEST_PATTERNS = [
    "npm test",
    "npm run test",
    "npx vitest",
    "npx jest",
    "npx playwright",
    "test:free",
    "test:all",
    "test:e2e",
    "test:unit",
    "pytest",
    "go test",
    "cargo test",
    "phpunit",
    "playwright test",
]

if not any(pattern in command for pattern in TEST_PATTERNS):
    sys.exit(0)

cwd = os.getcwd()
cwd_hash = hashlib.md5(cwd.replace("\\", "/").lower().encode()).hexdigest()[:12]

marker_dir = os.path.join(tempfile.gettempdir(), "claude-tdd-markers")
os.makedirs(marker_dir, exist_ok=True)
marker_file = os.path.join(marker_dir, f"tests-run-{cwd_hash}")

with open(marker_file, "w") as f:
    f.write(command)

sys.exit(0)
