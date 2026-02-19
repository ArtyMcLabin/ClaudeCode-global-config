---
name: sleep
description: End-of-session context preservation via GitHub Issues
user-invocable: false
---

# Sleep Skill

End-of-session context preservation via GitHub Issues.

## Triggers

- "I want to go sleep"
- "Let's wrap up"
- "Save session and close"
- "Going to bed"
- "/sleep"

## Purpose

Preserve all relevant session context so the next session can continue seamlessly without re-explaining anything. Context is stored in GitHub Issues in the PA repo.

## Procedure

### 0. Check If Context Preservation Is Needed

**Before creating any issues, evaluate if there's actually pending work:**

**SKIP context preservation if ALL of these are true:**
- All tasks/features were completed and deployed
- All commits are pushed
- Any QA submissions or testing issues are self-contained (don't need session context)
- No open questions or pending research
- No half-finished work that needs continuation

**If nothing is pending → Just say goodnight.** Don't create unnecessary issues.

**CREATE context issue only if:**
- Research is incomplete (need to continue investigating)
- Implementation is partially done (need to resume coding)
- There are open questions that need answers next session
- Complex context that would be lost (decisions made, options ruled out, etc.)

### 1. Identify Active Topic

Determine what the session was about:
- Research topic
- Implementation task
- Debugging session
- Planning discussion

### 2. Check for Existing Issue

Search for open issues that match the current topic:

```bash
gh issue list --repo <GITHUB_USER>/PersonalAssistant-ClaudeCode --state open --search "<topic keywords>"
```

### 3a. If Existing Issue Found → Update It

Append new context to the issue body:

```bash
gh issue edit <issue-number> --repo <GITHUB_USER>/PersonalAssistant-ClaudeCode --body "$(cat <<'EOF'
<existing body content>

---

## Session Update: <date>

<new findings, decisions, next steps>
EOF
)"
```

### 3b. If No Existing Issue → Create New

Create comprehensive issue with all context:

```bash
gh issue create --repo <GITHUB_USER>/PersonalAssistant-ClaudeCode \
  --title "<Descriptive title>" \
  --body "$(cat <<'EOF'
## Goal
<What we're trying to achieve>

## Context
<Background, constraints, user preferences>

## Research/Findings
<Everything discovered in the session>

## Decisions Made
<What was ruled out and why>

## Open Questions
<What still needs to be answered>

## Next Steps
<Specific TODOs for next session>

---
*Created from Claude Code session <date>*
EOF
)"
```

### 4. Report to User

Provide the issue URL and brief summary of what was saved.

## Content Guidelines

**Include generously:**
- All research findings (links, summaries, comparisons)
- Ruled-out options with reasons
- User preferences/constraints discovered
- Technical details (architecture, setup steps, commands)
- Open questions and uncertainties
- Specific next steps with checkboxes

**Don't worry about:**
- Issue length (bloat is fine)
- Redundancy (better to over-document)
- Perfect formatting (readable is enough)

## Example Issue Structure

```markdown
## Goal
<1-2 sentence objective>

## Requirements
- ✅ Must have X
- ❌ Ruled out Y (reason)

## Candidates/Options
### Option 1: Name
- What it is
- Pros/cons
- Links
- TODO items

### Option 2: Name
...

## Session Context
- User setup details
- Relevant existing tools/skills
- Preferences discovered

## Next Steps
- [ ] Research task 1
- [ ] Try approach X
- [ ] Ask user about Y

---
*Session date, any other metadata*
```

## Resuming Next Session

**Morning routine auto-surfaces sleep issues.** The morning-routine skill checks for open issues containing "Created from Claude Code session" and presents them before triage, asking user if they want to continue.

If user returns outside morning routine and mentions the topic, PA should:
1. Find the relevant issue
2. Read it to restore context
3. Continue from "Next Steps"
