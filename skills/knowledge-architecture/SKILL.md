---
name: knowledge-architecture
description: Knowledge management for Claude Code projects. Use when: creating skills or agents, deciding where to put new knowledge (skill vs CLAUDE.md vs reference-data vs agent), routing information, CLAUDE.md hygiene, editing/modifying CLAUDE.md or skills or agents, extracting content from bloated files, or any discussion about knowledge architecture, documentation structure, or SOP placement. MUST be invoked BEFORE proposing any edits to CLAUDE.md, skills, or agents - no exceptions.
---

# Claude Code Knowledge Management

## Part 1: Where Does Knowledge Go?

Evaluate in order. First match wins.

```
1. TABULAR/REGISTRY DATA (URLs, IDs, contacts, rosters):
   → Used by ONE skill: .claude/skills/{skill}/references/*.md
   → Used repo-wide: reference-data/*.md

2. SITUATIONAL PERSONAL DATA (address, ID, rarely-needed info):
   → Create pointer registry (reference-data/personal-data-sources.md)
   → Registry contains POINTERS to sources (Keep notes, sheets), not data
   → CLAUDE.md has one-liner: "check registry for personal info"
   → PA looks up dynamically when needed, doesn't cache in context
   → Pattern: reference-data/{type}-sources.md with table of pointers

3. NEEDS ISOLATED CONTEXT (heavy processing, browser automation):
   → Propose agent to user, await approval
   → If rejected: create skill instead

4. DOMAIN KNOWLEDGE (procedures, workflows, explanations):
   → .claude/skills/{name}/SKILL.md
   → This is the default for most content

5. ONE-LINER CROSS-CUTTING RULE:
   → CLAUDE.md (only if truly 1-2 lines)

6. UNCLEAR:
   → Ask user
```

**Pointer Registry Pattern (for situational data):**
When user provides info that PA needs occasionally but shouldn't bloat every session:
1. Ask: "Should I add this to a source registry for future lookup?"
2. Create/update `reference-data/{domain}-sources.md`
3. Store POINTER (source location), not actual data
4. Add one-liner to CLAUDE.md: "For X, check reference-data/{domain}-sources.md"
5. PA dynamically looks up only when needed

## Part 2: CLAUDE.md Hygiene

CLAUDE.md bloats fast. Rules:

- **One-liners only** - >2-3 lines = extract to skill
- **Pointers not content** - "See skill X" not the procedure
- **No procedures** - All procedures → skills
- **Skills are default** - When in doubt, create skill
- **Minimal edits** - Modify existing or remove violations OK; adding = max 1 line
- **Agents need approval** - Never auto-create

## Part 3: Skill Structure

```
.claude/skills/{name}/
├── SKILL.md              ← Required (exact filename)
│   ├── YAML frontmatter  ← Required: name + description
│   └── Markdown body     ← Instructions
├── references/           ← Docs loaded on demand
├── scripts/              ← Executable code
└── assets/               ← Templates, files for output
```

**Critical:**
- Path must be `.claude/skills/{name}/SKILL.md`
- Frontmatter `description` determines when skill triggers - be comprehensive
- Body only loads AFTER skill triggers
- `.claude/` must NOT be gitignored

## Part 4: Frontmatter

> **Official reference:** https://code.claude.com/docs/en/skills

**Standard template (use for ALL skills):**

```yaml
---
name: skill-name
description: What it does AND when to use it. This is critical - Claude uses it to decide when to apply the skill.
user-invocable: false
---
```

### Complete field reference

