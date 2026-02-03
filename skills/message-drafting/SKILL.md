---
name: message-drafting
description: Message drafting rules for emails, Slack, WhatsApp. Use when drafting messages on user's behalf, sending emails to GR team, composing internal communications, or any message composition task. Covers draft review workflow, post-send disposition, GR email addressing (role vs person), internal email format, and bilingual copypasta.
user-invocable: false
---

# Message Drafting Rules

## Core Workflow

- Authorized to draft messages in user's name (email, Slack, etc.)
- **Default: ASK FIRST** - show draft, wait for approval before sending
- **Draft review:** After drafting, tell user exactly how to review (e.g., "Draft is in Gmail compose window - check tab X" or "I'll paste the draft below for your review")
- Keep drafts visible/accessible - don't close windows or navigate away before user confirms

## Post-Send Disposition (MANDATORY)

🚨 **After every draft, explicitly state disposition:**
- "After sending → archive" — thread is closed/fire-and-forget
- "After sending → snooze to [date]" — expect a response or need to verify follow-through
- Never leave disposition implicit

🚨 **After sending, ALWAYS provide direct link** to the posted message (Slack, email thread, LinkedIn post, etc.) so user can verify/access it directly.

## Auto-Send Exception

**Trivial internal confirmations to GR team** — e.g., "Done, secrets are set" after completing a task they requested. No draft review needed for obvious task-completion acks.

## GR Email Addressing (Role vs Person)

- **User says a role** (e.g., "send to financial manager") → use the **role email** (e.g., financial.manager@yourcompany.com). Lookup from Roles sheet.
- **User says a person** (e.g., "send to <TEAMMATE>") → use the **person's personal @yourcompany.com email**. Lookup from Roles sheet. If personal email isn't in the Roles sheet, search Gmail (`from:<firstname>@yourcompany.com OR from:<firstname.lastname>@yourcompany.com`) to find it. Don't ask user — figure it out.
- Each GR team member has their own personal domain email in addition to any role emails they hold. These are different addresses — don't conflate them.

## Internal Emails (to GR team, @yourcompany.com)

- **Remove pre-filled signature** - select all in compose body, delete, then type draft
- **First line:** `Hey <Name>, <NAME>'s ClaudeCode here.`
- Then the actual message content
- No signature needed (it's clearly from PA)
- **Attach relevant evidence:** If user has screenshots, chat logs, or examples that illustrate the issue - ask user to attach them or offer to attach if available. Concrete examples > abstract descriptions.
