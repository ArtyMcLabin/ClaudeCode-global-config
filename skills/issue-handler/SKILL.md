---
name: issue-handler
description: Diagnose a single GitHub issue - query logs, reproduce, collect evidence, hand off to CTO agent. The "how it broke" investigation layer.
user-invocable: false
---

# Issue Handler

> **Part of:** Autonomous Issue Dispatch System
> **Upstream:** `issue-dispatcher` (or direct invocation)
> **Downstream:** CTO Agent → `qa-submission` (per-project)

## Purpose

The Handler answers: **"Why is this broken and how do we fix it?"**

It takes ONE issue and:
- Queries logs to find actual error
- Reproduces via test
- Collects evidence
- Packages diagnosis for CTO handoff

## Philosophy

**Handler is focused.** One issue at a time. Deep investigation.

**Handler is evidence-based.** No guessing. Query logs, reproduce, prove.

**Handler prepares, doesn't fix.** The moment you start writing production code, hand off to CTO.

---

## Handler Workflow

### Step 1: Assess Information & Ensure Context

```
Can I answer these questions from the issue?
├── WHAT failed? (which feature/endpoint)
├── WHEN did it fail? (timestamp or recency)
├── WHO experienced it? (user/session ID)
├── Any ERROR shown to user?
└── Source reference? (Slack thread, email for loop-back)
```

**If basic info missing — self-investigate BEFORE asking humans:**

1. **Query logs** — search for recent errors matching the described symptom
2. **Search codebase** — find relevant code paths, recent commits, related changes
3. **Check database** — look for affected records, user sessions, error patterns
4. **Read Slack thread** — if sourced from Slack, read full thread for additional context
5. **Check related issues** — similar past bugs may provide clues

