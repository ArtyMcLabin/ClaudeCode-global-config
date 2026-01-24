# CLAUDE.md - Global User Rules

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

### Check Before Asking

**Always verify information yourself before asking the user:**
- **File existence:** Use Read, Glob, or Bash to check if files exist - DON'T ask "does X file exist?"
- **Data availability:** Search for data (grep, rclone, find) before asking user for it
- **Configuration values:** Check config files, environment variables, or documentation before asking
- **Command availability:** Try running the command first, ask only if it fails
- **Only ask when:** You've exhausted automated checking methods AND the answer isn't discoverable

**Example:**
- ❌ Bad: "Does `~/.claude/agents/chrome-agent.md` exist?"
- ✅ Good: Use Read tool to check, report findings: "Found chrome-agent.md" or "chrome-agent.md doesn't exist"

This minimizes user interruptions and shows initiative.

When stuck on a problem and must involve the user, use Dan Martell's 1-3-1 technique and proceed with the recommended option by default.

## 📝 File Management Rules

- Compare functionality before file changes - ensure no features are lost
- Verify preservation of features after modifications
- Cleanup with careful dependency tracking - check imports and references

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
- **Task completion signal** - When a topic/task is fully done, explicitly say: "Done. Retrospective?" Don't wait for user to ask "is everything done?"

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

## 📋 Claude-Optimal Context Exports

**Design exports/logs specifically to give Claude perfect troubleshooting context**

When building applications with complex state, implement "Copy Full Status" functionality that exports comprehensive debugging information designed for Claude to understand issues without additional context:

### What to Include:

1. **Metadata**:
   
   - Script/app version
   - Export timestamp (ISO 8601)
   - Browser/environment info
   - Current URL/location

2. **System State**:
   
   - All relevant boolean flags
   - Current indices/positions
   - Counters and thresholds
   - Active processes

3. **Configuration**:
   
   - Active config values
   - Timeouts and delays
   - Thresholds and limits

4. **Data Categorization**:
   
   - Successful items (with details)
   - Failed items (with error reasons)
   - Pending items
   - Items needing attention
   - Current queue state

5. **Debug Information**:
   
   - Queue/array order with details
   - DOM state snapshots
   - Presence of critical elements

### Export Format:

- **JSON** for structured data
- Human-readable with proper indentation (`JSON.stringify(data, null, 2)`)
- Copy to clipboard via `navigator.clipboard.writeText()`
- Show toast confirmation
- Include ALL information Claude would need without user explanation

### Example Implementation:

```javascript
const copyFullStatusToClipboard = async () => {
  const statusReport = {
    metadata: {
      version: APP_VERSION,
      exportTime: new Date().toISOString(),
      browser: navigator.userAgent,
      currentUrl: window.location.href
    },
    systemState: {
      isProcessing: processingFlag,
      currentIndex: processIndex,
      consecutiveFailures: failureCounter
    },
    configuration: {
      TIMEOUT: CONFIG.TIMEOUT,
      MAX_RETRIES: CONFIG.MAX_RETRIES
    },
    summary: {
      totalItems: items.length,
      successful: successCount,
      failed: failCount
    },
    items: {
      successful: [...],
      failed: [...],
      pending: [...]
    },
    debugInfo: {
      queueOrder: [...],
      domState: {...}
    }
  };

  await navigator.clipboard.writeText(JSON.stringify(statusReport, null, 2));
  // Show toast notification
};
```

### Why This Matters:

- **Zero explanation needed**: User can paste JSON, Claude immediately understands full context
- **Complete state snapshot**: No missing information, no follow-up questions
- **Reproducible debugging**: Claude sees exact state at moment of issue
- **Future-proof**: When facing unknown issues, extend export to include new data

**Rule**: If an application has complex state that could require debugging, proactively implement Claude-optimal status export. Design it assuming you won't be there to explain - the export should tell the complete story.

## LLM Browser - Last Resort Only

**Priority Order for Task Execution:**

1. **ALWAYS try CLI tools FIRST** - Use Bash, WebFetch, WebSearch, gh CLI, playwright, or other available tools
2. **Attempt autonomous execution** - Fully exhaust all programmatic approaches
3. **LLM Browser prompt as LAST RESORT** - Only when CLI tools fail or task is clearly impossible to automate

**When to use LLM Browser prompts (ONLY after CLI attempts fail):**

- Interactive website navigation that bypasses automation protections
- JavaScript-heavy sites blocking programmatic access
- Visual inspection requiring human-like browser behavior
- Multi-step authentication flows that block automation
- Tasks that explicitly failed via WebFetch/Playwright/CLI tools

**What Claude should run autonomously via CLI:**

- All bash commands (git, npm, docker, etc.)
- Web content fetching (WebFetch, WebSearch)
- GitHub operations (gh CLI)
- File operations (Read, Write, Edit, Grep, Glob)
- Testing and QA (playwright, pytest, etc.)
- Build and deploy operations
- API calls and scripting

**Rule**: If you can run it via CLI/tools - DO IT. Browser LLM is for when automation fails, not as a first choice.

## 🌐 Chrome MCP (Always Delegate)

🚨 **NEVER use `mcp__claude-in-chrome__*` tools directly.** Always delegate to chrome-agent via Task tool.

**Why:** Screenshots and DOM trees consume massive context. The chrome-agent processes them in its own context window, returning only concise results.

