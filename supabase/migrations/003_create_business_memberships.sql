-- ============================================================
-- Migration 003: Create business_memberships table
-- Links users to businesses with role-based access
-- ============================================================

create table if not exists public.business_memberships (
    id uuid primary key default gen_random_uuid(),
    business_id uuid not null references public.businesses(id) on delete cascade,
    user_id uuid not null references auth.users(id) on delete cascade,
    role text not null default 'member' check (role in ('owner', 'member')),
    created_at timestamptz default now() not null
);

-- Unique constraint: one membership per user per business
create unique index if not exists idx_business_memberships_unique
    on public.business_memberships(business_id, user_id);

-- Index for user lookups
create index if not exists idx_business_memberships_user
    on public.business_memberships(user_id);

-- Index for business lookups
create index if not exists idx_business_memberships_business
    on public.business_memberships(business_id);

-- Enable RLS
alter table public.business_memberships enable row level security;

-- Users can see memberships for businesses they belong to
create policy "Members can see memberships of their businesses"
    on public.business_memberships for select
    using (
        exists (
            select 1 from public.business_memberships bm
            where bm.business_id = business_memberships.business_id
            and bm.user_id = auth.uid()
        )
    );

-- Service role / backend can insert memberships
-- (membership creation is handled by backend after business creation)
create policy "Service role can insert memberships"
    on public.business_memberships for insert
    with check (true);

-- Only owners can delete memberships
create policy "Owners can delete memberships"
    on public.business_memberships for delete
    using (
        exists (
            select 1 from public.business_memberships bm
            where bm.business_id = business_memberships.business_id
            and bm.user_id = auth.uid()
            and bm.role = 'owner'
        )
    );
