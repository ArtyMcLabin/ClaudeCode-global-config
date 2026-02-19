---
name: claude-code-session-extraction
description: Extract and read previous Claude Code conversations from local storage. Use when reviewing past sessions, finding previous context, or debugging session history.
user-invocable: false
---

# Claude Code Session Extraction

Extract and read previous Claude Code conversations from local storage.

## Session Storage Location

```
~/.claude/projects/<project-path-encoded>/<session-uuid>.jsonl
```

**Path encoding rules:**
- Drive letters: `C:` → `C-`
- Path separators: `/` or `\` → `-`
- Example: `/home/user/myproject` → `home-user-myproject`
- Example: `<LOCAL_PATH>/MyProject` → `<DRIVE>--<PATH>-MyProject`

**Platform locations:**
| Platform | Base Path |
|----------|-----------|
| Linux/macOS | `~/.claude/projects/` |
| Windows | `%USERPROFILE%\.claude\projects\` |

## Quick Commands

### List all projects with sessions
```bash
ls ~/.claude/projects/
```

### List sessions for a specific project (sorted by date)
```bash
ls -lt ~/.claude/projects/<PROJECT_PATH>/*.jsonl | head -20
```

### Resume a session interactively
```bash
claude --resume
```

### Resume a specific session by ID
```bash
claude --resume <session-uuid>
```

## JSONL Format Reference

Each line is a JSON object with a `type` field:

| Type | Contains | Key Fields |
|------|----------|------------|
| `summary` | Session title | `summary` |
| `user` | User messages | `message.content`, `timestamp` |
| `assistant` | Claude responses | `message.content[]` (array of blocks) |
| `file-history-snapshot` | File change tracking | `trackedFileBackups` |

### Assistant message content blocks

```json
{
  "type": "assistant",
  "message": {
    "content": [
      {"type": "thinking", "thinking": "..."},
      {"type": "text", "text": "..."},
      {"type": "tool_use", "name": "Bash", "input": {...}}
    ]
  }
}
```

## Extraction Script

### Basic extraction (markdown output)

```python
import json
import sys
import os

def extract_session(session_file):
    """Extract a Claude Code session to readable format."""
    if hasattr(sys.stdout, 'reconfigure'):
        sys.stdout.reconfigure(encoding='utf-8')

    conversation = []
    summary_title = None

    with open(session_file, 'r', encoding='utf-8') as f:
        for line in f:
            try:
                obj = json.loads(line.strip())
                msg_type = obj.get('type')

                if msg_type == 'summary':
                    summary_title = obj.get('summary', 'Untitled')

                elif msg_type == 'user':
                    content = obj.get('message', {}).get('content', '')
                    ts = obj.get('timestamp', '')[:19] if obj.get('timestamp') else ''
                    # Skip system/command messages
                    if content and not content.startswith('<'):
                        conversation.append({
                            'role': 'USER',
                            'content': content,
                            'timestamp': ts
                        })

                elif msg_type == 'assistant':
                    content_blocks = obj.get('message', {}).get('content', [])
                    ts = obj.get('timestamp', '')[:19] if obj.get('timestamp') else ''
                    texts = []
                    tools = []

                    for block in content_blocks:
                        if block.get('type') == 'text':
                            texts.append(block.get('text', ''))
                        elif block.get('type') == 'tool_use':
                            tools.append(block.get('name', 'unknown'))

                    if texts:
                        full_text = '\n'.join(texts)
                        conversation.append({
                            'role': 'ASSISTANT',
                            'content': full_text,
                            'tools': tools,
                            'timestamp': ts
                        })
            except Exception:
                pass

    return summary_title, conversation


def to_markdown(summary_title, conversation):
    """Convert extracted conversation to markdown."""
    output = []
    output.append(f"# {summary_title or 'Untitled Session'}\n")

    for msg in conversation:
        role = msg['role']
        ts = msg.get('timestamp', '')
        tools = msg.get('tools', [])
        content = msg['content']

        output.append(f"## {role}")
        if ts:
            output.append(f"*{ts}*")
        if tools:
            output.append(f"**Tools used:** {', '.join(tools)}")
        output.append(f"\n{content}\n")
        output.append("---\n")

    return '\n'.join(output)


def get_projects_dir():
    """Get the Claude Code projects directory for the current platform."""
    home = os.path.expanduser('~')
    return os.path.join(home, '.claude', 'projects')


def list_sessions(project_path_encoded, limit=20):
    """List session files for a project, sorted by modification time."""
    projects_dir = get_projects_dir()
    project_dir = os.path.join(projects_dir, project_path_encoded)

    if not os.path.exists(project_dir):
        return []

    sessions = []
    for f in os.listdir(project_dir):
        if f.endswith('.jsonl'):
            full_path = os.path.join(project_dir, f)
            mtime = os.path.getmtime(full_path)
            sessions.append((full_path, mtime))

    sessions.sort(key=lambda x: x[1], reverse=True)
    return [s[0] for s in sessions[:limit]]


if __name__ == '__main__':
    if len(sys.argv) < 2:
        print("Usage: python extract_session.py <session-file.jsonl>")
        sys.exit(1)

    title, convo = extract_session(sys.argv[1])
    print(to_markdown(title, convo))
```

### One-liner for quick preview

```bash
# Preview first few exchanges from a session
python3 -c "
import json,sys
for l in open(sys.argv[1],'r',encoding='utf-8'):
  o=json.loads(l)
  if o.get('type')=='user' and not o.get('message',{}).get('content','').startswith('<'):
    print('USER:',o['message']['content'][:200])
  elif o.get('type')=='assistant':
    for b in o.get('message',{}).get('content',[]):
      if b.get('type')=='text' and len(b.get('text',''))>20:
        print('CLAUDE:',b['text'][:200])
        break
" ~/.claude/projects/<PROJECT>/<SESSION>.jsonl | head -50
```

## Common Workflows

### Find a session by keyword

```bash
# Search session content for a keyword
grep -l "some keyword" ~/.claude/projects/<PROJECT>/*.jsonl
```

### Get session summaries (titles)

```bash
# List all session titles for a project
for f in ~/.claude/projects/<PROJECT>/*.jsonl; do
  title=$(head -5 "$f" | grep '"type":"summary"' | python3 -c "import json,sys; print(json.loads(sys.stdin.read()).get('summary',''))" 2>/dev/null)
  if [ -n "$title" ]; then
    echo "$(basename $f): $title"
  fi
done
```

### Export session to file

```bash
python3 extract_session.py ~/.claude/projects/<PROJECT>/<SESSION>.jsonl > conversation.md
```

## Notes

- **Thinking blocks** are stored but contain signatures (encrypted) - readable content is in `thinking` field
- **Tool results** are in separate JSONL entries, linked via `parentUuid`
- **Subagent sessions** are in `<session-uuid>/subagents/` subdirectories
- **Global history** (all prompts across projects) is in `~/.claude/history.jsonl`
- **Cross-platform:** Use `os.path.expanduser('~')` in Python or `$HOME`/`%USERPROFILE%` in shell
