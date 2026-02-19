---
name: slack
description: ALL Slack operations. Use for ANY task involving Slack - messages, channels, members, workspaces, invites, permissions, history, reactions, threads, DMs, bots, apps, settings. If the word "Slack" appears in the request, use this skill.
user-invocable: false
---

# Slack Messaging

**Purpose:** Send Slack messages via API (channels, DMs, notifications).

**Credential location:** `~/.claude/.env` (gitignored) - contains workspace tokens.

**References:**
- `references/workspace-setup.md` - Workspace configs, domain auto-join, bot capabilities, full scope list

🚨 **API first:** Use Slack API (curl) for ALL messaging operations. Chrome-agent only for admin UI actions (workspace settings, user invites on non-Enterprise plans).

🚨 **Slack URLs → parse and use API, NEVER navigate in browser.** When you encounter a Slack URL, extract the channel and timestamp and use the API:
```
URL: https://{workspace}.slack.com/archives/{CHANNEL_ID}/p{TS_NO_DOT}?thread_ts={THREAD_TS}&cid={CHANNEL_ID}
  → channel = CHANNEL_ID (e.g., <CHANNEL_ID>)
  → ts = THREAD_TS (e.g., 1771393596.062309)
  → API: conversations.replies?channel={CHANNEL_ID}&ts={THREAD_TS}
```
This applies even when URLs come from email, GitHub issues, or other external sources. A Slack URL is a Slack operation, not a browser operation.

🚨 **Blast radius check for app-level changes:** Before modifying ANY Slack app setting at api.slack.com (Socket Mode, Event Subscriptions, scopes, Request URL), MUST read `references/workspace-setup.md § PA Bot App Dependencies` to check all consumers. Changes like enabling Socket Mode silently disable HTTP event delivery, breaking other systems.

## Authentication (Browser)

**🚨 All Slack workspaces use `<YOUR_EMAIL>`** — this is the admin account and the active user across ALL workspaces.

- **Never use** `ceo@yourcompany.com` or any work domain email for Slack browser login
- Work domain emails may exist as dummy/integration users in some workspaces — they are NOT the admin and NOT the active user
- When chrome-agent needs Slack login, always authenticate with `<YOUR_EMAIL>`

---

## Quick Start

```bash
# 1. Load token from global .env
source ~/.claude/.env

# 2. Choose workspace token
export SLACK_TOKEN="$SLACK_<WORKSPACE_B>_TOKEN"    # or SLACK_<WORKSPACE_A>_TOKEN, etc.

# 3. Send message
curl -X POST "https://slack.com/api/chat.postMessage" \
  -H "Authorization: Bearer ${SLACK_TOKEN}" \
  -H "Content-Type: application/json; charset=utf-8" \
  --data '{"channel":"#channel-name","text":"Your message here"}'
```

---

## API Patterns

### Send to Channel

```bash
curl -X POST "https://slack.com/api/chat.postMessage" \
  -H "Authorization: Bearer ${SLACK_TOKEN}" \
  -H "Content-Type: application/json; charset=utf-8" \
  --data '{"channel":"#channel-name","text":"Message text"}'
```

**🚨 After posting, ALWAYS provide message link to user:**
```
https://{workspace}.slack.com/archives/{channel_id}/p{ts_without_dot}
```
- `ts` from response: `1769193392.153219` → remove dot → `p1769193392153219`
- Example: `https://<WORKSPACE>.slack.com/archives/<CHANNEL_ID>/p1769193392153219`

### Send DM to User

```bash
curl -X POST "https://slack.com/api/chat.postMessage" \
  -H "Authorization: Bearer ${SLACK_TOKEN}" \
  -H "Content-Type: application/json; charset=utf-8" \
  --data '{"channel":"@username","text":"Direct message"}'
```

### Send with Formatting (Blocks)

```bash
curl -X POST "https://slack.com/api/chat.postMessage" \
  -H "Authorization: Bearer ${SLACK_TOKEN}" \
  -H "Content-Type: application/json; charset=utf-8" \
  --data '{
    "channel": "#channel-name",
    "blocks": [
      {"type": "header", "text": {"type": "plain_text", "text": "Header"}},
      {"type": "section", "text": {"type": "mrkdwn", "text": "*Bold* and _italic_"}}
    ]
  }'
```

---

## Error Handling

### `not_in_channel` Error

Bot must be in channel before posting:

```bash
# 1. List channels to get ID
curl -s -X POST "https://slack.com/api/conversations.list" \
  -H "Authorization: Bearer $SLACK_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{"types":"public_channel","limit":100}' | grep -B2 "channel-name"

# 2. Join channel
curl -X POST "https://slack.com/api/conversations.join" \
  -H "Authorization: Bearer $SLACK_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{"channel":"CHANNEL_ID"}'

# 3. Retry message
```

### `channel_not_found` Error

- For channels: Use `#channel-name` format
- For DMs: Use `@username` or user ID
- Check workspace - token must match workspace where channel exists
- **Private channels:** Bot can't see private channels it's not a member of. Use Chrome to add bot first (see below)

### Private Channel Access

