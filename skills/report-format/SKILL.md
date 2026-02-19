---
name: report-format
description: Base format for all report-style outputs (audits, triages, reviews). Defines item identification, severity sections, BLUF structure, and voice-friendly naming. Use when creating or modifying any skill that produces a report. Other report skills inherit from this.
user-invocable: false
---

# Report Format (Base)

All report-style skills (audit-common, task-triage, employee-audit, etc.) inherit this format. Each consumer may override specific sections but must preserve the base principles.

## Principle: Every Item is Uniquely Addressable

Reports are discussed in voice and text. "About three" must never be ambiguous. Every item gets a globally unique identifier within the report. Numbers NEVER restart between sections.

## Item Identification

**Default: Adjective+Food names by severity category (STT-friendly):**

| Severity | Names |
|----------|-------|
| 🔴 Critical/Urgent (red foods) | Spicy Tomato, Crispy Pepper, Blazing Chili, Red Cherry, Hot Salsa, Smoky Beet |
| 🟡 Warning/Important (yellow foods) | Golden Mango, Sunny Lemon, Tangy Orange, Warm Honey, Ripe Peach, Bright Corn |
| 🔵 Long Term/Info (blue foods) | Frosty Blueberry, Icy Grape, Misty Plum, Cool Fig, Deep Prune, Calm Olive |
| 🟢 Low Risk/Quick Win (green foods) | Fresh Apple, Minty Kiwi, Zesty Lime, Crisp Pear, Juicy Melon, Green Basil |

**Override: Severity-prefixed sequential (for technical reports):**

`C1`, `C2`, `W3`, `W4`, `I5` — where prefix = severity, number = global sequence.

| Prefix | Severity |
|--------|----------|
| `C` | 🔴 Critical |
| `W` | 🟡 Warning |
| `I` | ℹ️ Info |

**Consumer declares which scheme it uses.** Both are valid. Key rule: IDs are globally unique within the report.

## Section Ordering

Severity descending. Skip empty sections entirely (no "None." placeholders).

1. **🔴 CRITICAL / URGENT** — Must act now
2. **🟡 WARNING / IMPORTANT** — Should act soon
3. **🔵 INFO / LONG TERM** — Nice to know / strategic
4. **🟢 QUICK WINS / LOW HANGING** — Easy fixes (optional section)
5. **Strengths** — What's working well (brief, 3-5 bullets max)
6. **Recommendations** — Prioritized action list referencing finding IDs

## Per-Item Structure (BLUF)

Every item follows this pattern. Fields can be renamed per domain but structure is mandatory:

```
**[ID]. [Title]** · [Source/Author]
  [Platform icon]
> **Action:** [What to do — one sentence, BLUF. No context bleed.]
> **Context:** [Self-sufficient summary — reader understands without opening source]
> **Ref:** [clickable URL]
```

**Rules:**
- **Action = BLUF only** — one sentence: what the reporter proposes. No background, no explanation. All context belongs in the Context field.
- **Context = self-sufficient** — reader understands the situation without opening the source
- **Ref = clickable** — full URL, never bare IDs

## Platform Icons (optional, for multi-source reports)

| Platform | Icon |
|----------|------|
| Email | ✉️ |
| GitHub | 🐙 |
| Google Tasks | ☑️ |
| Slack | 💬 |
| Audit finding | 🔍 |
| Schedule/Deferred | ⏰ |

## Report Ending

End with `**Actions?**` — let the reader drive. Don't suggest batch actions.

## Inheritance Rules

Consumer skills declare: `> **Inherits:** report-format` at the top of their output format section. Then they state only their overrides:

```markdown
> **Inherits:** report-format

**Overrides:**
- Item identification: uses C1/W3/I5 instead of food names
- Adds: Drift protocol section
- Adds: Registry logging requirement
```

If a consumer doesn't mention a base principle, it applies as-is.
