---
name: autonomous-issue-dispatch
description: Orchestration overview for the autonomous issue dispatch system. Handles bugs AND features from ANY entry point. References the component skills (dispatcher, handler) and per-project skills (bug-intake, qa-submission). Use when user says "dispatch", "fix these issues", "batch implement", "implement this", "build this", "develop this", "here's a plan", or any implementation/feature/fix request — including direct conversational requests to Claude Code.
user-invocable: false
---

# Autonomous Issue Dispatch System

## Goal

Claude Code receives issues (bugs OR features), diagnoses them, implements fixes/features, tests, deploys, and submits for QA - all without human intervention (except final QA approval).

**This SOP covers ALL implementation work**, not just dispatched issues. Whether the trigger is a Slack bug report, a GitHub issue, or a direct request in the Claude Code conversation — the same pipeline applies. The CTO Agent is always the implementation authority for non-trivial work.

## System Architecture

```
┌─────────────────────────────────────────────────────────────────┐
│  CHANNEL (Slack — unified bug + QA per workspace)               │
│  Bug report: "Caption generation is broken"                     │
│  QA response: thread reply "Approved" / "Rejected"              │
└─────────────────────┬───────────────────────────────────────────┘
                      │
                      ▼
┌─────────────────────────────────────────────────────────────────┐
│  BUG INTAKE (per-project)                                       │
│  Scans channel threads for actionable items:                    │
│                                                                 │
│  New top-level messages (bug reports):                           │
│  - Create GitHub issue with source reference                    │
│  - Reply in thread: "Documented as #123"                        │
│  - Route to → Dispatcher                                        │
│                                                                 │
│  Thread replies (QA responses):                                 │
│  - Rejection: Update issue → Route directly to CTO (skip Handler)│
│  - Approval: Close issue → Add checkmark to thread              │
│                                                                 │
│  Skill: .claude/skills/bug-intake-override/SKILL.md             │
└─────────────────────┬───────────────────────────────────────────┘
                      │
        ┌─────────────┴─────────────┐
        ▼                           ▼
   NEW ISSUES                  QA REJECTION
        │                           │
        ▼                           │
┌───────────────────────────┐       │
│  ISSUE DISPATCHER (global)│       │
│  - Triage queue, hygiene  │       │
│  - Prioritize actionable  │       │
│  - Invoke Handler         │       │
└───────────┬───────────────┘       │
            │                       │
            ▼                       │
┌───────────────────────────┐       │
│  ISSUE HANDLER (global)   │       │
│  - Query logs, diagnose   │       │
│  - Reproduce via test     │       │
│  - Package for CTO        │       │
└───────────┬───────────────┘       │
            │                       │
            └───────────┬───────────┘
                        ▼
┌─────────────────────────────────────────────────────────────────┐
│  CTO AGENT (global)                                             │
│  - Developer: implements fix                                    │
│  - QA Engineer: code review + tests                             │
│  - Integration Tester: E2E validation                           │
│  - Completion Gate: verify all criteria                         │
│  Agent: strategic-cto-planner                                   │
└─────────────────────┬───────────────────────────────────────────┘
                      │
                      ▼
┌─────────────────────────────────────────────────────────────────┐
│  QA SUBMISSION (per-project)                                    │
│  - Reply in bug thread: "Fix ready for QA" + test steps         │
│  - Include source reference + issue link                        │
│  - Human responds in same thread (approve/reject)               │
│  Skill: .claude/skills/qa-submission/SKILL.md                   │
└─────────────────────────────────────────────────────────────────┘
                      │
                      ▼
            ┌─────────────────┐
            │  Human reviews  │
            │  in thread      │
            └────────┬────────┘
                     │
     ┌───────────────┴───────────────┐
     ▼                               ▼
  APPROVED                       REJECTED
     │                               │
     ▼                               ▼
  Bug Intake                    Bug Intake
  sees approval                 sees rejection
     │                               │
     ▼                               ▼
  Close issue                   Route to CTO
  Add checkmark                 (skip Handler)
  to thread                     Iterate on fix
```

---

## Component Responsibilities

### Global Components (Uniform Across All Repos)

| Component | Purpose | Invokes |
|-----------|---------|---------|
| **Issue Dispatcher** | Queue triage, hygiene, prioritization | Issue Handler |
| **Issue Handler** | Diagnosis, reproduction, evidence | CTO Agent |
| **CTO Agent** | Fix implementation, testing, deployment | QA Submission |

