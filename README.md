# MediInsight

> Understand Your Health, Simply.

Medical laboratory report understanding application designed for ordinary patients.

MediInsight translates complex laboratory reports into clear, empathetic, and actionable everyday language with a PPT-inspired orange-red, neutral, mobile-first interface.

> **Pre-deployment verification:** 215 backend tests, 25 UI tests and 33 browser scenarios pass locally; the production build passes. Ready to begin manual Supabase integration. Live Supabase/OSM, clinical/native-language review and hosted acceptance remain outstanding. Follow [the current runbook](FINAL_MANUAL_SETUP.md).

[Mumbai snapshot, coverage limits and exact Railway/Vercel demo steps](docs/HYBRID_DOCTOR_DEMO.md). [Nationwide live OSM service limits](docs/OSM_DISCOVERY.md). MapLibre + OpenFreeMap need no API key. The existing Railway Dockerfile and Vercel API rewrite are preserved.

---

## Intended Flow

```
UPLOAD PDF / TAKE PHOTO
  → OCR AND ML EXTRACTION
  → VERIFY UNCERTAIN RESULTS
  → FIND HIGH/LOW FINDINGS
  → REVIEW AVAILABLE HISTORY
  → ASK PERSONALIZED QUESTIONS
  → SHOW SIMPLIFIED HEALTH EXPLANATION
  → OPTIONAL INLINE NUTRITION
  → OPTIONAL INLINE DOCTORS
```

> **Important**: The simplified health explanation appears strictly **AFTER** personalized context questions have been answered.

---

## Original Development Baseline (Historical)

- **Design System**: Warm Clarity (#F7F5F0 ivory, #183C43 teal, #B9DED4 mint, #D87763 coral, #272D2B charcoal). WCAG-compliant contrast, Devanagari typography support (`Noto Sans Devanagari`).
- **Primary Patient Navigation**: Home, My Reports, Profile.
- **Camera Capture**: Native device capture input, rear-camera preference, `getUserMedia` live preview with secure context checks, multi-page capture, rotate, retake, and blur/glare alerts.
- **Source Verification UI Foundation**: Side-by-side comparison between extracted values and source document bounding boxes with real-time editing and provenance recording.
- **Questionnaire & Report**: Enforced state machine where clarification questions precede the plain-language explanation.
- **Fixtures Notice**: Phase 1 uses explicitly labeled synthetic fixtures (`backend/app/fixtures/synthetic_data.py`).
- **Fail-Closed Security**: In production mode (`ENVIRONMENT=production`), the application strictly halts if Supabase credentials are missing.

---

## Local development and testing (Windows PowerShell)

Use Python 3.14 and Node.js 20+ (locally tested on Node 24). Install `backend/requirements.lock` into `backend/.venv` and run `npm.cmd ci` in `frontend` once.

From the repository root, Terminal 1:

```powershell
./scripts/Start-Backend.ps1 -Port 8001
```

Terminal 2:

```powershell
./scripts/Start-Frontend.ps1 -BackendPort 8001 -Port 3000
```

Open `http://127.0.0.1:3000`. Local mode requires no Supabase or map API keys. The scripts explicitly select isolated local auth; production forbids this mode. Backend `/api/v1/auth/configuration` must return 200 both directly on 8001 and through Vite on 3000. The prior proxy-to-8000 mismatch was reproduced and repaired.

Run all local verification:

```powershell
Set-Location frontend
npx.cmd playwright install chromium
Set-Location ..
./scripts/Test-All.ps1 -IncludeBrowser
```

The browser suite starts isolated test servers and disables cloud credentials. Provider results are explicitly mocked; report upload, extraction, nutrition, swaps, history and PDFs use the actual local backend. Real OCR image/scanned-PDF fixtures and two-page camera-file fallback are exercised. Physical device cameras and live providers remain manual acceptance work.

English/Hindi/Marathi report, nutrition, consultation and verification flows are covered. PDFs embed Devanagari fonts with HarfBuzz shaping. Qualified clinical/translation review is still required; local checks are not clinical validation or WCAG certification.

The trained extractor covers a limited canonical vocabulary. Preserve and review original source evidence; unsupported/ambiguous readings must not be treated as complete clinical interpretation. The meal planner scores constrained food combinations rather than selecting prewritten weekly plans; it refuses unsupported restrictions/complex clinical contexts rather than relaxing them.

For the exact Supabase migration order, two-user RLS test, OSM setup and later hosting setup, see [FINAL_MANUAL_SETUP.md](FINAL_MANUAL_SETUP.md), [persistence](docs/PERSISTENCE.md) and [verification audit](docs/PRODUCTION_AUDIT.md).

---

## Deployment Architecture

- **Frontend**: Vercel SPA routing prepared. Configure and verify the real HTTPS backend with `npm.cmd run configure:hosting -- --backend-url ...` before deploying; no placeholder backend URL remains.
- **Backend**: Prepared for Render / container deployment using Uvicorn.
- **Persistence**: Owner-scoped SQLite in development. Production uses verified Supabase Auth identities and the patient JWT with RLS; the included migration must be applied and live isolation tested before release.
- **Consultation**: Evidence-backed contact/external links and a consent-gated local PDF. No real scheduling integration or confirmed appointments.
