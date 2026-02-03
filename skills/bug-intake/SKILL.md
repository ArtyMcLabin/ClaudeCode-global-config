---
name: bug-intake
description: Generalized Slack bug intake. Scans bug-report channels, auto-fixes small bugs, defers big work. Uses emoji reactions to track state. Each repo provides workspace config via local bug-intake skill.
---

# Bug Intake (Generalized)

> **Part of:** Autonomous Issue Dispatch System
> See `~/.claude/skills/autonomous-issue-dispatch/SKILL.md` for full architecture.

## Purpose

Scan Slack channels for bug reports across **any workspace** and:
1. **Small bugs** -> Fix immediately, communicate result
2. **Big work** -> Create GitHub issue, defer to owner

This is the **generalized flow**. Each repo provides a local `.claude/skills/bug-intake/SKILL.md` with workspace config. Local skills extend this flow with `## Override:` sections — they never replace it.

**Trigger:** "Scan for bug reports" / "Run intake scan" / "Check bugs"

---

## Config Resolution (Inheritance Model)

1. Read the local `.claude/skills/bug-intake/SKILL.md` in the current repo
2. If no local skill exists -> error: "This repo has no bug-intake config."
3. Load this global skill as the **base flow**
4. Apply local skill as **override** — local sections marked `## Override:` augment or replace the corresponding global step
5. All non-overridden global steps execute as-is

**Think of it like C++ inheritance:** The global skill is the base class. Local skills call `super()` (use the global flow) and add their specific behavior on top. Local overrides never skip global steps — they extend them.

---

## Workspace Config Schema

Each repo's local bug-intake SKILL.md must provide these values in a markdown table:

| Key | Required | Description |
|-----|----------|-------------|
| Workspace | Yes | Human-readable workspace name |
| Slack domain | Yes | For permalink construction (e.g., `<workspace_a>` for `<workspace_a>.slack.com`) |
| Bug reports channel | Yes | Channel name and ID |
| QA channel | No | Separate QA channel (<PROJECT_C> only). Omit for in-thread QA. |
| QA mode | Yes | `in_thread` (default) or `separate_channel` (override) |
| GitHub repo | Yes | `owner/repo` format |
| Deploy mode | Yes | `auto-prod`, `auto-stage`, or `approval-required` (see Deployment Policy) |

**Token resolution:** The `~/.claude/skills/slack/SKILL.md` skill defines which token to use per workspace. This skill does NOT specify tokens — the Slack skill handles that.

### Optional: Repo Routing

When a workspace has multiple repos sharing one bug channel, the config includes keyword routing:

```
## Repo Routing
- "keyword1", "keyword2" -> owner/repo1
- "keyword3", "keyword4" -> owner/repo2
- default -> owner/repo3
```

The scan runs from ONE repo (the default), and routes issues to sibling repos based on keywords in the bug report.

---

## Generalized Flow

### Step 1: Load Config

```
Read local .claude/skills/bug-intake/SKILL.md
Extract workspace config table values
Resolve Slack token via ~/.claude/skills/slack/SKILL.md (workspace -> token mapping)
Check for ## Override: sections to apply after each global step
```

### Step 2: Scan for Unprocessed Messages

```bash
# Token resolved via slack skill (workspace -> token mapping)
curl -s "https://slack.com/api/conversations.history?channel=CHANNEL_ID&limit=50" \
  -H "Authorization: Bearer ${SLACK_TOKEN}"
```

**Unprocessed** = messages from humans (no `bot_id`) without any of these reactions: `:eyes:`, `:white_check_mark:`, `:hourglass:`

**Note:** `:white_check_mark:` messages are skipped here (new intake), but Step 9B re-checks their threads for follow-up replies that arrived after resolution. Resolved does not mean permanently ignored.

### Step 3: Mark as Processing

**IMMEDIATELY** add `:eyes:` reaction to prevent double-processing:

```bash
curl -s -X POST "https://slack.com/api/reactions.add" \
  -H "Authorization: Bearer ${SLACK_TOKEN}" \
  -H "Content-Type: application/json" \
  -d "{\"channel\":\"CHANNEL_ID\",\"timestamp\":\"MESSAGE_TS\",\"name\":\"eyes\"}"
```

### Step 4: Triage

**Small bug (fix immediately):**
- Clear error message or behavior
- Likely a single file fix
- No architectural changes

**Big work (ask approval):**
- Feature request disguised as bug
- Requires architectural changes
- Multiple systems affected
- Unclear scope

### Step 5: Route to Correct Repo

If config has `## Repo Routing`, match keywords in the bug report text against routing rules. If no match, use the default repo.

Create the GitHub issue in the matched repo:

```bash
gh issue create \
  --repo "OWNER/REPO" \
  --title "Bug: [Brief description]" \
  --body "## Bug Report

**Source:** Slack #CHANNEL_NAME
**Reporter:** @username
**Thread:** https://DOMAIN.slack.com/archives/CHANNEL_ID/pTIMESTAMP

## Description
[Content of the Slack message]

---
*Imported from Slack by bug-intake*"
```

### Step 6: Fix, Test, Deploy (Small Bugs)

**Autonomy rule:** Small bugs are auto-fixed without approval. No human sign-off needed — diagnose, fix, test, deploy, communicate.

**Pipeline:** Issue Handler (diagnose) → CTO Agent (implement) → Deploy

1. **Diagnose** via issue-handler: query logs, reproduce, build evidence package
2. **Hand off to CTO Agent** (`strategic-cto-planner`) — CTO orchestrates Developer, QA Engineer, Integration Tester. **Never dispatch directly to developer agent.**
3. **Run tests** — all existing tests must pass. If the fix touches testable logic, add or update tests. Tests must pass locally before any deployment.
4. **Deploy** according to the repo's `Deploy mode`:

