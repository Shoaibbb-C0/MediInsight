# Pre-deployment verification — 18 October 2026

**Ready for manual Supabase integration; not production-ready.** No Supabase cloud project was created/connected, no remote migration applied, no deployment performed. See [the exact manual runbook](../FINAL_MANUAL_SETUP.md).

## Current verified results

- Python 3.14 backend: **160 passed, 0 failed**. Includes real image/scanned PDF OCR, source/uncertainty/range regression cases, authentication failures/cookies/refresh/logout, owner isolation, local identity restart, Supabase REST contract mocks, nutrition constraints/swaps/localization, provider ranking/error states and consultation consent.
- Frontend Vitest: **17 passed, 0 failed**. Includes rejected verification, session refresh deduplication/expiration, report-consent reset and multilingual contact flow.
- Ordinary local Playwright Chromium: **29 passed, 0 failed**. Full source-file → verification → questionnaire → report → nutrition → swap → mocked-provider consultation → actual PDF → history/reload journeys pass in English/Hindi/Marathi. Camera permission-denial/file fallback processes both selected pages through real OCR.
- Requested widths 320, 375, 390, 430, 768, 1024, 1440 and 1920 covered; additional 360/1280 checks retained. Keyboard focus, modal Tab/Escape/restore, reduced motion, named controls and 200% font-size reflow pass in three languages. These are automated checks, not an exhaustive accessibility certification.
- Production frontend build: PASS. Dependency checks: pip check passes; npm audit and pip-audit reported zero known vulnerabilities. Pinned HarfBuzz and complete bundled Noto fonts fix mixed Latin/Indic PDF shaping; the final combined backend/UI/build/browser run passes.
- Direct Uvicorn on 8001 and Vite proxy on 3000: `/api/v1/auth/configuration` both return 200 in explicit local mode. Before repair, direct backend returned 200 while Vite targeted absent port 8000 and returned an empty 500. This was a proxy connection mismatch, not an exception raised by the configuration endpoint.
- Model/runtime preparation initializes the trusted extractor, bundled PDF fonts and OCR assets. English/Hindi/Marathi PDFs are rendered and source Latin units/text bounds checked; Hindi output visually inspected after enabling Indic shaping. Professional language/clinical review remains pending.

## Repairs and evidence boundaries

| Area | Implemented repair | Remaining boundary |
|---|---|---|
| Local environment | Configurable Vite backend URL/port; 8001 default; PowerShell startup/test scripts using npm.cmd/npx.cmd/venv Python; explicit environment-file paths | Operator must select supabase mode for manual cloud integration |
| Auth/configuration | Local mode explicit; persistent signed development identity; production fail-closed; reject malformed/partial/secret-key settings; controlled upstream errors; secure production cookies; refresh/logout tests | Actual Supabase token/RLS/session acceptance not executed |
| Persistence | Owner-keyed SQLite; verified patient JWT for Supabase REST; no production/local cloud fallback; controlled malformed responses and closed SQLite connections | Real PostgreSQL execution, backup/retention and deployment persistence checks pending |
| Migrations | Review all five ordered scripts; hardening retains historical schemas while revoking unused Data API access; owner USING/WITH CHECK and anonymous claim exclusion; pending appointment defaults | No local PostgreSQL/Docker executable was available, so execution/real RLS is a manual gate |
| Report pipeline | Wire uncertain readings into actual verification; save only after successful backend response; keep missing/ambiguous intervals unverified; process every selected camera page; bounded raster/image/upload sizes | Representative hospital layouts, source-language scans and physical phone cameras unverified |
| Clinical safety | Remove fixed vitamin D example from real pattern synthesis; use source classifications; exclude uncertain/nonfinite readings; no generic healthy-result fabrication; compatible interval/unit/history checks; duplicate readings do not inflate baselines | Qualified clinical review required; classifier trained on synthetic text corpus |
| PDF safety/localization | Escape patient text before PDF markup; prevent image/URL injection; embed fonts with HarfBuzz shaping; localized review/error/metadata strings | Human native-language and clinical review still required |
| Nutrition | Actual source signals/preferences score seven distinct daily combinations; enforce allergy restrictions across selected/alternative/swapped meals; unsupported contexts refused; require real-report safety answers; preserve swaps when changing language | Educational catalogue, not nutrient-calculated treatment; ingredients/portions need dietitian validation |
| Doctors | Default to report-related specialty; selectable suggested specialties with source reason; actual Google rating/count fields; rating/review-count/distance sorting; unrated remains unknown; Panvel/rural tests; incomplete/network/quota/auth/ambiguous-location handling | No live Google credentials; no verified contact/coverage or professional registration claim |
| Consultation | Evidence-backed supported contact routes only; user-selected report; unchecked explicit local PDF consent; no automatic sharing | No real booking scheduler; confirmed appointments/reminders/rescheduling/cancellation are not available |
| UI/accessibility | Preserve orange-red design; repair 768px header overflow, blank demo button, enlarged-text navigation reflow and nested modal focus; retain only language preference in browser storage | Original PPT not present in current workspace for a new direct comparison; established design preserved |
| Hosting | Remove unverified proxy target; configuration command verifies real backend before writing Vercel rewrites; Vercel build guard; correct Python root/startup/health; prepare models during build; CI adds isolated browser job | Actual cloud setup, CI/Linux execution status, hosting/cookies/load/monitoring remain unverified |

## Explicitly local/mocked provider verification

Contract tests cover Mumbai, Pune, Thane, Kalyan, Nashik, Nagpur, Chhatrapati Sambhajinagar, Kolhapur, Solapur, Amravati, Yavatmal, Pusad, Nanded, Ratnagiri, Gadchiroli, Panvel, New Panvel, Karjat, Mangaon and Digras. They preserve the requested place without substituting Mumbai and test failure/empty states. They do not establish live coverage or phone accuracy.

Google receives only the explicitly selected generic specialty and location; never the report/document/abnormal measurements. Ratings are source business reviews, not medical-quality certification. Capability registry records require independently checked HTTPS evidence and a recent review date; a phone number does not enable WhatsApp. No confirmed booking is manufactured.

## Browser policy history

Earlier in-app browser access remained denied by its saved origin policy. The latest user brief explicitly authorized ordinary local Playwright execution. The normal runner initially lacked its Chromium binary; installation and standard execution then succeeded. No managed policy/config was changed, no raw-CDP/alternate-origin workaround was used. Initial executed tests exposed actual failures and selectors; those were fixed and the suite rerun. Current browser results are executed results, not enumerated-test claims.

## Outstanding real-world gates

Manual Supabase project setup/migration execution and two-user RLS/session acceptance; Google billing/restricted keys, real local listings/maps/contacts; actual provider scheduling agreement/API if booking is desired; representative de-identified clinical corpus and qualified clinician/dietitian/native-language review; hardware camera checks; authorized deployment, cookie/proxy/upload/latency acceptance and operations/privacy/retention monitoring. No formal Codex Security scan, clinical certification, load certification or legal compliance approval is claimed.

Rate limiting remains process-local, and synchronous production persistence calls need concurrency validation before scaling. Raw source files are not retained by this implementation; stored provenance remains available after reload, while original previews require the current upload session. Local signing material/data must stay in a private directory and out of Git/shared backups. History is based on upload timestamps until document dates can be independently extracted/verified.

Ignored `artifacts/` and `frontend/test-results/` hold synthetic diagnostics/screenshots/PDFs. They contain no real patient documents or operator credentials and are not committed. Historical PPT/design audit documents are historical evidence; this audit and the current runbook supersede their setup/test-count statements.
