---
name: issue-dispatcher
description: Triage GitHub issues queue - check hygiene, identify actionable items, prioritize, invoke handler for each. The "what to work on" decision layer.
user-invocable: false
---

# Issue Dispatcher

> **Part of:** Autonomous Issue Dispatch System
> **Downstream:** `issue-handler` → CTO Agent → `qa-submission` (per-project)

## Purpose

The Dispatcher answers: **"What should we work on next?"**

It does NOT diagnose or fix. It manages the queue:
- Hygiene checks (labels match status, no orphaned items)
- Identifies actionable vs blocked vs backlog
- Prioritizes by severity, age, low-hanging fruit
- Invokes Issue Handler for each actionable item

## Philosophy

**Dispatcher is holistic.** It sees the entire queue, not individual issues.

**Dispatcher is not a fixer.** It triages and delegates. The moment you start reading logs or writing code, you've become a Handler.

**Dispatcher respects project status.** Backlog means backlog. Don't auto-promote items without explicit instruction.

## Trigger

- **Manual:** "Check pending issues" / "What's actionable?" / "Find low-hanging fruit"
- **Automated:** Daily maintenance cron (if configured)
- **Post-intake:** After Bug Intake creates new issues

---

## Dispatch Workflow

### Step 1: Fetch Queue

```bash
gh issue list --state open --json number,title,labels,projectItems,createdAt,updatedAt
```

### Step 1.5: Read Comments (MANDATORY)

**🚨 Labels alone are not sufficient.** For each issue, read comments:

```bash
gh issue view NUMBER --json body,comments,labels,state
```

**Why:** Comments contain critical status info that may not be reflected in labels:
- QA submission status + Slack links
- Implementation details and commit references
- Blocking reasons or clarifications
- Human decisions not yet tagged

**What to look for:**
| Comment Pattern | Meaning |
|-----------------|---------|
| "QA Submitted" + Slack link | Already in QA (should have `pending-qa` label) |
| "Fixed in commit X" | Implemented, may be ready for QA or closure |
| "Blocked on..." | Blocked, needs action |
| "Backlog" or "Later" | Should have `backlog` label |

**Auto-fix mismatches:** If comment says "QA Submitted" but no `pending-qa` label → add the label.

### Step 2: Hygiene Check

For each issue, verify:

| Check | Pass | Fail Action |
|-------|------|-------------|
| Has project board status | ✅ | Flag: "No status assigned" |
| Labels match status | ✅ | Flag: "needs-qa label but in Backlog" |
| Not stale (updated < 30 days OR in Backlog) | ✅ | Flag: "Stale - no updates in 30+ days" |

**Auto-fix hygiene issues when clear:**
- `needs-qa` label + Backlog status → Either remove label OR move to QA (ask)
- No status + has labels → Infer status from labels

**Report hygiene issues:**
```
HYGIENE ISSUES:
- #8: has 'needs-qa' but status is Backlog (mismatch)
- #45: no project status assigned
- #12: stale (last update 45 days ago)
```

### Step 3: Categorize

Sort issues into buckets:

| Bucket | Criteria | Action |
|--------|----------|--------|
| **Actionable** | In Todo/Doing, has enough info | → Handler |
| **Blocked** | Missing info, waiting on external | → Comment asking for info |
| **Backlog** | Explicitly backlogged | → Skip unless asked |
| **Needs QA** | In QA column or has needs-qa label | → Human QA, not Handler |

### Step 4: Prioritize Actionable

**🚨 Priority Labeling Policy:**
- We do NOT use "high-priority" labels
- `backlog` label = low priority / not urgent
- Everything else = use common sense to prioritize
- No label ≠ high priority - it means "normal, not deprioritized"

**Rank by (common sense):**
1. **Severity** - security > data loss > broken feature > cosmetic
2. **Effort** - low-hanging fruit get slight boost
3. **Dependencies** - blockers for other issues first
4. **User impact** - affects daily workflow > edge case
5. **Age** (minor tiebreaker) - **newer first** — newer issues are statistically more relevant and less likely stale. Older issues have had time to become outdated or self-resolve.

### Step 5: Dispatch to Handler

For each actionable issue (in priority order):

```
Invoke issue-handler for #71

Context:
- Priority: 2 of 5 actionable
- Age: 3 days
- Estimated effort: Low (UI fix)
- Labels: bug
- Status: Todo
```

**Batch vs Sequential:**
- Default: Sequential (one at a time, wait for completion)
- Parallel: Only if explicitly requested AND issues are independent

### Step 6: Report Summary

```
DISPATCH SUMMARY:

Queue: 30 open issues
- Actionable: 5
- Blocked: 3
- Backlog: 20
- Needs QA: 2

Hygiene issues fixed: 1
Hygiene issues flagged: 2 (need human decision)

Dispatched to Handler:
1. #71 - Role dropdown click-away (Low effort, 3 days old)
2. #68 - Approval counter bug (Low effort, 5 days old)
3. #67 - Hook/CTA propagation (Medium effort, 6 days old)

Skipped (blocked):
- #73 - Missing requirements, commented asking for clarification

Skipped (backlog):
- 20 issues in backlog (not dispatched unless requested)
```