### Per-Project Components (Customized Per Repo)

| Component | Purpose | Project Defines |
|-----------|---------|-----------------|
| **Bug Intake** | Receive reports, create issues, notify | Channel ID, QA mode, repo routing |
| **QA Submission** | Submit for review, notify reporter | QA process, notification channel. Currently: <PROJECT_C> only. Other workspaces use deploy-gate (<COMPANY_A>: approval-required) or auto-stage (<PROJECT_B>). |

> **Generalized flows:**
> - `~/.claude/skills/bug-intake/SKILL.md` — common scan/triage/fix/communicate procedure. Per-repo configs extend with `## Override:` sections.
> - `~/.claude/skills/dev-loop/SKILL.md` — continuous loop (5-min intervals). Runs the **full pipeline** (intake → dispatcher → handler → CTO → QA) per iteration.

### Workspaces

| Workspace | Slack Domain | Bug Channel | Repos |
|-----------|-------------|-------------|-------|
| **<BRAND>** | `<BRAND>` | `#cf-bugs-qa` (unified) | <PROJECT_C> |
| **<COMPANY_A> HQ** | `<WORKSPACE>` | `#bugs` | <REPO_NAME>, <REPO_NAME>, <REPO_NAME> |
| **<PROJECT_B>** | `<WORKSPACE_B>` | `#bugs-general` | <REPO_NAME>, <PROJECT_B>_Website, <REPO_NAME>-schema |

**<REPO_NAME> special case:** When invoked locally, scans Google Sheet (manager feedback) instead of Slack. When dispatched externally, handles Slack-routed issue + optionally scans Sheet with user approval. See `<LOCAL_PATH>\<REPO_NAME>\.claude\skills\bug-intake-override\SKILL.md`.

### Unified Pipeline

**All work — regardless of source — flows through the same pipeline:**

```
ANY entry point → Triage → [Handler if bug] → CTO Agent (implement) → Deploy → QA
```

| Entry Point | Intake | Dispatcher | Handler | CTO Agent | Deploy | QA |
|-------------|--------|------------|---------|-----------|--------|-----|
| **Slack bug** | Yes | Yes | Yes | Yes | Yes | Yes |
| **GitHub issue** | Skip | Yes | Yes | Yes | Yes | Yes |
| **Sheet (CS AI)** | Yes | Yes | Yes | Yes | Yes | Yes |
| **Direct request** | Skip | Triage only | Skip (feature) / Yes (bug) | **Yes** | **Yes** | **Yes** |
| **QA rejection** | Skip | Skip | Skip | Yes | Yes | Yes |

- **Slack-sourced:** Bug Intake creates GitHub issue → enters unified queue
- **GitHub-native:** Already in queue → Dispatcher picks up directly
- **Sheet-sourced (CS AI):** Bug Intake creates GitHub issue → enters unified queue
- **Direct request:** User asks Claude Code directly ("implement this", "build X", "here's a plan"). Triage for complexity → CTO Agent for non-trivial → Deploy → QA. No intake or handler needed.
- **QA rejection:** Routes back to CTO Agent directly (skip Handler — diagnosis exists)

**CTO Agent is always the implementation authority.** Never dispatch directly to developer agent.

---

## Trigger Mechanisms

### Batch Issue Dispatch (Features + Bugs from GitHub)

When user says "dispatch these issues", "implement these", "batch fix", or similar:
1. **Triage** the issues (easy vs big, per Issue Dispatcher skill)
2. **Diagnose** each via Issue Handler (query logs, reproduce, evidence)
3. **Dispatch each to CTO Agent** (`strategic-cto-planner`) — NEVER raw developer agents
4. CTO Agent handles the full DoD per issue (see Orchestrator-Owns-Deploy section)
5. Orchestrator tracks progress across all dispatched issues

This path skips Bug Intake (issues already exist in GitHub) but still uses Dispatcher and Handler for triage and diagnosis.

### Direct Request (Conversational)

When user directly asks Claude Code to implement something ("implement this", "build X", "here's a plan", "add feature Y"):

1. **Triage** — Is this trivial (typo, 1-line fix, single obvious change) or non-trivial?
   - **Trivial** (touches ≤2 files, no architectural decisions): Implement directly → Deploy → QA
   - **Non-trivial** (3+ files, new migration, new system/pattern, prompt changes): Continue to step 2
