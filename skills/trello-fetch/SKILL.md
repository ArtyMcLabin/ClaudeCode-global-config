---
name: trello-fetch
description: Trello API operations — read cards, add comments, move cards, search boards, fetch board JSON. Use when any task involves Trello cards, Trello boards, Trello comments, student card lookups, or Trello data. Triggers — "Trello card", "update Trello", "check Trello", "add comment to card", "move card", "fetch board JSON", "Trello board export".
user-invocable: false
---

# Trello API Operations

## Authentication

- **Method:** REST API with API key + token as query params
- **Credentials:** `~/.claude/.env` → `TRELLO_API_KEY`, `TRELLO_API_TOKEN`
- **Base URL:** `https://api.trello.com/1`
- **Auth pattern:** `?key=$TRELLO_API_KEY&token=$TRELLO_API_TOKEN` appended to every request

Load credentials:
```bash
export TRELLO_API_KEY=$(grep TRELLO_API_KEY ~/.claude/.env | cut -d= -f2)
export TRELLO_API_TOKEN=$(grep TRELLO_API_TOKEN ~/.claude/.env | cut -d= -f2)
```

On Windows (Python preferred over bash for reliability):
```python
import os, re
env_path = os.path.expanduser("~/.claude/.env")
env = open(env_path).read()
TRELLO_API_KEY = re.search(r'TRELLO_API_KEY=(.+)', env).group(1).strip()
TRELLO_API_TOKEN = re.search(r'TRELLO_API_TOKEN=(.+)', env).group(1).strip()
```

## Common Operations

### Read a card
```bash
curl -s "https://api.trello.com/1/cards/{cardId}?key=$TRELLO_API_KEY&token=$TRELLO_API_TOKEN&fields=name,desc,idList,shortUrl"
```

### Add a comment to a card
```bash
curl -s -X POST "https://api.trello.com/1/cards/{cardId}/actions/comments?key=$TRELLO_API_KEY&token=$TRELLO_API_TOKEN" \
  --data-urlencode "text=<OWNER>'s ClaudeCode PA: Your comment here"
```

### Update comment text
```bash
curl -s -X PUT "https://api.trello.com/1/actions/{actionId}/text?key=$TRELLO_API_KEY&token=$TRELLO_API_TOKEN" \
  --data-urlencode "value=Updated text"
```

### Get card comments
```python
url = f'https://api.trello.com/1/cards/{card_id}/actions?filter=commentCard&key={KEY}&token={TOKEN}'
```

### Move a card to a different list
```bash
curl -s -X PUT "https://api.trello.com/1/cards/{cardId}?key=$TRELLO_API_KEY&token=$TRELLO_API_TOKEN" \
  -H "Content-Type: application/json" -d '{"idList": "targetListId"}'
```

### Search across boards
```bash
curl -s "https://api.trello.com/1/search?query=NAME&key=$TRELLO_API_KEY&token=$TRELLO_API_TOKEN&modelTypes=cards&card_fields=name,shortUrl,idBoard"
```

### Fetch full board JSON (replaces Chrome method)
```bash
curl -s "https://api.trello.com/1/boards/{boardId}?key=$TRELLO_API_KEY&token=$TRELLO_API_TOKEN&fields=all&cards=all&card_fields=all&lists=all&list_fields=all&members=all&actions=all&actions_limit=1000" > board_export.json
```

## Write Safety Rules

### Comments = SAFE (append-only)
- Adding comments never destroys existing data
- **Always prefer comments** for logging PA activity, status updates, notes

### Descriptions = DANGEROUS (full replace)
- PUT to `desc` field **replaces the entire description**
- If Claude Code gets the content wrong or misses a section, original data is gone
- **Only write to descriptions when explicitly instructed by user AND after reading the current description first**
- When writing descriptions: read current, merge changes, write back (never blind overwrite)

### Card moves = ASK FIRST
- Moving cards between lists is a state change visible to the whole team
- Always confirm with user before moving cards

## Comment Prefix Convention

**Comments (no date needed — Trello UI shows timestamp):**
```
<OWNER>'s ClaudeCode PA: <content>
```

**Description edits (include date — descriptions have no timestamp):**
```
<OWNER>'s ClaudeCode PA (18/2/2026): <content>
```

Use the current date in DD/M/YYYY format for description edits.

## Card ID Formats

Trello accepts multiple card identifiers:
- **Short link:** `Corofj04` (from URL `https://trello.com/c/Corofj04`)
- **Full ID:** `65522d6c09b034cfd95f51f2`
- Both work interchangeably in API calls

## Board Registry

No centralized board registry. Known boards by context:
- **Sales Storage** — student cards, lead history: `<BOARD_ID>`
- **Education Leads / Sales** — incoming leads: `<BOARD_ID>`
- **Customer Service** — CS cases: `<BOARD_ID>`

For other boards, search Trello or check project-specific docs.

## Fallback: Chrome Agent (Board Export Only)

If API auth fails or tokens expire, the Chrome-based approach still works for read-only board exports:
1. User is logged into Trello in Chrome
2. Chrome agent navigates to `https://trello.com/b/{BOARD_ID}.json`
3. Session cookies authenticate the request
4. `get_page_text` extracts the JSON

Only use Chrome fallback if API returns 401/403.

## Encoding Note

When parsing Trello JSON in Python on Windows, use `encoding='utf-8'` explicitly. The default cp1252 will choke on Unicode characters in Hebrew names.
