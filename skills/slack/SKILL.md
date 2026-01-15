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

**Last updated:** 2026-01-15
