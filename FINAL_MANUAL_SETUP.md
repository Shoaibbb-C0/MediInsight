# MediInsight — manual integration and hosting runbook

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

## 4. OpenStreetMap nearby doctors and clinics

Google Maps has been replaced. No Google keys, billing or map ID are needed.
Follow [Mumbai snapshot coverage, demo and exact Railway/Vercel deployment steps](docs/HYBRID_DOCTOR_DEMO.md). Nationwide live limits remain in [OSM operations](docs/OSM_DISCOVERY.md).
Keep one backend replica and a persistent private APP_DATA_DIR for shared cache
and quotas. Public Overpass/Nominatim capacity is not guaranteed. Live Nominatim
resolved Panvel; Overpass facility retrieval remains unverified from this environment.
Only real matching OSM tags produce results; no ratings or confirmed bookings.

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
OSM_DISCOVERY_ENABLED=true
OSM_USER_AGENT="Simplifier2.0/1.0 (+https://github.com/Shoaibbb-C0/Simplifier2.0)"
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

No browser API key is required. Optional `VITE_OSM_MAP_STYLE_URL` selects the OpenFreeMap style. Server credentials stay on the Python host. Select the intended production/preview environment deliberately; new Vite build-time values require a rebuild.

After an authorized deployment, verify actual HTTPS sign-in, HttpOnly/Secure/SameSite cookies through the proxy, refresh/logout, upload (including files over 4.5 MB), OCR, food-plan swap/reload, PDF downloads, two-account isolation, Panvel search, maps, phone/directions links and mobile layouts. External rewrites have host limits; test the slowest permitted documents rather than assuming local timing proves hosted performance. A background-job upload design may be needed if realistic documents exceed proxy timeouts. Source: [Vercel external rewrites](https://vercel.com/docs/routing/rewrites).

## 6. Gates before real patient launch

Live Supabase/Auth/RLS and OSM/provider verification; representative de-identified hospital/photographed/rotated/poor-quality reports; qualified clinical/dietitian and Hindi/Marathi review; real device-camera checks; hosted performance and cookie checks; privacy/terms, retention/deletion and backup procedures; protected diagnostics/monitoring. Local automated accessibility checks are not a WCAG certification. A real booking agreement/API is required before offering confirmed appointments, reminders, rescheduling or cancellation.

Use the current audit and test evidence, not older historical phase documents, to decide release readiness. The next supported step is **manual Supabase integration**, not unrestricted production patient use.
