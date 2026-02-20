---
name: bug-intake
description: Generalized Slack bug intake. Scans bug-report channels, auto-fixes small bugs, defers big work. Uses emoji reactions to track state. Each repo provides workspace config via local bug-intake skill. Supports shared channels where multiple repos receive bugs from one Slack channel via semantic routing.
user-invocable: false
---

# Bug Intake (Generalized)

> **Part of:** Autonomous Issue Dispatch System
> See `~/.claude/skills/autonomous-issue-dispatch/SKILL.md` for full architecture.

## Purpose

Scan Slack channels for bug reports across **any workspace** and:
1. **Small bugs** -> Fix immediately, communicate result
2. **Big work** -> Create GitHub issue, defer to owner

This is the **generalized flow**. Each repo provides a local `.claude/skills/bug-intake-override/SKILL.md` with workspace config. Local skills extend this flow with `## Override:` sections — they never replace it.

**Trigger:** "Scan for bug reports" / "Run intake scan" / "Check bugs"

---

## Single-Thread Mode (Real-Time Trigger)

When invoked with a `thread_ts` parameter, process ONLY that specific thread instead of scanning the full channel. Used by the Slack Event Daemon for real-time bug response.

**Trigger:** "Run bug-intake in single-thread mode for thread_ts=X in channel Y"

**Behavior differences from full scan:**

| Aspect | Full Scan | Single-Thread |
|--------|-----------|---------------|
| Scope | All unprocessed messages in channel | One specific thread only |
| Emoji check | Scan skips messages with emoji | Daemon already added `👀` + `⚡` before dispatch |
| Step 2 | `conversations.history` | `conversations.replies?channel=CH&ts=THREAD_TS` |
| Step 9 | Check all `👀` and `✅` threads | Skip — only the triggered thread |

**Flow:** Receive thread_ts + channel → fetch thread via `conversations.replies` → read all messages for context → triage (Step 4) → route (Step 5) → fix/deploy or defer (Step 6/8) → communicate (Step 7).

The `⚡` emoji indicates real-time daemon trigger (vs `👀` alone from cron). Functionally identical — observability only.

**Deduplication:** Daemon adds `👀` before dispatch. Cron sees `👀` and skips. No conflict.

---

## Config Resolution (Inheritance Model)

1. Read the local `.claude/skills/bug-intake-override/SKILL.md` in the current repo
2. If no local skill exists -> error: "This repo has no bug-intake config."
3. Load this global skill as the **base flow**
4. Apply local skill as **override** — local sections marked `## Override:` augment or replace the corresponding global step
5. All non-overridden global steps execute as-is

**Think of it like C++ inheritance:** The global skill is the base class. Local skills call `super()` (use the global flow) and add their specific behavior on top. Local overrides never skip global steps — they extend them.

---

## Workspace Config Schema

Each repo's local bug-intake-override SKILL.md must provide these values in a markdown table:

| Key | Required | Description |
|-----|----------|-------------|
| Workspace | Yes | Human-readable workspace name |
| Slack domain | Yes | For permalink construction (e.g., `<WORKSPACE>` for `<WORKSPACE>.slack.com`) |
| Bug reports channel | Yes | Channel name and ID |
| QA channel | No | Separate QA channel (<PROJECT_C> only). Omit for in-thread QA. |
| QA mode | Yes | `in_thread` (default) or `separate_channel` (override) |
| GitHub repo | Yes | `owner/repo` format |
| Deploy mode | Yes | `auto-prod`, `auto-stage`, or `approval-required` (see Deployment Policy) |

**Token resolution:** The `~/.claude/skills/slack/SKILL.md` skill defines which token to use per workspace. This skill does NOT specify tokens — the Slack skill handles that.

### Optional: Repo Routing (Legacy -- Single-Repo Config)

When a workspace has multiple repos sharing one bug channel, the local config can include keyword routing:

```
## Repo Routing
- "keyword1", "keyword2" -> owner/repo1
- "keyword3", "keyword4" -> owner/repo2
- default -> owner/repo3
```

The scan runs from ONE repo (the default), and routes issues to sibling repos based on keywords in the bug report.

For shared channels with semantic routing, use the Shared Channel Registry below instead. Legacy keyword routing is kept for backward compatibility.

---

## Shared Channel Registry

When one Slack channel serves multiple repos (e.g., a company-wide `#bugs` channel), routing is defined here at the global level. Claude reads each bug report and **semantically understands** which repo(s) it belongs to -- no keyword matching.

### <COMPANY_A> HQ -- #bugs (`<CHANNEL_ID>`)

**Workspace:** <COMPANY_A> HQ | **Slack domain:** `<WORKSPACE>`

