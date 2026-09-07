-- ============================================================
-- Migration 009: Create action_items table
-- Stores actionable strategic initiatives and execution status tracking
-- ============================================================

create table if not exists public.action_items (
    id uuid primary key default gen_random_uuid(),
    business_id uuid not null references public.businesses(id) on delete cascade,
    file_id uuid not null references public.uploaded_files(id) on delete cascade,
    title text not null,
    domain text not null,
    urgency text not null check (urgency in ('high', 'medium', 'low')),
    expected_impact text not null,
    effort text not null check (effort in ('low', 'medium', 'high')),
    timeframe text not null,
    action_steps jsonb not null default '[]'::jsonb,
    owner text not null default 'Executive Team',
    risk_if_ignored text not null default '',
    status text not null default 'pending' check (status in ('pending', 'in_progress', 'completed', 'dismissed')),
    created_at timestamptz default now() not null,
    updated_at timestamptz default now() not null
);

create index if not exists idx_action_items_lookup
    on public.action_items(business_id, file_id, status);

-- Enable RLS
alter table public.action_items enable row level security;

-- Policies for action_items
create policy "Members can read action items for their businesses"
    on public.action_items for select
    using (
        exists (
            select 1 from public.business_memberships bm
            where bm.business_id = action_items.business_id
            and bm.user_id = auth.uid()
        )
    );

create policy "Members can insert action items for their businesses"
    on public.action_items for insert
    with check (
        exists (
            select 1 from public.business_memberships bm
            where bm.business_id = action_items.business_id
            and bm.user_id = auth.uid()
        )
    );

create policy "Members can update action items for their businesses"
    on public.action_items for update
    using (
        exists (
            select 1 from public.business_memberships bm
            where bm.business_id = action_items.business_id
            and bm.user_id = auth.uid()
        )
    )
    with check (
        exists (
            select 1 from public.business_memberships bm
            where bm.business_id = action_items.business_id
            and bm.user_id = auth.uid()
        )
    );

create policy "Owners can delete action items"
    on public.action_items for delete
    using (
        exists (
            select 1 from public.business_memberships bm
            where bm.business_id = action_items.business_id
            and bm.user_id = auth.uid()
            and bm.role = 'owner'
        )
    );

-- Auto-update updated_at for action_items
create or replace trigger action_items_updated_at
    before update on public.action_items
    for each row
    execute function public.update_updated_at();
