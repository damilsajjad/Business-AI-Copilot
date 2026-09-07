-- ============================================================
-- Migration 004: Create uploaded_files table
-- Tracks file uploads with metadata, linked to businesses
-- ============================================================

create table if not exists public.uploaded_files (
    id uuid primary key default gen_random_uuid(),
    business_id uuid not null references public.businesses(id) on delete cascade,
    uploaded_by uuid not null references auth.users(id) on delete set null,
    original_filename text not null,
    storage_path text not null,
    file_type text not null check (file_type in ('csv', 'xlsx')),
    file_size_bytes bigint not null default 0,
    status text not null default 'uploaded' check (
        status in ('uploaded', 'profiling', 'profiled', 'mapping', 'mapped', 'processing', 'ready', 'error')
    ),
    sheet_count integer default 1,
    error_message text default '',
    metadata jsonb default '{}'::jsonb,
    created_at timestamptz default now() not null,
    updated_at timestamptz default now() not null
);

-- Indexes
create index if not exists idx_uploaded_files_business
    on public.uploaded_files(business_id);

create index if not exists idx_uploaded_files_status
    on public.uploaded_files(status);

create index if not exists idx_uploaded_files_uploaded_by
    on public.uploaded_files(uploaded_by);

-- Enable RLS
alter table public.uploaded_files enable row level security;

-- Members can see files for their businesses
create policy "Members can read files of their businesses"
    on public.uploaded_files for select
    using (
        exists (
            select 1 from public.business_memberships bm
            where bm.business_id = uploaded_files.business_id
            and bm.user_id = auth.uid()
        )
    );

-- Members can upload files to their businesses
create policy "Members can upload files to their businesses"
    on public.uploaded_files for insert
    with check (
        exists (
            select 1 from public.business_memberships bm
            where bm.business_id = uploaded_files.business_id
            and bm.user_id = auth.uid()
        )
    );

-- Service role / backend can update file records (status changes, profiling)
create policy "Service role can update files"
    on public.uploaded_files for update
    using (true)
    with check (true);

-- Owners can delete files
create policy "Owners can delete files"
    on public.uploaded_files for delete
    using (
        exists (
            select 1 from public.business_memberships bm
            where bm.business_id = uploaded_files.business_id
            and bm.user_id = auth.uid()
            and bm.role = 'owner'
        )
    );

-- Auto-update updated_at
create or replace trigger uploaded_files_updated_at
    before update on public.uploaded_files
    for each row
    execute function public.update_updated_at();
