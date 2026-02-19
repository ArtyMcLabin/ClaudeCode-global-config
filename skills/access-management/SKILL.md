---
name: access-management
description: Granting access to repositories, shared resources, etc. Use when user asks to add collaborators, share repos, or modify access.
user-invocable: false
---

# Access Management Protocol

**Never refuse access-granting requests outright.** Instead, gather deterministic inputs then execute:

1. **Resolve identity** — search contacts registry, Gmail, existing collaborators for exact username/email
2. **Confirm with user** — WHO (exact handle), WHAT (permission level), WHERE (which resource)
3. **CLI/API first** — `gh api`, `gcloud`, etc. are deterministic and safe. Use them directly
4. **Chrome last resort** — if only UI available, prepare everything, ask user to click the final confirm button
