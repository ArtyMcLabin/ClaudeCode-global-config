# Bug Intake — Design Decisions & Philosophy

Reference document for the bug-intake skill. Captures architectural rationale and operator-level philosophy so reworks don't re-debate settled decisions.

---

## 1. No Auto-Closure (Non-Negotiable)

When a reporter doesn't respond to verification requests, the system **never** auto-closes the issue or removes `:eyes:`. Reporter non-response is a human problem, not a system gap.

**Rationale:** Auto-closure assumes silence = working. That assumption is wrong often enough to be dangerous — the reporter may be busy, on vacation, or simply forgot. A false "resolved" is worse than a stale thread.

**What happens instead:**
- First @mention at 2 days
- Second @mention at 7 days (final nudge)
- After that: accept as permanent state, report under Tier 1 (Auto-handled / FYI)

---

## 2. Verification Loop is Periodic, Not Passive

Step 9 (Verification Loop) runs every time Phase 2 runs — currently twice daily (morning + evening). Reporter responses are picked up at the next Phase 2 run, within 12 hours max.

**This is not a gap.** 12-hour latency is acceptable for non-CF repos. Only <PROJECT_C> has a continuous dev-loop (5-min rescan) because of its high throughput and dedicated QA person. Other repos (<PROJECT_B>, GR) use Phase 2 frequency by design.

**If this latency becomes problematic for a repo:** The fix is to add a dev-loop dispatch script for that repo (like `dispatch-cf-devloop.ps1`), not to change the verification architecture.

---

## 3. Morning Report Triage Rules

Items go in **Tier 1 (Auto-handled)** or **Tier 2 (Needs you)** based on one test:

> "Can the autonomous system act on this without the operator?"

| Scenario | Tier | Why |
|----------|------|-----|
| New bugs picked up by dev-loop | Tier 1 | Dev-loop handles autonomously |
| Reporter confirmed fix in thread | Tier 1 | Next Phase 2 closes it |
| Reporter said "yes, do it" confirming fix direction | Tier 1 | System applies the fix |
| Stale unverified threads (post-second @mention) | Tier 1 | Accepted permanent state |
| Merge conflict in application code | Tier 2 | Requires human judgment |
| Big work needing approval | Tier 2 | `approval-required` deploy mode |
| QA backlog overdue items (count + oldest) | Tier 2 | Only human can follow up with QA person |
| Branch mismatch | Tier 2 | Human decides which branch is correct |

**Anti-pattern:** Reporting autonomous items under "Needs you" creates noise. The operator stops reading Tier 2 if it's full of things they don't need to act on.

---

## 4. Phase 2 Completion Gate

Phase 2 is NOT complete until every channel from the Shared Channel Registry + repo-local overrides has been scanned. The operator must output a per-channel scan summary before declaring Phase 2 done.

**Required output format after Phase 2:**

```
Phase 2 scan results:
  [workspace] #channel-name: N unprocessed, N new issues created, N verification updates
  [workspace] #channel-name: clean
  ...
```

Any channel missing from this list = Phase 2 is incomplete. Do not proceed to Phase 3 without full coverage.

**Why this exists:** Prevents fabricated scan results. If a channel wasn't actually scanned via API, it cannot appear in the summary. The format forces explicit accountability per channel.

---

## 5. Stale Uncommitted Reporting

"15d uncommitted" alone is ambiguous — could mean a forgotten repo with zero activity, or an active repo where a few files were never staged.

**Required format:** Include last commit date alongside uncommitted age.

| Format | Meaning |
|--------|---------|
| `15d uncommitted, no commits` | Truly forgotten — no git activity at all |
| `15d uncommitted, last commit 2d ago` | Active repo, some files lingering |
| `15d uncommitted, last commit 15d ago` | Stale — both uncommitted and no commits |

This disambiguation lets the operator prioritize correctly without investigating each repo.

---

## 6. <PROJECT_C> Dev-Loop is an Exception, Not the Standard

Only <PROJECT_C> has a continuous dev-loop. This is intentional:
- CF has high bug throughput + dedicated QA person (<TEAMMATE>)
- CF uses `auto-prod` deploy mode — fixes go live immediately
- Other repos use `approval-required` — continuous scanning adds little value when fixes need human sign-off anyway

**Do not treat the absence of dev-loops in other repos as an architectural gap.** The Phase 2 twice-daily scan is the standard. Dev-loops are added per-repo based on throughput needs.

---

## 7. Fabrication Prevention

The operator (GH_Coordinator Claude instance) must never report scan results for channels it didn't actually scan. If a channel scan fails or is skipped, report it as "not scanned" — never invent results.

**Root cause of past fabrication:** Dispatching fewer subagents than channels, then filling in the report with assumed data. The Phase 2 completion gate (section 4) prevents this by requiring per-channel evidence.
