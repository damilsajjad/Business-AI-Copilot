-- ============================================================
-- Migration 010: Create scheduled_reports table
-- Stores periodic automated executive reports and scheduling configs
-- ============================================================

create table if not exists public.scheduled_reports (
    id uuid primary key default gen_random_uuid(),
    business_id uuid not null references public.businesses(id) on delete cascade,
    report_type text not null default 'weekly' check (report_type in ('weekly', 'monthly')),
    status text not null default 'active' check (status in ('active', 'paused')),
    last_generated_at timestamptz,
    last_report_content jsonb default '{}'::jsonb,
    created_at timestamptz default now() not null,
    updated_at timestamptz default now() not null
);

create unique index if not exists idx_scheduled_reports_biz
    on public.scheduled_reports(business_id, report_type);

-- Enable RLS
alter table public.scheduled_reports enable row level security;

-- Policies
create policy "Members can read scheduled reports for their businesses"
    on public.scheduled_reports for select
    using (
        exists (
            select 1 from public.business_memberships bm
            where bm.business_id = scheduled_reports.business_id
            and bm.user_id = auth.uid()
        )
    );

create policy "Members can insert scheduled reports for their businesses"
    on public.scheduled_reports for insert
    with check (
        exists (
            select 1 from public.business_memberships bm
            where bm.business_id = scheduled_reports.business_id
            and bm.user_id = auth.uid()
        )
    );

create policy "Members can update scheduled reports for their businesses"
    on public.scheduled_reports for update
    using (
        exists (
            select 1 from public.business_memberships bm
            where bm.business_id = scheduled_reports.business_id
            and bm.user_id = auth.uid()
        )
    )
    with check (
        exists (
            select 1 from public.business_memberships bm
            where bm.business_id = scheduled_reports.business_id
            and bm.user_id = auth.uid()
        )
    );

create policy "Owners can delete scheduled reports"
    on public.scheduled_reports for delete
    using (
        exists (
            select 1 from public.business_memberships bm
            where bm.business_id = scheduled_reports.business_id
            and bm.user_id = auth.uid()
            and bm.role = 'owner'
        )
    );

-- Auto-update updated_at trigger
create or replace trigger scheduled_reports_updated_at
    before update on public.scheduled_reports
    for each row
    execute function public.update_updated_at();
