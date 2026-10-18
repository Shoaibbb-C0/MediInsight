# Simplifier 2.0

> Medical laboratory report understanding application designed for ordinary patients.

Simplifier 2.0 translates complex laboratory reports into clear, empathetic, and actionable everyday language with a PPT-inspired orange-red, neutral, mobile-first interface.

> **Production readiness: BLOCKED.** 97 backend tests, 13 UI tests, dependency audits and the frontend build pass locally. Live Google/Supabase verification, browser acceptance and clinical review remain outstanding. See [the current audit and release steps](docs/PRODUCTION_AUDIT.md).

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

## Local Development (Windows PowerShell Compatible)

### Prerequisites
- Python 3.14 (locked environment tested locally)
- Node.js 20+ (tested on Node v24)
- PowerShell 5.1+ / pwsh

### 1. Setup & Start Backend (FastAPI)
```powershell
# Navigate to backend directory and set up virtual environment
cd backend
python -m venv .venv
.\.venv\Scripts\Activate.ps1

# Install all backend and ML dependencies
pip install -r requirements.lock

# Verify dependencies integrity
python -m pip check

# Start FastAPI server
$env:PYTHONPATH="."
python -m uvicorn app.main:app --host 127.0.0.1 --port 8000 --reload
```
API docs available at: `http://127.0.0.1:8000/docs`

### 2. Start Frontend (React + Vite)
```powershell
# In a separate terminal from project root
cd frontend
npm ci
npm run dev
```
Patient web interface available at: `http://localhost:3000/`

---

## Running Automated Tests

### Backend Unit & Integration Tests (pytest)
```powershell
# Inside backend directory with active .venv:
python -m pytest
```
*Latest verified: 97 tests passed. Includes owner isolation, source-preserving multi-page extraction, nutrition constraints, mocked Google discovery in 15 Maharashtra locations, and consultation PDF consent. Actual OCR ran successfully on a generated image and scanned PDF. Hardware camera and representative clinical documents remain unverified.*

### Frontend Component Tests (Vitest)
```powershell
cd frontend
npm run test
```
*Latest verified: 13 component/integration tests passed, including consultation contact options and explicit PDF consent in English, Hindi and Marathi.*

### End-to-End Real Browser Tests (Playwright)
```powershell
cd frontend
# Start Vite with --port 3001, or set PLAYWRIGHT_BASE_URL to your permitted local preview.
npx playwright test tests/journey.spec.js
```
*20 browser tests are enumerated, not executed. Eight consultation scenarios use mocked providers and cannot verify real booking. The saved browser policy still denies the local preview despite user approval.*

### Frontend Production Build
```powershell
cd frontend
npm run build
```
*Build output: `frontend/dist` compiled successfully via Vite.*

---

## Deployment Architecture

- **Frontend**: Prepared for Vercel static deployment with single-page app routing.
- **Backend**: Prepared for Render / container deployment using Uvicorn.
- **Persistence**: Owner-scoped SQLite in development. Production uses verified Supabase Auth identities and the patient JWT with RLS; the included migration must be applied and live isolation tested before release.
- **Consultation**: Evidence-backed contact/external links and a consent-gated local PDF. No real scheduling integration or confirmed appointments.