| Repo | Local Path | GitHub | Handles | Deploy Mode |
|------|-----------|--------|---------|-------------|
| <REPO_NAME> | `<LOCAL_PATH>\<REPO_NAME>` | `<GITHUB_USER>/CS_AI` | AI chatbot responses, auto-replies, n8n workflows, customer service bot behavior, AI knowledge base accuracy, Respond.io integration | `auto-prod` |
| <REPO_NAME> | `<LOCAL_PATH>\<REPO_NAME>` | `<GITHUB_USER>/<REPO_NAME>` | WordPress dashboard (logged-in users only), user registration/login, payment processing backend, CRM, Respondio/WhatsApp integrations, automations, Trello powerups, mentor management, trial lesson scheduling, admin tools | `approval-required` |
| <REPO_NAME> | `<LOCAL_PATH>\<REPO_NAME>` | `<GITHUB_USER>/<REPO_NAME>` | ALL public-facing pages (logged-out users), Next.js site, Payload CMS, landing pages, pricing pages, website UI/UX, SEO, course/learning path content, instructor profiles, portfolio, blog, testimonials, FAQ, multi-language (EN/HE), media optimization | `approval-required` |
| <REPO_NAME> | `<LOCAL_PATH>\<REPO_NAME>` | `<COMPANY_A>-Studio/sops-docusaurus` | Internal documentation site, SOPs, procedures, onboarding docs, Docusaurus static site, knowledge base content | `approval-required` |
| <REPO_NAME> | `<LOCAL_PATH>\<REPO_NAME>` | `<COMPANY_A>-Studio/<REPO_NAME>` | Internal Chrome extension for GR staff workflows, productivity tools, browser-based work utilities | `approval-required` |

### <PROJECT_B> -- #bugs-general (`<CHANNEL_ID>`)

**Workspace:** <PROJECT_B> | **Slack domain:** `<WORKSPACE_B>`

| Repo | Local Path | GitHub | Handles | Deploy Mode |
|------|-----------|--------|---------|-------------|
| <REPO_NAME> | `<LOCAL_PATH>\<REPO_NAME>` | `<GITHUB_USER>/<REPO_NAME>` | WhatsApp AI assistant, message handling, AI response quality, conversation history, authorized user auth, group chat interactions, media processing, bot commands (/summarize), OpenRouter API, Supabase user authorization | `approval-required` |
| <PROJECT_B>_Website | `<LOCAL_PATH>\<PROJECT_B>_Website` | `<GITHUB_USER>/<PROJECT_B>_Website` | SaaS dashboard, user authentication, organization/team management, group chat associations, user invitations, billing, settings, password reset, email verification, role-based permissions, data source imports | `approval-required` |

**Note:** `<REPO_NAME>-schema` is a shared dependency — never create issues there directly. Issues belong in <REPO_NAME> or <PROJECT_B>_Website; schema changes happen as part of fixing those issues.

### <PROJECT_B> -- #hook-problem-reports (`<CHANNEL_ID>`)

**Workspace:** <PROJECT_B> | **Slack domain:** `<WORKSPACE_B>`

Same repo routing as #bugs-general above. This channel captures webhook/integration failures specific to the bot's hook system.

### Semantic Routing Rules

1. **Read the full bug report** -- understand what system/feature is affected, not just surface keywords
2. **Match against "Handles" descriptions** -- which repo's domain covers the reported issue?
3. **Single-repo bugs (most common):** Create issue in the matched repo only
4. **Cross-repo bugs:** When a bug spans multiple systems (e.g., "chatbot sends wrong payment link" = CS_AI response + site payment page), create issues in ALL affected repos with cross-references:
   ```
   ## Cross-Reference
   Related issues: <GITHUB_USER>/CS_AI#N, <GITHUB_USER>/<REPO_NAME>#N
   ```
5. **Ambiguous bugs:** If genuinely unclear which repo handles it, create the issue in the most likely repo and add a `needs-triage` label. Mention the ambiguity in the issue body.
6. **Unknown repos:** If the bug doesn't match any repo in the registry, report it to the operator: "Bug about [X] doesn't match any registered repo. Skip or create in [suggested repo]?"

### Dispatch Behavior (GH_Coordinator)

GH_Coordinator is the for-loop wrapper — it runs the same bug-intake flow across multiple repos. The effect must be identical to running bug-intake from inside each repo individually.

**Step A: Scan Shared Channel Registry** (multi-repo channels above)
1. Scan each registered channel for unprocessed messages (same as Step 2)
2. For each message, determine target repo(s) via semantic routing
3. Mark as processing (`:eyes:`) immediately
4. Create GitHub issue in the matched repo(s) per Step 5

**Step B: Discover repo-local overrides**
1. For each repo in the registry, check if `{local_path}/.claude/skills/bug-intake-override/SKILL.md` exists
2. If it does, read its Workspace Config table — it may define additional channels not in the Shared Channel Registry
3. Scan those channels using the local override's rules (QA mode, emoji nuances, communication overrides, etc.)
4. Apply all `## Override:` sections from the local skill on top of the global flow

**Result:** Repos without local overrides get the global flow only. Repos with overrides (e.g., separate QA channels, custom communication steps) get the full augmented flow — discovered automatically, never hardcoded.

**CS_AI special rule:** External dispatch only — handle the Slack-routed issue, do NOT auto-trigger sheet scanning

---

## Generalized Flow

### Step 1: Load Config

