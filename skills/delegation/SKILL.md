---
name: delegation
description: Self-contained delegation philosophy for handoffs that don't fall through cracks. Use when delegating tasks to team members, contractors, or AI agents.
user-invocable: false
---

# Self-Contained Delegation

**Philosophy:** Every delegation should contain everything needed to close itself - including what the recipient should do AND communicate upon completion.

## The Problem

Standard delegation:
1. You delegate task X to someone
2. They complete it
3. They say "done"
4. You forgot what you needed it for
5. Ball dropped. Context lost. Follow-up forgotten.

## The Solution: Self-Contained Delegation

Every delegation includes:
1. **The task itself** - what needs to be done
2. **Success criteria** - how to know it's done correctly
3. **Callback template** - the EXACT message/email to send upon completion
4. **Next action context** - what the requester will do with the result

## Template

```
TASK: [What needs to be done]

SUCCESS CRITERIA:
- [Criterion 1]
- [Criterion 2]

UPON COMPLETION, SEND THIS TO [recipient]:
---
Subject: [Pre-written subject]

[Pre-written message body with placeholders for results]

Next step for you: [What requester will do when they receive this]
---
```

## Example: Developer Task

**Bad delegation:**
> "Implement a pricing API endpoint"

**Self-contained delegation:**
> **TASK:** Implement GET `/api/v1/pricing` endpoint that returns current plan prices
>
> **SUCCESS CRITERIA:**
> - Returns JSON with all plan tiers and prices
> - Includes regional pricing (Israel vs international)
> - Has proper error handling
> - Deployed to production
>
> **UPON COMPLETION, EMAIL <PROJECT_OWNER_EMAIL>:**
> ```
> Subject: Pricing API endpoint implemented
>
> The pricing API endpoint is now live:
> - Endpoint: <API_ENDPOINT>
> - Returns: [paste sample response]
>
> You can now use this in the Weekly Digest audit SOP to verify
> balance adjustments match official pricing.
> ```

## Why This Works

1. **Nothing falls through cracks** - the callback template ensures follow-up happens
2. **Context preserved** - recipient knows WHY this matters, not just WHAT to do
3. **Zero back-and-forth** - no "what was this for again?" messages
4. **Requester can forget safely** - the delegation carries its own memory
5. **Scales to async** - works across timezones, AI agents, long-running tasks

## Related Concepts

| Concept | Relationship |
|---------|--------------|
| **Closed-loop communication** (aviation) | Confirms receipt; SCD goes further by pre-loading the response |
| **Definition of Done** (Agile) | Defines completion criteria; SCD adds callback template |
| **Runbooks** (DevOps) | Pre-written incident responses; SCD applies this to delegation |

## When to Use

- Delegating to team members (especially across timezones)
- Creating GitHub issues for developers
- Assigning tasks to AI agents
- Any handoff where you might forget context by completion time
- Tasks with long lead times (days/weeks)

## Anti-Patterns

- ❌ "Do X and let me know when done" (no callback template)
- ❌ "Implement feature Y" (no success criteria, no next-action context)
- ❌ Assuming you'll remember what to do when notified of completion
- ❌ Relying on recipient to know what you need from the result
