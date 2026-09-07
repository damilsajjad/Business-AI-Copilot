-- ============================================================
-- Migration 006: Create analytics_results table
-- Stores computed deterministic analytics results per uploaded dataset
-- ============================================================

create table if not exists public.analytics_results (
    id uuid primary key default gen_random_uuid(),
    business_id uuid not null references public.businesses(id) on delete cascade,
    file_id uuid not null references public.uploaded_files(id) on delete cascade,
    results jsonb not null default '{}'::jsonb,
    created_at timestamptz default now() not null,
    updated_at timestamptz default now() not null
);

-- Unique analytics result per file in a business workspace
create unique index if not exists idx_analytics_results_business_file
    on public.analytics_results(business_id, file_id);

create index if not exists idx_analytics_results_file
    on public.analytics_results(file_id);

-- Enable RLS
alter table public.analytics_results enable row level security;

-- Members can see analytics results for their businesses
create policy "Members can read analytics of their businesses"
    on public.analytics_results for select
    using (
        exists (
            select 1 from public.business_memberships bm
            where bm.business_id = analytics_results.business_id
            and bm.user_id = auth.uid()
        )
    );

-- Members can insert analytics results for their businesses
create policy "Members can insert analytics for their businesses"
    on public.analytics_results for insert
    with check (
        exists (
            select 1 from public.business_memberships bm
            where bm.business_id = analytics_results.business_id
            and bm.user_id = auth.uid()
        )
    );

-- Members can update analytics results for their businesses
create policy "Members can update analytics for their businesses"
    on public.analytics_results for update
    using (
        exists (
            select 1 from public.business_memberships bm
            where bm.business_id = analytics_results.business_id
            and bm.user_id = auth.uid()
        )
    )
    with check (
        exists (
            select 1 from public.business_memberships bm
            where bm.business_id = analytics_results.business_id
            and bm.user_id = auth.uid()
        )
    );

-- Owners can delete analytics results
create policy "Owners can delete analytics results"
    on public.analytics_results for delete
    using (
        exists (
            select 1 from public.business_memberships bm
            where bm.business_id = analytics_results.business_id
            and bm.user_id = auth.uid()
            and bm.role = 'owner'
        )
    );

-- Auto-update updated_at
create or replace trigger analytics_results_updated_at
    before update on public.analytics_results
    for each row
    execute function public.update_updated_at();