**Only after exhausting automated investigation:** If the issue is genuinely ambiguous or requires information that cannot be fetched programmatically (e.g., "what did the user see on screen?", "what was the intended behavior?"), then ask for clarification:
- Reply in the GitHub issue (or Slack thread) with a **specific question** — not "need more info" but "Was this on mobile or desktop? The error only reproduces on viewport < 768px."
- Add a `needs-info` label
- Move to Blocked bucket
- Log: "Blocked #N — asked: [specific question]"
- Continue to next issue (don't wait)

### Step 2: Query Logs

> **Prerequisite:** Project must have queryable logging infrastructure.
> See "Repository Requirements" section below.

```sql
-- Example: Find recent failures
SELECT * FROM audit_logs
WHERE operation_name = 'generate_captions'
  AND status = 'error'
  AND created_at > NOW() - INTERVAL '24 hours'
ORDER BY created_at DESC;
```

**Look for:**
- The specific failing request
- The actual error (not user-reported symptoms)
- Patterns (one user or everyone? one input type or all?)

**For LLM operations:**
- Full rendered prompt
- Raw LLM response
- Parse error details

### Step 3: Reproduce

Write or identify E2E test that triggers the bug:

```typescript
test('reproduces issue #123 - caption parse failure', async () => {
  // Create test data matching the failing scenario
  const entry = await createTestEntry({ transcript: '...' });

  // Trigger the operation
  const result = await generateCaptions(entry.id);

  // This should fail before fix, pass after
  expect(result.status).toBe('success');
});
```

**If reproduction fails:** Report as blocker. Can't verify fix without reproduction.

### Step 4: Root Cause Analysis

From logs and reproduction, identify:

| Finding | Document |
|---------|----------|
| Root cause | "LLM returned markdown instead of JSON" |
| Trigger condition | "Only when transcript > 5000 chars" |
| Affected scope | "All caption generation, ~5% of requests" |
| Suggested fix | "Add markdown stripping before JSON parse" |

### Step 5: Hand Off to CTO

Package everything for CTO agent:

```markdown
## Diagnosis for Issue #123

**Root cause:** LLM returns markdown-wrapped JSON when transcript exceeds 5000 characters.
The JSON parser fails on the markdown code fence.

**Evidence:**
- Log entry [timestamp]: `ParseError: Unexpected token at position 0`
- Raw LLM response started with "```json" instead of "{"
- 47 similar failures in last 24 hours

**Reproduction:** `tests/e2e/caption-parse-failure.spec.ts`
- Currently fails (expected)
- Should pass after fix

**Suggested fix:**
- File: `api/lib/llmClient.ts:142`
- Add markdown fence stripping before JSON.parse()

**Relevant files:**
- `api/generate-captions.ts:87` - calls parseJSON
- `api/lib/llmClient.ts:142` - parseJSON implementation
- `tests/e2e/caption-flow.spec.ts` - existing test (add failure case)
```

**CTO takes over from here.** Handler's job is done.

---

## Blocker Reporting

If Handler cannot complete diagnosis, report WHY:

### Insufficient Logging

```markdown
BLOCKER: Cannot diagnose autonomously.

**Gap:** No logging for caption generation failures.
The error "parse failed" is shown to users but the actual
LLM response that failed to parse is not captured.

**Required:** Implement audit_logs for LLM operations.
**Blocks:** All LLM-related bug diagnosis.
```

### No Reproduction Path

```markdown
BLOCKER: Cannot reproduce.

**Issue says:** "video-2 failed"
**Problem:**
- No content_entry_id provided
- Cannot identify which entry "video-2" refers to
- No test fixture for this scenario

**Required:** Either provide entry ID, or create E2E test fixture.
```

### Missing E2E Coverage

```markdown
BLOCKER: Cannot verify fix safely.

**Feature:** Bulk caption generation
**Problem:** No E2E tests exist for this feature.
I can diagnose but cannot confirm fix works without manual testing.

**Required:** E2E test for bulk caption generation.
```

### No Database Access

```markdown
BLOCKER: Cannot query logs.

**Logs exist in:** Vercel dashboard
**Problem:** No programmatic query access.

**Required:** Either:
- Database-backed logging (queryable via SQL)
- Log export API access
```

---

## Repository Requirements

For Handler to work, each repo needs:

### 1. Error Logging Infrastructure

| What to Log | Why |
|-------------|-----|
| Full input (request body, params) | Reproduce exact scenario |
| Full output (response, return) | See what actually happened |
| Error type and message | Classify failure |
| Stack trace | Locate code path |
| Timestamp | Correlate with reports |
| User/session ID | Find specific request |

**For LLM operations:**
- Full rendered prompt
- Raw LLM response (before parsing)
- Model identifier
- Token counts

### 2. Queryable Logs

Handler must be able to query, not just view in dashboard:
- Database table (preferred): `SELECT * FROM audit_logs WHERE...`
- Structured JSON files: grep-able
- Log aggregation API: If external service, provide query access

### 3. E2E Test Framework

- Tests runnable via CLI (`npm test`, `pytest`)
- Tests can create own test data
- Tests cover critical paths
- New tests can be added for specific bugs

### 4. Database Access

Handler needs read access to:
- Audit/error logs
- Related entities (what content entry failed?)
- Configuration (what settings were active?)

---

## Handler Modes

### Full Diagnosis (Default)

Complete workflow: assess → logs → reproduce → analyze → handoff.

```
"Diagnose issue #71"
```

### Quick Assessment

Just check if issue is diagnosable, don't do full investigation.

```
"Can we diagnose #71?" / "Is #71 actionable?"
```

Returns: diagnosable / blocked (with reason)

### Evidence Collection Only

Skip reproduction, just gather log evidence.

```
"Find logs for issue #71"
```

Useful when reproduction is known but need log correlation.

---

## What Handler Does NOT Do

| Not Handler's Job | Who Does It |
|-------------------|-------------|
| Scan full queue | Dispatcher |
| Write production fix | CTO Agent (Developer) |
| Run test suite | CTO Agent (QA Engineer) |
| Deploy | CTO Agent |
| Notify reporter | Bug Intake / QA Submission |
| Prioritize issues | Dispatcher |

Handler is the **investigator**, not the fixer or the traffic controller.

---

## Integration with CTO Agent

Handler prepares a **diagnosis package**. CTO Agent expects:

1. **Root cause** - What's actually broken
2. **Evidence** - Log entries, error messages
3. **Reproduction** - Test name or steps
4. **Suggested fix** - Optional but helpful
5. **Relevant files** - Where to look

CTO Agent then orchestrates:
- Developer implements fix
- QA Engineer reviews code + tests
- Integration Tester validates
- Completion Gate verifies all criteria
- QA Submission notifies reporter

Handler does NOT wait for CTO completion. Handoff is fire-and-forget (Dispatcher tracks overall status).

---

## Related Skills

| Skill | Location | Relationship |
|-------|----------|-------------|
| `autonomous-issue-dispatch` | `~/.claude/skills/` | Parent architecture — defines the full pipeline this skill belongs to |
| `issue-dispatcher` | `~/.claude/skills/` | **Upstream** — Dispatcher triages queue, invokes Handler per actionable issue |
| `strategic-cto-planner` | `~/.claude/agents/` | **Downstream** — Handler packages diagnosis, hands off to CTO Agent for implementation |
| `bug-intake` | `~/.claude/skills/` | **Indirect upstream** — Bug Intake creates issues that eventually reach Handler via Dispatcher |
| `qa-submission` | `.claude/skills/` (per-project) | **Downstream** (via CTO) — QA submission after CTO completes the fix |
