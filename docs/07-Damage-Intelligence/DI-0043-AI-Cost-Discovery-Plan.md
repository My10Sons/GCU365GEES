# DI-0043 — Gemini Analysis Cost-Discovery Plan

**Status:** Operational plan
**Owner:** Damage Intelligence
**Goal:** Determine the **real SAR cost per Trip Inspection** on Gemini via the Emergent
Universal Key, and turn it into a cost model we can plug into the budget (`costPer1kTokens`).
**Related:** DI-0041 (Maintenance cost interface), DI-0042 (scaling), AI Usage dashboard + token
telemetry changelog (2026-07-02).

---

## 1. What we already have

- **Real token telemetry per inspection** — every analysis records input/output/total tokens and
  AI-call count (from the Gemini response `Usage`), visible on **AI Usage** and in the audit log.
- **Two cost levers** already measurable: **mode** (Fast=Flash vs Thorough=Pro) and **number of
  angles** (each area = 1 call; escalated areas add a Pro call).

## 2. The one unknown

Emergent does **not publish** an exact per-token price for the Universal Key (confirmed with
support). So the missing number is: **SAR (or credits) per 1,000 tokens**, per model, and how
**image tokens** are counted. We get this two ways, run in parallel.

---

## 3. Track A — Ask Emergent (authoritative rate)

Email **support@emergent.sh** (include Job ID + production URL). Ask for:
1. Per-1M-token (or per-1K) price for **`gemini-3.5-flash`** and **`gemini-3.1-pro-preview`** via
   the Universal Key (input vs output token pricing if they differ).
2. How **image inputs** are converted to tokens (per-image / per-tile formula).
3. Whether there is any **markup** over Google's list price.
4. The **credit → SAR** conversion (e.g. $1 ≈ 5 credits) and where per-call cost is itemised.

*(Draft email is in §6.)*

## 4. Track B — Empirical measurement (real cost, no rate needed)

This yields the true cost even if the rate stays unpublished.

### 4.1 Setup
- Use a **non-production tenant** (or a quiet window) so no other AI usage pollutes the balance.
- Freeze the variables: same photos, same image size, same angles per run.
- Record the **Universal Key balance** at Profile → Universal Key (start/end of each block).

### 4.2 Scenario matrix (run each block back-to-back)

| # | Scenario | Runs | What it isolates |
|---|----------|------|------------------|
| 1 | Fast, 1 angle (Front), no damage | 10 | Baseline Flash cost / call |
| 2 | Fast, full 5-angle walkaround, no damage | 10 | Flash cost for a real inspection |
| 3 | Thorough, full 5-angle walkaround | 10 | Pro cost for a real inspection |
| 4 | Fast, 5-angle, with clear high-severity damage | 10 | Flash + auto-escalation (extra Pro calls) |

For each block record: **balance before**, **balance after**, and **total tokens** (sum the AI
Usage dashboard delta, or the audit `totalTokens` for those runs).

### 4.3 Derive the numbers
- **Cost per block** = balanceBefore − balanceAfter (convert credits→SAR).
- **Cost per inspection** = costPerBlock ÷ runs.
- **Effective cost per 1K tokens** = costPerBlock ÷ (blockTokens ÷ 1000).
  - Compute separately for Flask-only (blocks 1–2) and Pro (block 3) to get **per-model** rates.
- Cross-check Track A's quoted rate against the measured effective rate.

### 4.4 Expected shape (from telemetry already collected)
- Single Fast front-angle ≈ **~4,000 tokens** (mostly image input).
- Full 5-angle Fast ≈ **~20,000 tokens**; Thorough (all-Pro) similar token count but **higher $/token**.
- Escalation adds one Pro call only for uncertain/high-severity areas.

---

## 5. Deliverable — the cost model

A small table we can rely on and reuse:

| Mode / scenario | Avg tokens | SAR / inspection |
|---|---|---|
| Fast, 5-angle | ~20k | (measured) |
| Thorough, 5-angle | ~20k | (measured) |
| Fast + escalation | ~20k + | (measured) |

Then:
- Enter the derived **cost per 1K tokens** into the **AI Usage → budget** field so the dashboard
  shows live SAR estimates + projections.
- Multiply avg cost/inspection × expected monthly inspection volume → **monthly forecast** and a
  sensible **monthly token budget**.

---

## 6. Draft email to Emergent (Track A)

> **Subject:** Universal Key per-token pricing — Job ID <your-job-id>
>
> Hi Emergent Support,
> My deployed app (production: https://damage-cases.emergent.host) uses the Universal Key to call
> Gemini vision models `gemini-3.5-flash` and `gemini-3.1-pro-preview` for image analysis.
> To forecast cost I need: (1) the per-1M (or per-1K) token price for each of those two models via
> the Universal Key, input vs output if different; (2) how image inputs are counted as tokens;
> (3) whether there's any markup over Google's list price; (4) the credit→USD/SAR conversion and
> where per-call cost is itemised. Thank you.

---

## 7. Optional app support for the measurement
- A **date-range filter** on AI Usage already lets you isolate a test window.
- (Optional build) A "usage since timestamp" readout or CSV export of the audit token rows to make
  Track B's token totals one click instead of summing the daily chart.