| Field | Required | Default | Description |
|-------|----------|---------|-------------|
| `name` | No | directory name | Display name. Lowercase, numbers, hyphens only (max 64 chars). |
| `description` | Recommended | first paragraph of body | WHAT + WHEN. Claude uses this to decide when to apply the skill. |
| `user-invocable` | **Yes (our standard)** | `true` | **Set to `false` on ALL skills.** Our skills are background knowledge, not user-invocable commands. |
| `disable-model-invocation` | No | `false` | Set `true` to prevent Claude from auto-loading. Use for side-effect workflows user must trigger manually. |
| `allowed-tools` | No | conversation permissions | Tools Claude can use without per-use approval when skill is active. String or array. |
| `model` | No | inherits | Model override (`sonnet`, `opus`, `haiku`). |
| `context` | No | inline | Set to `fork` to run in a forked subagent context (isolated context window). |
| `agent` | No | `general-purpose` | Which subagent type when `context: fork` is set. Built-in: `Explore`, `Plan`, `general-purpose`, or custom from `.claude/agents/`. |
| `argument-hint` | No | none | Hint for autocomplete, e.g. `[issue-number]`. |
| `hooks` | No | none | Hooks scoped to this skill's lifecycle. |

**Invocation matrix (how fields interact):**

| Frontmatter | User can `/invoke` | Claude auto-loads | Context loading |
|---|---|---|---|
| (default) | Yes | Yes | Description always in context, body loads on invoke |
| `disable-model-invocation: true` | Yes | No | Description NOT in context |
| `user-invocable: false` | No | Yes | Description always in context, body loads on invoke |

**String substitutions available in skill body:**
- `$ARGUMENTS` — all arguments passed on invocation
- `$ARGUMENTS[N]` or `$N` — specific argument by 0-based index
- `${CLAUDE_SESSION_ID}` — current session ID
- `` !`command` `` — dynamic context injection (shell command runs before skill content is sent)

### Our standard: `user-invocable: false`

**ALL skills MUST include `user-invocable: false`.** Our skills are model-invoked background knowledge (Claude decides when to load them based on description). Only slash commands in `.claude/commands/` are user-invocable. Omitting this field defaults to `true`, which pollutes the `/` menu with non-actionable entries.

### When to propose `context: fork`

`context: fork` runs the skill in an isolated subagent context. The skill body becomes the subagent's task prompt — it won't have conversation history.

**Propose `context: fork` when:**
- Skill involves heavy browser automation or screenshot processing
- Skill processes large data (parsing spreadsheets, logs, transcripts)
- Skill runs multi-step workflows that could bloat parent context
- Skill is frequently delegated to Task tool subagents anyway
- Skill has explicit task instructions (not just guidelines/conventions)

**Do NOT use when:**
- Skill is lightweight (lookup, simple procedure, reference)
- Skill needs to read/write parent conversation state
- Skill is a quick decision tree or routing logic
- Skill contains conventions/guidelines without an actionable task (subagent gets guidelines but no task = useless)

**Workflow:** When creating/editing a skill and `context: fork` seems beneficial, propose to user: "This skill involves [heavy processing/browser automation/etc.] — recommend adding `context: fork` so it runs in an isolated context. Approve?" Do NOT add silently. If proposing fork, also suggest an appropriate `agent:` value.

### Troubleshooting Misbehaving Skills

If a skill is not triggering, triggers too often, or behaves unexpectedly, fetch the troubleshooting section from https://code.claude.com/docs/en/skills for current diagnostic steps. Key issues:

| Symptom | Likely Cause | Fix |
|---------|-------------|-----|
| Skill not triggering | Description missing keywords users naturally say | Rephrase description with concrete trigger phrases |
| Skill triggers too often | Description too broad | Narrow description; consider `disable-model-invocation: true` |
| Claude doesn't see all skills | Too many skill descriptions exceed character budget (default 15k) | Run `/context` to check; set `SLASH_COMMAND_TOOL_CHAR_BUDGET` env var to increase |
| Fork skill returns empty | Skill has guidelines but no actionable task | `context: fork` needs explicit task instructions, not just conventions |

Always fetch the live URL — troubleshooting guidance may be updated upstream.

## Part 5: Writing Guidelines

