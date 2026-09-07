-- ============================================================
-- Migration 007: Create ml_forecasts table
-- Stores time-series sales forecasts and customer churn risk scores
-- ============================================================

create table if not exists public.ml_forecasts (
    id uuid primary key default gen_random_uuid(),
    business_id uuid not null references public.businesses(id) on delete cascade,
    file_id uuid not null references public.uploaded_files(id) on delete cascade,
    forecast_type text not null check (forecast_type in ('sales', 'churn')),
    results jsonb not null default '{}'::jsonb,
    created_at timestamptz default now() not null,
    updated_at timestamptz default now() not null
);

-- Unique forecast per business, file, and type
create unique index if not exists idx_ml_forecasts_lookup
    on public.ml_forecasts(business_id, file_id, forecast_type);

-- Enable RLS
alter table public.ml_forecasts enable row level security;

-- Members can read forecasts of their businesses
create policy "Members can read forecasts of their businesses"
    on public.ml_forecasts for select
    using (
        exists (
            select 1 from public.business_memberships bm
            where bm.business_id = ml_forecasts.business_id
            and bm.user_id = auth.uid()
        )
    );

-- Members can insert forecasts for their businesses
create policy "Members can insert forecasts for their businesses"
    on public.ml_forecasts for insert
    with check (
        exists (
            select 1 from public.business_memberships bm
            where bm.business_id = ml_forecasts.business_id
            and bm.user_id = auth.uid()
        )
    );

-- Members can update forecasts for their businesses
create policy "Members can update forecasts for their businesses"
    on public.ml_forecasts for update
    using (
        exists (
            select 1 from public.business_memberships bm
            where bm.business_id = ml_forecasts.business_id
            and bm.user_id = auth.uid()
        )
    )
    with check (
        exists (
            select 1 from public.business_memberships bm
            where bm.business_id = ml_forecasts.business_id
            and bm.user_id = auth.uid()
        )
    );

-- Owners can delete forecasts
create policy "Owners can delete forecasts"
    on public.ml_forecasts for delete
    using (
        exists (
            select 1 from public.business_memberships bm
            where bm.business_id = ml_forecasts.business_id
            and bm.user_id = auth.uid()
            and bm.role = 'owner'
        )
    );

-- Auto-update updated_at
create or replace trigger ml_forecasts_updated_at
    before update on public.ml_forecasts
    for each row
    execute function public.update_updated_at();
