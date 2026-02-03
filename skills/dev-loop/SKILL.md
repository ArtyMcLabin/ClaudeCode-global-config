---
name: dev-loop
description: Standard development SOP for ALL code changes — bug fixes, features, refactors, any implementation. Defines the universal pipeline (investigate → fix → test → deploy → QA) and scope-based decision matrix. Also provides continuous scanning mode for autonomous operation. Use when implementing ANY code change, fixing bugs, building features, or when user says "start dev loop", "cowork", "fix this", "implement this", "build this". Each workspace can override with local skill.
---

# Dev Loop — Universal Development SOP

> **Part of:** Autonomous Issue Dispatch System
> See `~/.claude/skills/autonomous-issue-dispatch/SKILL.md` for full architecture.

## 🚨 This Skill Applies to ALL Development Work

This is NOT just for continuous scanning. **Every code change** — whether from a direct user request, a GitHub issue, a Slack bug report, or autonomous scanning — follows this SOP. The only variable is **scope**, which determines which steps are mandatory.

### Scope: What This SOP Covers

**IN SCOPE (dev-loop applies):**
- Project/application code that lives in a repository
- Code that will be maintained, deployed, used by others
- Bug fixes, features, refactors to existing codebase

**OUT OF SCOPE (dev-loop does NOT apply):**
- Temporary scripts Claude writes for one-off automation (sync scripts, data transforms, scratchpad utilities)
- Context engineering files (CLAUDE.md, skills, agents) — these have their own governance
- Documentation-only changes (.md, .txt)

**Signal words for exemption:** When writing a temporary script, mention "temporary script", "one-off", or "scratchpad" in the conversation — the stop hook recognizes these as exempt from dev-loop enforcement.

---

## Development Pipeline (Universal)

```
ANY code change request
  │
  ▼
┌─── SCOPE ASSESSMENT ──────────────────────────────────────┐
│                                                             │
│  How many files? What's the blast radius?                   │
│                                                             │
│  SMALL (1-3 files, clear fix, no architecture decisions)    │
│  → Investigate → Fix → Test → Deploy → QA                  │
│                                                             │
│  MEDIUM (4+ files, crosses modules, needs planning)         │
│  → Investigate → Plan → Fix → Test → Deploy → QA           │
│                                                             │
│  LARGE (new system, schema change, architecture)            │
│  → CTO Agent orchestrates full pipeline                     │
│  → Or defer if autonomous (big work rule)                   │
│                                                             │
└─────────────────────────────────────────────────────────────┘
```

### Step-by-Step Pipeline

| # | Step | Small | Medium | Large | Details |
|---|------|-------|--------|-------|---------|
| 1 | **Investigate** | ✅ | ✅ | ✅ | Understand the problem. Read code, reproduce, root cause. |
| 2 | **Plan** | Skip | ✅ | ✅ | Use EnterPlanMode or CTO Agent. Get user approval. |
| 3 | **Fix** | ✅ | ✅ | ✅ | Implement the change. |
| 4 | **Test** | ✅ | ✅ | ✅ | Run test suite. Add/update tests if touching testable logic. |
| 5 | **Commit** | ✅ | ✅ | ✅ | Commit with descriptive message. |
| 6 | **Deploy** | ✅ | ✅ | ✅ | Per repo's deploy mode (auto-prod, auto-stage, approval-required). |
| 7 | **QA Submit** | ✅ | ✅ | ✅ | Invoke the project's `qa-submission` skill (`.claude/skills/qa-submission/SKILL.md`). Do NOT post to Slack directly. If no skill exists, report gap to orchestrator. **No exceptions.** |
| 8 | **Report** | ✅ | ✅ | ✅ | Tell user: what changed, deployed (yes/no), QA status. |

**Steps 4-7 are MANDATORY for every code change.** The Stop hook enforces this.

### When User Says "Don't Bother with QA" or "Just a Quick Fix"

Follow the pipeline anyway. The user's CLAUDE.md says "EVERY change gets submitted to QA. No exceptions based on perceived simplicity." If the user explicitly overrides in the moment, comply but note it.

### QA Submission — Skill, Not Raw API

The qa-submission skill encapsulates the full QA workflow (GitHub issue, Slack formatting, labels, poka-yoke). Posting directly to a QA channel via Slack API bypasses all of this.

**Correct:** Invoke `.claude/skills/qa-submission/SKILL.md` (per-project)
**Wrong:** Call Slack MCP tools directly to post a QA message
**Wrong:** Skip QA because "it's a small fix"

If the current project has no qa-submission skill, report this gap to the orchestrator rather than improvising.

