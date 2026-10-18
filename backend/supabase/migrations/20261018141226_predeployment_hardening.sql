-- Current runtime uses patient_app_state only. Keep historical tables/data intact,
-- but close their unused Data API surface until a real supported integration exists.
revoke all on public.patient_profiles, public.reports, public.report_extractions,
    public.doctor_appointments, public.patient_nutrition_plans, public.patient_appointments
    from public, anon, authenticated;

alter table public.patient_app_state force row level security;
alter table public.patient_app_state add constraint patient_state_payload_object
    check (jsonb_typeof(payload) = 'object');

-- Explicit owner predicates protect SELECT, INSERT, UPDATE and DELETE. Client-editable
-- user_metadata is never used. Anonymous Supabase Auth sign-ins are not patient accounts.
drop policy "patient owns application state" on public.patient_app_state;
create policy "patient owns application state" on public.patient_app_state
    for all to authenticated
    using ((select auth.uid()) = owner_id and not coalesce((auth.jwt()->>'is_anonymous')::boolean, false))
    with check ((select auth.uid()) = owner_id and not coalesce((auth.jwt()->>'is_anonymous')::boolean, false));
revoke all on public.patient_app_state from public, anon;
grant select, insert, update, delete on public.patient_app_state to authenticated;

-- A row/default must never manufacture provider confirmation.
alter table public.doctor_appointments alter column status set default 'PENDING_REQUEST';
alter table public.patient_appointments alter column status set default 'pending_request';
alter table public.patient_appointments alter column booking_capability set default 'external_request';
