# Simplifier 2.0 — manual integration and hosting runbook

Updated 18 October 2026. Code is prepared for local verification and the next manual Supabase phase. **No cloud project was created or connected, no migration applied remotely, and nothing deployed.** Local test fixtures are deliberately synthetic. Live services and clinical/native-language review remain separate acceptance gates.

## 1. Start the current application locally — no keys needed

Open PowerShell in `C:\Users\ADMIN\OneDrive\Desktop\Shoaib\Projects\Simplifier2.0`.

Install once (skip virtual-environment creation if it already exists):

```powershell
py -3.14 -m venv backend/.venv
./backend/.venv/Scripts/python.exe -m pip install -r backend/requirements.lock
Set-Location frontend
npm.cmd ci
Set-Location ..
```

Terminal 1:

```powershell
./scripts/Start-Backend.ps1 -Port 8001
```

Terminal 2, from the same repository root:

```powershell
./scripts/Start-Frontend.ps1 -BackendPort 8001 -Port 3000
```

Open `http://127.0.0.1:3000`. These scripts explicitly select local authentication; they do not use cloud credentials. Existing environment files are not overwritten. The older `backend/.env` may contain `SUPABASE_KEY`; that name is deliberately unused by current authentication. Do not substitute a service-role key.

The startup investigation reproduced HTTP 200 directly on backend 8001 and HTTP 500 through the old proxy targeting absent port 8000. The repaired proxy targets 8001 by default and accepts `BACKEND_PORT` or `BACKEND_URL`. Both direct and proxied configuration now return 200 in local mode. `/health` belongs to the backend; frontend `/health` alone is SPA HTML and is not a backend health check.

Expected local response at `http://127.0.0.1:3000/api/v1/auth/configuration`:

```json
{"configured":false,"sign_in_required":false,"development_mode":true}
```

If a port is occupied, stop the old project terminal with Ctrl+C before restarting. To change ports, pass matching parameters to both scripts. Development CORS includes localhost/127.0.0.1 on 3000/3001; additional frontend ports require explicit `CORS_ORIGINS`. Do not disable a managed policy to run tests.

## 2. Repeat the local checks

```powershell
Set-Location frontend
npx.cmd playwright install chromium
Set-Location ..
./scripts/Test-All.ps1 -IncludeBrowser
```

The browser runner starts its own isolated backend on 8101 and frontend on 3001, with private throwaway test state and cloud keys disabled. It does not reuse the operator's cloud-connected backend. Stop conflicting test servers first. `scripts/Test-E2E.ps1 -InstallChromium` is the browser-only alternative. Test logs/screenshots are under ignored `artifacts/` and `frontend/test-results/`. The 29 browser scenarios include real local report/nutrition/PDF/persistence and camera-file fallback processing; provider responses are explicitly mocked, and physical camera hardware is not verified.

## 3. STAGE A — connect Supabase manually, only when ready

### A1. Create the intended test project

