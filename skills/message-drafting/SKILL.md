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

🚨 **Every sent email MUST be archived or snoozed. Never leave in inbox.**

**Before sending**, declare disposition:
- "After sending → archive" — thread is closed/fire-and-forget
- "After sending → snooze to [date]" — expect a response or need to verify follow-through

**Immediately after sending**, execute the disposition:
- **Archive:** `gmail_modify` → remove `INBOX` label
- **Snooze:** `gmail_modify` → remove `INBOX` label + add to snooze (or add to schedule.yaml deferred section if Gmail snooze unavailable via MCP)
- **Never skip this step.** If send succeeds but disposition fails, retry disposition. Report both send and disposition status to user.

🚨 **After sending, ALWAYS provide direct link** to the posted message (Slack, email thread, LinkedIn post, etc.) so user can verify/access it directly.

## Auto-Send Exception

**Trivial internal confirmations to GR team** — e.g., "Done, secrets are set" after completing a task they requested. No draft review needed for obvious task-completion acks.

## GR Email Addressing (Role vs Person)

- **User says a role** (e.g., "send to financial manager") → use the **role email** (e.g., financial.manager@yourcompany.com). Lookup from Roles sheet.
- **User says a person** (e.g., "send to <TEAMMATE>") → use the **person's personal @yourcompany.com email**. Lookup from Roles sheet. If personal email isn't in the Roles sheet, search Gmail (`from:<firstname>@yourcompany.com OR from:<firstname.lastname>@yourcompany.com`) to find it. Don't ask user — figure it out.
- Each GR team member has their own personal domain email in addition to any role emails they hold. These are different addresses — don't conflate them.

## Reply-From Address Matching (MANDATORY)

🚨 **When replying to an email, ALWAYS reply from the same address the original was sent TO.**

Before composing any reply:
1. Check the `To:` / `Delivered-To:` header of the incoming email
2. Set the `From:` / send-as address to match that recipient address
3. If the email was sent to `ceo@yourcompany.com`, reply FROM `ceo@yourcompany.com` — not from `<YOUR_EMAIL>`
4. If send-as alias isn't configured for that address, flag to user: "This was sent to X but I can only send from Y. Proceed from Y or set up alias first?"

**Why:** Replying from a different address breaks support cases, confuses recipients, and can get rejected by ticketing systems (e.g., LinkedIn support incident 260209-021351).

## Sent Email Corrections (MANDATORY)

🚨 **NEVER resend or correct a sent email without user approval.**

Once an email is sent, the recipient has it. Archiving on our end does NOT undo delivery. Rules:

1. **Wrong thread / wrong content / wrong address discovered after send:** Report the problem to user. Do NOT auto-resend a corrected version — that creates duplicates for the recipient.
2. **User decides:** They may say "resend corrected," "leave it," or "I'll handle it manually." PA waits.
3. **Never assume archiving fixes a misfired email** — archiving is local cleanup, not a recall.
4. **If user approves a correction resend:** Acknowledge in the corrected email that it's a resend (e.g., "Resending — previous email went to wrong thread, please disregard").

**Why:** Duplicate emails confuse recipients, look unprofessional, and can't be unsent. The blast radius of a correction can be worse than the original mistake.

## Delegation Emails — Self-Sustaining Threads

**SSoT for delegation pattern:** `~/.claude/skills/delegation/SKILL.md`. Read it. This section adds email-specific rules on top.

When the email being composed **asks someone to do something** (fix a bug, provide credentials, debug an issue, review a PR — anything with a deliverable), it is a delegation email and MUST include:

### 1. Definition of Done (in the email body)

Explicit, measurable conditions. The recipient should know exactly when they're done. Not "please look into this" — instead: "Done when: (1) bot responds to messages in chat X, (2) root cause identified, (3) creds sent via WhatsApp."

### 2. Callback Instructions (in the email body)

Tell the recipient what to reply with upon completion. This makes the thread self-sustaining — no external tracking needed.

```
When done, reply to this thread with:
- [Result/deliverable]
- [Any follow-up info needed]

My next step after your reply: [what requester will do]
```

**Why "my next step":** When the reply lands, whoever reads the thread (user or Claude Code PA) can immediately execute the next action without digging through external trackers. The thread carries its own memory.

### 3. Thread Self-Sustainability Principle

The goal: **anyone reading just this email thread can reconstruct the full context and next actions.** No Google Tasks entry, no separate Trello card, no "I'll remember to follow up." The thread IS the tracker.

This means:
- DoD is in the thread (what "done" looks like)
- Callback is in the thread (what to reply with)
- Next action is in the thread (what happens after reply)
- If the recipient forgets to include the callback, Claude Code PA can reconstruct it by reading the thread history

### When NOT to force delegation structure

- Fire-and-forget informational emails ("FYI, trunk-based CI/CD is now live")
- Trivial ack emails ("Done, secrets are set")
- Emails where no action is expected from the recipient

Only apply when there's a deliverable you're waiting for.

## Internal Emails (to GR team, @yourcompany.com)

- **Remove pre-filled signature** - select all in compose body, delete, then type draft
- **First line:** `Hey <Name>, <OWNER>'s ClaudeCode here.`
- Then the actual message content
- No signature needed (it's clearly from PA)
- **Attach relevant evidence:** If user has screenshots, chat logs, or examples that illustrate the issue - ask user to attach them or offer to attach if available. Concrete examples > abstract descriptions.

## Conciseness First (Internal Messages — MANDATORY)

🚨 **Minimize noise in both directions.** Team members are busy. Every sentence they have to read costs attention.

- **Task-completion replies:** Just say "Done." — no implementation details, no recap of what changed. They reported a problem, we fixed it, end of story.
- **Only include details the recipient needs to act on.** If they don't need to change behavior or make a decision based on what changed, don't explain what changed.
- **Ask yourself:** "Does the recipient care about this, or am I just showing my work?" If the latter, cut it.
- **Details on request only.** If they ask "what did you change?" — then explain.

**Examples:**
| Situation | Reply |
|-----------|-------|
| Bug report, we fixed it | "Done." |
| Credentials request, we set them | "Done." |
| Fix requires THEIR action to verify | "Fixed, please verify [specific thing]." |
| They asked a question | Answer the question. Nothing more. |

## Directive Tone (Internal Messages)

🚨 **Tell, don't ask.** When communicating decisions or instructions to employees/team members:
- **Give directives** — state what needs to happen, not what "could" happen
- **Never offer to discuss** — if the decision is made, it's not a consultation
- **No trailing questions** — "Want to discuss?" / "Should this be a separate ticket?" / "What do you think?" are prohibited when the message conveys a decision
- **Subordinates execute, they don't get vote** — PA drafts messages that reflect the CEO's authority, not a peer collaboration

Bad: "The API should pull from the DB. Want to discuss the migration approach, or should this be a separate ticket?"
Good: "The API should pull from the DB. Migrate the pricing data from the Sheet to the website database."
