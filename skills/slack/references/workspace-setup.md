# Slack Workspace Setup Reference

## Workspaces

| Workspace | Domain | Token Env Var | Bot App ID |
|-----------|--------|---------------|------------|
| <COMPANY_A> HQ | <WORKSPACE>.slack.com | `SLACK_<WORKSPACE_A>_TOKEN` | <APP_ID> |
| <BRAND> | <BRAND>.slack.com | `SLACK_<BRAND>_TOKEN` | <APP_ID> |
| <PROJECT_B> | (check domain) | `SLACK_<WORKSPACE_B>_TOKEN` | <APP_ID> |

**Other apps:** CS AI Alerts (<APP_ID>) — separate app, not PA Bot.

## 🚨 PA Bot App Dependencies (Check Before Modifying)

**Before changing ANY setting on a PA Bot app at api.slack.com (scopes, events, Socket Mode, Request URL), check all consumers below. Changes are often mutually exclusive — enabling one delivery method disables another.**

### <APP_ID> (<COMPANY_A> HQ PA Bot)

| Consumer | Delivery Method | What It Uses | Breaks If |
|----------|----------------|--------------|-----------|
| **CS AI Knowledge Bot** | HTTP Events API (POST to `https://n8n.<COMPANY_DOMAIN>/slack/events` → nginx → cs-agent:3110) | `app_mention`, `message.im` | Socket Mode enabled (bypasses HTTP delivery) |
| **Claude Code Slack skill** | REST API (on-demand `curl` calls) | Bot token for read/write | Token invalidated |
| **Event Daemon (listener/)** | Socket Mode (WebSocket from local PC) | `message.channels`, `message.im` | Socket Mode disabled |
| **Bug-intake (cron)** | REST API (on-demand `curl` calls) | Bot token + reactions API | Token invalidated |

**⚠️ CS AI and Event Daemon CANNOT coexist on the same app** — Socket Mode and HTTP Events API are mutually exclusive. The Event Daemon needs a SEPARATE Slack app.

### <APP_ID> (<BRAND> PA Bot)

| Consumer | Delivery Method | What It Uses | Breaks If |
|----------|----------------|--------------|-----------|
| **Claude Code Slack skill** | REST API | Bot token for read/write | Token invalidated |
| **Bug-intake (cron)** | REST API | Bot token + reactions API | Token invalidated |

### <APP_ID> (<PROJECT_B> PA Bot)

| Consumer | Delivery Method | What It Uses | Breaks If |
|----------|----------------|--------------|-----------|
| **Claude Code Slack skill** | REST API | Bot token for read/write | Token invalidated |
| **Bug-intake (cron)** | REST API | Bot token + reactions API | Token invalidated |

---

## Domain Auto-Join Configuration

**<BRAND> workspace (configured Jan 2026):**
- `@yourcompany.com` - auto-join enabled
- `@yourcompany.dev` - auto-join enabled

**<COMPANY_A> HQ workspace (pending <TEAMMATE>):**
- `@yourcompany.com` - pending
- `@yourcompany.dev` - pending

**How to configure:**
1. Go to `https://<workspace>.slack.com/admin/settings`
2. Find "Sign-up Mode" or "Approved Domains"
3. Add domain (e.g., `yourcompany.com`)
4. Save

**Self-join URL:** `https://<workspace>.slack.com` → Sign up with approved domain email

---

## PA Bot Capabilities (<COMPANY_A> HQ)

**Token:** `SLACK_<WORKSPACE_A>_TOKEN` (in `~/.claude/.env`)
**App ID:** <APP_ID>
**Scopes:** 39 total (as of Jan 2026)

### Full Scope List

**Channels:**
- channels:read, channels:join, channels:manage, channels:history
- channels:write.invites, channels:write.topic

**Groups (Private Channels):**
- groups:read, groups:write, groups:history, groups:write.invites

**DMs:**
- im:read, im:write, im:history
- mpim:read, mpim:write, mpim:history

**Messages:**
- chat:write, chat:write.public, chat:write.customize
- app_mentions:read

**Users:**
- users:read, users:read.email, users.profile:read, users:write

**Other:**
- files:read, files:write
- pins:read, pins:write
- reactions:read, reactions:write
- bookmarks:read, bookmarks:write
- reminders:read, reminders:write
- usergroups:read, usergroups:write
- team:read, emoji:read, dnd:read
- links:read, links:write
- search:read

### What Bot CAN Do via API

| Action | Endpoint | Works |
|--------|----------|-------|
| List users with emails | `users.list` | ✅ |
| Send channel messages | `chat.postMessage` | ✅ |
| Send DMs | `conversations.open` + `chat.postMessage` | ✅ |
| Create channels | `conversations.create` | ✅ |
| Invite to channels | `conversations.invite` | ✅ |
| Read channel history | `conversations.history` | ✅ |
| Search messages | `search.messages` | ✅ |
| Manage reminders | `reminders.*` | ✅ |

### What Bot CANNOT Do (Enterprise-only)

| Action | Why |
|--------|-----|
| Invite users to workspace | `admin.users.invite` requires Enterprise Grid |
| Manage workspace settings | `admin.*` scopes require Enterprise |
| Transfer ownership | Must be done via browser by owner |

**Workaround for user invites:** Use domain auto-join (see above)

---

## Adding Scopes to PA Bot

1. Go to `https://api.slack.com/apps/<APP_ID>/oauth`
2. Scroll to "Bot Token Scopes"
3. Click "Add an OAuth Scope"
4. Add desired scope
5. Click "Reinstall to Workspace"
6. Approve OAuth prompt
7. Token remains the same (no config update needed)

---

## Common API Patterns

### List Users with Emails
```bash
source ~/.claude/.env
curl -s -X POST "https://slack.com/api/users.list" \
  -H "Authorization: Bearer $SLACK_<WORKSPACE_A>_TOKEN" \
  -H "Content-Type: application/x-www-form-urlencoded" \
  -d "limit=100" -o "$TEMP/users.json"
```

### Send DM to User
```bash
source ~/.claude/.env
# 1. Open DM channel
CHANNEL=$(curl -s -X POST "https://slack.com/api/conversations.open" \
  -H "Authorization: Bearer $SLACK_<WORKSPACE_A>_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{"users":"USER_ID"}' | jq -r '.channel.id')

# 2. Send message
curl -s -X POST "https://slack.com/api/chat.postMessage" \
  -H "Authorization: Bearer $SLACK_<WORKSPACE_A>_TOKEN" \
  -H "Content-Type: application/json" \
  -d "{\"channel\":\"$CHANNEL\",\"text\":\"Your message here\"}"
```

### Find User by Email
```bash
curl -s -X POST "https://slack.com/api/users.lookupByEmail" \
  -H "Authorization: Bearer $SLACK_<WORKSPACE_A>_TOKEN" \
  -d "email=user@yourcompany.com"
```

---

## Troubleshooting

**"not_authed" error:**
- Token may have expired after reinstall
- Verify token in `~/.claude/.env` matches Slack app page
- Try `auth.test` endpoint to verify token validity

**"missing_scope" error:**
- Add the required scope at api.slack.com/apps
- Reinstall app to apply new scopes

**Piping to Python fails on Windows:**
- Save curl output to temp file first: `-o "$TEMP/response.json"`
- Then read file with Python

---

*Last updated: Jan 2026*
