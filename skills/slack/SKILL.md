---
name: slack
description: Send Slack messages via API (channels, DMs, notifications). Use when needing to post to Slack channels or send DMs programmatically.
---

# Slack Messaging

**Purpose:** Send Slack messages via API (channels, DMs, notifications).

**Credential location:** `~/.claude/.env` (gitignored) - contains workspace tokens.

---

## Quick Start

```bash
# 1. Load token from global .env
source ~/.claude/.env

# 2. Choose workspace token
export SLACK_TOKEN="$SLACK_BORZAI_TOKEN"    # or SLACK_GAMEREADY_TOKEN, etc.

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

---

## Available Workspaces

Check `~/.claude/.env` for available tokens. Common pattern:
- `SLACK_<WORKSPACE>_TOKEN` - e.g., `SLACK_BORZAI_TOKEN`, `SLACK_GAMEREADY_TOKEN`

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

# ContentFactory Workflows

**Workspace:** RawCEO (`rawceo.slack.com`)
**Token:** `SLACK_RAWCEO_TOKEN`

## Channel Reference

| Channel | ID | Purpose |
|---------|-----|---------|
| `#changelog` | `C0A8ZQL2K38` | Deployment notifications, feature releases |
| `#bug-reports` | `C0A8LCLSV6K` | Bug reports & feature requests from team |
| `#qa` | `C0A93LG2KCN` | QA review items |

---

## Post Changelog

**When:** After deploying changes to ContentFactory (push to master, Vercel deploy)

```bash
source ~/.claude/.env && export SLACK_TOKEN="$SLACK_RAWCEO_TOKEN"

JSON=$(printf '{"channel":"C0A8ZQL2K38","text":"%s","unfurl_links":false}' "YOUR_CHANGELOG_MESSAGE")

curl -s -X POST "https://slack.com/api/chat.postMessage" \
  -H "Authorization: Bearer ${SLACK_TOKEN}" \
  -H "Content-Type: application/json; charset=utf-8" \
  --data "$JSON"
```

**Changelog format:**
```
*ContentFactory - New Features* :rocket:

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
source ~/.claude/.env && export SLACK_TOKEN="$SLACK_RAWCEO_TOKEN"

curl -s -X POST "https://slack.com/api/conversations.history" \
  -H "Authorization: Bearer ${SLACK_TOKEN}" \
  -H "Content-Type: application/json" \
  -d '{"channel":"C0A8LCLSV6K","limit":20}'
```

**Parse response:** Look for messages not from bot (no `bot_id` field) - those are user reports.

---

## Create GitHub Issue from Slack Report

**Workflow:**
1. Read bug reports from Slack
2. Create GitHub issue:

```bash
gh issue create \
  --repo "RawCEO/ContentFactoryCC" \
  --title "Bug: [summary from Slack message]" \
  --body "Reported in Slack #bug-reports by @username

---
**Original message:**
[Slack message content]

---
*Auto-created from Slack report*"
```

3. Reply in Slack thread:

```bash
source ~/.claude/.env && export SLACK_TOKEN="$SLACK_RAWCEO_TOKEN"

JSON=$(printf '{"channel":"C0A8LCLSV6K","thread_ts":"%s","text":"Created GitHub issue: %s"}' "MESSAGE_TS" "ISSUE_URL")

curl -s -X POST "https://slack.com/api/chat.postMessage" \
  -H "Authorization: Bearer ${SLACK_TOKEN}" \
  -H "Content-Type: application/json; charset=utf-8" \
  --data "$JSON"
```

---

## Notify Issue Resolution

**When:** After closing a GitHub issue that originated from Slack

```bash
source ~/.claude/.env && export SLACK_TOKEN="$SLACK_RAWCEO_TOKEN"

JSON=$(printf '{"channel":"C0A8LCLSV6K","text":"Resolved: %s\n\n*Fix:* %s\n*Commit:* %s"}' "ISSUE_TITLE" "FIX_SUMMARY" "COMMIT_URL")

curl -s -X POST "https://slack.com/api/chat.postMessage" \
  -H "Authorization: Bearer ${SLACK_TOKEN}" \
  -H "Content-Type: application/json; charset=utf-8" \
  --data "$JSON"
```

---

## ContentFactory Typical Workflow

```
1. Editor posts bug in #bug-reports
   ↓
2. User tells Claude: "Check Slack bug reports and create GitHub issues"
   ↓
3. Claude reads #bug-reports
   ↓
4. Claude creates GitHub issues
   ↓
5. Claude replies in Slack thread with issue link
   ↓
6. User triggers Claude to fix issue (autonomous-bug-fixing skill)
   ↓
7. Issue resolved, Claude posts to #bug-reports
   ↓
8. Claude posts changelog to #changelog
```

---

**Last updated:** 2026-01-16
