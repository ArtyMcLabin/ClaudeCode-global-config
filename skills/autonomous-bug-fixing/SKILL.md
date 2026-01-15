---
name: autonomous-bug-fixing
description: SOP for autonomous bug detection, diagnosis, and fixing without human intervention. Use when treating GitHub issues or when assessing repository readiness for autonomous maintenance.
---

# Autonomous Bug Fixing - Standard Operating Procedure

## Philosophy

**Goal:** Claude Code should be able to receive a bug report, diagnose it, fix it, test it, and push the fix - all without human intervention.

**Reality:** Most bug reports are vague. Users say "it broke" not "the JSON parser failed on line 42 because the LLM returned markdown instead of raw JSON."

**Solution:** Don't rely on detailed bug reports. Build infrastructure that lets Claude Code self-diagnose:
- **Comprehensive logging** that captures inputs, outputs, and errors
- **E2E tests** that can reproduce and verify fixes
- **Queryable error trails** so Claude Code can investigate

## The Workflow

```
┌─────────────────────────────────────────────────────────────────┐
│  User/Tester                                                    │
│  "Caption generation broke on my video"                         │
└─────────────────────┬───────────────────────────────────────────┘
                      │ email
                      ▼
┌─────────────────────────────────────────────────────────────────┐
│  Personal Assistant AI                                          │
│  Creates GitHub issue from email                                │
│  (Basic info: what failed, when, any error message shown)       │
└─────────────────────┬───────────────────────────────────────────┘
                      │ GitHub issue
                      ▼
┌─────────────────────────────────────────────────────────────────┐
│  Repository Claude Code (this skill)                            │
│  1. Read issue                                                  │
│  2. Query logs to find actual error                             │
│  3. Reproduce via E2E test                                      │
│  4. Fix the code                                                │
│  5. Run E2E to verify                                           │
│  6. Push to master                                              │
│  7. Close issue with explanation                                │
└─────────────────────────────────────────────────────────────────┘
```

## Repository Requirements

For autonomous bug fixing to work, each repository needs:

### 1. Error Logging Infrastructure

**Principle:** Every operation that can fail should log enough context to diagnose WHY it failed.

| What to Log | Why |
|-------------|-----|
| Full input (request body, parameters) | Reproduce the exact scenario |
| Full output (response, return value) | See what actually happened |
| Error type and message | Classify the failure |
| Stack trace | Locate the code path |
| Timestamp | Correlate with user reports |
| User/session ID | Find the specific failing request |

**For AI/LLM operations specifically:**
- Full rendered prompt sent
- Raw LLM response received
- Parse success/failure
- Parse error details if failed

### 2. E2E Test Coverage

**Principle:** If it can break, there should be a test that exercises it.

E2E tests serve dual purposes:
1. **Reproduction** - Create the failing scenario programmatically
2. **Verification** - Confirm the fix works

Tests should:
- Create their own test data (no external dependencies)
- Cover both happy path and known failure modes
- Be runnable via CLI (`npm test`, `pytest`, etc.)

### 3. Queryable Logs

Logs must be queryable by Claude Code, not just visible in dashboards.

Options by tech stack:
- **Database table** (preferred) - `SELECT * FROM error_logs WHERE...`
- **Structured log files** - JSON logs that can be grepped
- **Log aggregation API** - If using external service, provide query access

### 4. Direct Database Access

Claude Code needs to query:
- Error/audit logs
- Related entities (what content entry failed?)
- Configuration (what settings were active?)

Provide read access credentials or CLI tools.

## Autonomous Fix Procedure

When treating a GitHub issue:

### Step 1: Assess Information Sufficiency

```
Can I answer these questions?
├── WHAT failed? (which feature/endpoint)
├── WHEN did it fail? (timestamp or recency)
├── WHO experienced it? (user/session ID)
└── Any ERROR shown to user?
```

If basic info is missing, check if logs can fill the gaps.

### Step 2: Query Logs

