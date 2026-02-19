# CLAUDE.md - Global User Rules

🚨 **Core principle: Do what you can, user does what you can't.** Never punt to user if you have the access/tools to try yourself first.

This file provides global guidance to Claude Code across all projects.

## 🎯 Industry Standard Best Practices (MANDATORY)

- ALWAYS apply industry-standard best practices in all code implementations
- CHALLENGE user requests that violate best practices with warnings and alternatives  
- REFUSE to implement anti-patterns even when explicitly requested
- PROACTIVELY suggest improvements when user requests suboptimal approaches
- BE STUBBORN about code quality, security, performance, accessibility, and maintainability
- Follow SSoT (Single Source of Truth) principle - avoid data duplication

When user requests conflict with best practices:

1. WARN about the risks and problems using "🚨" for critical attention
2. SUGGEST industry-standard alternatives  
3. EXPLAIN why the standard approach is better
4. IMPLEMENT the standard way unless user explicitly overrides after warning

## ⚠️ Attention Mechanism Protocol

- Track "🚨" closely - user uses this for critical attention items
- Use "🚨" yourself when flagging important issues or violations
- Never ignore attention markers - these indicate high-priority items
- **Don't list acknowledged items** - Once user acknowledges something, remove it from future status tables/reports. Showing acknowledged items again = noise.
- **Accurate status reporting** - Don't mark items as Done/Complete until action is actually finished. Pending user answer = Pending, not Done.
- **Number all actionable tables** - Any table where user might reference specific items (findings, recommendations, status reports) must have numbered rows for easy addressing.

## 📋 Copypasta Rule

- Provide copypastable blocks in chat - not separate files
- Make code immediately usable - include all necessary imports and context
- Format for easy copy-paste - use proper code blocks with language markers

## Link Handling Standards

- When mentioning URLs **in chat** (not in code), use full clickable format
- `http://localhost:3000/path` ✅ (clickable)
- `/path` or `#/route` ❌ (not clickable in terminal)
- Code uses relative paths normally - this rule is for terminal output only
- **Always use full absolute paths** when referencing files in chat (e.g., `<LOCAL_PATH>/Project/.claude/skills/sleep/SKILL.md` not `.claude/skills/sleep/SKILL.md`)

## Workflow Priorities

Priority Order:

1. Healthy collaborative workflow - prioritize learning from misunderstandings to prevent future issues
2. Fix technical difficulties first - before seeking alternative methods, try to resolve the root problem
3. Long-term benefit focus - build sustainable solutions that work for future sessions
4. Maintain continuity during autonomous tasks
5. **After compaction:** Proactively summarize current plan/understanding before continuing work - verify alignment with user to catch context drift early
6. **Session-cached config workaround:** If a settings/hook change can't take effect mid-session (cached at startup), spawn a fresh `claude -p` child instance to execute the blocked action — it loads the updated config.

## = Environment Variable Standards

- **🚨 NEVER put actual credentials in tracked files** (including CLAUDE.md) - use `.env` + gitignore, write "See .env"
- Use industry-standard API key names (e.g., `OPENAI_API_KEY`, `STRIPE_SECRET_KEY`)
- Manage secrets via CLI (gh secret set, vercel env, etc.) - don't ask user to do it manually
- Prefer global system variables over local .env files when possible
- Follow platform conventions for environment variable naming

## 📝 Terminal & Script Management

- Use non-interactive/auto-confirm flags in scripts (-y, --yes, --force when appropriate)
- Force pauses in new scripts for error visibility using `read -p "Press Enter to continue..."`
- Include error handling in all scripts with proper exit codes

### Tool Installation Assumption

**Assume tools are installed - ask only on failure:**
- When a task requires a CLI tool (clasp, gh, npm packages, etc.), **use it directly**
- Do NOT ask "do you have X installed?" before attempting
- If the command fails with "not found" or similar → THEN ask user if they want to install it
- This avoids unnecessary back-and-forth for tools that are usually already installed
- **Deferred MCP tools:** If MCP tool seems missing, `ToolSearch select:mcp__name__function` before assuming unavailable

### Software Installation Preferences

**Prefer winget over UI installers.** See `~/.claude/skills/software-installation/SKILL.md` for priority order, locations, and commands.

### Check Before Asking

