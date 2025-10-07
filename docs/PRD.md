# Product Requirements Document (PRD)

**Title:** AI Agent for Automating Bing Ads Account Quality Check (QC)
**Authors:** Sumit Tripathy & Sasmita Mandal
**Date:** May 15, 2025
**Version:** 1.1 (refined)

---

## 0. Changelog (v1.1)

* Added **Goals & Non-Goals**, **Personas & User Stories**, **Success Metrics**, and **NFRs**.
* Expanded **QC Rule Catalog** with severities, acceptance criteria, and data sources.
* Added **Rule Engine & Config Model**, **Architecture**, **Data Schema**, **API Design**, **Security/Privacy**, **Observability**, **Rollout Plan**, **Test Plan**, **Risks**, and **Open Questions**.
* Included **sample report JSON**, **PDF outline**, and **rule YAML** examples.

---

## 1. Overview

An AI-driven agent automates QC for newly onboarded Microsoft Advertising (Bing Ads) accounts—reducing manual effort, improving consistency, and accelerating launch-readiness. It validates structure, targeting, bidding, budgets, tracking, ads, assets, and landing pages, then generates a shareable, color‑coded report with prioritized fixes.

---

## 2. Problem Statement

Manual QC is slow, variable by operator skill, and error-prone across many layers (account → campaign → ad group → ad/asset → keyword → tracking → landing pages). This causes inconsistent quality, delayed launches, and avoidable performance risks. Automated, standardized QC ensures accuracy and speed while preserving human review for judgment calls.

---

## 3. Goals & Non‑Goals

**Goals**

* Run **26+ automated checks** across account, campaign, ad group, ad, keyword, tracking, and site.
* **Flag** misconfigurations, missing elements, policy/editorial blockers, and optimization gaps.
* **Recommend fixes** with clear severity (Critical, Major, Minor) and rationale.
* **Generate shareable reports** (PDF/HTML) and machine-readable JSON.
* **Pluggable rule engine** enabling brand/team-level naming/taxonomy rules.

**Non‑Goals (v1)**

* Auto-remediation in the ad account (no write operations).
* Deep content/policy rewriting of ads.
* Site performance optimization beyond basic functional checks.

---

## 4. Scope

**In-Scope**

* QC automation for new Microsoft Ads accounts (manually built or Google-imported).
* Audit: structure & naming, keywords/negatives, ads/ad strength, assets, tracking, landing pages, UET/conversions, settings, bidding/budgets, import-specific checks.
* MS Ads API integration (read-only), headless browser for site/UET checks.
* Report generation (PDF/HTML/JSON), email share.

**Out-of-Scope (v1)**

* Shopping feed validation, Audience Network placement quality analysis, RSA creative scoring via LLM beyond basic strength metadata (plan for v1.x).
* Bulk rewrite of naming structures or mass label fixes.

---

## 5. Personas & Key User Stories

**Persona A – Account Strategist (Primary)**

* *As a Strategist*, I run QC after setup/import to ensure launch‑readiness.
* *As a Strategist*, I want severity-tagged findings with steps to fix, so I can prioritize quickly.
* *As a Strategist*, I want a downloadable report to share with my AM/Client.

**Persona B – Account Manager / Reviewer**

* *As an AM*, I need a concise summary with a pass/fail score and critical blockers.
* *As an AM*, I want history to show improvements over time.

**Persona C – Lead / QA Reviewer**

* *As a Lead*, I want customizable rules and naming templates across portfolios.

---

## 6. Success Metrics (with targets)

* **Time to QC:** Reduce average QC time per new account from 60–90 min to **<10 min** (80%+ reduction).
* **Coverage:** **100%** of critical checks executed on every run.
* **Accuracy:** **<2% false negatives** on critical checks; **<5% false positives** overall.
* **Adoption:** 90% of newly onboarded accounts run QC within 24 hours of setup/import.

* **Turnaround:** 95% of critical issues resolved within 48 hours of detection (tracked via follow‑up runs).

---

## 7. Assumptions

* Read-only access tokens to Microsoft Ads API are available.
* Account structures follow internal taxonomies that can be expressed as regex/DSL.
* Landing pages are accessible from the checker’s egress IPs.

---

## 8. High-Level Workflow

1. **Initiate QC**: Input Account ID / CID (optionally MCC) and choose ruleset (default or client-specific).
2. **Data Extraction**: Pull account, campaigns, ad groups, ads/assets, keywords & negatives, budgets, bids, settings, extensions, UET/conversions, tracking templates, final URLs.
3. **Diagnostics**: Run module checks in parallel (idempotent).
4. **Site/UET Check**: Headless browse key URLs, validate status codes, redirects, UET presence, and (if configured) goal trigger smoke tests.
5. **Score & Report**: Compute score and severity breakdown; generate HTML/PDF + JSON.
6. **Distribute**: Email link, download, or export JSON to internal dashboards.