1. **Imperative form** - "Create documents" not "This skill creates"
2. **Description is trigger** - Include all contexts when skill should activate
3. **Don't repeat** - Info in SKILL.md OR references, not both
4. **Concise** - Claude is smart; only add context it lacks
5. **Compliance reporting** - After creating/editing a skill, just say "✅ Compliant with knowledge-architecture" — don't enumerate every rule that was followed
6. **Deterministic output format** - When a skill or SOP produces user-facing output (reports, tables, status updates), define the EXACT format in the skill body. Include:
   - A template/example showing the structure
   - Emoji legends for visual scanning (e.g., 💻 = code, 📄 = docs, ✅ = done, ⚠️ = attention)
   - Column names, row ordering, section order
   - This ensures identical formatting across sessions — user builds muscle memory for scanning output. Ad-hoc formatting = cognitive overhead every time.

## Part 6: Size Management

| Component | Guideline | Loaded |
|-----------|-----------|--------|
| SKILL.md body | ~500 lines | When skill triggers |
| references/ | Unlimited | On demand |
| scripts/ | Unlimited | Executed, not loaded |

If >500 lines: keep core workflow in SKILL.md, move details to references/.

## Part 7: Global vs Local

| Location | Scope |
|----------|-------|
| `~/.claude/skills/` | All projects |
| `.claude/skills/` (repo) | This project only |

## Part 8: Post-Creation

1. Frontmatter has `name:`, `description:`, and `user-invocable: false`
2. Description explains WHAT + WHEN comprehensively
3. Located at `.claude/skills/{name}/SKILL.md`
4. Add to `.claude/settings.json`: `"Skill(name)"` in `permissions.allow`
5. Register in CLAUDE.md skills index (local skills only)
6. Evaluate whether `context: fork` is appropriate — if yes, propose to user
7. 🧪 Evaluate whether a **reminder hook** is appropriate (see Part 12) — if Claude repeatedly forgets to follow this skill and it maps to a matchable action, create a PostToolUse hook and log it on the tracking issue

## Part 9: Agents (Require Approval)

Never auto-create agents. Protocol:
1. Identify candidate (needs isolated context, heavy processing)
2. Propose: "This could be an agent because [X]. Create agent?"
3. User approves → `.claude/agents/*.md`
4. User rejects → Create skill instead

## Part 10: Search Both Locations

When searching for agents or skills, ALWAYS check both:

| Type | Local (project) | Global (user home) |
|------|-----------------|-------------------|
| Skills | `.claude/skills/` | `~/.claude/skills/` |
| Agents | `.claude/agents/` | `~/.claude/agents/` |

Never assume "not found" after checking only one location.

## Part 11: Auto-Fix Rule

When this skill is invoked to review an edit that already happened (post-hoc), do NOT ask the user whether to fix violations. **Fix them immediately**, then report:
1. What was violated
2. What was fixed
3. What was learned

Asking "want me to fix this?" after reading a skill that clearly states the rules wastes the user's time. The rules are unambiguous — just apply them.

## Part 12: Skill Reminder Hooks (🧪 Experimental)

> **Tracking issue:** https://github.com/<GITHUB_USER>/PersonalAssistant-ClaudeCode/issues/23
> **Status:** Evaluating until 2026-02-02. When implementing this pattern, **comment on the issue** with where you applied it (repo, skill name, hook matcher) so we can track all implementations and roll back if needed.

### Problem

Claude frequently forgets to load relevant skills before/during actions. CLAUDE.md instructions are suggestions; hooks are **deterministic guarantees**.

### Pattern: PostToolUse Reminder Hook

A `PostToolUse` hook fires after every tool call matching a pattern. By exiting with code 2 and writing to stderr, the message is fed **directly to Claude as feedback** (not just shown to the user). This forces Claude to acknowledge and follow the skill.

### How It Works

```
Claude edits file → PostToolUse hook fires → script checks file type →
  If match: exit 2 + stderr reminder → Claude receives feedback, loads skill
  If no match: exit 0 → silent, no overhead
```

### Implementation Steps

When creating or modifying a skill that Claude frequently forgets to follow:

1. **Create the hook script** in the skill's `scripts/` folder:

