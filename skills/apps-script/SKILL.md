---
name: apps-script
description: Google Apps Script development best practices learned from production. Use when building Apps Script automation, payment API integrations, Google Sheets menu functions, modal dialogs, or Poka Yoke quality gates. Covers UI dialog philosophy, API field discovery, submission architecture (source_amount vs transfer_amount), clasp CLI logging, and gate flow design.
user-invocable: false
---

# Apps Script Best Practices (Learned Lessons)

NOT generic best practices. Specific philosophies discovered through production experience.

## UI Dialog Philosophy

### Modal Dialogs Block the Sheet
- `ui.alert()` and `ui.showModalDialog()` block user from interacting with the sheet
- **NEVER** tell user to "go check the sheet, then click YES" — the dialog is blocking them
- **Gate checks BEFORE dialogs**: If user needs to do something in the sheet first (check a column, fill data), verify it's done BEFORE showing the dialog. If not done, exit with instructions — don't block with a modal

### Gate Flow (Correct)
```
1. Read sheet context
2. Check gate → FAIL EARLY with specific names + column letter
3. Do expensive work (API calls, plan generation)
4. Show results + confirmation
```

### Gate Flow (Wrong)
```
1. Do expensive work
2. Show blocking modal asking user to check the sheet
3. User can't check sheet because modal is blocking
4. Check gate after user clicks YES — too late
```

### Dialog Content Rules
- Don't show counts without names. "7 missing" is useless — list the actual names
- Don't show information that's inherently obvious (e.g., pre-submission "not yet in Airwallex" for employees about to be submitted)
- Show only actionable information

## API Amount Fields — Don't Guess Names

### Discovery Protocol
When integrating with any payment/transfer API:
1. **Log ALL fields** from the first API response: `Object.keys(response).sort().join(', ')`
2. **Log amount-related fields** specifically: filter keys matching `/amount|fee|cost|charge|rate|price|settle/i`
3. **Use `clasp logs`** to read execution logs from CLI
4. Field names are often surprising (e.g., Airwallex uses `amount_payer_pays` not `source_amount`)

### Diagnostic Logging Pattern
```javascript
if (items.length > 0) {
  const sample = items[0];
  Logger.log(`[DIAG] Fields: ${Object.keys(sample).sort().join(', ')}`);
  const amountFields = Object.entries(sample)
    .filter(([k]) => /amount|fee|cost|charge|rate|price|settle/i.test(k))
    .map(([k, v]) => `${k}=${JSON.stringify(v)}`)
    .join(', ');
  Logger.log(`[DIAG] Amount fields: ${amountFields}`);
}
```

### Don't Round-Trip Through GOOGLEFINANCE
- If you convert USD->NGN via GOOGLEFINANCE at submission, converting NGN->USD via GOOGLEFINANCE for verification gives back the original amount. This is **circular and useless**
- The API response has the actual charged amount. Find that field and use it directly
- GOOGLEFINANCE rate != provider's FX rate — there's always a spread

## Submission Architecture — Source Amount vs Transfer Amount

### Who Controls the Conversion?
- **USD-sourced cross-currency**: Let the payment provider handle conversion. Send `source_amount` (exact USD to pay). Don't care what target currency amount recipient gets
- **ILS-sourced (or non-standard source)**: You DO care because you're depleting a specific balance. Convert via GOOGLEFINANCE, send `transfer_amount` in target currency
- **Same currency**: Direct — no conversion needed

### Why This Matters
Sending `transfer_amount` in target currency for USD-sourced transfers:
1. You convert $365 -> NGN 493,326 via GOOGLEFINANCE
2. Provider converts NGN 493,326 -> $370.57 via their rate (with spread)
3. You're charged $370.57, not $365 — hidden cost

Sending `source_amount` = $365: provider charges exactly $365.

## Clasp CLI Logging

```bash
clasp logs          # Plain text, most recent first
clasp logs --json   # JSON format for programmatic parsing
clasp push --force  # Deploy changes
```

- Logs available after execution completes
- Use for debugging when `clasp run` isn't configured
- `clasp run` requires API executable deployment setup — not always worth the config

## Poka Yoke Gates

- Gates are **hard stops** — function exits if gate fails
- Check gates **before expensive operations** (API calls, sheet writes)
- When gate fails: list exactly what needs to be fixed, reference column letter dynamically
- Multiple functions share same gate via shared helper (SSoT)
- Dynamic column letters: resolve from header titles, never hardcode "column P"