2. **Dispatch to CTO Agent** (`strategic-cto-planner`) — CTO orchestrates Developer, QA Engineer, Integration Tester
3. **Deploy** — Run migrations, commit, push. This is NOT a TODO — do it as part of the work.
4. **QA Submission** — Per project's qa-submission skill. No exceptions.

**The direct request path skips Bug Intake (no channel to scan) and Handler (no bug to diagnose for features).** But CTO Agent and QA are mandatory for non-trivial work.

**What counts as non-trivial?**
- Touches 3+ files
- New database migration
- Architectural changes (new systems, new patterns)
- Prompt/pipeline logic changes
- New UI sections or components

### Bug Intake (Slack Channel Scanning)

Bug Intake can be triggered in multiple ways:

| Trigger | When | Command |
|---------|------|---------|
| **Manual** | On-demand by operator | "Scan for bug reports" / "Check QA responses" |
| **Daily scheduled** | Morning or night cron | Future: automated daily run |
| **Webhook** | Real-time on new message | Future: Slack webhook triggers scan |

**Current implementation:** Manual trigger only. Design is compatible with future automation.

**Manual trigger commands:**
```
"Scan for new bug reports"        → Check bug channel for new unaddressed messages
"Check QA responses"              → Check threads for QA approve/reject responses
"Run intake scan"                 → Full scan (new bugs + thread responses)
```

---

## Loop-Back Notifications

The reporter receives updates at key milestones:

| Milestone | Who Notifies | Where | Message |
|-----------|--------------|-------|---------|
| Bug documented | Bug Intake | Thread reply | "Created issue #123" |
| Fix in QA | QA Submission | Thread reply | "Fix ready for QA" + test steps |
| QA approved | Bug Intake | Thread reply + checkmark | "Resolved and deployed" |
| QA rejected | Bug Intake | Thread reply | Acknowledgment, then routes to CTO |

**Unified thread flow (all in same bug thread):**
1. Reporter posts bug → Bug Intake replies in thread with issue link
2. Fix ready → QA Submission replies in same thread with test steps
3. QA reviewer responds in same thread (approve/reject)
4. Bug Intake sees response:
   - Approved → close issue, add checkmark to thread
   - Rejected → route to CTO for iteration

**Source reference storage:** Bug Intake stores original report location (Slack thread URL) in GitHub issue metadata. This enables loop-back to the correct thread.

---

## Invocation Patterns

### Full Intake Scan (Recommended Entry Point)

```
"Run intake scan" / "Scan for bug reports and QA responses"
```

1. Bug Intake scans bug channel for new unaddressed top-level messages
2. Bug Intake scans threads for QA approve/reject responses
3. New reports → create issues → Dispatcher → Handler → CTO
4. Rejections → route directly to CTO (skip Handler)
5. Approvals → close issues, add checkmark to thread

### Manual Trigger Points

| Command | Starts At | Use When |
|---------|-----------|----------|
| "Run intake scan" | Bug Intake | Full channel scan (new bugs + QA responses) |
| "Scan for new bug reports" | Bug Intake | Only check for new top-level messages |
| "Check QA responses" | Bug Intake | Only check threads for QA responses |
| "Check pending issues" / "Find low-hanging fruit" | Dispatcher | Triage GitHub queue |
| "Diagnose issue #71" | Handler | Investigate specific issue |
| "Fix issue #71" | CTO Agent | Known diagnosis, ready to fix |
| "Implement this" / "Build X" / "Here's a plan" | Direct Request → CTO Agent | User requests feature/fix directly |
| "Submit #71 for QA" | QA Submission | Ready for human review |

### Skip Layers When Appropriate

- **Direct GitHub issue:** Skip Bug Intake (no Slack notification needed)
- **QA rejection:** Skip Handler → straight to CTO (diagnosis exists)
- **Known diagnosis:** Skip Handler → straight to CTO
- **Simple fix:** Handler notes "trivial" → CTO may fast-track

### Future Automation Triggers

| Trigger Type | Implementation | Status |
|--------------|----------------|--------|
| Daily scheduled | Cron job runs "Run intake scan" | 🔮 Future |
| Webhook on Slack message | Slack app triggers scan | 🔮 Future |
| GitHub issue created | Webhook triggers Dispatcher | 🔮 Future |

