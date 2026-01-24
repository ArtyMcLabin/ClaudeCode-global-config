---
name: retrospective
description: Context engineering audit after mistakes. Use when something went wrong to fix instructions so future sessions don't repeat the error.
---

# Retrospective (Context Engineering Audit)

**Trigger:** "retrospective", "retro", "context audit", "what went wrong"

**Purpose:** When a mistake happens, audit whether:
1. Instructions existed but weren't followed → make more prominent/enforceable
2. Instructions don't exist → create them
3. Opportunity to enrich SOPs with learned patterns

**Philosophy:** Current session memory won't persist. Fixes must be encoded in files that future sessions will read.

---

## Audit Scope

| Location | What to Check |
|----------|---------------|
| **Current Project** | CLAUDE.md, .claude/skills/*.md |
| **Global Config** `~/.claude/` | CLAUDE.md, skills/*.md, settings |

Both must be checked - some rules belong globally (all projects), some are project-specific.

---

## Process

### Step 1: Identify Issues

List what went wrong in the session. For each issue:
- What happened?
- What should have happened?
- Was it a violation of existing instructions or a gap?

### Step 2: Check Existing Coverage

For each issue, search:
```
1. Project CLAUDE.md - grep for relevant keywords
2. Project .claude/skills/ - check if relevant skill exists
3. Global ~/.claude/CLAUDE.md - check global rules
4. Global ~/.claude/skills/ - check global skills
```

Classify each issue:
- **✅ Covered** - Rule exists, was violated
- **⚠️ Partial** - Rule exists but is weak/buried/ambiguous
- **❌ Gap** - No rule exists

### Step 3: Create Prevention Table

| Issue | Prevention Step | Location | Status |
|-------|-----------------|----------|--------|
| [What went wrong] | [Specific rule/instruction to add] | [Project or Global, which file] | [Pending/Done] |

### Step 4: Decide Placement

**Goes in Global (`~/.claude/`):**
- Cross-project patterns (API vs browser, check before asking, etc.)
- Tool-level behaviors (how to use specific tools)
- Claude Code operational rules

**Goes in Project Repo:**
- Project-specific workflows
- User preferences specific to this project
- Business/domain context

**Goes in Skill:**
- Domain-specific procedure (>2 lines of instruction)
- Has clear trigger/use case
- Reusable pattern

### Step 5: Implement Fixes

For each pending prevention step:
1. Edit the appropriate file
2. Mark as done in the table
3. Verify the instruction is clear and actionable

### Step 6: Verify

Ask: "If a fresh Claude Code session reads these files, will it avoid this mistake?"

If no → instruction is too weak or buried. Strengthen it.

---

## Common Patterns

### Pattern: Rule Exists But Was Violated

**Symptoms:** Did X, but CLAUDE.md clearly says "don't do X"

**Fixes:**
- Add 🚨 attention marker
- Move rule higher in the file (more prominent)
- Add to relevant skill as well (redundancy for important rules)
- Add concrete example of violation and correct behavior

### Pattern: Rule Is Ambiguous

**Symptoms:** Interpreted rule differently than intended

**Fixes:**
- Add explicit examples (good vs bad)
- Add "This means..." clarification
- Add edge cases

### Pattern: No Rule Exists

**Symptoms:** Had no guidance, made reasonable but wrong choice

**Fixes:**
- Create new rule in appropriate location
- If pattern is complex, create a skill
- Add to relevant existing skill if it fits

### Pattern: Skill Exists But Wasn't Consulted

**Symptoms:** Used a concept (e.g., "delegation") without reading the skill first

**Fixes:**
- Add global rule: "Before using concept X, read skill X"
- Add trigger words to skill description so it's loaded automatically

---

## Output Format

**🚨 Be concise.** User wants TLDR, not process dump.

**To user:** Max 2-3 sentences:
- What went wrong
- What fix was added (or "no fix needed - one-off")

**Process details:** Keep in thinking block. User can ask if they want to see the audit work.

---

## Cost-Benefit Filter

**Before adding any rule, ask:**

1. Does this fix add friction to every interaction to prevent occasional issues?
2. Would the user's existing pattern (this retrospective) catch it anyway?
3. Is this a one-off mistake or does it repeat?

| Situation | Action |
|-----------|--------|
| Fix costs more than problem | Don't add rule |
| One-off mistake, not repeating | Skip - not worth documenting |
| User's retrospective pattern handles it | Note as "system working" |
| Repeating pattern, low-cost fix | Add rule |

**Prefer editing over adding.** Can we modify an existing rule instead of creating a new one?

---

## Anti-Patterns

- ❌ Adding vague rules like "be more careful"
- ❌ Duplicating rules across many files (use references instead)
- ❌ Adding rules without clear actionable instruction
- ❌ Fixing only project repo when rule should be global (or vice versa)
- ❌ Skipping verification step
- ❌ Proposing fixes that cost more than the problems they solve
- ❌ Bloating CLAUDE.md with verbose explanations (keep it minimal)

---

## Example Retrospective

**Issue:** Used browser automation for API calls when MCP tool was available

**Check existing:**
- Project CLAUDE.md: No MCP priority rule for this tool
- Global CLAUDE.md: General "prefer API over browser" exists but not specific

**Classification:** ⚠️ Partial

**Prevention:** Add to relevant skill:
```
🚨 **API first:** Use MCP tools for all operations. Browser only for UI-specific actions not available via API.
```

**Location:** Global `~/.claude/skills/[relevant-skill]/SKILL.md`

**Status:** ✅ Implemented