```sql
-- Example: Find recent failures
SELECT * FROM error_logs
WHERE feature = 'caption_generation'
  AND status = 'error'
  AND created_at > NOW() - INTERVAL '24 hours'
ORDER BY created_at DESC;
```

Look for:
- The specific failing request
- The actual error (not user-reported symptoms)
- Patterns (is it one user or everyone? one input type or all?)

### Step 3: Reproduce

Write or run E2E test that triggers the bug:

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

If reproduction fails (can't trigger the bug), report this as a blocker.

### Step 4: Fix

Apply minimal fix that addresses root cause. Common patterns:

| Error Type | Typical Fix |
|------------|-------------|
| Parse error | Add defensive parsing, handle edge cases |
| Null/undefined | Add null checks, validate inputs |
| Timeout | Add retry logic, increase timeout |
| Auth error | Check token refresh, permissions |
| Rate limit | Add backoff, queue requests |

### Step 5: Verify (TDD Gate)

**Tests MUST pass before ANY commit.**

Run the reproduction test - it should now pass.
Run full E2E suite - ensure no regressions.

### Step 6: Push, Verify Deploy, Close

```bash
git add .
git commit -m "fix: Handle edge case in caption parsing (#123)

Root cause: LLM occasionally returns markdown-wrapped JSON.
Added detection and stripping of markdown code fences.

Closes #123

Co-Authored-By: Claude Opus 4.5 <noreply@anthropic.com>"
git push origin master
```

**Verify deployment succeeded** (check repo's CLAUDE.md for platform):

| Platform | Verification |
|----------|--------------|
| Vercel | `vercel ls` -> wait for "Ready" |
| AWS/GCP | Check deployment status via CLI |
| Self-hosted | Verify health endpoint responds |

**Only after deployment is confirmed:**
```bash
gh issue close 123 --comment "Fixed in [commit]. Deployed and verified."
```

## Reporting Blockers

If autonomous fixing is NOT possible, report WHY in the issue:

### Blocker Types

**Insufficient Logging**
```
BLOCKER: Cannot diagnose this issue autonomously.

Missing: No logging for caption generation failures.
The error "parse failed" is shown to users but the actual
LLM response that failed to parse is not captured.

Required: Implement generation_logs table (see issue #10)
```

**No Reproduction Path**
```
BLOCKER: Cannot reproduce this issue.

The bug report says "video-2 failed" but:
- No content_entry_id provided
- Cannot identify which entry "video-2" refers to
- No test fixture exists for this scenario

Required: Either provide entry ID, or add E2E test that
creates similar content and triggers generation.
```

**Missing E2E Coverage**
```
BLOCKER: Cannot verify fix safely.

The failing feature (bulk caption generation) has no E2E tests.
I can write a fix but cannot confirm it works without manual testing.

Required: E2E test for bulk caption generation flow.
```

**No Database Access**
```
BLOCKER: Cannot query error logs.

Error logs exist in [Vercel/Datadog/etc] but I don't have
query access. Cannot investigate root cause.

Required: Either provide log query access, or implement
database-backed logging that I can query via SQL.
```

## Repository Readiness Checklist

Use this to assess if a repo is ready for autonomous bug fixing:

```
[ ] Error logging captures full context (inputs, outputs, errors)
[ ] Logs are queryable (database table or structured files)
[ ] E2E tests exist for critical paths
[ ] E2E tests can be run via CLI
[ ] Database credentials available for log queries
[ ] Git push access to main branch
[ ] CI/CD runs tests before deploy
```

## Tech-Stack-Agnostic Principles

This SOP applies regardless of stack. Implementations vary:

| Principle | Node/JS | Python | Go |
|-----------|---------|--------|----|
| Error logging | Winston/Pino + DB | logging + SQLAlchemy | zerolog + GORM |
| E2E tests | Playwright/Jest | pytest | go test |
| Query logs | Drizzle/Prisma | SQLAlchemy | database/sql |

The concepts remain constant:
1. Log everything needed to diagnose
2. Make logs queryable
3. Have tests that can reproduce
4. Verify fixes before pushing

## Continuous Improvement

After fixing a bug autonomously, consider:

1. **Add E2E test** for this specific failure mode
2. **Improve logging** if diagnosis was difficult
3. **Update error messages** shown to users (more specific = better reports)
4. **Document pattern** if it's a recurring issue type

Each bug fixed makes the next one easier.

---

# Implementation Guide

## Setting Up a New Repository

When tasked with making a repository ready for autonomous bug fixing:

### Step 1: Discover the Stack

Before implementing anything, understand:
- Language/framework?
- Database type? (SQL, NoSQL, file-based, none?)
- Existing test framework?
- Existing logging solution?
- Deployment method?

Read CLAUDE.md, dependency files, and project structure first.

### Step 2: Gap Analysis

Assess and create GitHub issues for each gap:

```
LOGGING INFRASTRUCTURE
[ ] Is there centralized error/audit logging?
[ ] Does it capture: input, output, error, timestamp, entity IDs?
[ ] For AI/LLM features: are prompts and responses logged?
[ ] Can Claude Code query it? (not just view in dashboard)

E2E TEST COVERAGE
[ ] Is a test framework configured?
[ ] What critical paths have tests?
[ ] What critical paths are MISSING tests?
[ ] Can tests run via single CLI command?

DATABASE/LOG ACCESS
[ ] Can Claude Code connect and query?
[ ] What credentials/tools are available?

CI/CD
[ ] Are tests run before deploy?
[ ] Can Claude Code push to main/master or need PR?
```

### Step 3: Implement Logging

**Required data points (storage mechanism varies by stack):**

| Field | Purpose |
|-------|---------|
| operation_type | Category: 'api', 'llm', 'job', etc. |
| operation_name | Specific: 'generate_captions', 'send_email' |
| entity_type + entity_id | What record this relates to |
| user_id / org_id | Who triggered it |
| request_data | Full input |
| status | 'success', 'error', 'timeout', etc. |
| response_data | Full output (on success) |
| error_message | Human-readable error |
| error_details | Stack trace, raw error |
| duration_ms | How long it took |
| timestamp | When |

**For AI/LLM operations, also capture:**
- Full rendered prompt (system + user)
- Raw response (before parsing)
- Model identifier
- Token counts

**Integration approach:** Use a wrapper/decorator/middleware pattern appropriate to the language. Don't scatter logging calls - centralize them.

### Step 4: Add E2E Tests

**Prioritize tests for:**
1. Features users complain about
2. External service integrations (APIs, LLMs, payments)
3. Complex logic with multiple failure modes

**Each test should:**
- Create its own test data
- Exercise the operation
- Assert success case
- Have variant(s) for failure modes
- Clean up after

### Step 5: Document in CLAUDE.md

Add to the repo's CLAUDE.md:

```markdown
## Autonomous Bug Fixing Readiness

### Logging
- **Storage:** [where logs live]
- **Query command:** [how to query failures]

### E2E Tests
- **Run all:** [command]
- **Run specific:** [command]

### Database Access
- **Connection:** [how]
- **Query tool:** [what]

### Critical Paths Covered
- [x] [covered feature]
- [ ] [TODO feature]
```

---

## Maintenance Mode

When invoked to check and treat issues:

### Daily Maintenance Sequence

1. **List open issues:**
   ```
   gh issue list --state open --json number,title,createdAt,labels
   ```

2. **For each issue:**
   - Enough info to diagnose?
   - Can query logs for context?
   - Can reproduce via E2E?

3. **Take action:**
   - Fixable → Fix, test, push, close
   - Blocked → Comment with blocker
   - Needs info → Comment with questions

4. **Report summary:**
   ```
   Issues processed: X
   - Fixed: [list]
   - Blocked: [list with reasons]
   - Needs info: [list]
   ```

### Infrastructure Gap Issues

When blocked by missing infrastructure, create issue:

```markdown
## Infrastructure Gap: [Type]

**Context:** Blocked while attempting issue #X

**Gap:** [What's missing]

**Required:**
- [What to implement]
- [Acceptance criteria]

**Blocks:** [Category of bugs this affects]
```