**URL opening:** When user asks to "open" a URL, just launch it with `start <url>` (opens in default browser), not chrome-agent.

**🚨 API vs Browser UI:** When delegating tasks where API can't do something (e.g., bot can't see private Slack channels), explicitly tell chrome-agent: "Use BROWSER UI only, do NOT use API calls - the user is logged in and can see things the bot API cannot."

### Batch Parallelization Protocol

When chrome-agent receives repetitive tasks (N entries, N uploads, N form submissions):

**Phase 1 - Evidence Gathering (First Run):**
- Complete ONE full iteration end-to-end
- Report steps to parent, ask user: "Did this work? Continue with remaining N-1?"
- **Skip this phase if:** documented SOP exists, user says "we've done this before", or prior success in conversation

**Phase 2 - Parallel Batch Setup:**
- Open tabs for remaining items: `min(remaining_items, 4)` tabs
- Navigate all to starting URL

**Phase 3 - Interleaved Execution:**
- Advance ALL tabs to each checkpoint together (not one tab at a time)
- **Human input consolidation:** When workflow needs user input (file upload, QA, CAPTCHA):
  1. Prepare ALL tabs to the input point
  2. Pause ONCE with consolidated list:
     ```
     "All 4 entries ready for your input:
     - Tab 1: needs ProductA.png
     - Tab 2: needs ProductB.png
     - Tab 3: needs ProductC.png
     - Tab 4: needs ProductD.png
     Complete all, then say 'continue'"
     ```
  3. Resume after single user confirmation

**Phase 4 - Completion:**
- Verify all tabs, report consolidated results
- Failed tabs don't stop batch - marked and reported at end for optional retry

**Anti-patterns:**
- ❌ Processing items one-by-one with separate confirmations
- ❌ Opening all tabs before knowing workflow works
- ❌ Stopping entire batch when one item fails
- ❌ Re-asking for same human input per tab

### 🧪 JS-First Clicking (Experimental)

When clicking buttons/elements, prefer JavaScript over mouse clicks:

**Priority order:**
1. **javascript_tool** - Direct DOM query + click (fastest, most reliable)
2. **read_page → ref click** - Get element ref, click by ref
3. **Mouse click** - Last resort, use coordinates from screenshot

**Why JS-first:**
- No coordinate guessing (mouse can miss if UI shifts)
- No accidental keyboard shortcuts (Ctrl+Enter = submit)
- Faster (no screenshot → analyze → move mouse cycle)
- Deterministic

**Example JS click:**
```javascript
document.querySelector('button[data-testid="submit"]').click()
// or find by text/aria
document.evaluate("//button[contains(text(),'Post')]", document, null, XPathResult.FIRST_ORDERED_NODE_TYPE, null).singleNodeValue.click()
```

### Method Reporting (Required)

Chrome-agent MUST report the method used for each action:

```
✓ Typed tweet 1 via: keyboard input
✓ Clicked + button via: javascript_tool - document.querySelector('svg path[d*="M11"]').closest('div').click()
✓ Typed tweet 2 via: keyboard input
✓ Clicked + button via: mouse click at [450, 320] (JS selector failed)
```

**Why:** Enables debugging, learning which methods work, and retroactive verification.

## 📂 Local Git Repository Locations

- `<YOUR_REPOS_PATH>` - Primary local git repositories
- `<YOUR_SECONDARY_REPOS_PATH>` - Secondary local git repositories (NVME drive)

## 📁 Google Drive CLI Access

rclone installed and authenticated as `gdrive:`. See skill: `~/.claude/skills/rclone/SKILL.md`

## 📝 CLAUDE.md Scope Rule

When user asks to "add something to CLAUDE.md":
- **DEFAULT to LOCAL** project CLAUDE.md (create if doesn't exist)
- Only modify GLOBAL CLAUDE.md (`~/.claude/CLAUDE.md`) if user explicitly says "global"
- Project-specific settings belong in local CLAUDE.md files

## "I can't do it but here's how you can"

 If you can't do something but you know that it's possible through CLI commands, then do it yourself instead of asking me to do it. you have CLI access just like me.

## 🤖 Personal Assistant Delegation

For admin tasks (email, calendar, Slack, contacts): invoke Claude Code in the Personal Assistant repository via Task tool.

## 🚨 Database Migration Tools - Fix Root Causes, Never Workaround

**If `drizzle-kit migrate` (or any migration tool) fails:**

1. **NEVER bypass with raw SQL** (psql, direct queries, etc.)
2. **NEVER manually apply migrations** outside the tooling
3. **FIX THE ROOT CAUSE** of why the migration tool is failing:
   - Debug the migration script
   - Fix driver/connection issues
   - Update dependencies if needed
   - Modify migration files to be compatible
4. **Workarounds create drift** between schema.ts, migrations, and database state
5. **The migration tool is the SSoT** - bypassing it breaks the entire system

**Why this matters:**
- Manual SQL bypasses migration tracking → future migrations break
- Schema drift causes silent failures and data corruption
- CI/CD pipelines depend on migration tools working correctly

**Drizzle ORM specifics:**
- Migration tracking table: `drizzle.__drizzle_migrations` (in the `drizzle` schema, NOT `public`)
- Always check `drizzle` schema when debugging migrations
- Don't confuse with `public` schema tables