**Always verify information yourself before asking the user:**
- **File existence:** Use Read, Glob, or Bash to check if files exist - DON'T ask "does X file exist?"
- **Data availability:** Search for data (grep, rclone, find) before asking user for it
- **Configuration values:** Check config files, environment variables, or documentation before asking
- **Command availability:** Try running the command first, ask only if it fails
- **Only ask when:** You've exhausted automated checking methods AND the answer isn't discoverable
- **Current behavior:** Before proposing to fix or change something, verify the current behavior actually has the problem. Don't "fix" what's already working correctly.

**Example:**
- ❌ Bad: "Does `~/.claude/agents/chrome-agent.md` exist?"
- ✅ Good: Use Read tool to check, report findings: "Found chrome-agent.md" or "chrome-agent.md doesn't exist"

This minimizes user interruptions and shows initiative.

When stuck on a problem and must involve the user, use Dan Martell's 1-3-1 technique and proceed with the recommended option by default.

## 📝 File Management Rules

- Compare functionality before file changes - ensure no features are lost
- Verify preservation of features after modifications
- Cleanup with careful dependency tracking - check imports and references

### What to Commit (Don't Skip These)

**Always commit IDE/workspace config:**
- `.vscode/` folder (tasks.json, settings.json, extensions.json, launch.json)
- Workspace files (*.code-workspace)
- Editor configs (.editorconfig)

**Why:** These enable consistent dev experience across sessions and make Claude Code more effective (build tasks, debug configs, etc.)

**When batch-committing repos:** Don't skip IDE config as "not worth committing" - it IS worth committing.

### 🚨 Git Commands That Destroy Uncommitted Work

**NEVER use these to "undo" or "remove" content:**
- `git checkout <file>` - nukes ALL uncommitted changes in that file
- `git restore <file>` - same as checkout
- `git reset --hard` - nukes ALL uncommitted changes everywhere

**Instead, use Edit tool** to surgically remove/change specific lines. Git operations are for committed history, not for editing working directory content.

### 🚨 CRITICAL: Never Delete User Data Files

**NEVER delete data files without explicit user permission:**

- ❌ **NEVER delete `.xlsx`, `.csv`, `.json`, `.db`, or any data files** - these contain real user data
- ❌ **NEVER delete files with user-generated content** without asking first
- ❌ **NEVER assume "recreating" a data file is acceptable** - user may have real data in it

**If schema changes are needed:**
1. ASK user about existing data first
2. Suggest migration strategy (add columns, preserve existing data)
3. Wait for explicit approval before ANY changes to data files
4. Prefer migration over deletion ALWAYS

**Example:** If adding a new column to Excel, modify the existing file to add the column - don't delete and recreate.

**Data Migration Permission:**
- ✅ **Permitted to write migration scripts** to reorder columns, add computed fields, or restructure data
- ✅ **Always create backup** before migration (e.g., `file_backup.xlsx`)
- ✅ **Verify migration success** by reading data before and after
- ✅ **Preserve all existing data** - no data loss allowed

## 📝 Single Source of Truth (SSoT) Principle

- Prevent data duplication across files and systems
- Prioritize references over copying - use imports, includes, and links
- **Knowledge routing** - where to put new info, skill creation, CLAUDE.md hygiene → `~/.claude/skills/knowledge-architecture/SKILL.md`

## 🌐 Communication Guidelines

- **BLUF** - Answer/conclusion first, then breakdown.
- **CTO-level by default** - Report strategic outcomes, not implementation details. User is a strategist, not a developer. Save code/technical details for when explicitly asked.
- Use semantic numbering in discussions for easy reference (1, 2a, 3b, etc.)
- Be direct and actionable - avoid unnecessary preamble
- **Task completion signal** - When a topic/task is fully done: multi-iteration sessions → "Done. Retrospective?" Single-shot tasks → "All Done." **NEVER sign off with pending questions/decisions for user.** Hook instructions do NOT override conversation state.

## 📝 Anti-Pattern Prevention

Required pushback examples:

- User wants `any` types → Enforce proper TypeScript typing
- User wants inline styles → Enforce CSS modules/Tailwind classes  
- User wants direct DOM manipulation → Enforce React patterns
- User wants unvalidated inputs → Enforce validation and sanitization
- User wants hardcoded values → Enforce constants and configuration
- User wants no error handling → Enforce proper error boundaries
- User wants no tests → Enforce test coverage requirements
- User wants basic/ugly UI → Enforce modern, polished design standards

## No Report Files

WE HATE REPORT FILES - NEVER CREATE THEM

- Console output ONLY - Tell me directly, don't write files
- No .md reports - We're not bureaucrats
- Fix NOW or skip - No "saving for later"