```python
#!/usr/bin/env python3
"""PostToolUse reminder hook for {skill-name}."""
import json, sys

try:
    data = json.load(sys.stdin)
except (json.JSONDecodeError, EOFError):
    sys.exit(0)

file_path = data.get("tool_input", {}).get("file_path", "")

# Adjust condition to match the skill's domain
if not file_path.lower().endswith(".md"):
    sys.exit(0)

print(
    "You modified a file relevant to {skill-name}. "
    "Follow the {skill-name} skill (~/.claude/skills/{name}/SKILL.md).",
    file=sys.stderr,
)
sys.exit(2)
```

2. **Register the hook** in `~/.claude/settings.json` (global) or `.claude/settings.json` (project):

🚨 **Cross-platform compatibility:** Use `python -c` with `os.path.expanduser('~')` to resolve the home directory. `$HOME` doesn't expand on Windows, and hardcoded paths aren't portable. Only `$CLAUDE_PROJECT_DIR` is reliably injected by Claude Code (for project-scoped hooks only).

```json
{
  "hooks": {
    "PostToolUse": [
      {
        "matcher": "Edit|Write|MultiEdit",
        "hooks": [{
          "type": "command",
          "command": "python -c \"import os;exec(open(os.path.expanduser('~/.claude/skills/{name}/scripts/postToolUse-reminder.py')).read())\"",
          "timeout": 5
        }]
      }
    ]
  }
}
```

