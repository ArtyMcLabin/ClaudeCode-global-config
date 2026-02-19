---
name: n8n
description: n8n workflow management via direct SQL (preferred over browser/chrome-agent). Use when modifying n8n workflows, debugging n8n issues, checking workflow executions, updating workflow nodes or connections, or when chrome-agent fails with n8n UI. Key insight - n8n stores workflows in PostgreSQL, direct SQL is faster and more reliable than UI automation. 🚨 CHROME AGENT IS FORBIDDEN FOR N8N - use SQL methods in this skill instead.
user-invocable: false
---

# n8n Workflow Management

## 🚨 CHROME AGENT FORBIDDEN FOR N8N

**DO NOT delegate n8n tasks to chrome-agent.** This skill exists specifically because:
1. Chrome-agent has reliability issues with n8n UI (tab detachment, connection drops)
2. SQL is 10x faster and more reliable
3. n8n stores everything in PostgreSQL - direct access is the correct approach

**If you're reading this because chrome-agent refused your task:** Good. That's working as intended. Use the SQL methods below.

## When to Use This Skill
- Modifying n8n workflows programmatically
- Debugging n8n workflow issues
- Automating n8n workflow updates
- ANY n8n operation that doesn't require first-time OAuth setup

## Key Discovery: SQL > Chrome for n8n

**Direct SQL manipulation is faster and more reliable than UI automation.**

n8n stores workflows in PostgreSQL. You can query and update them directly.

---

## Prerequisites

Find your n8n PostgreSQL access:
```bash
# Check container names
docker ps --format '{{.Names}}' | grep -i n8n

# Common patterns:
# - n8n-postgres, n8n_postgres_1, n8n-postgres-1
# - Database: n8n, User: n8n
```

---

## Common Operations

### List All Workflows
```bash
docker exec <postgres-container> psql -U n8n -d n8n -c \
  "SELECT id, name, active FROM workflow_entity ORDER BY \"updatedAt\" DESC;"
```

### Get Workflow Details
```bash
# Get nodes (all node configs)
docker exec <postgres-container> psql -U n8n -d n8n -c \
  "SELECT nodes FROM workflow_entity WHERE id = '<workflow-id>';"

# Get connections (how nodes link together)
docker exec <postgres-container> psql -U n8n -d n8n -c \
  "SELECT connections FROM workflow_entity WHERE id = '<workflow-id>';"

# Pretty-print with Python
docker exec <postgres-container> psql -U n8n -d n8n -t -c \
  "SELECT nodes FROM workflow_entity WHERE id = '<workflow-id>';" | \
  python3 -c "import json,sys; print(json.dumps(json.loads(sys.stdin.read().strip()), indent=2))"
```

### Check Recent Executions
```bash
docker exec <postgres-container> psql -U n8n -d n8n -c \
  "SELECT \"startedAt\", \"stoppedAt\", status
   FROM execution_entity
   WHERE \"workflowId\" = '<workflow-id>'
   ORDER BY \"startedAt\" DESC LIMIT 10;"
```

---

## Updating Workflows via SQL

### Method 1: Direct SQL (simple changes)
```bash
# Update nodes
docker exec <postgres-container> psql -U n8n -d n8n -c \
  "UPDATE workflow_entity SET nodes = '<JSON>' WHERE id = '<workflow-id>';"

# Update connections
docker exec <postgres-container> psql -U n8n -d n8n -c \
  "UPDATE workflow_entity SET connections = '<JSON>' WHERE id = '<workflow-id>';"
```

### Method 2: SQL File (complex JSON with quotes)
```bash
# Create SQL file to handle escaping
cat > /tmp/update_workflow.sql << 'SQLEOF'
UPDATE workflow_entity
SET nodes = '[{"parameters":{...},"type":"n8n-nodes-base.webhook",...}]'
WHERE id = 'your-workflow-id';
SQLEOF

# Execute it
docker exec -i <postgres-container> psql -U n8n -d n8n < /tmp/update_workflow.sql
```

### After SQL Update: Restart n8n
```bash
docker restart <n8n-container>
```

**WARNING:** Restarting n8n causes ~15-20 seconds of downtime. Any webhooks during this window are LOST (no retry). Ask user permission before restarting.

---

## Workflow JSON Structure

### Nodes Array
```json
[
  {
    "parameters": { /* node-specific config */ },
    "type": "n8n-nodes-base.webhook",
    "typeVersion": 2.1,
    "position": [0, 0],
    "id": "unique-node-id",
    "name": "Node Display Name",
    "webhookId": "webhook-unique-id",
    "credentials": {
      "credentialType": {
        "id": "credential-id",
        "name": "Credential Display Name"
      }
    }
  }
]
```

### Connections Object
```json
{
  "Source Node Name": {
    "main": [
      [
        {"node": "Target Node Name", "type": "main", "index": 0}
      ]
    ]
  }
}
```

**Important:** Connection keys must match exact node names. If you rename a node, update connections too!

---

## Common Node Types

| Node Type | Purpose |
|-----------|---------|
| `n8n-nodes-base.webhook` | HTTP webhook trigger |
| `n8n-nodes-base.set` | Transform/set data fields |
| `n8n-nodes-base.googleSheets` | Google Sheets read/write |
| `n8n-nodes-base.httpRequest` | Make HTTP requests |
| `n8n-nodes-base.code` | Custom JavaScript |

---

## Troubleshooting

### Webhook Returns 404
- Check `httpMethod` matches your request (GET vs POST)
- Verify workflow is active: `SELECT active FROM workflow_entity WHERE id = '...'`
- Restart n8n after SQL changes

### Execution Shows "error" Status
- Check n8n logs: `docker logs <n8n-container> --tail 50`
- Common: Missing credentials, invalid node config, connection name mismatch

### "Cannot read properties of undefined"
- Usually means node config is malformed
- Compare your JSON structure against a working workflow
- Check `typeVersion` matches what n8n expects

---

## When to Still Use Chrome

- First-time credential setup (OAuth flows)
- Exploring unfamiliar node options
- Visual debugging of complex workflows

For everything else: **SQL is faster and more reliable.**
