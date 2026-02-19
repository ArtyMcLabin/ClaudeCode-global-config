---
name: research-sop
description: Research methodology using Claude Code + Perplexity. Use when conducting competitive research, market analysis, person/lead research (pre-call prep, "who is this person", background checks), or any external research that requires verification. Core principle - Unknown is better than bullshit.
triggers:
  - "research alternatives"
  - "compare * vs *"
  - "evaluate competitors"
  - "find options for"
  - "what are the alternatives"
  - "market research"
  - "competitive analysis"
  - "deep research"
  - "Perplexity"
  - "search who is"
  - "research this person"
  - "look up this lead"
  - "who is this"
  - "background check"
  - "before the call"
  - "sales call prep"
user-invocable: false
---

# Research SOP Skill

Standard Operating Procedure for conducting research using Claude Code and Perplexity.

## Core Principle: "Unknown is Better Than Bullshit"

**NEVER fill in data you haven't verified.** Mark unverified fields as "Unknown" rather than guessing or assuming.

- ❌ Bad: "Audio Transcription: No" (assumed because research didn't mention it)
- ✅ Good: "Audio Transcription: Unknown" (honest - we didn't verify)

Reasoning: False data causes bad decisions. "Unknown" signals a gap that can be filled later with actual research.

---

## Tool Comparison: Claude Code vs Perplexity

### Claude Code - Best For:

| Strength | Use Case |
|----------|----------|
| **Codebase analysis** | Extracting current technical capabilities from YOUR repos |
| **Context retention** | Multi-step tasks where context builds over time |
| **File operations** | Reading, writing, organizing research outputs |
| **Data processing** | Parsing research results, populating spreadsheets |
| **Tool orchestration** | Combining multiple tools (rclone, bash, APIs) |
| **Verification** | Cross-checking claims against actual code/docs |

**Limitations:**
- Knowledge cutoff (can't access real-time web data reliably)
- WebFetch/WebSearch are limited compared to dedicated search
- Can hallucinate if asked to "research" without actual sources

### Perplexity - Best For:

| Strength | Use Case |
|----------|----------|
| **Deep web research** | Finding current info about competitors, markets, trends |
| **Citation tracking** | Provides sources for claims (verify them!) |
| **Real-time data** | Pricing, funding rounds, recent announcements |
| **Broad exploration** | "Who else does X?" type queries |
| **Multi-source synthesis** | Combining info from many websites |

**Limitations:**
- No access to YOUR codebase or private data
- Can still hallucinate or misinterpret sources
- Citations need verification - not always accurate
- Lacks context about your specific product/situation

---

## Research Workflow SOP

### Phase 1: Define What You Know (Claude Code)

Before external research, scan your own repos to establish ground truth:

```
Scan [your repos] to extract current technical state:
- What's implemented vs planned
- Actual capabilities (not marketing claims)
- Architecture and technical decisions
```

This prevents drift from reality and gives Perplexity accurate context.

### Phase 2: External Research (Perplexity)

Craft prompts that:
1. **Provide your context** - What you're building, your capabilities
2. **Ask specific questions** - Not "tell me about X" but "does X have feature Y?"
3. **Demand sources** - "Cite documentation or say 'Not documented'"
4. **List exclusions** - What's NOT relevant to avoid noise

**Prompt template:**
```
Research [topic] for [your context].

## My Current State
[Paste output from Phase 1]

## Specific Questions
For each [entity], verify:
1. [Specific capability] - cite source
2. [Specific capability] - cite source

## Rules
- If not explicitly documented, say "Not documented"
- Do not assume or infer
- Provide URLs for all claims
```

### Phase 3: Verify & Populate (Claude Code)

Take Perplexity output and:
1. **Cross-check claims** against cited sources if critical
2. **Mark unverified as "Unknown"** - don't propagate assumptions
3. **Populate structured storage** (spreadsheet, database, etc.)
4. **Note sources** for future verification

---

## Red Flags: When Research is Going Wrong

| Red Flag | Problem | Fix |
|----------|---------|-----|
| All cells filled, no "Unknown" | Likely assumptions | Audit each cell for evidence |
| Same value for all rows | Copy-paste without verification | Check each entity individually |
| No sources cited | Claims are unverified | Ask for citations or mark Unknown |
| Research contradicts your code | Either research is wrong or code changed | Verify against actual implementation |
| "Seems like" / "Probably" | Speculation not fact | Mark as Unknown |

---

## Data Quality Tiers

When populating research data, categorize confidence:

| Tier | Meaning | Action |
|------|---------|--------|
| **Verified** | Confirmed from official docs/code | Use as fact |
| **Reported** | From credible source (press, reviews) | Note source, use cautiously |
| **Inferred** | Reasonable assumption, no direct evidence | Mark as "Unknown" or note assumption |
| **Unknown** | No evidence either way | Leave blank or mark "Unknown" |

---

## Reusable Research Artifacts

After research, save:
1. **Raw Perplexity outputs** - For future reference
2. **Structured data** - Spreadsheet/database with sources
3. **Research prompts** - So you can re-run with fresh data
4. **Assumptions log** - What you assumed and why (to verify later)

Location convention:
- Project-specific: `[project]/docs/research/`
- Competitor research prompts: `[project]/docs/competitor-research-prompt.md`

---

## Person / Lead Research

Researching a specific person (sales lead, contact, candidate) is a distinct workflow from product/market research. Follow this procedure.

### Identity Verification Rule

**Never assume a search result IS the target person.** Common names yield multiple people. A LinkedIn/ZoomInfo/RocketReach profile is **Unmatched** until corroborated.

| Evidence Type | Strength | Example |
|---------------|----------|---------|
| **Unique identifier match** | Strong | Same email handle, same phone, same company + role from your source |
| **Photo match** | Strong | Profile photo matches known photo (WhatsApp, email avatar, Facebook) |
| **Self-referencing content** | Strong | Person's own post/bio confirms details from your source |
| **Name + country + industry** | Weak | Common names have many matches — NOT sufficient alone |
| **Name + job title** | Weak | Job titles change, multiple people share titles |

- ❌ Bad: "LinkedIn shows X as CEO at Y" (assumed match, no corroboration)
- ✅ Good: "Found LinkedIn profile for 'X, CEO at Y' — **Unmatched** to our lead. No unique identifier overlap."

### Tool Selection: Perplexity First

**Person research = external entity research → Perplexity is the primary tool.**

WebSearch/WebFetch are insufficient:
- Limited result depth, can't synthesize across sources
- LinkedIn blocks WebFetch (HTTP 999), ZoomInfo/RocketReach return 403
- Facebook posts behind login walls

**Execution:** Use chrome-agent to run queries via Perplexity UI at https://www.perplexity.ai/. Enable Pro Search if available.

### Person Research Prompt Template

```
Research the person "[Full Name]" ([name in other scripts if applicable]) from [Country].

Known facts (from direct communication):
- [Phone/email/handle]
- [Context: where they were found, what they said]

Specific questions (cite sources for each):
1. Full name, location, current role/company
2. Professional background (previous companies, roles)
3. Education
4. Relevant domain experience ([VR/AI/whatever is relevant])
5. Social media profiles (LinkedIn, GitHub, Facebook, Twitter)
6. Any funding, press mentions, or public presence for their projects
7. [Project-specific questions]

Rules:
- If not explicitly documented, say "Not documented"
- Do not assume or infer
- Provide URLs for all claims
- Note: there may be multiple people with this name — distinguish between them
```

### Output Format

Present with confidence tiers from the start. Two tables:

**Table 1: Verified (from direct communication)**
| Data Point | Value | Source |

**Table 2: External Research (requires identity match)**
| Data Point | Value | Confidence | Match Evidence | Source |

Confidence tiers: Verified / Reported / Unmatched / Unknown.
"Unmatched" = found data about someone with this name, can't confirm it's the same person.

End every brief with:
1. What you can confirm (direct sources only)
2. What remains Unknown
3. Recommended questions for the call/meeting to fill gaps

---

## Quick Reference

**Use Claude Code when:**
- Analyzing your own code/repos
- Processing and organizing research outputs
- Need multi-step workflows with context
- Populating spreadsheets/databases

**Use Perplexity when:**
- Researching external entities (competitors, markets)
- Need current/real-time information
- Want cited sources
- Broad exploration of a topic

**Always:**
- Mark unverified data as "Unknown"
- Note sources for claims
- Re-verify before major decisions
- Update research periodically (quarterly minimum for competitors)
