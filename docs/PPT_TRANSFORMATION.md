# PPT transformation verification

Status: PARTIAL — implementation tested; post-change browser acceptance blocked.

Reference: `MedReport_Simplification_Presentation.pptx`, found in Downloads. Inspected all slide text and the embedded upload, report, trend, desktop, nutrition, and doctor mockups. Academic branding and presentation assets were not copied into the application. Local reference extractions and screenshots are ignored by Git.

## Implemented

- Orange-red primary actions, neutral backgrounds, peach surfaces, dark editorial headings, larger measurements, and responsive type. Darker orange text provides contrast on pale surfaces.
- Upload panel, camera entry, desktop header, mobile bottom navigation, and report-context Nutrition/Doctors destinations.
- Calculated attention count, abnormal-first ordering, original values and units, source-derived interval meters, progressive disclosure, and related action panels.
- Session report history opens the actual report identity. Trends use compatible numeric observations only, show the clinical interval separately, and require four observations for a descriptive historical average. Dates are explicitly upload dates.
- Food preferences before plan generation, weekday selection, server-confirmed swaps, and saved meal identities preserved through translation and PDF downloads. Failed saves remain errors.
- Provider discovery no longer fabricates verified doctors on network failure. The bundled provider registry is explicitly demonstration-only, without contact links that could reach unrelated people. Real reports show unavailable provider discovery. The former synthetic pin field is replaced by an honest map availability state.
- Existing simulated booking, rescheduling, cancellation, and slot locking remain. Simulated status stays explicit after rescheduling.
- Keyboard-operable questionnaire choices, dialog focus containment/restoration, Escape handling, labelled controls, visible focus, reduced motion, zoom permission, and locally bundled Devanagari fonts.
- Shared report/nutrition PDF palette, translated structural meal labels, repeatable table headers, Latin font fallback for source names and units, and report provenance.

## Integrity corrections

Real uploads fail with HTTP 422 if extraction yields no measurements. Unknown report identities return HTTP 404 rather than synthetic findings. Synthetic measurements are restricted to the explicitly selected `rep_demo_fixture`. An absent trained model no longer guesses a test identity. Printed laboratory intervals and recognized printed units survive extraction. Seeded historical observations are isolated under `demo_patient`.

## Verified

- Backend: 49 tests passed, including real synthetic PDF extraction, preserved mmol/L interval, failure behavior, clinical calculations, nutrition constraints, saved swaps across EN/HI/MR, PDF generation, and simulated appointment isolation.
- Frontend: 10 component/integration tests passed, including actual report identity retrieval from history and failed-upload handling.
- Production build passed. Baseline main JavaScript: 409.37 kB / 108.88 kB gzip. Final main JavaScript: 381.77 kB / 110.02 kB gzip. The compressed bundle increased by 1.14 kB; no performance score is claimed.
- Generated and rendered report and nutrition PDFs in EN/HI/MR. Inspected every page through overview images and checked horizontal text bounds. These are synthetic local QA artifacts, excluded from Git.
- `git diff --check` passed.

## Blocked acceptance

Before screenshots were captured at desktop and 390px. The app's browser permission gate subsequently denied the local preview. The user authorized access and reported enabling it, but the tool continued returning a saved-permission/managed-policy denial for `http://127.0.0.1:3001`. No alternative browser or hidden browser connection was used to bypass that denial.

Consequently, the post-change screenshot matrix, browser journey suite, 200% zoom, landscape layouts, touch interaction, camera capture, responsive maps, and visual comparison cannot be marked passed. Updated Playwright tests are ready but unexecuted. Production build and component tests are not substitutes for this acceptance gate.

## Remaining limitations

- Full visual acceptance remains required. Camera hardware and image OCR were not validated end to end. Digital PDF extraction was validated with the trained model.
- History is session-local; backend development stores are in memory. A persistent authenticated patient account flow is not implemented by this redesign. Existing production configuration checks and Supabase migrations/RLS were preserved.
- No verified live provider source or live appointment integration is configured. Bundled appointments are simulations. Embedded maps are unavailable; no invented distances or geographic pins are shown in real mode.
- EN/HI/MR layouts and PDFs have automated coverage, but clinical translation review has not occurred. Some existing detailed clinical rationale and metadata remain English. Devanagari shaping needs native-reader review.
- Meal preferences retain existing planner capabilities; the planner does not promise support for every cuisine, budget, or medical restriction from the presentation.
- Reminders and family profiles remain proposed. No account deletion feature was invented.

## Remaining manual action

Resolve the app's saved browser-origin permission or managed policy, then run the browser acceptance suite and visual matrix. Local preview: `http://127.0.0.1:3001`. Use `PLAYWRIGHT_BASE_URL` to target a permitted local preview. A live provider source and authenticated persistence require separately configured services.