---

## Ad-Hoc Mode (Direct User Request)

When the user asks to fix/build something directly (not via dev-loop scanning):

```
User request → Investigate → Fix → Test → Commit → Deploy → QA → Report
```

**No intake scan. No dispatcher triage. No iteration loop.** Just the pipeline.

**Decision matrix for direct requests:**

| User says... | Scope | Action |
|-------------|-------|--------|
| "Fix this bug" / "This is broken" | Usually small | Pipeline steps 1,3-8 |
| "Build this feature" / "Implement this" | Usually medium | Pipeline steps 1-8 |
| "Refactor X" / "Redesign Y" | Usually large | CTO Agent or defer |
| "Just change this text" / "Rename X" | Small | Pipeline steps 3-8 (investigate optional) |

---

## Continuous Scan Mode

**Trigger:** "Start dev loop" / "Run continuous scan" / "Scan and fix bugs" / "Cowork with <TEAMMATE>"

Uses `~/.claude/skills/bug-intake/SKILL.md` for each scan iteration.

```
START (silently - no announcement message)
  │
  ▼
┌─── ITERATION ──────────────────────────────────────────────┐
│                                                             │
│  PHASE 1: INTAKE SCAN                                       │
│  Run bug-intake skill (full scan of configured channels)    │
│  Intake sources: Slack channels, Google Sheets (per-repo)   │
│  Also checks: GitHub issues (existing, not from intake)     │
│  Identifies: new bugs, verification responses, questions    │
│                                                             │
│  PHASE 2: TRIAGE (Dispatcher)                               │
│  Run issue-dispatcher for the repo's GitHub issue queue:    │
│    - Hygiene checks (labels, staleness, duplicates)         │
│    - Categorize: Actionable / Blocked / Backlog / Needs QA  │
│    - Prioritize: severity > effort > dependencies > impact   │
│      Age is minor tiebreaker: newer first (more relevant)   │
│    - Issues from Phase 1 AND pre-existing GitHub issues     │
│      are triaged together — one unified queue               │
│                                                             │
│  PHASE 3: PROCESS ACTIONABLE ISSUES                         │
│  For each actionable issue (in priority order):             │
│                                                             │
│  Actionable issue →                                         │
│    1. Run issue-handler:                                    │
│       a. Ensure context (self-investigate: logs, codebase,  │
│          database, Slack thread, related issues)             │
│       b. If genuinely ambiguous: ask specific question,     │
│          label needs-info, move to Blocked, continue        │
│       c. Diagnose: query logs, reproduce, root cause        │
│    2. Hand off diagnosis package to CTO Agent               │
│       (strategic-cto-planner)                               │
│    3. CTO orchestrates: Developer, QA Engineer,             │
│       Integration Tester, Completion Gate                   │
│    4. TDD — all tests must pass before deploy               │
│    5. Deploy per repo's deploy mode                         │
│    6. Communicate result (per bug-intake Step 7)            │
│    7. Submit for QA (per qa-submission, if applicable)      │
│    8. Log: "Fixed #N, deployed/awaiting approval"           │
│                                                             │
│  Big work (flagged by Dispatcher) →                         │
│    1. If from Slack: Add :hourglass: reaction               │
│    2. Create/update GitHub issue                            │
│    3. Reply in thread: "Noted — needs owner approval.       │
│       Created issue #N for tracking."                       │
│    4. Log: "Deferred #N (big work)"                         │
│    ⚠️ Do NOT attempt big work autonomously.                 │
│                                                             │
│  Verification response (reporter confirms) →                │
│    1. Close GitHub issue                                    │
│    2. Replace :eyes: with :white_check_mark:                │
│    3. Log: "Closed #N (verified)"                           │
│                                                             │
│  Verification response (reporter/QA rejects) →              │
│    1. Read rejection details                                │
│    2. Route back to CTO Agent (skip Handler — diagnosis     │
│       exists, just needs iteration)                         │
│    3. CTO re-fixes, tests, deploys                          │
│    4. Re-submit for QA                                      │
│    5. Update thread with new fix details                    │
│    6. Log: "Re-fixed #N after rejection"                    │
│                                                             │
│  Direct question from team member →                         │
│    1. Read question context                                 │
│    2. Reply in thread with answer                           │
│    3. If question requires owner decision, say so           │
│    4. Log: "Answered question in thread"                    │
│                                                             │
│  PHASE 4: WAIT                                              │
│  Sleep 5 minutes (300 seconds)                              │
│  Then go back to PHASE 1                                    │
│                                                             │
└─────────────────────────────────────────────────────────────┘
```

