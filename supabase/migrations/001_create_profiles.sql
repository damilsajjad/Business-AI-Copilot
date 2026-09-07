-- ============================================================
-- Migration 001: Create profiles table
-- Links to Supabase auth.users for user profile data
-- ============================================================

create table if not exists public.profiles (
    id uuid primary key references auth.users(id) on delete cascade,
    email text not null,
    full_name text default '',
    avatar_url text default '',
    created_at timestamptz default now() not null,
    updated_at timestamptz default now() not null
);

-- Index for email lookups
create index if not exists idx_profiles_email on public.profiles(email);

-- Enable RLS
alter table public.profiles enable row level security;

-- Users can read their own profile
create policy "Users can read own profile"
    on public.profiles for select
    using (auth.uid() = id);

-- Users can update their own profile
create policy "Users can update own profile"
    on public.profiles for update
    using (auth.uid() = id)
    with check (auth.uid() = id);

-- Service role can insert profiles (used by trigger)
create policy "Service role can insert profiles"
    on public.profiles for insert
    with check (true);

-- Auto-create profile when a new user signs up
create or replace function public.handle_new_user()
returns trigger
language plpgsql
security definer
set search_path = ''
as $$
begin
    insert into public.profiles (id, email, full_name)
    values (
        new.id,
        new.email,
        coalesce(new.raw_user_meta_data ->> 'full_name', '')
    );
    return new;
end;
$$;

-- Trigger on auth.users insert
create or replace trigger on_auth_user_created
    after insert on auth.users
    for each row
    execute function public.handle_new_user();

-- Auto-update updated_at timestamp
create or replace function public.update_updated_at()
returns trigger
language plpgsql
as $$
begin
    new.updated_at = now();
    return new;
end;
$$;

create or replace trigger profiles_updated_at
    before update on public.profiles
    for each row
    execute function public.update_updated_at();
