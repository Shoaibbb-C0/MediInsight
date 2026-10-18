# Production readiness audit — 18 October 2026

Overall release status: **BLOCKED**. Local checks pass; live integrations, browser acceptance and clinical validation are not complete. No deployment was performed.

## Findings and implemented repairs

| Severity | Finding | Implemented resolution | Verification boundary |
|---|---|---|---|
| Critical | Requests had no verified identity or report ownership | Supabase Auth server verification; owner-scoped state; RLS migration; production fails closed | Forged-token and cross-session API tests pass. Real Supabase accounts/RLS untested |
| High | Reports and plans were process-local dictionaries | Development SQLite; production patient-JWT REST persistence; persisted history retrieval | Local owner isolation passes; remote persistence awaits credentials/migration |
| High | Restrictive meal pools could fall back to unsafe food | Removed fallback; validate dietary preferences, all selected meals, alternatives and swaps; reject unsupported constraints | Deterministic automated tests pass; catalogue/clinical review outstanding |
| High | Report signals did not meaningfully change selected meals | Score actual source findings plus dietary preference, budget and cooking context; select seven distinct safe daily combinations | Different glucose, iron, lipid, dietary and budget inputs change selected food IDs |
| High | Scanned PDF/OCR handling was broken; source metadata inferred | Per-page digital extraction or raster OCR; RapidOCR 3 API; preserve printed values, units, intervals and page/line provenance | Generated image/scanned/digital documents tested; representative hospital corpus and hardware photos untested |
| High | Unknown places silently resolved to Mumbai | Official Geocoding + Places API (New), manual location/geolocation, actual distances and radius filtering | Mocked API contract tests pass; no Google key/billing configured |
| High | Only simulated doctor booking existed | Evidence-based profile/contact options; no dates, fees, qualifications or confirmations invented; production booking API unavailable | Mocked consultation tests pass; no real scheduler exists |
| High | Medical sharing could become implicit | Report selection; explicit unchecked consent required for local preparation PDF; external links contain no report data | Consent, ownership and EN/HI/MR UI tests pass; no external report transmission implemented |
| Medium | Root-level backend deployment import path wrong | Uvicorn `--app-dir backend`, health check, locked dependencies and explicit env settings | Fresh local Uvicorn startup and HTTP health pass; hosted deployment untested |
| Medium | Dependency vulnerabilities | Updated Vitest/Tailwind and lockfile; pinned tested Python environment | npm audit and pip-audit report zero known vulnerabilities; not a security certification |
| Medium | Chunked uploads could bypass declared-size guard | ASGI byte limit plus bounded upload reads, page/image limits | Declared and chunked oversized requests return 413 |

## Executed checks

- `backend/.venv/Scripts/python.exe -m pytest -q`: **97 passed, 0 failed**. One Starlette/httpx test-client deprecation warning.
- `npm run test` in frontend: **13 passed, 0 failed**.
- `npm run build`: PASS. Tailwind 4 migration included; old-browser and visual regression acceptance remain unverified.
- `python -m pip check`: PASS. npm audit and pip-audit: no known vulnerabilities at audit time.
- Fresh Uvicorn process: `/health` returned 200/healthy; test process shut down cleanly.
- Generated English/Hindi/Marathi report and nutrition PDFs: rendered and horizontal text bounds checked; Marathi nutrition overview inspected. Safety section kept together. This does not establish clinical translation accuracy.
- Actual RapidOCR execution on a generated image and scanned PDF, plus digital PDF: glucose `124.5 mg/dL`, interval `70 - 99`; creatinine `0.9 mg/dL`, interval `0.7 - 1.3` preserved.
- Multi-page column reconstruction, distinct input values, missing-range review state and page-limit rejection covered by tests.
- Consultation subset: **20 backend + 3 UI tests = 23 passed, 0 failed**. These are local/mocked checks, not real-provider booking verification.
- Playwright: **20 scenarios enumerated; 0 executed**. The local browser origin remains denied by a saved permission/managed policy despite the user's approval. No alternate-browser workaround was used.

Ignored local `artifacts/` contains diagnostic logs, generated synthetic inputs and PDF renders; no patient documents, credentials or generated databases were committed.

## Doctor and consultation behavior

Mocked location tests cover Mumbai, Pune, Thane, Kalyan, Nashik, Nagpur, Chhatrapati Sambhajinagar, Kolhapur, Solapur, Amravati, Yavatmal, Pusad, Nanded, Ratnagiri and Gadchiroli. This verifies query preservation, distance/radius behavior and adapter contracts, **not** local coverage or real contact accuracy.