```
Read local .claude/skills/bug-intake-override/SKILL.md
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

**Shared channel (registry exists):** Use the Shared Channel Registry above. Semantically match the bug report against repo "Handles" descriptions. See "Semantic Routing Rules" for single-repo, cross-repo, and ambiguous cases.

**Single-repo channel (legacy):** If config has `## Repo Routing`, match keywords in the bug report text against routing rules. If no match, use the default repo.

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
- **No response after 2 days** -> 🚨 First run **QA Backlog Auditing** (below) to verify they genuinely haven't responded (check emoji states + thread replies). Only then @mention the reporter in-thread asking for verification
- **No response after 7 days** (5 days after first @mention) -> Send second @mention: "Following up — this fix is still pending your verification. Please test when you can." This is the final nudge.
- **After second @mention with no response** -> Accept as permanent state. `:eyes:` stays. Report as "stale unverified" in morning reports under Tier 1 (Auto-handled), not Tier 2. No auto-closure ever. See `references/design-decisions.md` for rationale.

**B. Threads with `:white_check_mark:` (resolved — reopened check):**

Scan threads of checkmarked messages for **new human replies posted AFTER the bot's last message**. This catches the case where someone replied with a follow-up bug in a thread we already marked as resolved.

If found:
1. Remove `:white_check_mark:`, add `:eyes:` (re-open for processing)
2. Read the new reply to understand the follow-up issue
3. Process as a new small bug (fix, test, deploy, communicate)
4. Log: "Reopened thread — follow-up bug reported after resolution"

**Why this matters:** Without this check, a resolved thread with a new reply is invisible to the scan (checkmark = skip). The reporter's follow-up gets lost.

**C. Threads with `:hourglass:` (big work — owner response check):**

Scan `:hourglass:` threads for new owner replies (replies without bot `:eyes:` reaction):

- **Owner approved** → Remove `:hourglass:`, route to implementation (CTO Agent). Add `:eyes:` to owner's reply.
- **Owner answered questions** → Update GitHub issue with answers. Add `:eyes:` to reply. Re-evaluate: if scope is now clear and small, implement. If still big, keep deferred with updated context.
- **Owner declined** ("not now", "backlog", "later") → Keep `:hourglass:`. Add `:eyes:` to reply. Log: "Owner deferred #N."
- **No response** → No action (deadline rules per local override).

This loop applies universally. Local overrides may add additional verification steps (e.g., separate QA channel) on top of this.

---

## Emoji State Machine (Universal)

| Emoji | Meaning | When to Add |
|-------|---------|-------------|
| `:eyes:` | **Processing lock** — claimed by a scan, prevents double-processing | Immediately on intake. Removed when resolved (replaced by `:white_check_mark:`) |
| `:white_check_mark:` | Resolved | Fix deployed and confirmed, or clear-cut fix deployed |
| `:hourglass:` | Deferred (big work, needs approval) | When triaged as big work |

**Unprocessed** = messages without any of these reactions.

**Thread reply emojis** (prevents double-processing):

| Emoji | On What | Meaning |
|-------|---------|---------|
| `:eyes:` | Individual thread reply | This reply has been read and acted upon |

When scanning threads, skip replies that already have `:eyes:` from the bot. Only process new (unreacted) human replies.

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

---

## QA Backlog Auditing

When auditing pending-qa issues against Slack QA channel:

**Always check reaction state before reporting backlog.** A QA submission with `:white_check_mark:` reaction means it was auto-closed — <TEAMMATE>'s reply is NOT expected.

**Audit procedure:**
1. Get list of GitHub issues with `pending-qa` label
2. For each corresponding Slack QA thread, check:
   - Does thread have `:white_check_mark:` reaction? → Auto-closed, not waiting
   - Does thread have replies from <TEAMMATE> (non-bot user)? → Responded
   - Neither? → **Genuinely waiting**
3. Report only genuinely waiting items as backlog
4. Clean up: Remove `pending-qa` label from closed GitHub issues

**Common false positive:** Reporting all pending-qa issues as "waiting" without checking which Slack threads have checkmarks.

**Trust past closures:** Issues that were closed before the current scan session are trusted by default. Do NOT raise alarms about missing QA trail on pre-existing closures. Past ad-hoc decisions to skip QA or close without full process were made with context you don't have — trust them. Only re-examine if there's an active red flag (regression reported, new complaint, reopened by user).

---

## References

- `references/design-decisions.md` — Architectural rationale, operator philosophy, report triage rules, no-auto-closure policy. Read before proposing changes to verification logic or reporting format.

## Related Skills

| Skill | Location | Relationship |
|-------|----------|-------------|
| `autonomous-issue-dispatch` | `~/.claude/skills/` | Parent architecture — defines the full pipeline |
| `issue-dispatcher` | `~/.claude/skills/` | **Downstream** — Dispatcher triages issues created by Bug Intake |
| `dev-loop` | `~/.claude/skills/` | **Wrapper** — Dev Loop runs Bug Intake repeatedly in 5-min intervals |
| `slack` | `~/.claude/skills/` | API patterns, error handling for all Slack operations |
| `qa-submission` | `.claude/skills/` (per-project) | Separate QA channel submission after fix |