Sign in at [Supabase Dashboard](https://supabase.com/dashboard). Create a dedicated integration project and select an available region suitable for your users/backend. Keep its database password in your password manager. Do not use an existing production database for initial testing.

Open the project's **Connect** dialog for its project URL and publishable key; keys are also under **Settings → API Keys**. This application needs only `SUPABASE_URL` and `SUPABASE_PUBLISHABLE_KEY`. It does not need a service-role/secret key. See [official key guidance](https://supabase.com/docs/guides/getting-started/api-keys).

### A2. Apply the reviewed schema, in order, to a NEW empty project

In **SQL Editor**, run the complete contents of each file, separately, in this exact order:

1. `backend/supabase/migrations/001_initial_schema_and_rls.sql`
2. `backend/supabase/migrations/002_nutrition_plans_schema.sql`
3. `backend/supabase/migrations/003_appointments_schema.sql`
4. `backend/supabase/migrations/20261018120946_patient_app_state.sql`
5. `backend/supabase/migrations/20261018141226_predeployment_hardening.sql`

Do not rerun already-applied scripts: policy/constraint creation is migration history, not a reset command. For an existing project, inspect its migration history and use the normal CLI migration workflow instead. No SQL was applied remotely during this work. A local PostgreSQL/Docker engine was unavailable; SQL execution/RLS acceptance must be done in this manual stage.

The runtime uses **`patient_app_state`**. The first three migrations are historical schemas. The final hardening migration preserves those tables/data but revokes their unused patient/anonymous Data API access; it does not pretend they implement a real scheduler. Its state policy requires the authenticated owner for both `USING` and `WITH CHECK`, excludes anonymous Auth identities, and checks JSON payloads. Its primary key already indexes owner/namespace/state key.

Verify:

```sql
select tablename, rowsecurity
from pg_tables
where schemaname = 'public'
order by tablename;

select policyname, roles, qual, with_check
from pg_policies
where schemaname = 'public' and tablename = 'patient_app_state';
```

`patient_app_state` must have RLS enabled, the authenticated owner policy and its write check. The authenticated role needs Data API table grants; public/anon must not have access. Do not test isolation only as the SQL Editor's unrestricted administrator.

### A3. Configure two test accounts

In **Authentication**, enable email/password sign-in and leave anonymous sign-ins disabled. Create two separate test users (A and B) in **Authentication → Users**, with passwords and confirmed email addresses for these controlled test accounts. The current application has sign-in/refresh/logout; it does not implement public registration or password-reset screens. Use controlled pilot accounts until that onboarding scope is implemented.

For later email/redirect flows, set **Authentication → URL Configuration** to your actual application URL and exact approved redirect URLs. Local testing uses `http://127.0.0.1:3000`; later replace/add the real HTTPS frontend. Do not turn off verification for real patients to simplify testing. Review JWT/session lifetime and Supabase's access-token revocation semantics for your service requirements.

### A4. Configure the local backend privately

Create/edit the root `.env` using `.env.example` as a reference. Do not overwrite an existing file blindly. Set:

```dotenv
ENVIRONMENT=development
AUTH_MODE=supabase
SUPABASE_URL=https://YOUR-PROJECT.supabase.co
SUPABASE_PUBLISHABLE_KEY=YOUR-PUBLISHABLE-KEY
CORS_ORIGINS=http://127.0.0.1:3000,http://localhost:3000
```

Keep it out of Git. Do not paste credentials into chat or source code. Root `.env` loads first, then `backend/.env` fills missing values; process environment values take precedence. Partial/malformed Supabase configuration fails safely instead of selecting anonymous mode.

Restart Terminal 1 explicitly in integration mode:

```powershell
./scripts/Start-Backend.ps1 -Port 8001 -AuthMode supabase
```

Keep Terminal 2 running the frontend on 3000. A configured Supabase project uses patient-JWT remote persistence even while `ENVIRONMENT=development`; it does not silently save integration reports to SQLite.

### A5. Verify the real service, not just configuration flags

The proxied `/api/v1/auth/configuration` should now return `configured:true`, `sign_in_required:true`, `development_mode:false`. This only validates configuration shape; actual sign-in and persistence must also work. Sign in as A and use only de-identified/synthetic documents during acceptance.

Create a source fixture without PowerShell binary-redirection issues:

```powershell
./backend/.venv/Scripts/python.exe backend/scripts/create_test_report.py --output artifacts/manual-test-report.pdf
```

Upload it through the app, review uncertain readings, answer context questions, generate nutrition, swap a meal and download report/consultation PDFs. Refresh the browser, restart the backend, sign out/in, and verify A's history and selected meal persist. No appointment should appear confirmed.

### A6. Two-user application acceptance

Create a report/plan under A and note its opaque report/plan IDs. In a private browser window, sign in as B and create B's own report. B's history must omit A's report. A's summary, extractions, PDFs, consultation preparation, nutrition plan and swap/delete APIs must return 404 to B. Signing out must clear patient UI state; expired sessions must request refresh or sign-in. Repeat A's reload/restart check.

### A7. Two-user RLS acceptance

Use your test users' actual UUIDs from Authentication. After creating both users' own rows, the following SQL Editor transaction impersonates the restricted database role; replace the two UUID placeholders first:

```sql
begin;
set local role authenticated;
set local request.jwt.claims = '{"sub":"USER_B_UUID","role":"authenticated","is_anonymous":false}';
select owner_id, state_key from public.patient_app_state;
select owner_id, state_key from public.patient_app_state
where owner_id = 'USER_A_UUID'::uuid;
rollback;
```

The first query must show only B's rows; the second must show zero rows. In a separate rolled-back transaction under B, attempt INSERT with A's owner UUID and UPDATE of B's own existing row to A's owner UUID: both must be rejected by RLS. Under anon, table access must be denied. Do not weaken policies to make these checks pass. If any step fails, stop before patient use and inspect migrations, grants and the active role.

## 4. Google Maps and Panvel-related doctors — manual setup

1. Open [Google Cloud Console](https://console.cloud.google.com/), select/create the intended project and enable its billing. This is a human account/billing step, not performed by the app.
2. In **APIs & Services → Library**, enable **Geocoding API**, **Places API (New)** and **Maps JavaScript API**.
3. In **Credentials**, create a dedicated server API key restricted to Geocoding and Places API (New). Restrict application access to the allowed backend outbound IPs where supported; use the actual backend host's outbound addresses. Use a separate restricted development key if needed for a changing home IP.
4. Put that value only in root/backend private `.env` as `GOOGLE_MAPS_SERVER_KEY`. On Render it belongs only in backend environment settings.
5. Create a separate browser key, API-restricted to Maps JavaScript API and website-restricted to your exact application referrers, for example `http://127.0.0.1:3000/*`, `http://127.0.0.1:3001/*` and your actual HTTPS production domain. Never reuse the server key here.
6. Under **Google Maps Platform → Map Management**, create a **JavaScript** map ID (vector map supports Advanced Markers). See [map ID instructions](https://developers.google.com/maps/documentation/javascript/map-ids/get-map-id).
7. Create/edit `frontend/.env.local` using `frontend/.env.example`:

```dotenv
VITE_GOOGLE_MAPS_BROWSER_KEY=YOUR-RESTRICTED-BROWSER-KEY
VITE_GOOGLE_MAPS_MAP_ID=YOUR-JAVASCRIPT-MAP-ID
```

8. Restart the backend and Vite. On a report, open Doctors, enter **Panvel, Maharashtra** or a precise PIN, select a report-related specialty/radius and search. Results default to the first suggested specialty from reliable source findings; General Physician remains available. Change specialties when several findings need discussion.
9. Sorting defaults to highest returned Google rating, then review count, then distance. Unrated listings stay unrated and sort below rated ones. Nearest sorting is optional. This ranks **returned matches**, not every doctor in Panvel, and Google review ratings are not verified clinical competence or registration. No findings/values/document are sent to Google; the selected generic specialty and location are sent after the patient's search action.
10. Check actual clinic names, locations, ratings/counts, phone links, marker positions and Google Maps directions. Verify Mumbai, Pune, Thane, Kalyan, Nashik, Nagpur, Chhatrapati Sambhajinagar, Kolhapur, Solapur, Amravati, Yavatmal, Pusad, Nanded, Ratnagiri, Gadchiroli and smaller towns. Test location denial, invalid/ambiguous PIN/place, no results and quota failures.
11. Set API quotas and billing alerts appropriate to your account. Ratings, contact and website fields affect the applicable Places billing tier; see [Text Search field/SKU documentation](https://developers.google.com/maps/documentation/places/web-service/text-search). Alerts are not a guarantee of a hard spending cap. Finalize public privacy/terms pages and attribution review before launch.

No real appointment API is supplied by this discovery setup. Optional `PROVIDER_CAPABILITIES_FILE` entries must use actual place IDs, source URLs, recent review dates and independently supported booking/online/WhatsApp routes. WhatsApp is never inferred from a phone. Until a real scheduler is integrated, contact/external enquiry does not create a confirmed booking. PDF consent only includes data in a local download; no report is sent externally.

## 5. STAGE B — host the frontend and backend later

This is a later human-controlled stage. **Do not perform it until Stage A acceptance passes.** The prepared path is Vercel frontend + separately hosted Python backend + Supabase. A static Vite deployment does not host FastAPI/OCR. Python serverless hosting would need separate payload, bundle, timeout and storage design work; it is not prepared as a drop-in all-Vercel backend.

### B1. Prepare the actual frontend domain

In Vercel, create/import `Shoaibbb-C0/Simplifier2.0` as a project with Root Directory **frontend**, Framework **Vite**, Install **npm ci**, Build **npm run build**, Output **dist**. Record the actual project production domain from Vercel settings. The frontend intentionally refuses a Vercel build until a real backend proxy has been configured; an initial incomplete setup is not a working deployment.

### B2. Create the Python service when authorized

In Render, New → Web Service → connect the same GitHub repository and `main` branch. Leave Root Directory blank (repository root). Use Python runtime and Python 3.14.0 as pinned in `render.yaml`.

Build:

```text
pip install -r backend/requirements.lock && python backend/scripts/check_runtime.py
```

Start:

```text
python -m uvicorn app.main:app --app-dir backend --host 0.0.0.0 --port $PORT --no-access-log
```

Health path: `/health`. The build prepares OCR assets and verifies the extraction checkpoint and bundled Devanagari PDF fonts. Start with sufficient RAM for OCR (the prepared Standard/1c-2g template has 2 GB), then measure representative multi-page documents and concurrency before selecting production capacity. Resource selection/billing is your manual decision. Singapore is the example nearby region; confirm operational/data-location requirements before creation. See [Render regions](https://render.com/docs/regions) and [compute plans](https://render.com/docs/compute-plans).

Backend environment:

```dotenv
ENVIRONMENT=production
AUTH_MODE=supabase
SUPABASE_URL=https://YOUR-PROJECT.supabase.co
SUPABASE_PUBLISHABLE_KEY=YOUR-PUBLISHABLE-KEY
CORS_ORIGINS=https://YOUR-ACTUAL-FRONTEND-DOMAIN
GOOGLE_MAPS_SERVER_KEY=YOUR-SERVER-KEY
MAX_FILE_SIZE_MB=15
```

Use the exact HTTPS origin without a path/trailing slash; do not wildcard all Vercel previews. `$PORT` is provided by the backend host. Do not use development local auth or SQLite for production. No persistent disk is required for patient state when Supabase is configured; model assets are prepared in the build image.

### B3. Configure the actual same-origin API proxy

After backend `/health` and `/api/v1/auth/configuration` are healthy with production authentication, run locally:

```powershell
Set-Location frontend
npm.cmd run configure:hosting -- --backend-url https://YOUR-ACTUAL-BACKEND-HOST
```

The script checks the backend health/configuration and then generates `frontend/vercel.json` with `/api/:path*` forwarded to that real origin plus the SPA fallback. `API_PROXY_TARGET` can supply the origin to this configuration command. Do this **before** Vercel reads the deployment configuration, not by hoping to interpolate an env variable inside JSON. Review, commit and push the generated public URL configuration when you authorize this later stage. No secret belongs in the JSON.

The repository currently contains SPA routing only, with no unverified Render placeholder. API configuration must precede deployment. The browser should continue calling same-origin `/api/v1/...`, which keeps authentication cookies on the frontend origin. Do not switch patient calls directly to a third-party backend origin without redesigning cookie/CORS behavior.

### B4. Configure Vercel build environment and verify

Set only `VITE_GOOGLE_MAPS_BROWSER_KEY` and `VITE_GOOGLE_MAPS_MAP_ID` as needed for map rendering. They are public browser configuration; restrict the key by referrer. Server credentials stay on the Python host. Select the intended production/preview environment deliberately; new Vite build-time values require a rebuild.

After an authorized deployment, verify actual HTTPS sign-in, HttpOnly/Secure/SameSite cookies through the proxy, refresh/logout, upload (including files over 4.5 MB), OCR, food-plan swap/reload, PDF downloads, two-account isolation, Panvel search, maps, phone/directions links and mobile layouts. External rewrites have host limits; test the slowest permitted documents rather than assuming local timing proves hosted performance. A background-job upload design may be needed if realistic documents exceed proxy timeouts. Source: [Vercel external rewrites](https://vercel.com/docs/routing/rewrites).

## 6. Gates before real patient launch

Live Supabase/Auth/RLS and Google/provider verification; representative de-identified hospital/photographed/rotated/poor-quality reports; qualified clinical/dietitian and Hindi/Marathi review; real device-camera checks; hosted performance and cookie checks; privacy/terms, retention/deletion and backup procedures; protected diagnostics/monitoring. Local automated accessibility checks are not a WCAG certification. A real booking agreement/API is required before offering confirmed appointments, reminders, rescheduling or cancellation.

Use the current audit and test evidence, not older historical phase documents, to decide release readiness. The next supported step is **manual Supabase integration**, not unrestricted production patient use.