---

## 9. QC Rule Catalog (v1)

**Severity levels**:

* **Critical (Red):** Launch blocker, data loss risk, policy/editorial block, broken landing.
* **Major (Yellow):** Material performance or measurement risk.
* **Minor (Green/Info):** Best‑practice improvement.

> Each rule lists: *Acceptance*, *Data Source*, *Auto-Fix Hint* (for human remediation).

### 9.1 Structure & Naming

1. **Campaign naming matches template** (regex list per portfolio).

   * *Accept:* All campaigns match.
   * *Source:* Campaign names.
   * *Hint:* Show mismatches and suggested rename.
2. **Ad group naming matches template**.
3. **Label hygiene (optional)**: presence of required labels (e.g., Brand/Non‑Brand, Market, Device).
4. **Campaign type alignment** (Search/Shopping/Audience) per plan.

### 9.2 Keyword Hygiene

5. **No empty ad groups** (must have ≥1 keyword or target). *(Critical)*
6. **No duplicate keywords** across account (normalized by text + match type). *(Major)*
7. **Match type coverage** within ad group per mapping rules (e.g., Exact+Phrase for core themes). *(Major)*
8. **Negative keywords configured** at campaign/ad group where applicable; **no negative conflicts** blocking active keywords. *(Major)*
9. **KW to LP intent match (LLM optional)** for top K keywords to detect misintent LPs. *(Minor → Major if systemic)*

### 9.3 Ads & Ad Strength

10. **No adless ad groups** (≥1 RSA per ad group). *(Critical)*
11. **RSA completeness**: ≥12 headlines, ≥4 descriptions; limited pinning unless required. *(Major)*
12. **Ad strength**: Aim **Good+**, flag Average/Poor. *(Major)*
13. **Editorial/Policy**: flag disapproved/limited ads or assets. *(Critical if block)*

### 9.4 Tracking & Parameters

14. **MSCLKID auto-tagging enabled** at account. *(Critical for attribution)*
15. **Tracking template validity**: macros & URL parameters valid for Microsoft Ads; no stray Google-only tokens. *(Major)*
16. **Final URL vs template consistency**; lpurl availability. *(Major)*

### 9.5 Landing Pages

17. **HTTP status**: 200 OK; flag 3xx>1 hop, 4xx/5xx, mixed content, infinite redirects. *(Critical if 4xx/5xx)*
18. **Mobile friendliness** & **TTFB/Load** basic thresholds (headless metrics). *(Major)*
19. **LP intent check** vs ad group theme (optional NLP). *(Minor)*

### 9.6 Campaign Settings

20. **Ad schedule**: 00:00–24:00 (or specified plan), flag gaps. *(Major)*
21. **Location targeting**: “People in targeted locations” or approved variant. *(Major)*
22. **Device bid modifiers** within allowed range; no -100% on primary device unless intended. *(Major)*
23. **Language** aligns with market (e.g., en‑US, ar‑SA). *(Major)*
24. **Budgeting**: Non‑zero daily budgets; appropriate delivery (Accelerated if policy permits) and pacing vs plan. *(Critical if 0 budget)*
25. **Bidding strategy**: eCPC (launch default) or approved tCPA/tROAS; surface eligibility. *(Major)*
26. **Network distribution**: Search partner inclusion per policy; flag if mismatched. *(Minor–Major)*

### 9.7 Ad Extensions / Assets

27. **Sitelinks**: ≥4 at account/campaign; with descriptions. *(Major)*
28. **Callouts**: ≥4 configured. *(Major)*
29. **Structured snippets**: ≥2 types used. *(Major)*
30. **Other assets** (call, location, price, promo) per vertical. *(Minor)*

### 9.8 UET & Conversions

31. **UET tag present** and firing on LP; dedupe multiple tags; pageview event captured. *(Critical if absent)*
32. **Conversion goals configured**; at least one assigned to campaigns in scope. *(Critical)*
33. **Goal settings**: counting type (One vs Every), attribution window, revenue tracking currency. *(Major)*
34. **No orphan goals** (configured but never fire). *(Minor)*

### 9.9 Import Audit & Budget/Bid Verification

35. **Auto‑sync disabled** post‑import (prevent overwrites). *(Major)*
36. **Currency & bid normalization** if source currency unsupported; budgets validated. *(Major)*
37. **Final URL replacement** performed; no google.com remnants. *(Major)*

### 9.10 Account Settings & Identity

38. **AIV completed** (Advertiser Identity Verification). *(Critical if required)*
39. **Time zone & currency** correct; market alignment. *(Major)*

> **Total v1 rules:** 39 (26+ requirement satisfied). Rules are togglable and weightable.

