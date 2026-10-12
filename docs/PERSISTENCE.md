# Database & Persistence Architecture for Simplifier 2.0

## Development Mode
In Phase 1, state is handled in-memory and local session cache without requiring any external cloud database.

## Production Supabase PostgreSQL / RLS Integration (Prepared)
- When deployed with `ENVIRONMENT=production`, the application requires `SUPABASE_URL` and `SUPABASE_KEY`.
- If missing, the backend fails closed immediately (`backend/app/core/config.py`).
- Tables prepared for Phase 6 migration:
  - `patient_profiles` (Auth UID, preferred language, age bracket)
  - `reports` (id, user_id, filename, status, created_at)
  - `report_extractions` (report_id, biomarker_id, canonical_name, value, unit, status, confidence, verified_value)
  - `report_summaries` (report_id, summary_json, generated_at)
- Row Level Security (RLS) ensures patients can only read and mutate their own reports.
