-- ============================================================
-- Migration 005: Create data_mappings table
-- Persists confirmed schema mappings between source files and canonical schema
-- ============================================================

create table if not exists public.data_mappings (
    id uuid primary key default gen_random_uuid(),
    business_id uuid not null references public.businesses(id) on delete cascade,
    file_id uuid not null references public.uploaded_files(id) on delete cascade,
    mappings jsonb not null default '[]'::jsonb,
    status text not null default 'confirmed' check (status in ('draft', 'confirmed')),
    created_at timestamptz default now() not null,
    updated_at timestamptz default now() not null
);

-- Unique mapping per file in a business workspace
create unique index if not exists idx_data_mappings_business_file
    on public.data_mappings(business_id, file_id);

create index if not exists idx_data_mappings_file
    on public.data_mappings(file_id);

-- Enable RLS
alter table public.data_mappings enable row level security;

-- Members can see mappings for their businesses
create policy "Members can read mappings of their businesses"
    on public.data_mappings for select
    using (
        exists (
            select 1 from public.business_memberships bm
            where bm.business_id = data_mappings.business_id
            and bm.user_id = auth.uid()
        )
    );

-- Members can insert mappings for their businesses
create policy "Members can insert mappings for their businesses"
    on public.data_mappings for insert
    with check (
        exists (
            select 1 from public.business_memberships bm
            where bm.business_id = data_mappings.business_id
            and bm.user_id = auth.uid()
        )
    );

-- Members can update mappings for their businesses
create policy "Members can update mappings for their businesses"
    on public.data_mappings for update
    using (
        exists (
            select 1 from public.business_memberships bm
            where bm.business_id = data_mappings.business_id
            and bm.user_id = auth.uid()
        )
    )
    with check (
        exists (
            select 1 from public.business_memberships bm
            where bm.business_id = data_mappings.business_id
            and bm.user_id = auth.uid()
        )
    );

-- Owners can delete mappings
create policy "Owners can delete mappings"
    on public.data_mappings for delete
    using (
        exists (
            select 1 from public.business_memberships bm
            where bm.business_id = data_mappings.business_id
            and bm.user_id = auth.uid()
            and bm.role = 'owner'
        )
    );

-- Auto-update updated_at
create or replace trigger data_mappings_updated_at
    before update on public.data_mappings
    for each row
    execute function public.update_updated_at();
