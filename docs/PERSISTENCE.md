# Current persistence and ownership contract

Updated 18 October 2026. See [manual setup](../FINAL_MANUAL_SETUP.md) for migration order and live acceptance. No cloud migration has been applied by this task.

## Local development

`AUTH_MODE=local` is explicit offline development and is forbidden in production. Each browser receives a random HMAC-signed HttpOnly/SameSite cookie. Its private signing key is persisted in `.dev-session-key`, so the same browser identity can reopen reports after a backend restart. Different browser identities have separate owner keys.

SQLite stores `(owner, namespace, key, payload)` under `APP_DATA_DIR`, default `backend/data`. Reports, extraction/correction provenance, questionnaire answers and nutrition plans are durable. The signing key and databases are ignored by Git. Choose a private, access-controlled `APP_DATA_DIR` outside shared/synced folders before storing sensitive test data; application code does not claim to encrypt local files. Do not remove the signing key if you need existing local cookies to retain access. Clearing cookies intentionally loses anonymous account recovery; use Supabase for real patient accounts.

Original report/photo files are not persisted. Browser source previews exist only during the upload session; stored source lines/page numbers/boxes remain available. Logs should contain operational events, not report bodies or tokens.

## Supabase integration and production

`AUTH_MODE=supabase` requires a valid project URL and publishable/legacy anon key. It verifies each identity at Auth `/auth/v1/user`; client `user_id` and editable metadata are never authorization inputs. The application keeps access/refresh tokens in HttpOnly cookies and uses the patient's JWT for REST/RLS, never a service-role key.

When valid Supabase auth is configured, persistence is remote even during local integration testing. Production refuses missing/malformed configuration, local auth and non-HTTPS/wildcard CORS origins. Unavailable/malformed remote responses return controlled 503 errors; there is no SQLite or anonymous production fallback.

The runtime table is `public.patient_app_state`, with namespaces `reports` and `nutrition`. Its primary key `(owner_id, namespace, state_key)` supports owner retrieval; the owner UUID references `auth.users` with cascade on account deletion. RLS applies the authenticated owner predicate in both USING and WITH CHECK. The final hardening migration blocks anonymous Auth claims and closes unused historical schemas to patient/anon Data API roles.

The normalized tables in migrations 001–003 are historical, unused runtime contracts. They are retained for migration history and data preservation, not duplicate active storage or a real booking service. Apply all five migrations in order to a fresh test project as documented; inspect existing migration history before any existing-project change.

`DELETE /api/v1/reports/{report_id}` checks ownership and removes the report and matching saved nutrition entries. Other users receive 404. This API does not delete operator backups or implement account-deletion/legal-retention workflows. Development appointment simulations are process-local only and are blocked as production booking operations.

Local tests validate isolation, reopen/restart behavior, malformed responses and JWT/owner request contracts. Actual PostgreSQL/RLS execution and real two-user Supabase acceptance remain manual gates; mocks are not live verification.
