# SIMPLIFIER 2.0 — FINAL MANUAL SETUP & PRODUCTION RUNBOOK

This runbook guides the human operator through connecting live cloud providers, performing necessary professional reviews, and validating end-to-end production operations **after Phase 6**.

---

## 1. GitHub Remote Connection

Because external credentials were intentionally withheld during autonomous development phases, the local git repository was initialized and committed cleanly locally.

To connect your GitHub remote repository:
```powershell
cd "c:\Users\shaik\OneDrive\Desktop\Simplifier 2.0\simplifier-2"
git remote add origin https://github.com/<YOUR_ORGANIZATION_OR_USERNAME>/simplifier-2.git
git branch -M main
git push -u origin main --tags
```

---

## 2. Supabase Cloud Configuration

1. Log in to [Supabase Console](https://supabase.com/).
2. Create a new project named `simplifier-2`.
3. Note your project URL (`https://<project-ref>.supabase.co`) and API `anon` / `service_role` keys.
4. Navigate to **SQL Editor** and run the initial migration script:
   - File location: `backend/supabase/migrations/001_initial_schema_and_rls.sql`
5. Verify that **Row Level Security (RLS)** is enabled for:
   - `patient_profiles`
   - `reports`
   - `report_extractions`
   - `doctor_appointments`
6. In **Authentication > URL Configuration**:
   - Site URL: `https://simplifier-2.vercel.app`
   - Allowed Redirect URLs: `https://simplifier-2.vercel.app/**`

---

## 3. Render Backend Deployment

1. Log in to [Render](https://render.com/).
2. Create a new **Web Service** connected to your GitHub repository.
3. Select **Python** environment with root directory or specify:
   - Build Command: `pip install -r backend/requirements.txt`
   - Start Command: `python -m uvicorn app.main:app --host 0.0.0.0 --port $PORT`
4. Set Environment Variables:
   - `ENVIRONMENT`: `production`
   - `PROJECT_NAME`: `Simplifier 2.0`
   - `API_V1_STR`: `/api/v1`
   - `SUPABASE_URL`: `https://<your-project>.supabase.co`
   - `SUPABASE_KEY`: `<your-supabase-service-role-or-anon-key>`
5. Deploy and verify health check:
   - `GET https://<your-render-url>.onrender.com/health` returns `200 OK` with `status: healthy`.

---

## 4. Vercel Frontend Deployment

1. Log in to [Vercel](https://vercel.com/).
2. Import the `simplifier-2` repository.
3. Set **Root Directory** to `frontend`.
4. Build & Development Settings:
   - Framework Preset: `Vite`
   - Build Command: `npm run build`
   - Output Directory: `dist`
5. In `frontend/vercel.json`, ensure the proxy rewrite points to your active Render backend URL.
6. Deploy and verify frontend loads smoothly.

---

## 5. Live Production Acceptance Checklists

### A. RLS Two-User Isolation Verification
- Log in with User A (`user_a@example.com`) and upload a test document.
- Log in with User B (`user_b@example.com`) in an incognito window.
- Confirm User B cannot view User A's reports, biomarker values, or appointments in the API response or UI.

### B. Live Provider Directory Verification
- In development/local mode, doctors are clearly labeled **Demo Physician Directory** and bookings are simulated.
- Before onboarding real doctors in production, verify national medical council license numbers, clinic addresses, and consultation consent agreements.

### C. Qualified Medical & Translation Review
- **Clinical Review Status**: The knowledge base rules (`backend/app/services/medical_knowledge.py`), lab reference intervals, and conservative patterns (`backend/app/services/pattern_engine.py`) have been developed conservatively according to published clinical guidelines (ADA, NKF, AHA, WHO). Formal institutional medical board sign-off remains **PENDING** operator sign-off before full diagnostic deployment.
- **Translation Review Status**: Plain-language translations for Hindi and Marathi (`frontend/src/fixtures/translations.js`) were drafted for accessibility. Professional clinical translation review remains **PENDING** operator review before public regional marketing.

---

## 6. Emergency & Security Protocol

- If Supabase credentials are missing when `ENVIRONMENT=production`, the backend strictly **fails closed** on startup to prevent unauthenticated data exposure.
- Report deletion requests immediately invoke cascading deletion in the database and purge local sessions.
