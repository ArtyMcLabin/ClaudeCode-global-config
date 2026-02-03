---
name: sleep
description: End-of-session context preservation via GitHub Issues
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

When user returns and mentions the topic, PA should:
1. Find the relevant issue
2. Read it to restore context
3. Continue from "Next Steps"