3. **Comment on the tracking issue** (https://github.com/<GITHUB_USER>/PersonalAssistant-ClaudeCode/issues/23) with:
   - Skill name and path
   - Hook matcher used
   - File type / condition that triggers the reminder

### Hook Event Reference

| Event | When | Use For |
|-------|------|---------|
| `PostToolUse` | After tool succeeds | Remind after file edits (most common) |
| `PreToolUse` | Before tool runs | Block/warn before dangerous actions |
| `Stop` | Claude finishes responding | Verify all rules were followed |
| `SubagentStop` | Subagent finishes | Validate subagent output quality |
| `SessionStart` | Session begins | Inject context (schedule, state) |

**Matchers:** Tool name patterns — `Edit|Write|MultiEdit`, `Bash`, `mcp__gmail__send_email`, `*` (all), etc.

**Exit codes:** 0 = silent, 2 = feedback to Claude (stderr), other = non-blocking error.

**🚨 Hook stdin input varies by event type:**

| Event | stdin fields | How to get transcript data |
|-------|-------------|--------------------------|
| `PreToolUse` | `tool_name`, `tool_input` | N/A |
| `PostToolUse` | `tool_name`, `tool_input`, `tool_output` | N/A |
| `Stop` | `session_id`, `transcript_path`, `cwd`, `stop_hook_active` | Parse JSONL file at `transcript_path` |

**Stop hooks do NOT receive `transcript_summary` or `tools_used`.** Must read and parse `transcript_path` (JSONL, one JSON object per line, entries have `type: "assistant"` with `content` blocks containing `tool_use` and `text`).

> **Official docs:** https://code.claude.com/docs/en/hooks

### Pattern: PreToolUse Blocking Hook

A `PreToolUse` hook fires **before** tool execution. Exit code 2 **blocks the tool call entirely** and feeds the stderr message to Claude. Use this to permanently blacklist dangerous/faulty tool variants.

```json
{
  "hooks": {
    "PreToolUse": [
      {
        "matcher": "mcp__dangerous__tool_name",
        "hooks": [{
          "type": "command",
          "command": "echo 'BLOCKED: Use mcp__safe__tool_name instead. Reason: [why].' && exit 2",
          "timeout": 5
        }]
      }
    ]
  }
}
```

**When to use blocking hooks:**
- Two MCP tools overlap in function but one is broken/unsafe
- A tool silently fails (no error, wrong behavior) — worse than crashing
- The correct alternative is known and deterministic

**When NOT to use:**
- Tool works but needs guardrails → use reminder hook instead
- Tool is the only option → fix the tool, don't block it

### Testing Hooks (Subprocess Verification)

🚨 **Hook changes in `settings.json` only apply to NEW Claude Code sessions.** The current session uses the settings loaded at startup.

**To verify a hook works without restarting your session:**

```bash
# Safe test — spawns a fresh CC instance that loads new settings
# Use --print flag to run non-interactively (prints output, exits)
claude --print "Try calling mcp__google-workspace__gmail_send to <YOUR_EMAIL> with subject 'Hook verification test' and body 'This should be blocked by PreToolUse hook.'" --allowedTools "mcp__google-workspace__gmail_send,mcp__google-workspace__gmail_*"
```

**Safety rules for subprocess hook testing:**
- **ONLY test blocking hooks** — never test reminder hooks this way (they don't block, so the action executes)
- **ONLY use self-targeted test data** — send to user's own email, use test subjects
- **NEVER test hooks that involve destructive actions** — if the hook fails, the action runs
- **Expected result:** The subprocess should report the hook blocked the tool. If the tool executes, the hook is misconfigured.
- **If test fails (tool executes):** Check matcher pattern, exit code (must be 2), and that settings.json is valid JSON

### When to Add a Reminder Hook

Add a hook when ALL of these are true:
- Claude **repeatedly forgets** to follow the skill (proven pattern, not hypothetical)
- The skill applies to a **matchable action** (file type, tool name, MCP call)
- The skill is **corrective/preventive** (rules to enforce, not just reference info)

Do NOT add hooks for:
- Informational skills (lookup, reference data)
- Skills that already trigger reliably via description
- One-off workflows the user explicitly invokes

### Existing Implementations

| Skill | Matcher | Condition | Script |
|-------|---------|-----------|--------|
| knowledge-architecture (reminder) | `Edit\|Write\|MultiEdit` | `*.md` files (PostToolUse) | `~/.claude/skills/knowledge-architecture/scripts/postToolUse-reminder.py` |
| knowledge-architecture (blocker) | `Edit\|Write\|MultiEdit` | **BLOCKS** `CLAUDE.MD` and `SKILL.MD` (PreToolUse) | `~/.claude/skills/knowledge-architecture/scripts/preToolUse-block-knowledge-files.py` |
| message-drafting | `mcp__google-workspace__gmail_send\|..gmail_createDraft\|..gmail_sendDraft\|mcp__gmail__send_email\|..draft_email` | Any gmail send/draft call | `.claude/skills/message-drafting/scripts/preToolUse-reminder.py` |
| email-verification | `Bash\|mcp__google-workspace__gmail_send\|..gmail_createDraft\|..gmail_sendDraft\|mcp__gmail__send_email\|..draft_email` | Bash with `mail.google.com`/`mailto:` + all gmail send/draft | `.claude/skills/message-drafting/scripts/preToolUse-email-verification.py` |
| gmail-send-blocker | `mcp__google-workspace__gmail_send\|mcp__google-workspace__gmail_sendDraft` | **BLOCKS** — these tools silently break threading | Inline `echo + exit 2` in `~/.claude/settings.json` |

## Common Mistakes

| Mistake | Fix |
|---------|-----|
| Flat file `skills/foo.md` | Move to `.claude/skills/foo/SKILL.md` |
| Missing frontmatter | Add `name:`, `description:`, and `user-invocable: false` |
| Missing `user-invocable: false` | Add it — skills are never user-invocable |
| Vague description | Describe WHAT + WHEN comprehensively |
| Body >500 lines | Move details to `references/` |
| Procedure in CLAUDE.md | Extract to skill |
| Multi-paragraph in CLAUDE.md | Extract to skill |
| Searched only local for agent/skill | Check both local `.claude/` AND global `~/.claude/` |
| Asked user "should I fix?" after skill showed clear violation | Just fix it and report what was done |
| Created reminder hook without logging on tracking issue | Comment on https://github.com/<GITHUB_USER>/PersonalAssistant-ClaudeCode/issues/23 with skill name, matcher, and condition |
| Added hook for skill that triggers reliably already | Only add hooks for skills Claude repeatedly forgets — don't over-hook |
