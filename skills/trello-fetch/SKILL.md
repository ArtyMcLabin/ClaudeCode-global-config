---
name: trello-fetch
description: Fetch Trello board JSON exports. Use when downloading Trello boards, exporting Trello data, fetching Trello JSON, or when a training/retraining workflow requires fresh Trello board data. Covers both private and public boards.
user-invocable: false
---

# Trello Board JSON Fetch

## Why Not curl

Trello's `/b/{ID}.json` endpoint requires authentication. `curl` without cookies/tokens returns 401 for private boards. This broke our old SOP that used `curl -sL "https://trello.com/b/{ID}.json"`.

## Fetch Method: Chrome Agent

The user is logged into Trello in Chrome. Use the chrome-agent (via Task tool) to:

1. Navigate to `https://trello.com/b/{BOARD_ID}.json`
2. The page renders raw JSON (the user's session cookies authenticate)
3. Use `get_page_text` to extract the full JSON content
4. Save to the target file path

### Template prompt for chrome-agent:

```
Navigate to https://trello.com/b/{BOARD_ID}.json in Chrome.
The user is logged into Trello so the page will show raw JSON content.

1. Call tabs_context_mcp first
2. Create a new tab navigating to https://trello.com/b/{BOARD_ID}.json
3. Wait for it to load
4. Use get_page_text to get ALL the text content (this is raw JSON)
5. Save the complete content to {TARGET_FILE_PATH}
6. Report file size and confirm save
```

### Encoding note

Chrome-exported JSON may have UTF-8 BOM. When parsing in Python, use `encoding='utf-8-sig'` instead of `utf-8`.

## File Naming Convention

`{board-slug}_YYYY-MM-DD.json` in the project's `TrainingData/` directory.

Examples:
- `<company_a>-customer-service_2026-02-01.json`
- `<company_a>-sales-training-procedures_2026-02-01.json`

## Fallback: Manual Browser Export

If chrome-agent fails (extension issues, tab detachment):

1. Ask user to open `https://trello.com/b/{BOARD_ID}.json` in Chrome
2. Ctrl+S to save the page as a `.json` file
3. Save to the target path with dated filename

Alternative: Board UI export (Menu → ... → Print and Export → Export as JSON). Same result but through Trello UI instead of the `.json` URL.

## Known Board Registry

This skill doesn't own any board registry. Each project maintains its own board list in its training data docs (e.g., `TrainingData/RELATED_REPOSITORIES.md`). Check project docs for board IDs before fetching.
