-- ============================================================
-- Migration 008: Create ai_insights and copilot_chats tables
-- Stores multi-agent executive briefs and conversational chat logs
-- ============================================================

create table if not exists public.ai_insights (
    id uuid primary key default gen_random_uuid(),
    business_id uuid not null references public.businesses(id) on delete cascade,
    file_id uuid not null references public.uploaded_files(id) on delete cascade,
    insights jsonb not null default '{}'::jsonb,
    created_at timestamptz default now() not null,
    updated_at timestamptz default now() not null
);

-- Unique insights report per business and file
create unique index if not exists idx_ai_insights_lookup
    on public.ai_insights(business_id, file_id);

-- Copilot chat history table
create table if not exists public.copilot_messages (
    id uuid primary key default gen_random_uuid(),
    business_id uuid not null references public.businesses(id) on delete cascade,
    file_id uuid not null references public.uploaded_files(id) on delete cascade,
    user_id uuid not null references auth.users(id) on delete cascade,
    role text not null check (role in ('user', 'assistant', 'system')),
    content text not null,
    context jsonb not null default '{}'::jsonb,
    created_at timestamptz default now() not null
);

create index if not exists idx_copilot_messages_lookup
    on public.copilot_messages(business_id, file_id, created_at asc);

-- Enable RLS
alter table public.ai_insights enable row level security;
alter table public.copilot_messages enable row level security;

-- Policies for ai_insights
create policy "Members can read insights of their businesses"
    on public.ai_insights for select
    using (
        exists (
            select 1 from public.business_memberships bm
            where bm.business_id = ai_insights.business_id
            and bm.user_id = auth.uid()
        )
    );

create policy "Members can insert insights for their businesses"
    on public.ai_insights for insert
    with check (
        exists (
            select 1 from public.business_memberships bm
            where bm.business_id = ai_insights.business_id
            and bm.user_id = auth.uid()
        )
    );

create policy "Members can update insights for their businesses"
    on public.ai_insights for update
    using (
        exists (
            select 1 from public.business_memberships bm
            where bm.business_id = ai_insights.business_id
            and bm.user_id = auth.uid()
        )
    )
    with check (
        exists (
            select 1 from public.business_memberships bm
            where bm.business_id = ai_insights.business_id
            and bm.user_id = auth.uid()
        )
    );

create policy "Owners can delete insights"
    on public.ai_insights for delete
    using (
        exists (
            select 1 from public.business_memberships bm
            where bm.business_id = ai_insights.business_id
            and bm.user_id = auth.uid()
            and bm.role = 'owner'
        )
    );

-- Policies for copilot_messages
create policy "Members can read chat messages for their businesses"
    on public.copilot_messages for select
    using (
        exists (
            select 1 from public.business_memberships bm
            where bm.business_id = copilot_messages.business_id
            and bm.user_id = auth.uid()
        )
    );

create policy "Members can insert chat messages for their businesses"
    on public.copilot_messages for insert
    with check (
        exists (
            select 1 from public.business_memberships bm
            where bm.business_id = copilot_messages.business_id
            and bm.user_id = auth.uid()
        )
    );

-- Auto-update updated_at for ai_insights
create or replace trigger ai_insights_updated_at
    before update on public.ai_insights
    for each row
    execute function public.update_updated_at();