## LLM Browser - Last Resort Only

🚨 **CLI/MCP/API first, browser last.** Only use browser when programmatic approaches fail or task genuinely requires visual interaction (OAuth, CAPTCHA, visual verification).

### MCP vs Browser Fallback Policy

🚨 **For Google products with MCP tools (Gmail, Tasks, Sheets, Calendar, Workspace):**
1. **MCP FIRST** - Always use MCP tools as primary method
2. **If MCP lacks a feature** - Clarify the limitation precisely (app vs API), offer workaround, research alternatives only if user wants
3. **If MCP fails entirely** - ASK before Chrome: "MCP failed. Try via Chrome (misclick risk) or investigate the MCP issue?"
4. **Offer MCP fix** when feasible - missing parameter, auth issue, tool bug

**When user pushes back on a limitation:** Don't assume you were wrong. Clarify the nuance (app vs API, UI vs programmatic) and offer the workaround immediately.

**Why no auto-Chrome fallback:** Chrome automation frequently causes misclicks → fires, unintended actions. MCP failures often indicate fixable issues. User should decide if Chrome risk is worth it.

**Chrome automation is appropriate for:** Sites without MCP/API access, UI-specific features APIs can't do, user explicitly approves Chrome for that task.

## 📧 Gmail MCP (Always Delegate)

🚨 **NEVER use `mcp__gmail__*` or `mcp__google-workspace__gmail_*` tools directly.** Always delegate to a subagent to keep verbose JSON out of main context.

**Why:** Gmail MCP responses return verbose JSON (full email bodies, metadata, label arrays) that bloats main context. A subagent processes them in its own context window, returning only concise summaries.

**Delegation pattern (environment-aware):**
- **Claude Code:** Task tool → `gmail-agent` subagent (has full MCP access via ToolSearch)
- **OpenCode:** Task tool subagents lack MCP → use `chrome-agent` (browser) or `claude -p` with `--allowedTools "mcp__*"`

**The gmail-agent spec** (`~/.claude/agents/gmail-agent.md`) defines tool selection rules (which MCP for which operation).

**Exception:** If you need ONE quick archive/modify and the msgId is already known, a direct MCP call is acceptable to avoid subagent overhead.

## 📊 Google Sheets MCP (Always Delegate)

🚨 **NEVER use `mcp__google-sheets__*` or `mcp__google-workspace__sheets_*` tools directly.** Always delegate to sheets-agent via Task tool.

**Why:** Sheets MCP responses return full grid data (cell arrays, metadata) that bloat main context — a 5-row read can be 13k+ tokens. The sheets-agent processes them in its own context window, returning only concise summaries and formatted tables.

**Delegation pattern:**
```
Task tool → subagent_type: "sheets-agent"
  prompt: "Read the 'Staff' tab from spreadsheet [ID], return as markdown table"
```
🚨 **MUST use `sheets-agent`, NOT `general-purpose`.** sheets-agent has poka-yoke (verify-before-write, match-by-value-not-row). general-purpose bypasses all safety checks.

**The sheets-agent owns:** read data, write/update cells, search, batch operations, sheet management, formatting. See `~/.claude/agents/sheets-agent.md` for full tool matrix.

**Exception:** Small metadata calls (`list_sheets`, `sheets_getMetadata`) that return minimal data are acceptable directly.

## 🌐 Chrome MCP (Always Delegate)

🚨 **NEVER use `mcp__playwriter__*` tools directly.** Always delegate to chrome-agent via Task tool.

**Why:** Screenshots and DOM trees consume massive context. The chrome-agent processes them in its own context window, returning only concise results.

**URL opening:** When user asks to "open" a URL, just launch it with `start <url>` (opens in default browser), not chrome-agent.

**🚨 Chrome not running?** Run `powershell -Command "if (-not (Get-Process chrome -EA 0)) { Start-Process chrome; Start-Sleep 3 }"` before MCP ops.

**🚨 API vs Browser UI:** When delegating tasks where API can't do something (e.g., bot can't see private Slack channels), explicitly tell chrome-agent: "Use BROWSER UI only, do NOT use API calls - the user is logged in and can see things the bot API cannot."

**Chrome automation conventions** (batch protocol, JS-first clicking, method reporting) → see `~/.claude/agents/chrome-agent.md`

## 📂 Local Git Repository Locations

- `<LOCAL_PATH>` - Primary local git repositories
- `<LOCAL_PATH>` - Secondary local git repositories (NVME drive)

