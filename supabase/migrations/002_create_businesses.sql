-- ============================================================
-- Migration 002: Create businesses table
-- Core entity for multi-tenant business ownership
-- ============================================================

create table if not exists public.businesses (
    id uuid primary key default gen_random_uuid(),
    name text not null,
    industry text default '',
    description text default '',
    created_at timestamptz default now() not null,
    updated_at timestamptz default now() not null
);

-- Enable RLS
alter table public.businesses enable row level security;

-- Users can only see businesses they are members of
create policy "Members can read their businesses"
    on public.businesses for select
    using (
        exists (
            select 1 from public.business_memberships bm
            where bm.business_id = id
            and bm.user_id = auth.uid()
        )
    );

-- Any authenticated user can create a business
create policy "Authenticated users can create businesses"
    on public.businesses for insert
    with check (auth.role() = 'authenticated');

-- Only owners can update their business
create policy "Owners can update their businesses"
    on public.businesses for update
    using (
        exists (
            select 1 from public.business_memberships bm
            where bm.business_id = id
            and bm.user_id = auth.uid()
            and bm.role = 'owner'
        )
    );

-- Only owners can delete their business
create policy "Owners can delete their businesses"
    on public.businesses for delete
    using (
        exists (
            select 1 from public.business_memberships bm
            where bm.business_id = id
            and bm.user_id = auth.uid()
            and bm.role = 'owner'
        )
    );

-- Auto-update updated_at
create or replace trigger businesses_updated_at
    before update on public.businesses
    for each row
    execute function public.update_updated_at();