**Problem:** API returns `channel_not_found` for private channels bot isn't in. API can't list them either.

**Solution:** Use Chrome automation to add bot via browser UI (user IS logged in and CAN see the channel):

1. Navigate to Slack workspace in browser
2. Click on the private channel in sidebar
3. Click channel name → Integrations → Add apps
4. Search "PA Bot" → Add
5. Get channel ID from URL: `/client/TEAM_ID/CHANNEL_ID`
6. Now API works for that channel

**🚨 Don't give up:** If Chrome fails once, try again with different approach. Don't fall back to asking user for manual steps.

### `invalid_auth` Error

- Token expired or incorrect
- Check `~/.claude/.env` has correct token for target workspace

---

## JSON Escaping & Dynamic Content

**Important:** Use `--data` with single quotes to avoid shell escaping issues:

```bash
# ✅ Correct - single quotes around JSON
--data '{"channel":"#general","text":"Hello"}'

# ❌ Wrong - double quotes require escaping
-d "{\"channel\":\"#general\",\"text\":\"Hello\"}"
```

**For dynamic content, use printf (NOT heredoc):**

```bash
# ✅ Correct - printf avoids BOM/encoding issues on Windows
JSON=$(printf '{"channel":"%s","text":"%s"}' "#channel-name" "Dynamic: $VARIABLE")
curl -X POST "https://slack.com/api/chat.postMessage" \
  -H "Authorization: Bearer ${SLACK_TOKEN}" \
  -H "Content-Type: application/json; charset=utf-8" \
  --data "$JSON"
```

**🚨 AVOID heredocs on Windows** - they introduce BOM characters that appear as `??` in Slack:

```bash
# ❌ Wrong - heredoc adds BOM on Windows (shows "??" prefix in messages)
--data @- <<EOF
{"channel":"#general","text":"Hello"}
EOF
```

**🚨 Special characters get garbled:** Bullets (•), arrows (→), emojis may render as `?` in Slack. Use ASCII alternatives:
- `•` → `-` or `*`
- `→` → `->`
- Or use Slack's built-in emoji syntax: `:arrow_right:`, `:white_check_mark:`

---

## Available Workspaces

Check `~/.claude/.env` for available tokens. Common pattern:
- `SLACK_<WORKSPACE>_TOKEN` - e.g., `SLACK_<WORKSPACE_B>_TOKEN`, `SLACK_<WORKSPACE_A>_TOKEN`

---

## Common Use Cases

1. **Notify about GitHub issues** - Post link to new/updated issues
2. **System alerts** - Automated notifications from scripts
3. **Team updates** - Broadcast messages to channels
4. **Cross-repo notifications** - Any Claude Code session can send Slack messages

---

## Adding New Workspaces

1. Create Slack App in target workspace (or invite existing PA Bot)
2. Get Bot User OAuth Token (`xoxb-...`)
3. Add to `~/.claude/.env`: `SLACK_<WORKSPACE>_TOKEN=xoxb-...`
4. Ensure bot is invited to required channels

---

## Bot Token Scopes Reference

When creating a new Slack App, add these scopes under OAuth & Permissions → Bot Token Scopes:

| Scope | Purpose |
|-------|---------|
| `chat:write` | Send messages to channels/DMs |
| `channels:read` | List public channels |
| `channels:join` | Join public channels |
| `channels:manage` | Create/archive/rename channels (replaces deprecated `channels:write`) |
| `channels:history` | Read message history in channels bot is member of |
| `users:read` | List users (for DMs) |

**🚨 Note:** `channels:write` no longer exists in Slack API - use `channels:manage` instead.

---

# <COMPANY_A> Workflows

**Workspace:** <COMPANY_A> (`<WORKSPACE>.slack.com`)
**Token:** `SLACK_<WORKSPACE_A>_TOKEN`
**Team ID:** `<TEAM_ID>`

## Channel Reference

| Channel | ID | Purpose | Notes |
|---------|-----|---------|-------|
| `#all-<COMPANY_A>` | `<CHANNEL_ID>` | General announcements | Public, bot is member |
| `#managers` | `<CHANNEL_ID>` | Managers-only discussions | Private, bot added 2026-01-23 |
| `#admins` | `<CHANNEL_ID>` | Admin discussions | Private, created 2026-02-09 |
| `#cs` | `<CHANNEL_ID>` | Customer service | Private, created 2026-02-09 |
| `#sales` | `<CHANNEL_ID>` | Sales | Private, created 2026-02-09 |
| `#studio-administration` | `<CHANNEL_ID>` | Studio admin (<OWNER>, <TEAMMATE>, <TEAMMATE>) | Private, created 2026-02-09 |
| `#affiliate` | `<CHANNEL_ID>` | Affiliate program | Private, created 2026-02-09 |
| `#hr-intake` | `<CHANNEL_ID>` | HR intake | Private, created 2026-02-09 |
| `#bugs` | `<CHANNEL_ID>` | Bug reports from employees | Public, bot created 2026-01-29 |
| `#editing` | — | Content editing channel | Private |

---

# <PROJECT_C> Workflows

**Workspace:** <BRAND> (`<BRAND>.slack.com`)
**Token:** `SLACK_<BRAND>_TOKEN`

