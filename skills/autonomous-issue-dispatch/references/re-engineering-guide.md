# Autonomous Issue Dispatch — Re-Engineering Guide

This document exists for sessions that need to **modify the framework itself** — adding skills, changing contracts, evolving the pipeline. It does NOT describe how the framework operates (the skills themselves are the SSoT for that).

**When to read this:** You're about to change a SKILL.md in this framework. Read this first.
**When NOT to read this:** You're running the framework (intake, dispatch, fix, deploy). Just follow the skills.

---

## Reading Order (Orientation)

When you need to understand the full framework before modifying it:

1. `autonomous-issue-dispatch/SKILL.md` — Hub. System architecture diagram + pipeline overview.
2. `bug-intake/SKILL.md` — How issues enter. Shared Channel Registry, emoji state machine, verification loop.
3. `issue-dispatcher/SKILL.md` — Queue triage. What to work on next.
4. `issue-handler/SKILL.md` — Single-issue diagnosis. Evidence packaging for CTO.
5. `dev-loop/SKILL.md` — Continuous mode wrapper. Scope decision matrix.
6. Per-repo `qa-submission/SKILL.md` — QA after deployment (varies by workspace).

Each skill says "Part of: Autonomous Issue Dispatch System" and has a "Related Skills" table showing its neighbors.

---

## Change Impact Matrix

When you modify one skill, check these others for consistency:

| If you change... | Also check... | Why |
|-----------------|---------------|-----|
| Bug-intake emoji states | dev-loop (scans for same emojis) | Dev-loop relies on emoji meanings defined in bug-intake |
| Bug-intake Shared Channel Registry | GH_Coordinator CLAUDE.md Phase 2 | Coordinator scans these channels |
| Deploy mode values | All per-repo bug-intake configs | They declare deploy mode per the schema |
| Issue-handler evidence format | CTO Agent expectations (see Contract below) | Handler packages evidence for CTO |
| Dev-loop scope matrix | autonomous-issue-dispatch pipeline | Scope categories must match |
| QA submission format | Per-repo qa-submission skills | They implement the contract |
| Verification loop timing | bug-intake/references/design-decisions.md | Rationale for timing is documented there |

---

## Component Contracts

These are the input/output agreements between skills. The skills themselves define the full behavior; this section only captures the interface boundaries.

### Handler → CTO Agent

Handler produces an **evidence package** and hands off. CTO expects:
- GitHub issue reference (owner/repo#N)
- Root cause hypothesis
- Affected files/functions
- Reproduction steps (if available)
- Logs/error messages

CTO returns: implemented fix + test results + deployment status + QA submission.

### Bug-Intake → Issue-Dispatcher

Bug-intake creates GitHub issues. Dispatcher expects:
- Issue has "Bug:" or "Feature:" prefix in title
- Issue body contains Slack permalink (bidirectional link)
- Issue has appropriate labels (if workspace defines them)

### Dev-Loop → Bug-Intake

Dev-loop invokes bug-intake repeatedly. Bug-intake expects:
- Slack token resolved (via slack skill)
- Channel IDs from config
- Returns: count of new issues, count of verification updates

---

## Design Philosophy (Cross-Skill)

These principles apply across ALL skills in the framework. Individual design decisions specific to one skill live in that skill's `references/design-decisions.md`.

- **No auto-closure.** Reporter non-response is human, not system. See `bug-intake/references/design-decisions.md` for full rationale.
- **TDD is non-negotiable.** Every fix has tests before deployment regardless of deploy mode.
- **CTO Agent is always the implementation authority** for non-trivial work. Never dispatch directly to developer agent.
- **QA submission is never skipped.** Every code change gets QA.
- **Deploy mode is per-repo, not per-issue.** Repos declare their mode; the framework respects it.

---

## Extending the Framework

### Adding a New Skill

1. Read this guide (you're doing it)
2. Determine where the skill fits in the pipeline (after which existing skill?)
3. Create the skill with "Part of: Autonomous Issue Dispatch System" header
4. Add it to the "Related Skills" table in `autonomous-issue-dispatch/SKILL.md`
5. Add it to the "Related Skills" table in its immediate neighbors
6. Update the Change Impact Matrix above
7. If the skill has design decisions worth preserving, create `references/design-decisions.md`

### Adding a New Workspace

1. Create per-repo `bug-intake/SKILL.md` with Workspace Config table
2. If the workspace has a dedicated bug channel, add to Shared Channel Registry in global `bug-intake/SKILL.md`
3. Create per-repo `qa-submission/SKILL.md` if workspace has QA process
4. Optionally create per-repo `dev-loop/SKILL.md` override if continuous scanning needed

### Deprecating a Skill

1. Remove from all "Related Skills" tables
2. Remove from Change Impact Matrix above
3. Update `autonomous-issue-dispatch/SKILL.md` architecture diagram
4. Delete the skill directory