---

## Repository Readiness Checklist

For autonomous issue dispatch to work, each repo needs:

### Infrastructure (Technical)

```
[ ] Error logging captures full context (inputs, outputs, errors)
[ ] Logs are queryable (database or structured files)
[ ] E2E tests exist for critical paths
[ ] E2E tests runnable via CLI
[ ] Database read access for log queries
[ ] CI/CD runs tests before deploy
```

### Skills (Context Engineering)

```
[ ] .claude/skills/bug-intake-override/SKILL.md - workspace config (channel ID, QA mode, deploy mode, repo routing)
    Global base: ~/.claude/skills/bug-intake/SKILL.md
    Override example: <PROJECT_C>/.claude/skills/bug-intake-override/SKILL.md
[ ] .claude/skills/dev-loop-override/SKILL.md - continuous scanning override (optional)
    Global base: ~/.claude/skills/dev-loop/SKILL.md
    Override example: <PROJECT_C>/.claude/skills/dev-loop-override/SKILL.md
[ ] .claude/skills/qa-submission/SKILL.md - QA process (required for repos with dedicated QA channels; other repos rely on deploy-gate or approval-required mode)
```

### GitHub Setup

```
[ ] Project board with status columns (Todo, Doing, QA, Done, Backlog)
[ ] Labels for categorization (bug, enhancement, security, etc.)
[ ] needs-qa label for QA tracking
```

---

## Failure Modes & Recovery

### Handler Blocked (Can't Diagnose)

**Symptom:** Missing logs, can't reproduce, no test coverage.

**Recovery:**
1. Handler reports blocker type
2. Dispatcher may ask Bug Intake to request more info from reporter
3. Create infrastructure gap issue if systemic

### CTO Blocked (Can't Fix)

**Symptom:** Requires architectural change, external dependency, unclear requirements.

**Recovery:**
1. CTO reports blocker
2. Issue moves to "blocked" status
3. Dispatcher skips on future runs until unblocked

### QA Rejected

**Symptom:** Fix doesn't work, introduces regression, incomplete.

**Recovery:**
1. Human posts rejection as thread reply in bug channel
2. Bug Intake sees rejection during next scan (or webhook trigger)
3. Bug Intake routes directly to CTO (skips Handler - diagnosis still valid)
4. CTO iterates on fix
5. QA Submission re-posts in same thread with updated test steps
6. Cycle repeats until approved

### Reporter Unresponsive

**Symptom:** Asked for more info, no response.

**Recovery:**
1. Wait threshold (e.g., 7 days)
2. Dispatcher marks as stale
3. Eventually close with "unable to reproduce, please reopen with details"

---

## Metrics (Future)

Track system health:

| Metric | Target |
|--------|--------|
| Intake → Closed (median) | < 48 hours |
| Handler diagnosis rate | > 80% (can diagnose) |
| QA first-pass rate | > 90% (pass on first try) |
| Reporter satisfaction | Notified at all milestones |

---

## Parallel Claude Code Instances

**The user may run multiple Claude Code instances on the same repo simultaneously.** This is normal and sanctioned.

**Rules for the orchestrator:**
1. **NEVER assume all unstaged changes are yours.** Another instance may be working on different issues in the same working directory.
2. **Before reverting/discarding ANY unstaged changes:** ASK the user if another instance is working. If changes look unrelated to your dispatched work, they probably belong to another instance.
3. **Stage only YOUR files.** When committing, explicitly stage only the files your agents modified. Never `git add -A` or `git add .` on a shared working directory.
4. **If you see unexpected changes** (files you didn't touch, migrations you didn't create, schema changes outside your scope): treat them as belonging to another instance until the user confirms otherwise.
5. **Journal/config files may have entries from both instances.** Don't remove entries you didn't add — you could nuke another instance's migrations.

**The safe pattern:**
```
git add file1.ts file2.ts file3.ts   # Explicit files only
git add -A                            # NEVER on shared workdir
git restore file.ts                   # Could nuke another instance's work
```

---

## Orchestrator-Owns-Deploy Model

### The Problem

The CTO Agent (`strategic-cto-planner`) handles: Developer → QA Engineer → Integration Tester → QA Submission. But its Completion Gate does NOT explicitly include "commit + push to deploy." When multiple issues are dispatched in parallel, having each CTO sub-agent deploy independently causes:
- Merge conflicts from parallel commits
- Rogue scope going undetected (no diff audit)
- No batch deployment opportunity
- Risk of nuking parallel instance work

