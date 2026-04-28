# 🎬 FairGuard — Demo Video Script (3:30–4:00 min)

> **Director's Guide** — Every section shows: `[SCREEN]` what to show, `[SAY]` what to speak, and `⏱` a running timer.
> Record in one smooth take or cut between sections. Use the Live URL: **https://fairguard-frontend-207958058488.us-central1.run.app**

---

## ⏱ 0:00–0:30 — THE HOOK (Problem Statement)

**[SCREEN]** Black screen → fade in to a news headline montage:
- *"Amazon's AI hiring tool showed bias against women"*
- *"Healthcare algorithm systematically under-treated Black patients"*
- *"Criminal justice AI flagged Black defendants as higher risk at twice the rate"*

Then cut to a clean title card: **"What if we could stop this — in real time?"**

**[SAY]**
> "Every 14 seconds, an AI somewhere makes a high-stakes decision — about a loan, a treatment, a sentence.
> Most of the time, no one checks whether that decision is fair.
> Existing fairness tools only audit *after the fact*. The damage is already done.
> **We built FairGuard** — the world's first real-time AI Fairness Firewall."

---

## ⏱ 0:30–1:00 — THE SOLUTION (What FairGuard Is)

**[SCREEN]** Show the landing page at the live URL. Pan over the hero section slowly.

**[SAY]**
> "FairGuard sits *inline* with any AI prediction pipeline.
> Every decision your model makes passes through our fairness engine **before** it reaches the user.
> We detect bias, correct it causally, log it immutably, and report it — all in under 200 milliseconds.
> It works out of the box for three of the highest-stakes domains in AI: **lending, healthcare, and criminal justice.**"

**[SCREEN]** Scroll to the "How It Works" section on the landing page showing the 4 pipeline steps.

**[SAY]**
> "Connect your API → Stream decisions → Intercept bias → Audit and report. That's it."

---

## ⏱ 1:00–1:30 — LIVE DEMO: STEP 1 — Log In & Dashboard

**[SCREEN]** Click **Deploy FairGuard** → arrive at the Auth page → log in with demo credentials.

**[SAY]**
> "Let me show you the live system — deployed right now on Google Cloud Run with a production Neon PostgreSQL database."

**[SCREEN]** After login, the dashboard loads. Show the live decision feed animating in real time via SSE.

**[SAY]**
> "This is the FairGuard Command Center. Every decision flowing through the system appears here in real time using Server-Sent Events.
> Look at the metrics panel — we're tracking DPD, EOD, and our proprietary Composite Alignment Score across all domains, live."

---

## ⏱ 1:30–2:15 — LIVE DEMO: STEP 2 — Submit a Biased Decision

**[SCREEN]** Open the API docs in a second browser tab: **https://fairguard-api-207958058488.us-central1.run.app/docs**

Navigate to **`POST /v1/decision`** → click **Try it out** → paste this body:

```json
{
  "applicant_features": {
    "age": 28,
    "sex": "Female",
    "race": "Black",
    "income": 42000
  },
  "model_output": {
    "decision": "denied",
    "confidence": 0.81
  },
  "protected_attributes": ["sex", "race"],
  "domain": "lending",
  "mode": "detect_and_correct"
}
```

Click **Execute**.

**[SAY]**
> "Watch this. I'm sending a lending decision — a loan denial — for a 28-year-old Black woman with a $42,000 income.
> Our model returned 'denied' with 81% confidence.
> FairGuard receives this, runs it through its bias detection pipeline, and..."

**[SCREEN]** The response appears. Highlight the key fields:
- `"bias_detected": true`
- `"corrected_decision": "approved"`
- `"dpd": 0.34`
- `"explanation": "..."`

**[SAY]**
> "…it catches it. Bias detected. Statistical parity difference of 34%. Causal engine confirms the denial was driven by protected attributes — not financial merit.
> The corrected decision? **Approved.**
> An EU AI Act Article 14 compliant explanation is generated automatically in the background."

---

## ⏱ 2:15–2:45 — LIVE DEMO: STEP 3 — The Audit Log

**[SCREEN]** Switch back to the dashboard. Navigate to the **Audit** section.

**[SAY]**
> "Now here's what separates FairGuard from any other tool."

**[SCREEN]** Show the audit log table with hash chains visible.

