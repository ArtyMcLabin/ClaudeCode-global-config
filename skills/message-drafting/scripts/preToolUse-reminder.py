#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""PreToolUse reminder hook for message-drafting skill.

Fires before gmail send/draft operations to ensure the message-drafting
skill is acknowledged before any email goes out.
"""
import json
import sys

try:
    data = json.load(sys.stdin)
except (json.JSONDecodeError, EOFError):
    sys.exit(0)

tool_name = data.get("tool_name", "")

# Match any gmail send or draft tool
gmail_send_tools = {
    "mcp__google-workspace__gmail_send",
    "mcp__google-workspace__gmail_createDraft",
    "mcp__google-workspace__gmail_sendDraft",
    "mcp__gmail__send_email",
    "mcp__gmail__draft_email",
}

if tool_name not in gmail_send_tools:
    sys.exit(0)

content = (
    "Reminder: You are about to send/draft an email. "
    "Ensure you have loaded the message-drafting skill "
    "(~/.claude/skills/message-drafting/SKILL.md) and followed its rules: "
    "draft review workflow, post-send disposition, GR email addressing, internal email format."
)

border = "=" * 70
boxed = "\n".join(f"| {line}" for line in content.split("\n"))
msg = f"\n+{border}\n| PRETOOLUSE HOOK OUTPUT\n+{border}\n{boxed}\n+{border}\n"
print(msg, file=sys.stderr)
sys.exit(0)