---

## Integration Points

### Upstream: Bug Intake (per-project)

Bug Intake creates issues with:
- Clear title and description
- Source reference (Slack thread URL, email ID)
- Initial labels (bug, enhancement, etc.)
- Project board assignment

Dispatcher expects these to exist. If missing, flag as hygiene issue.

### Downstream: Issue Handler (global)

Handler receives:
- Issue number
- Priority context (where in queue)
- Any dispatcher notes

Handler returns:
- Diagnosis complete → handed to CTO
- Blocked → needs more info (Dispatcher may re-ask reporter)
- Not reproducible → Dispatcher decides (close? ask reporter?)

### Loop-back: Reporter Notification

**When Handler completes diagnosis → CTO picks up:**
Dispatcher does NOT notify reporter yet. Wait for QA Submission.

**When Handler is blocked:**
Dispatcher may ask Bug Intake to loop back to reporter for more info.

---

## Dispatcher Modes

### Triage Mode (Default)

Full queue scan, hygiene checks, prioritization, dispatch.

```
"Run issue triage" / "Check pending issues"
```

### Low-Hanging Fruit Mode

Filter for quick wins only.

```
"Find low-hanging fruit" / "What can we fix quickly?"
```

Criteria:
- Estimated effort: Low
- Clear reproduction steps
- Isolated scope (single file/component)

### Single-Issue Mode

Skip queue scan, dispatch specific issue directly.

```
"Handle issue #71"
```

Still performs hygiene check on that issue.

---

## What Dispatcher Does NOT Do

| Not Dispatcher's Job | Who Does It |
|---------------------|-------------|
| Read logs | Handler |
| Write code | CTO Agent (Developer) |
| Run tests | CTO Agent (QA Engineer) |
| Diagnose root cause | Handler |
| Notify reporter | Bug Intake / QA Submission |
| Accept/reject QA | Human |

Dispatcher is the **traffic controller**, not the mechanic.

---

## Relationship with github-issue-manager Agent

The `github-issue-manager` agent and `issue-dispatcher` skill are **complementary**:

| Component | Responsibility | Operations |
|-----------|---------------|------------|
| `github-issue-manager` | READ/WRITE individual issues | Create, update status, verify Kanban, fetch with filtering |
| `issue-dispatcher` | TRIAGE/ORCHESTRATE queue | Analyze, prioritize, dispatch to handler |

**The manager owns all issue I/O** (including due-date filtering). The dispatcher is a higher-level workflow that triages and dispatches.

**When to use which:**
- Reading issues / "check the issues"? → `github-issue-manager`
- Creating a new issue? → `github-issue-manager`
- Updating issue status/labels? → `github-issue-manager`
- "What should we work on?" / bulk triage → `issue-dispatcher`
- "Check queue hygiene" → `issue-dispatcher`

**🚨 Filtering is the manager's job.** The dispatcher inherits the manager's due-date filtering. When the dispatcher fetches issues (Step 1), it must apply the same filtering rules defined in the manager (skip future-dated issues silently).

---

## Communication Rules

**🚨 ALWAYS include issue titles when referencing issues:**
- User does NOT memorize issue numbers
- Every mention of an issue ID MUST include the title/description
- In ALL outputs: tables, summaries, lists, conversations

**Examples:**
- ❌ Bad: "#13, #65, #67 - NOT implemented"
- ✅ Good: "#13 (OpenRouter referer fix), #65 (Email verification), #67 (Hook/CTA propagation) - NOT implemented"

**Table format:**
```
| Issue | Status |
|-------|--------|
| #13 - Fix hardcoded OpenRouter referer | NOT implemented |
| #65 - Email verification | NOT implemented |
```

Never assume user remembers what issue numbers mean.

---

## Configuration

Dispatcher behavior can be tuned per-project via CLAUDE.md:

```markdown
## Issue Dispatcher Config

- **Auto-dispatch:** false (require manual trigger)
- **Max parallel:** 1 (sequential only)
- **Stale threshold:** 14 days (faster for active projects)
- **Skip labels:** ["wontfix", "duplicate", "on-hold"]
```

If not specified, defaults apply.

---

## Related Skills

| Skill | Location | Relationship |
|-------|----------|-------------|
| `autonomous-issue-dispatch` | `~/.claude/skills/` | Parent architecture — defines the full pipeline this skill belongs to |
| `issue-handler` | `~/.claude/skills/` | **Downstream** — Dispatcher invokes Handler for each actionable issue |
| `bug-intake` | `~/.claude/skills/` | **Upstream** — Bug Intake creates GitHub issues that Dispatcher triages |
| `dev-loop` | `~/.claude/skills/` | **Upstream** — Dev Loop runs Bug Intake repeatedly, feeding this queue |
| `qa-submission` | `.claude/skills/` (per-project) | **Downstream** (via CTO) — QA submission after Handler → CTO completes fix |
| `github-issue-manager` | Agent | **Tool** — All issue I/O (read, write, label, status) delegated to this agent |
