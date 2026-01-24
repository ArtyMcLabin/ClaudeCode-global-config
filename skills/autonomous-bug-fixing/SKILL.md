---
name: autonomous-bug-fixing
description: Orchestration overview for the autonomous bug fixing system. References the component skills (dispatcher, handler) and per-project skills (bug-intake, qa-submission).
---

# Autonomous Bug Fixing System

## Goal

Claude Code receives a bug report, diagnoses it, fixes it, tests it, and notifies the reporter - all without human intervention (except final QA approval).

## System Architecture

```
┌─────────────────────────────────────────────────────────────────┐
│  CHANNELS (Slack/Email/GitHub/etc.)                             │
│  #bug-reports: "Caption generation is broken"                   │
│  #qa-review: "Rejected - still broken" / "Approved"             │
└─────────────────────┬───────────────────────────────────────────┘
                      │
                      ▼
┌─────────────────────────────────────────────────────────────────┐
│  BUG INTAKE (per-project)                                       │
│  Scans BOTH channels for actionable items:                      │
│                                                                 │
│  From #bug-reports (new issues):                                │
│  - Create GitHub issue with source reference                    │
│  - Notify reporter: "Documented as #123"                        │
│  - Route to → Dispatcher                                        │
│                                                                 │
│  From #qa-review (QA responses):                                │
│  - Rejection: Update issue → Route directly to CTO (skip Handler)│
│  - Approval: Close issue → Notify reporter in #bug-reports      │
│                                                                 │
│  Skill: .claude/skills/bug-intake/SKILL.md                      │
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
│  - Post to #qa-review: "Fix ready for QA"                       │
│  - Include source reference + issue link                        │
│  - Human responds in thread (approve/reject)                    │
│  Skill: .claude/skills/qa-submission/SKILL.md                   │
└─────────────────────────────────────────────────────────────────┘
                      │
                      ▼
            ┌─────────────────┐
            │  Human reviews  │
            │  in #qa-review  │
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
  Notify reporter               (skip Handler)
  in #bug-reports               Iterate on fix
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
| **Bug Intake** | Receive reports, create issues, notify | Channel (Slack/email), notification format |
| **QA Submission** | Submit for review, notify reporter | QA process, notification channel |

---

## Trigger Mechanisms

Bug Intake can be triggered in multiple ways:

| Trigger | When | Command |
|---------|------|---------|
| **Manual** | On-demand by operator | "Scan for bug reports" / "Check QA responses" |
| **Daily scheduled** | Morning or night cron | Future: automated daily run |
| **Webhook** | Real-time on new message | Future: Slack webhook triggers scan |

**Current implementation:** Manual trigger only. Design is compatible with future automation.

**Manual trigger commands:**
```
"Scan for new bug reports"        → Check #bug-reports for unaddressed items
"Check QA responses"              → Check #qa-review for approve/reject responses
"Run intake scan"                 → Check both channels
```

---

## Loop-Back Notifications

The reporter receives updates at key milestones:

| Milestone | Who Notifies | Channel | Message |
|-----------|--------------|---------|---------|
| Bug documented | Bug Intake | #bug-reports | "Created issue #123" |
| Fix in QA | QA Submission | #qa-review | "Ready for QA: [issue link]" |
| QA approved | Bug Intake | #bug-reports | "Resolved and deployed" |
| QA rejected | Bug Intake | #qa-review | Acknowledgment, then routes to CTO |

**Channel flow:**
1. Reporter posts in #bug-reports → Bug Intake replies with issue link
2. Fix ready → QA Submission posts in #qa-review
3. Human responds in #qa-review (approve/reject)
4. Bug Intake sees response:
   - Approved → notify reporter in #bug-reports, close issue
   - Rejected → route to CTO for iteration

**Source reference storage:** Bug Intake stores original report location (Slack thread URL) in GitHub issue metadata. This enables loop-back to the correct thread.

---

## Invocation Patterns

### Full Intake Scan (Recommended Entry Point)

```
"Run intake scan" / "Scan for bug reports and QA responses"
```

1. Bug Intake scans #bug-reports for new unaddressed reports
2. Bug Intake scans #qa-review for approve/reject responses
3. New reports → create issues → Dispatcher → Handler → CTO
4. Rejections → route directly to CTO (skip Handler)
5. Approvals → close issues → notify reporter

### Manual Trigger Points

| Command | Starts At | Use When |
|---------|-----------|----------|
| "Run intake scan" | Bug Intake | Full channel scan |
| "Scan for new bug reports" | Bug Intake | Only check #bug-reports |
| "Check QA responses" | Bug Intake | Only check #qa-review |
| "Check pending issues" / "Find low-hanging fruit" | Dispatcher | Triage GitHub queue |
| "Diagnose issue #71" | Handler | Investigate specific issue |
| "Fix issue #71" | CTO Agent | Known diagnosis, ready to fix |
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

For autonomous bug fixing to work, each repo needs:

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
[ ] .claude/skills/bug-intake/SKILL.md - defines intake channel + notifications
[ ] .claude/skills/qa-submission/SKILL.md - defines QA process + notifications
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
1. Human posts rejection in #qa-review thread
2. Bug Intake sees rejection during next scan (or webhook trigger)
3. Bug Intake routes directly to CTO (skips Handler - diagnosis still valid)
4. CTO iterates on fix
5. QA Submission re-posts to #qa-review
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

## Related Skills

| Skill | Location | Purpose |
|-------|----------|---------|
| issue-dispatcher | `~/.claude/skills/issue-dispatcher/` | Queue triage |
| issue-handler | `~/.claude/skills/issue-handler/` | Diagnosis |
| bug-intake | `.claude/skills/bug-intake/` (per-project) | Intake + notification |
| qa-submission | `.claude/skills/qa-submission/` (per-project) | QA + notification |
| strategic-cto-planner | `~/.claude/agents/` | Fix orchestration |
