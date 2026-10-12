# Simplifier 2.0

> Medical laboratory report understanding application designed for ordinary patients.

Simplifier 2.0 translates complex laboratory reports into clear, empathetic, and actionable everyday language following the **Warm Clarity** patient-first design system.

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

## Phase 1 Implementation Summary

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
- Python 3.10+ (tested on Python 3.14)
- Node.js 18+ (tested on Node v24)
- PowerShell 5.1+ / pwsh

### 1. Setup & Start Backend (FastAPI)
```powershell
# Navigate to backend directory and set up virtual environment
cd backend
python -m venv .venv
.\.venv\Scripts\Activate.ps1

# Install all backend and ML dependencies
pip install -r requirements.txt

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
npm install
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
*Tests pass: 24/24 tests covering ML extraction, OCR, abnormality detection, patient history, adaptive questions, nutrition & doctor discovery, and report APIs.*

### Frontend Component Tests (Vitest)
```powershell
cd frontend
npm run test
```
*Tests pass: 5/5 tests covering navigation, upload triggers, source verification editing, questionnaire gating, and plain English explanation.*

### End-to-End Real Browser Tests (Playwright)
```powershell
cd frontend
npx playwright test tests/journey.spec.js
```
*Tests pass: 1/1 full interactive browser journey with real DOM interactions.*

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
- **Persistence**: Supabase PostgreSQL + Auth with Row-Level Security (RLS) configured to fail-closed in production if credentials are not configured.