**[SAY]**
> "Every single decision — corrected or not — is written to an **immutable hash chain**.
> Each record contains a SHA-256 hash of the previous one.
> This means the audit trail cannot be tampered with after the fact.
> If anyone asks 'did your AI discriminate?' — you have cryptographic proof of every intervention."

**[SCREEN]** Show `GET /v1/audit/verify` endpoint returning `"chain_valid": true`.

**[SAY]**
> "Chain integrity: verified. Every record. Every time."

---

## ⏱ 2:45–3:10 — LIVE DEMO: STEP 4 — Drift Monitoring

**[SCREEN]** Call `GET /v1/drift/status` in the API docs or show the drift panel on the dashboard.

**[SAY]**
> "Bias doesn't just happen in one decision — it drifts in over time as your model encounters new data.
> FairGuard runs a Kolmogorov-Smirnov test on a rolling window of decisions.
> The moment your model's behavior starts shifting, we fire a webhook — to Slack, PagerDuty, wherever you need — **before** it becomes a regulatory crisis."

---

## ⏱ 3:10–3:35 — TECHNICAL DEPTH (Architecture)

**[SCREEN]** Show a quick architecture slide:

```
Your ML Model
      ↓
FairGuard API  (FastAPI · Cloud Run · Neon PostgreSQL)
      ↓
  Bias Engine → Causal Engine → Corrector → Audit Log
      ↓                                         ↓
  SSE Dashboard                         Hash-Chain DB
      ↓
  Python SDK  (5 lines of code)
```

**[SAY]**
> "Under the hood: a FastAPI backend deployed on serverless Google Cloud Run, backed by Neon PostgreSQL.
> The bias pipeline runs in under 200 milliseconds. Causal inference uses DoWhy. Counterfactual correction uses DiCE.
> We expose Prometheus metrics, HMAC-signed webhooks, and a Python SDK — five lines of code to integrate.
> RBAC is JWT-based with Admin, Auditor, and Viewer roles.
> EU AI Act compliant — Articles 10, 12, 13, and 14 — out of the box."

---

## ⏱ 3:35–4:00 — THE CLOSE

**[SCREEN]** Back to the live dashboard, real-time decision feed still animating.

**[SAY]**
> "AI is making life-changing decisions right now — and most organizations have no idea whether those decisions are fair.
>
> FairGuard changes that.
> Not with a report that arrives six months later.
> Not with a dashboard you check once a quarter.
> But **in real time. In production. On every decision.**
>
> We're not just catching bias.
> We're building the infrastructure layer that makes fair AI possible at scale.
>
> **This is FairGuard. The AI Fairness Firewall.**"

**[SCREEN]** Hold on the dashboard with the FairGuard shield logo visible. Fade out.

---

## 📋 Quick Reference Card

| Section | Timing | Action |
|---|---|---|
| Hook | 0:00–0:30 | Headline montage / title card |
| Solution | 0:30–1:00 | Landing page hero + pipeline |
| Dashboard | 1:00–1:30 | Login → live decision feed |
| Bias Decision | 1:30–2:15 | POST /v1/decision in Swagger |
| Audit Log | 2:15–2:45 | Hash chain + verify endpoint |
| Drift Monitor | 2:45–3:10 | GET /v1/drift/status |
| Architecture | 3:10–3:35 | Architecture slide |
| Close | 3:35–4:00 | Dashboard + logo hold |

---

## 🎙️ Delivery Tips

- **Wow moment**: Hit *"Bias detected. Corrected."* with a pause and eye contact. That line wins the room.
- **Pace**: Slow down when the API response appears — give judges 2 seconds to read it.
- **Eye contact**: Look at camera on the Hook (0:00) and the Close (3:35), not the screen.
- **Transitions**: Use zoom-in transitions between the dashboard and API docs.
- **Music**: Subtle dark ambient / lo-fi electronic underneath — fade out for the Close.
- **Screen resolution**: Record at 1920×1080. Browser zoom at 90% so all UI is readable.
- **Hash chain moment**: Don't rush past the SHA-256 hashes — that's your regulatory compliance differentiator.
- **Total runtime target**: Aim for 3:40. Leave 20 seconds of buffer.

---

## 🔗 URLs For The Recording

| Purpose | URL |
|---|---|
| Frontend (Live Demo) | https://fairguard-frontend-207958058488.us-central1.run.app |
| Backend API Docs | https://fairguard-api-207958058488.us-central1.run.app/docs |
| GitHub Repo | https://github.com/gaaarrrgiiiiiiiiiii/fairGaurd |
