#!/usr/bin/env python3
"""
PreToolUse hook: Block raw SQL write operations against production databases.

Poka-yoke pattern: Block by default, allow bypass with explicit flag.

Matches on Bash tool calls. Blocks if the command contains BOTH:
1. psql (or similar SQL CLI tools)
2. A write operation keyword (UPDATE, INSERT, DELETE, ALTER, DROP, TRUNCATE)

Bypass: If the command contains the flag --sql-write-confirmed, the hook
allows it through. This forces Claude to consciously acknowledge that
direct SQL is the right approach (e.g., when Admin API doesn't support
the operation).

Exit codes:
  0 = allow (no raw SQL write detected, or bypass flag present)
  2 = block (raw SQL write detected without bypass flag)
"""

import json
import re
import sys

try:
    data = json.load(sys.stdin)
except (json.JSONDecodeError, EOFError):
    sys.exit(0)

tool_name = data.get("tool_name", "")
if tool_name != "Bash":
    sys.exit(0)

tool_input = data.get("tool_input", {})
command = tool_input.get("command", "")

if not command:
    sys.exit(0)

# Check if the command actually INVOKES a SQL CLI tool (not just mentions one in a string).
# Extract the actual executable: first token, or first token after && / || / ; / | chains.
# This prevents false positives from e.g. git commit messages that quote SQL examples.
def get_executables(cmd):
    """Extract command names that are actually being executed (not quoted text)."""
    executables = set()
    # Split on shell operators to get individual commands
    # Rough split — good enough to catch "git commit ..." vs "psql ..."
    parts = re.split(r'\s*(?:&&|\|\||;|\|)\s*', cmd)
    for part in parts:
        part = part.strip()
        if not part:
            continue
        # Get the first word (the executable)
        tokens = part.split()
        if tokens:
            # Handle env prefixes like PGCLIENTENCODING=UTF8 psql ...
            for token in tokens:
                if '=' in token and not token.startswith('-'):
                    continue  # skip env var assignments
                executables.add(token.lower())
                break
    return executables

executables = get_executables(command)

SQL_CLI_TOOLS = {"psql", "mysql", "sqlite3", "pgcli"}
has_sql_cli = bool(executables & SQL_CLI_TOOLS)

# Also catch python/node scripts that shell out to psql (e.g. subprocess.run(['psql',...]))
# But only if psql appears as a command argument, not inside a quoted commit message
if not has_sql_cli:
    # Check for python -c "...psql..." pattern (common in this project)
    if any(exe in ("python", "python3", "node") for exe in executables):
        # Only match if psql appears as a subprocess target, not in arbitrary strings
        if re.search(r"""['"]psql['"]""", command) or re.search(r"""\bsubprocess\.run\(\s*\[\s*['"]psql['"]""", command):
            has_sql_cli = True

if not has_sql_cli:
    sys.exit(0)

# Check for write operations (case-insensitive, word boundaries)
WRITE_KEYWORDS = [
    r"\bUPDATE\b",
    r"\bINSERT\b",
    r"\bDELETE\b",
    r"\bALTER\b",
    r"\bDROP\b",
    r"\bTRUNCATE\b",
    r"\bCREATE\s+TABLE\b",
    r"\bCREATE\s+INDEX\b",
]

has_write_op = any(re.search(pat, command, re.IGNORECASE) for pat in WRITE_KEYWORDS)

if not has_write_op:
    sys.exit(0)

# Check for bypass flag
BYPASS_FLAG = "--sql-write-confirmed"
if BYPASS_FLAG in command:
    # Flag present - allow through (psql will ignore the unknown flag in a comment)
    sys.exit(0)

# Block: raw SQL write without bypass flag
content = (
    "BLOCKED: Direct SQL write operation detected (UPDATE/INSERT/DELETE/ALTER/DROP/TRUNCATE via psql).\n"
    "\n"
    "PREFERRED APPROACH: Use the Admin API instead of raw SQL.\n"
    "  - Check if an API endpoint exists for this operation (see the relevant sysadmin skill, Admin API section)\n"
    "  - API calls have proper audit trails; direct SQL bypasses logging\n"
    "\n"
    "IF SQL IS GENUINELY REQUIRED (no API available for this operation):\n"
    f"  Re-run the command with a comment containing the bypass flag: {BYPASS_FLAG}\n"
    '  Example: psql "$DB_URL" -c "/* --sql-write-confirmed */ UPDATE org_hooks SET ..."\n'
    "\n"
    "This is a poka-yoke safety mechanism. The bypass flag confirms you've verified\n"
    "that no API alternative exists for this specific write operation."
)

border = "=" * 70
boxed = "\n".join(f"| {line}" for line in content.split("\n"))
msg = f"\n+{border}\n| PRETOOLUSE HOOK OUTPUT\n+{border}\n{boxed}\n+{border}\n"
print(msg, file=sys.stderr)
sys.exit(2)
