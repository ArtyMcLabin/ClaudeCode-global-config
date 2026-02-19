#!/usr/bin/env python3
"""PreToolUse poka-yoke hook: block rclone unless MCP fallback approved.

Process:
1. Claude tries MCP (Google Drive/Sheets/Workspace) first
2. If MCP fails -> tell user -> get permission
3. Only then use rclone with #RCLONE-FALLBACK-APPROVED flag

Bypass: Include #RCLONE-FALLBACK-APPROVED in the Bash command.
"""
import json
import sys

try:
    data = json.load(sys.stdin)
except (json.JSONDecodeError, EOFError):
    sys.exit(0)

tool_name = data.get("tool_name", "")
tool_input = data.get("tool_input", {})
command = tool_input.get("command", "")

# Only check Bash commands containing rclone
if "rclone" not in command.lower():
    sys.exit(0)

BYPASS_FLAG = "#RCLONE-FALLBACK-APPROVED"

# Check for bypass flag
if BYPASS_FLAG in command:
    sys.exit(0)  # User approved fallback, allow through

# Block with instructions
border = "=" * 70
content = (
    "BLOCKED: rclone command detected.\n"
    "\n"
    "rclone is a READ-ONLY FALLBACK. Required process:\n"
    "1. Use Google Drive/Sheets/Workspace MCP tools FIRST\n"
    "2. If MCP fails -> tell user the failure\n"
    "3. Get explicit user permission to use rclone as fallback\n"
    "4. Re-run with {} in the command\n"
    "\n"
    "NEVER use rclone for write/delete operations (deletefile, move, copy-to-remote).\n"
    "NEVER assume .xlsx on Drive is a standalone file -- Google Sheets appear as .xlsx in rclone.\n"
    "\n"
    "Example: rclone lsf gdrive: {} --max-depth 3"
).format(BYPASS_FLAG, BYPASS_FLAG)

msg = "\n+{}+\n| PRETOOLUSE HOOK OUTPUT\n+{}+\n| {}\n+{}+\n".format(
    border, border, content.replace("\n", "\n| "), border
)
print(msg, file=sys.stderr)
sys.exit(2)