### Exit Conditions

| Condition | Action |
|-----------|--------|
| **3 consecutive empty scans** (15 min idle) | Log summary in chat, exit silently |
| **User returns** ("stop", "I'm back", Ctrl+C) | Log summary in chat, exit silently |
| **Critical failure** (deploy fails, API down) | Log summary + blocker details, exit |
| **Context window pressure** | Log summary, exit (user re-invokes in fresh session) |

**No Slack announcements for session start/end.** Only post to Slack for actual work items.

### Iteration Logging

After each iteration, maintain a running log in chat:

```
── Iteration 1 (14:30) ──────────────────────
• Fixed #134 "caption not saving" → tests passed → deployed
• Closed #131 (verified by reporter)
• Deferred: "redesign sidebar" (big work)
⏳ Waiting 5 minutes...

── Iteration 2 (14:35) ──────────────────────
• No new bugs
• No verification responses
⏳ Waiting 5 minutes... (idle: 1/3)
```

### Session Summary (On Exit)

Log summary in chat only (NO Slack post):

```
Dev loop complete. N iterations.

Fixed: #134, #135, #137
Verified: #131, #134
Pending verification: #137 (awaiting reporter)
Deferred: "redesign sidebar" (needs owner)
```

---

## TDD Requirements

**Every fix MUST have passing tests before deployment.** This is enforced regardless of deploy mode.

| Step | Required |
|------|----------|
| Run existing test suite | Always |
| Add/update tests for the fix | When fix touches testable logic |
| All tests pass | Must pass before deploy |
| Test results in log | Always (report pass/fail count) |

For `approval-required` repos, the test results are part of the evidence presented to the developer before they approve deployment.

---

## Deployment Policy Awareness

The loop reads `Deploy mode` from the repo's bug-intake config and adjusts behavior:

### `auto-prod` (e.g., <PROJECT_C>)
- No stage environment. Tests pass locally → deploy to production.
- Fast iteration. Acceptable risk because team is the only user.

### `auto-stage` (e.g., <PROJECT_B>)
- Stage environment exists. Default branch = stage.
- Push automatically after tests pass. Breaking stage is fine — fast iteration.

### `approval-required` (e.g., <COMPANY_A>)
- Production with live clients. No stage environment (yet).
- **The loop still starts automatically** — bugs are scanned, triaged, fixed, and tested without asking.
- **Deployment requires explicit developer approval.** Present:
  1. What was fixed
  2. Test results (pass/fail)
  3. Files changed
  4. Ask: "Deploy to production?"
- Developer says yes → deploy. Developer says no → log and move on.

---

## Actionable Slack Replies Only

Every Slack reply MUST be actionable. Never leave things hanging.

**If fix is deployed and needs testing:** Tell the reporter exactly what to test.
  - "Fix deployed. Please test: [specific steps]. Reply here if still broken."

**If deferred:** Be clear about what happens next.
  - "Noted for owner review. No action needed from you."

**Never:** Post vague "tracking this" messages that leave people wondering if they need to do anything.

---

## Wait Implementation

```bash
# 5-minute wait between iterations
sleep 300
```

Or on Windows:
```powershell
Start-Sleep -Seconds 300
```

---

## Response Deadline (Verification)

If a reporter hasn't confirmed or rejected a fix within **2 days**, @mention them in the thread asking for verification. This is checked on every scan.

Local overrides may add additional response deadline behavior (e.g., escalating to a manager).

---

## Local Override Pattern

Repos can provide `.claude/skills/dev-loop/SKILL.md` to extend this skill. Common overrides:

- **Additional scan targets** (e.g., separate QA channel)
- **Dedicated QA person** (e.g., always mention a specific team member)
- **Custom escalation** (e.g., escalate to CEO after N days)
- **Modified exit conditions** (e.g., different idle threshold)
- **Custom test steps** (e.g., E2E tests for UI changes)

The override pattern works the same as bug-intake: `## Override:` sections augment global steps, never skip them.

---

## Related Skills

| Skill | Location | Relationship |
|-------|----------|-------------|
| `autonomous-issue-dispatch` | `~/.claude/skills/` | Parent architecture — defines the full pipeline |
| `bug-intake` | `~/.claude/skills/` | **Core** — Each scan iteration runs bug-intake |
| `issue-dispatcher` | `~/.claude/skills/` | **Downstream** — Dispatcher triages issues |
| `slack` | `~/.claude/skills/` | Underlying API patterns for Slack operations |
| `qa-submission` | `.claude/skills/` (per-project) | Used by overrides that have separate QA channels |