## Channel Reference

| Channel | ID | Purpose |
|---------|-----|---------|
| `#changelog` | `<CHANNEL_ID>` | Deployment notifications, feature releases |
| `#cf-bugs-qa` | `<CHANNEL_ID>` | Bug reports + QA submissions (unified) |
| `#cf-qa` | `<CHANNEL_ID>` | LEGACY — scan for pending items only, no new posts |

---

## Post Changelog

**When:** After deploying changes to <PROJECT_C> (push to master, Vercel deploy)

```bash
source ~/.claude/.env && export SLACK_TOKEN="$SLACK_<BRAND>_TOKEN"

JSON=$(printf '{"channel":"<CHANNEL_ID>","text":"%s","unfurl_links":false}' "YOUR_CHANGELOG_MESSAGE")

curl -s -X POST "https://slack.com/api/chat.postMessage" \
  -H "Authorization: Bearer ${SLACK_TOKEN}" \
  -H "Content-Type: application/json; charset=utf-8" \
  --data "$JSON"
```

**Changelog format:**
```
*<PROJECT_C> - New Features* :rocket:

- *Feature Name* - Description
- *Feature Name* - Description

_as of commit <short_hash>_
```

**Finding new features since last changelog:**
```bash
# Get the last reported commit from #changelog, then:
git log <last_commit>..HEAD --oneline | grep "feat:"
```

The commit hash in the message IS the tracking mechanism (SSoT). No separate tracking needed.

---

## Read Bug Reports

**When:** User asks to check bug reports or create GitHub issues from Slack

```bash
source ~/.claude/.env && export SLACK_TOKEN="$SLACK_<BRAND>_TOKEN"

# <CHANNEL_ID> = #cf-bugs-qa (unified bugs + QA channel)
curl -s -X POST "https://slack.com/api/conversations.history" \
  -H "Authorization: Bearer ${SLACK_TOKEN}" \
  -H "Content-Type: application/json" \
  -d '{"channel":"<CHANNEL_ID>","limit":20}'
```

**Parse response:** Look for messages not from bot (no `bot_id` field) - those are user reports.

---

## Create GitHub Issue from Slack Report

**Workflow:**
1. Read bug reports from Slack
2. Create GitHub issue:

```bash
gh issue create \
  --repo "<BRAND>/<PROJECT_C>" \
  --title "Bug: [summary from Slack message]" \
  --body "Reported in Slack #cf-bugs-qa by @username

---
**Original message:**
[Slack message content]

---
*Auto-created from Slack report*"
```

3. Reply in Slack thread:

```bash
source ~/.claude/.env && export SLACK_TOKEN="$SLACK_<BRAND>_TOKEN"

JSON=$(printf '{"channel":"<CHANNEL_ID>","thread_ts":"%s","text":"Created GitHub issue: %s"}' "MESSAGE_TS" "ISSUE_URL")

curl -s -X POST "https://slack.com/api/chat.postMessage" \
  -H "Authorization: Bearer ${SLACK_TOKEN}" \
  -H "Content-Type: application/json; charset=utf-8" \
  --data "$JSON"
```

---

## Notify Issue Resolution

**When:** After closing a GitHub issue that originated from Slack

```bash
source ~/.claude/.env && export SLACK_TOKEN="$SLACK_<BRAND>_TOKEN"

JSON=$(printf '{"channel":"<CHANNEL_ID>","text":"Resolved: %s\n\n*Fix:* %s\n*Commit:* %s"}' "ISSUE_TITLE" "FIX_SUMMARY" "COMMIT_URL")

curl -s -X POST "https://slack.com/api/chat.postMessage" \
  -H "Authorization: Bearer ${SLACK_TOKEN}" \
  -H "Content-Type: application/json; charset=utf-8" \
  --data "$JSON"
```

---

## <PROJECT_C> Typical Workflow

```
1. Editor posts bug in #cf-bugs-qa
   ↓
2. User tells Claude: "Check Slack bug reports and create GitHub issues"
   ↓
3. Claude reads #cf-bugs-qa
   ↓
4. Claude creates GitHub issues
   ↓
5. Claude replies in Slack thread with issue link
   ↓
6. User triggers Claude to fix issue (autonomous-issue-dispatch skill)
   ↓
7. Issue resolved, Claude posts to #cf-bugs-qa
   ↓
8. Claude posts changelog to #changelog
```

---

---

# <PROJECT_B> Workflows

**Workspace:** <PROJECT_B> (`<WORKSPACE_B>.slack.com`)
**Token:** `SLACK_<WORKSPACE_B>_TOKEN`
**Team ID:** `<TEAM_ID>`

## Channel Reference

| Channel | ID | Purpose | Notes |
|---------|-----|---------|-------|
| `#bugs-general` | `<CHANNEL_ID>` | Bug reports from co-founders | Public, pre-existing channel |

## Team

| Name | Slack ID | Role |
|------|----------|------|
| <OWNER> | `<USER_ID>` | Co-founder |
| <NAME> | `<USER_ID>` | Co-founder |

---

**Last updated:** 2026-01-29
