#!/usr/bin/env python3
"""
PreToolUse hook: Block creation of scripts that directly access production database.

Matches on Write tool calls. Blocks if the file content contains BOTH:
1. A production database hostname pattern (ep-flat-block)
2. A direct database client call (neon(, pg(, Pool(, Client(, sql`)

This prevents creating bypass scripts that run raw SQL against prod,
while allowing legitimate files like migrate.ts and import scripts
(which go through proper Drizzle ORM channels).

Exit codes:
  0 = allow (no prod bypass detected)
  2 = block (prod bypass script detected)
"""
import json
import sys

try:
    data = json.load(sys.stdin)
except (json.JSONDecodeError, EOFError):
    sys.exit(0)

tool_name = data.get("tool_name", "")
if tool_name != "Write":
    sys.exit(0)

tool_input = data.get("tool_input", {})
file_path = tool_input.get("file_path", "").lower()
content = tool_input.get("content", "")

# Only check TypeScript/JavaScript files (bypass scripts)
if not any(file_path.endswith(ext) for ext in (".ts", ".js", ".mts", ".mjs")):
    sys.exit(0)

# Allow known blessed files that legitimately reference prod
blessed_files = [
    "scripts/migrate.ts",
    "scripts/import-from-xlsx.ts",
    "scripts/import-longs-from-xlsx.ts",
    "scripts/import-cli.ts",
    "scripts/quick-count.ts",
    "api/db/index.ts",
]
for blessed in blessed_files:
    if file_path.replace("\\", "/").endswith(blessed):
        sys.exit(0)

# Production database hostname patterns
prod_patterns = [
    "ep-flat-block",           # Neon prod host
    "PROD_DATABASE_URL",       # Env var naming convention
    "prod_url",                # Variable naming
    "production_url",          # Variable naming
]

# Direct database client patterns (bypassing Drizzle ORM)
db_client_patterns = [
    "neon(",                   # @neondatabase/serverless
    "new Pool(",               # pg Pool
    "new Client(",             # pg Client
    "createPool(",             # mysql2/postgres pools
    "sql`",                    # Tagged template SQL
]

content_lower = content.lower()

has_prod_ref = any(p.lower() in content_lower for p in prod_patterns)
has_db_client = any(p.lower() in content_lower for p in db_client_patterns)

if has_prod_ref and has_db_client:
    content = (
        "BLOCKED: This script directly accesses the production database, "
        "bypassing Drizzle ORM migration tracking. "
        "All database changes MUST go through `npm run db:migrate` or Vercel CI/CD. "
        "See CLAUDE.md: 'Database Migration Tools - Fix Root Causes, Never Workaround'. "
        "If you believe this is a false positive, ask the user for permission."
    )

    border = "=" * 70
    boxed = "\n".join(f"| {line}" for line in content.split("\n"))
    msg = f"\n+{border}\n| PRETOOLUSE HOOK OUTPUT\n+{border}\n{boxed}\n+{border}\n"
    print(msg, file=sys.stderr)
    sys.exit(2)

sys.exit(0)