### The Solution: Orchestrator = CTO Agent with Deploy Authority

When dispatching multiple issues, the **orchestrator itself is a CTO Agent** with a special temporary role:
- It coordinates and orchestrates all sub-CTO agents
- It is **exclusively responsible for deployment** (commit, push, QA submission)
- Sub-CTO agents are explicitly told: **do NOT deploy — your DoD is "ready for deployment"**

### Two-Tier CTO Architecture

```
┌─────────────────────────────────────────────────────────────┐
│  ORCHESTRATOR CTO (you, temporary role)                      │
│  Responsibilities:                                           │
│  - Triage issues (easy vs big)                               │
│  - Dispatch to sub-CTO agents                                │
│  - Audit agent output for rogue scope                        │
│  - Batch commit + push (owns deployment)                     │
│  - Submit QA for all issues                                  │
│  - Label issues pending-qa                                   │
└──────────────────────┬──────────────────────────────────────┘
                       │
         ┌─────────────┼─────────────┐
         ▼             ▼             ▼
┌──────────────┐ ┌──────────────┐ ┌──────────────┐
│ Sub-CTO #119 │ │ Sub-CTO #108 │ │ Sub-CTO #126 │
│              │ │              │ │              │
│ Developer    │ │ Developer    │ │ Developer    │
│ QA Engineer  │ │ QA Engineer  │ │ QA Engineer  │
│ Int. Tester  │ │ Int. Tester  │ │ Int. Tester  │
│              │ │              │ │              │
│ DoD: "Ready  │ │ DoD: "Ready  │ │ DoD: "Ready  │
│  for deploy" │ │  for deploy" │ │  for deploy" │
└──────────────┘ └──────────────┘ └──────────────┘
```

### Sub-CTO Agent DoD (reports back to orchestrator)
1. Implement fix/feature (Developer agent)
2. Write/update tests (Developer agent)
3. Run test suite — all pass
4. Code review (QA Engineer)
5. Integration test (Integration Tester, if UI changes)
6. **Report: "Ready for deployment"** — list files modified, tests passed

### Orchestrator DoD (after all sub-CTOs report ready)
1. **Audit** all agent output for rogue scope (files outside issue scope)
2. **Run full test suite** across all changes
3. **Stage only in-scope files** (explicit `git add`, never `-A`)
4. **Commit with all issue references**
5. **Push to deploy** (trigger CI/CD)
6. **Submit QA** to Slack for each issue (per qa-submission skill)
7. **Label all issues** `pending-qa`
8. Wait for QA pass → close issues

### Standard Sub-CTO Dispatch Prompt Suffix

Include this in every sub-CTO dispatch:
```
DEPLOYMENT RULES:
- Do NOT commit or push. Your DoD is "ready for deployment."
- Report back: files modified, tests written, tests passed count.
- Only modify files directly related to this issue.
- Use @playwright/test for tests (NOT vitest, NOT jest).

QA RULES:
- After tests pass, invoke the project's qa-submission skill
  (.claude/skills/qa-submission/SKILL.md). Do NOT post to Slack manually.
- If no qa-submission skill exists, report "QA: no qa-submission skill
  found — orchestrator must handle QA submission."
- NEVER skip QA submission. Every code change gets QA. No exceptions.
```

**Never stop at "code is written." That's step 1 of the orchestrator's 8-step pipeline.**

---

## References

- `references/re-engineering-guide.md` — Change impact matrix, component contracts, extension procedures. Read before modifying any skill in this framework.

## Related Skills

| Skill | Location | Purpose |
|-------|----------|---------|
| issue-dispatcher | `~/.claude/skills/issue-dispatcher/` | Queue triage |
| issue-handler | `~/.claude/skills/issue-handler/` | Diagnosis |
| bug-intake | `~/.claude/skills/bug-intake/` (global) + `.claude/skills/bug-intake-override/` (per-project config) | Intake + notification |
| dev-loop | `~/.claude/skills/dev-loop/` (global) + `.claude/skills/dev-loop-override/` (per-project override) | Continuous scanning loop |
| qa-submission | `.claude/skills/qa-submission/` (per-project) | QA + notification |
| strategic-cto-planner | `~/.claude/agents/` | Fix orchestration |