| Deploy Mode | Behavior |
|-------------|----------|
| `auto-prod` | Deploy to production automatically after tests pass. No stage environment exists. |
| `auto-stage` | Push to stage/default branch automatically after tests pass. Stage can break — fast iteration. |
| `approval-required` | Tests must pass. Then present the fix + test results to the developer operating the loop. Deploy only after explicit approval. |

**TDD is non-negotiable.** Every fix must have passing tests before deployment, regardless of deploy mode. The difference is only *who approves the deploy* — the system or the human.

### Step 7: Communicate Result

**Universal rule:** Slack back-and-forth is only relevant when the bug reporter is NOT the person currently operating this Claude Code instance.

**Detection:** The person who invoked "scan for bugs" / "run intake" is the current operator. If the Slack message author matches, they're self-reporting.

#### Reporter IS the current operator

They reported a bug in Slack (e.g., from phone, or while chatting) and are now at the computer running Claude Code:
- Communicate directly in chat, NOT via Slack
- Add `:white_check_mark:` to Slack silently
- Tell the operator in chat: "Fixed [bug]. Deployed. You can verify at [URL]."

#### Reporter is NOT the current operator

Reply in the bug-report thread:

```bash
# Reply in thread
JSON=$(printf '{"channel":"%s","thread_ts":"%s","text":"%s"}' "CHANNEL_ID" "MESSAGE_TS" "Fix deployed. Please verify: [specific test steps]. Reply here if still broken.")

curl -s -X POST "https://slack.com/api/chat.postMessage" \
  -H "Authorization: Bearer ${SLACK_TOKEN}" \
  -H "Content-Type: application/json; charset=utf-8" \
  --data "$JSON"
```

If the fix is clear-cut and doesn't need reporter verification:
- Replace `:eyes:` with `:white_check_mark:`
- Reply: "Fixed and deployed. [brief description]"

If verification is needed, ask in-thread and keep `:eyes:` until confirmed (see Step 9).

#### `separate_channel` override

If the local skill has `QA mode: separate_channel` and `## Override:` sections, apply those overrides after the global steps above. The local override adds additional steps (e.g., QA submission to a dedicated channel) without skipping the base flow.

### Step 8: Big Work

1. Add `:hourglass:` reaction (instead of `:eyes:`)
2. Create GitHub issue
3. Reply in thread: "Noted — needs owner approval. Created issue #N for tracking."
4. Report to current operator in chat

### Step 9: Verification Loop

On subsequent scans, check two things:

**A. Threads with `:eyes:` (awaiting verification):**

- **Reporter confirms fix works** -> Close GitHub issue, replace `:eyes:` with `:white_check_mark:`
- **Reporter says still broken** -> Fix again, re-deploy, update thread, keep `:eyes:`
- **No response after 2 days** -> @mention the reporter in-thread asking for verification

**B. Threads with `:white_check_mark:` (resolved — reopened check):**

Scan threads of checkmarked messages for **new human replies posted AFTER the bot's last message**. This catches the case where someone replied with a follow-up bug in a thread we already marked as resolved.

If found:
1. Remove `:white_check_mark:`, add `:eyes:` (re-open for processing)
2. Read the new reply to understand the follow-up issue
3. Process as a new small bug (fix, test, deploy, communicate)
4. Log: "Reopened thread — follow-up bug reported after resolution"

**Why this matters:** Without this check, a resolved thread with a new reply is invisible to the scan (checkmark = skip). The reporter's follow-up gets lost.

This loop applies universally. Local overrides may add additional verification steps (e.g., separate QA channel) on top of this.

---

## Emoji State Machine (Universal)

| Emoji | Meaning | When to Add |
|-------|---------|-------------|
| `:eyes:` | **Processing lock** — claimed by a scan, prevents double-processing | Immediately on intake. Removed when resolved (replaced by `:white_check_mark:`) |
| `:white_check_mark:` | Resolved | Fix deployed and confirmed, or clear-cut fix deployed |
| `:hourglass:` | Deferred (big work, needs approval) | When triaged as big work |

**Unprocessed** = messages without any of these reactions.

`:eyes:` is a **mutex**, not a status indicator. It means "a scan has claimed this message." It stays until the fix is verified, then gets replaced by `:white_check_mark:`. If the fix is clear-cut (no verification needed), skip straight to `:white_check_mark:`.

### Lifecycle

```
New bug (clear-cut)          -> eyes -> fix -> deploy -> remove eyes, add checkmark
New bug (needs verification) -> eyes -> fix -> deploy -> keep eyes + "please verify"
                                            -> reporter confirms -> remove eyes, add checkmark
Big work                     -> hourglass + defer to owner
```

---

## Bidirectional Linking

Always maintain links between Slack and GitHub:
- **Slack -> GitHub:** Include Slack thread permalink in GitHub issue body
- **GitHub -> Slack:** Reply in Slack thread with GitHub issue URL after creation

```
Thread permalink format:
https://{domain}.slack.com/archives/{channel_id}/p{ts_without_dot}
```

---

## Related Skills

| Skill | Location | Relationship |
|-------|----------|-------------|
| `autonomous-issue-dispatch` | `~/.claude/skills/` | Parent architecture — defines the full pipeline |
| `issue-dispatcher` | `~/.claude/skills/` | **Downstream** — Dispatcher triages issues created by Bug Intake |
| `dev-loop` | `~/.claude/skills/` | **Wrapper** — Dev Loop runs Bug Intake repeatedly in 5-min intervals |
| `slack` | `~/.claude/skills/` | API patterns, error handling for all Slack operations |
| `qa-submission` | `.claude/skills/` (per-project) | Separate QA channel submission after fix |