---

## 10. Scoring Model

* **Baseline score:** 100.
* **Weighted deductions** by severity (e.g., Critical −15, Major −5, Minor −2; tunable).
* **Module caps:** prevent one module over-penalizing (e.g., LP checks max −30).
* **Category breakdown:** Structure, Keywords, Ads, Tracking/LP, Settings, Assets, UET/Conv, Import, Account.
* **Pass thresholds:**

  * **Launch‑Ready:** ≥85 overall, 0 Critical, ≤3 Major.
  * **Review Required:** 70–84 or any Critical present.
  * **Fail:** <70 or ≥2 Critical.

---

## 11. User Experience (UX)

**Entry:** Account ID → choose ruleset → (optional) upload naming plan CSV → Run.
**Views:**

* **Summary Card:** Overall score, status chips (Critical/Major/Minor counts).
* **Module Tabs:** each with findings table (Rule, Severity, What we checked, What we found, How to fix, Link).
* **Export:** PDF/HTML (client‑ready), JSON (system).
  **States:** Running (progress %), Success, Partial (API errors), Failed (auth/perm).
  **History:** Past runs, diffs vs previous run.

---

## 12. Rule Engine & Config Model

* **DSL/Config** for rules (YAML/JSON) with: id, name, description, severity, regex/conditions, API sources, thresholds, remediation text, links, enabled flag, weight.
* **Portfolio presets**: global default + client overrides.
* **Versioned rulesets** with backward compatibility.

**Example (YAML)**

```yaml
- id: CMP_NAME_REGEX
  severity: MAJOR
  pattern: "^(Brand|NonBrand)_[A-Z]{2}_[A-Za-z0-9-]+$"
  source: CAMPAIGN
  remediation: "Rename to <Type>_<Market>_<Intent> per template."
  weight: 5
  enabled: true
```

---

## 13. System Architecture

**Components**

* **API Adapter (MS Ads API)**: Bulk read of entities; rate-limit aware; retry/backoff.
* **QC Orchestrator**: Kicks off modules, parallelizes checks, aggregates results.
* **Rule Engine**: Loads ruleset, evaluates expressions, applies weights.
* **Headless Checker**: Playwright fleet for LP/UET validation; collects status, redirects, UET pixel, basic perf.
* **Report Generator**: HTML/PDF (wkhtmltopdf/Chromium) + JSON.
* **Store**: Results, history, rule versions, account metadata.
* **Notifier**: Email with report links.

**Flow**
Client → Auth (OAuth 2.0) → API Adapter pulls data → Orchestrator runs modules → Rule Engine evaluates → Headless validates LP/UET → Aggregate & Score → Persist → Report → Notify.

**Performance targets**

* 50 campaigns / 500 ad groups / 20k keywords: **<8 min** end‑to‑end (p95).
* Headless checks: parallelized up to 10 URLs/sec per worker (configurable; respect robots/TTL where relevant).

---

## 14. Data Schema (relational or doc‑store)

**Entities**

* `accounts` (id, name, market, currency, timezone, aiv_status)
* `runs` (run_id, account_id, started_at, finished_at, score, status)
* `findings` (run_id, rule_id, entity_type, entity_id, severity, message, remediation, metadata_json)
* `rules` (rule_id, version, severity, weight, enabled, config_json)
* `reports` (run_id, html_path, pdf_path, json_path)

Indexes on account_id, run timestamps, severity; partition by month.

---

## 15. Public API (internal use)

* `POST /qc/run`

  * body: `{ accountId, rulesetId?, options: { sampleUrlsPerAdGroup?: 2 } }`
  * resp: `{ runId, status }`
* `GET /qc/runs/:runId` → status/progress.
* `GET /qc/runs/:runId/report` → summary + signed URLs.
* `GET /qc/runs?accountId=...` → history.
* `GET /rulesets/:id` → view; `PATCH /rulesets/:id` (admin).

**Idempotency**: `Idempotency-Key` header to avoid duplicate runs.

---

## 16. Security, Privacy, Compliance

* **OAuth 2.0** with MS identity; store refresh tokens **encrypted (KMS)**; least-privilege scopes.
* **PII:** Do not store LP page content beyond minimal telemetry (status, title, pixel presence).
* **Secrets** in vault; **audit logs** for access & runs.
* **Compliance posture:** SOC 2 controls alignment (logging, change mgmt, backups).
* **Data retention:** findings/reports retained 180 days (configurable) with purge job.

---

## 17. Observability

* **Metrics:** run time, module durations, API calls, error rates, rule hit rates, false‑positive feedback.
* **Tracing:** request‑scoped trace IDs across modules.
* **Logging:** structured JSON; entity counts; redactions for URLs/params.
* **Alerts:** API quota near limits; headless failures > threshold; report generation failed.