The real flow is Find providers → View profile → Consult Doctor → Choose a supported contact/external option → Contact provider. Phone comes from the source listing; a website is labeled Contact Clinic. Clinic request, online, external booking and WhatsApp links require an operator-reviewed capability record with a source URL and review date no older than 90 days. A phone number alone never enables WhatsApp. Business listing information is explicitly not verified professional registration. Missing qualifications, fees and appointment availability are omitted.

No scheduler is integrated. No local date picker, confirmed appointment, reminder, cancellation or rescheduling is presented as real. External bookings must be managed at the provider. The old simulation API remains development-only and rejects booking in production. Real booking integration: **NOT AVAILABLE**.

Preparation can select an owned report, show abnormal findings/questions, and download a local PDF only after explicit consent. Nothing is automatically sent to clinics, WhatsApp, Maps or booking sites. External links carry generic contact/location data only. Download consent authorizes local PDF inclusion, not external transmission. There is no shared-report URL or third-party storage link.

Google content is fetched on demand, not persisted in patient state. Google Maps attribution assets and returned third-party attribution are displayed. Markers use the same provider coordinates as the list. Live map loading/authentication, attribution visibility and marker interactions await browser testing. Public Terms and Privacy pages must be finalized before launching Google services, per [Google's Places policies](https://developers.google.com/maps/documentation/places/web-service/policies).

## Configuration and unavoidable release steps

1. **Supabase:** provision the intended project and test accounts, configure `SUPABASE_URL` and `SUPABASE_PUBLISHABLE_KEY` server-side, and apply `backend/supabase/migrations/20261018120946_patient_app_state.sql` through the normal migration workflow. Do not use a service-role/secret key. Test two real users against RLS, sign-in, refresh, logout, reload, restart, historical comparison and plan persistence. No remote migration was applied here.
2. **Google:** enable billing, Geocoding and Places API (New). Set restricted `GOOGLE_MAPS_SERVER_KEY` on the server. For the map, enable Maps JavaScript API and configure a separate referrer-restricted `VITE_GOOGLE_MAPS_BROWSER_KEY` and map ID using `frontend/.env.example`. Do not expose the server key. Verify real city/PIN/geolocation results and contacts in all requested locations, smaller-town empty states, quota failures, directions and markers.
3. **Provider capabilities:** independently verify supported consultation routes before supplying `PROVIDER_CAPABILITIES_FILE`. Each record is keyed by the actual Google place ID, with HTTPS `source_url`, ISO `reviewed_at`, and only supported `clinic_request_url`, `online_consultation_url`, `booking_url`, or explicitly supported E.164 WhatsApp number. No populated registry or real provider integration was invented.
4. **Browser acceptance:** resolve the app's saved origin policy and execute the prepared suite at the permitted local preview. Check real camera permission/capture, keyboard focus, EN/HI/MR layouts, all requested mobile/tablet/desktop sizes, downloads and real contact links. Component tests cannot replace this.
5. **Clinical review:** use de-identified representative hospital reports, photographed/rotated/blurred scans, mixed-page documents and CBC/qualitative layouts. Verify extraction coverage, source boxes, classifications and translated explanations with qualified reviewers. The extraction vocabulary/unit patterns are limited; unsupported/unreadable input fails rather than substituting data. The food catalogue, allergen/ingredient tags, portions and translations require dietitian review. Plans are deterministic educational meal combinations, not nutrient-calculated prescriptions; complex clinical contexts are refused.
6. **Deployment:** `render.yaml` and the CI pipeline now use the locked Python environment and correct app path. Configure exact HTTPS `CORS_ORIGINS`, a same-origin API proxy and production secrets. Verify the actual Render URL in `frontend/vercel.json`, cookie behavior through that proxy, database access and persistent deployment behavior. Pre-provision/warm OCR model assets and verify offline/model-fetch failure behavior. Deployment and hosting credentials/approval were not supplied.
7. **Operations/privacy:** finish public privacy/terms content and the service's consent, retention/deletion, backup, monitoring and incident procedures before handling real patient data. No compliance certification, load test or exhaustive security audit is claimed. Rate limits are process-local; production storage calls are synchronous, so multi-instance throttling and concurrency capacity need operational validation.
8. **Booking (optional integration):** obtain an actual provider scheduling contract/API and sandbox credentials before implementing authenticated availability, confirmed booking IDs, status/webhook verification, cancellation/rescheduling and opt-in reminders. Current contact-only fallback is intentional and must remain clearly labeled.

## Remaining boundaries

Development anonymous cookies are process-signed and expire on server restart; this mode is for local testing, not durable patient account recovery. Production is designed around verified stable Supabase identities. Source files are not persisted by this change; extracted provenance and report/plan state are. Questionnaire context is stored per report; a complete cross-report patient-profile management product is not implemented.

Automated local checks pass. Production acceptance stays blocked until real auth/RLS, Google/provider evidence, browser/device checks, clinical review and deployment validation are completed. Consultation booking is **not production-ready**.