## 📁 Google Drive CLI Access

rclone installed and authenticated as `gdrive:`. See skill: `~/.claude/skills/rclone/SKILL.md`

## 📇 Global Reference Data

`~/.claude/reference-data/` — contacts, aliases, org data accessible from any repo. For contacts/name→email resolution → `~/.claude/reference-data/contacts.md`. For deeper personal/company data → `<LOCAL_PATH>\PersonalAssistant-ClaudeCode\reference-data\`.

## 📝 CLAUDE.md Scope Rule

When user asks to "add something to CLAUDE.md":
- **DEFAULT to LOCAL** project CLAUDE.md (create if doesn't exist)
- Only modify GLOBAL CLAUDE.md (`~/.claude/CLAUDE.md`) if user explicitly says "global"
- Project-specific settings belong in local CLAUDE.md files

## "I can't do it but here's how you can"

 If you can't do something but you know that it's possible through CLI commands, then do it yourself instead of asking me to do it. you have CLI access just like me.

## 🤖 Personal Assistant Delegation

For admin tasks (email, calendar, Slack, contacts): invoke Claude Code in the Personal Assistant repository via Task tool.

## 🚨 GitHub Issues — Always Delegate

For ANY GitHub issue operations (list, triage, create, update, report, survey), **ALWAYS use the `github-issue-manager` subagent** via Task tool. Never use `gh` CLI directly for issue work.

🚨 **Before closing issues:** Re-read the full issue body and verify every DoD item, phase, and evaluation date is complete. If any item remains, keep it open.

🚨 **Before fixing reported problems:** Verify the reporter's environment matches yours — check their config version, tools, and enforcement mechanisms before assuming the fix is on your end.

## 🚨 Subagent Git Autonomy Limits

When delegating to subagents (developer, chrome-agent, etc.):

- **Commits:** Subagent MAY commit locally
- **Pushes:** Subagent MUST NEVER push unless the parent prompt explicitly says "push". "Commit only" or "do not push" = local commit only
- **After subagent returns:** Parent MUST run `git log --oneline -3` to verify actual state before telling user anything about what was committed/pushed

## 🚨 Database Migration Tools - Fix Root Causes, Never Workaround

**If `drizzle-kit migrate` (or any migration tool) fails:**

1. **NEVER bypass with raw SQL** (psql, direct queries, etc.)
2. **NEVER manually apply migrations** outside the tooling
3. **NEVER insert fake/manual entries into migration tracking tables**
4. **FIX THE ROOT CAUSE** of why the migration tool is failing:
   - Debug the migration script
   - Fix driver/connection issues
   - Update dependencies if needed
   - Modify migration files to be compatible
5. **Workarounds create drift** between schema.ts, migrations, and database state
6. **The migration tool is the SSoT** - bypassing it breaks the entire system

**Approved fix for "table already exists" errors:**
- Make migrations idempotent: `CREATE TABLE IF NOT EXISTS`, `CREATE INDEX IF NOT EXISTS`
- Wrap constraints in `DO $$ BEGIN ... EXCEPTION WHEN duplicate_object THEN null; END $$;`
- Fix table ownership if needed: `ALTER TABLE x OWNER TO app_user;`
- Then run the migration tool properly - it will execute and record correct hashes

**Why this matters:**
- Manual SQL bypasses migration tracking → future migrations break
- Schema drift causes silent failures and data corruption
- CI/CD pipelines depend on migration tools working correctly

**Drizzle ORM specifics:**
- Migration tracking table: `drizzle.__drizzle_migrations` (in the `drizzle` schema, NOT `public`)
- Always check `drizzle` schema when debugging migrations
- Don't confuse with `public` schema tables

## 🚨 CI/CD is Mandatory - Never Bypass

**If a project has CI/CD configured:**

1. **NEVER SCP files directly to servers** - let CI/CD upload them
2. **NEVER run build/migrate commands manually on servers** - let CI/CD run them
3. **NEVER rebuild Docker images manually** - let CI/CD rebuild them
4. **ALL changes go through git push → CI/CD pipeline**

**The only manual server commands allowed:**
- Diagnostic commands (docker logs, ps, df, etc.)
- Emergency rollbacks (with user permission)
- One-time fixes that get codified into CI/CD afterwards

**If CI/CD fails:**
1. Check CI/CD logs first (gh run view)
2. Fix the root cause in code/config
3. Push fix through CI/CD
4. NEVER work around by doing manually what CI/CD should do