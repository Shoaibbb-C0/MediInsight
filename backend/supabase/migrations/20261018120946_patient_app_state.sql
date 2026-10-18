-- Owner-scoped application state; production REST calls use the patient's JWT, never service_role.
create table if not exists public.patient_app_state (
    owner_id uuid not null references auth.users(id) on delete cascade,
    namespace text not null check (namespace in ('reports','nutrition')),
    state_key text not null,
    payload jsonb not null,
    primary key (owner_id, namespace, state_key)
);
alter table public.patient_app_state enable row level security;
create policy "patient owns application state" on public.patient_app_state
    for all to authenticated
    using ((select auth.uid()) = owner_id)
    with check ((select auth.uid()) = owner_id);
grant select, insert, update, delete on public.patient_app_state to authenticated;
revoke all on public.patient_app_state from anon;