---

## 18. Rollout Plan

**MVP (4–6 weeks)**

* Core reads (campaigns/ad groups/ads/keywords/negatives/budgets/settings).
* 20 critical/major rules (incl. MSCLKID, LP 200 check, RSA presence, UET on LP, conversion goals exist & assigned).
* HTML report + JSON export; email delivery; single ruleset.
* Manual rules config (YAML) and basic scoring.

**v1.0 (add 4–6 weeks)**

* Full 39-rule catalog, weighted scoring, PDF export, history & diffs, portfolio presets.
* Headless perf metrics; duplicate/negative conflict detection; editorial checks.
* Basic NLP for KW↔LP intent sampling.

**v1.x**

* UI for rule management, multi-ruleset A/B, Slack notifications, custom dashboards.

---

## 19. Test Plan

**Unit**: rule evaluation, regex, scoring, URL parsing.
**Integration**: MS Ads API sandbox; pagination, retries, partial failures.
**E2E**: synthetic account fixtures (good, bad, edge).
**Headless**: site matrix (200/3xx/4xx/5xx), JS redirects, SPA routes, consent banners.
**Accuracy QA**: compare vs human QC baseline; track FN/FP.
**Performance**: load tests at portfolio scale.

---

## 20. Acceptance Criteria (samples)

* Running QC on an account with **0 ads** produces **Critical** finding `ADLESS_ADGROUPS` listing all impacted ad groups with remediation text.
* Accounts with **MSCLKID disabled** are flagged **Critical** with clear enable steps.
* If **UET missing** on sampled LPs, report shows affected URLs and evidence (no `bat.bing.com` calls).
* **PDF** report downloads under **10 seconds** for a 20-page report (p95).
* **False negatives** for Critical rules under **2%** on validation set.

---

## 21. Risks & Mitigations

* **API Quotas/Latency** → Use bulk endpoints; cache; exponential backoff.
* **LP access blocked (WAF/Geo)** → regional workers; fallback to HTTP HEAD; manual verification flag.
* **False positives on NLP intent** → keep optional; require human confirm.
* **Rule drift** → versioned rulesets; change log; controlled rollout.
* **Browser automation flakiness** → retries; deterministic selectors; timeouts.

---

## 22. Open Questions

1. Final stance on **Accelerated delivery** vs Standard for new accounts?
2. Markets requiring **multi‑language** ads & assets at launch (e.g., GCC Arabic + English)?
3. Thresholds for **mobile perf** (LCP/TTFB) acceptable at launch?
4. Desired **partner notifications** (Slack/MS Teams) in v1 or v1.x?

---

## 23. Sample Outputs

**23.1 JSON (redacted)**

```json
{
  "runId": "run_2025-05-15_12345",
  "accountId": "123456789",
  "score": 78,
  "status": "REVIEW_REQUIRED",
  "breakdown": {"critical": 1, "major": 4, "minor": 6},
  "modules": [
    {
      "module": "TRACKING",
      "findings": [
        {
          "ruleId": "MSCLKID_AUTOTAG",
          "severity": "CRITICAL",
          "entity": {"type": "ACCOUNT", "id": "123456789"},
          "message": "MSCLKID auto-tagging is disabled.",
          "remediation": "Enable auto-tagging in Account > Settings.",
          "evidence": {"autotag": false}
        }
      ]
    }
  ]
}
```

**23.2 PDF/HTML Outline**

* Cover: Account, Date, Score, Status chips.
* TOC: Modules.
* Per Module: Findings table (Rule • Severity • Entity • What we found • How to fix • Link).
* Appendix: Rule catalog summary & glossary.

---

## 24. Implementation Notes (Dev)

* Prefer **Bulk Service** reads; normalize entities into internal schema.
* **Normalization**: keyword text lowercased, trimmed, dedup by (text, matchType, adGroupId).
* **Sampling**: per ad group, test top N final URLs by spend or top keyword’s final URL.
* **Retry policy**: jittered backoff, circuit breaker per module.
* **Feature flags**: toggle NLP checks; toggle headless perf metrics.

---

## 25. Future Enhancements

* **Auto‑fix suggestions** with 1‑click drafts (requires write perms).
* **Creative linting** (policy terms, clarity, capitalization, numbers).
* **Shopping** feed diagnostics and Merchant Center parity checks.
* **Audience Network** placement heuristics & blocklists.
* **LLM‑generated client summary** page with prioritized actions.

---

## 26. Glossary

* **AIV**: Advertiser Identity Verification.
* **UET**: Universal Event Tracking (Microsoft).
* **RSA**: Responsive Search Ad.
* **DSA**: Dynamic Search Ads (future scope).
* **LP**: Landing Page.
