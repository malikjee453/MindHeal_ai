-- Run this script in Supabase SQL Editor before enabling MindHeal accounts.
-- Supabase Auth handles password hashing; passwords are never stored by MindHeal tables.

create table if not exists public.mindheal_profiles (
  user_id uuid primary key references auth.users(id) on delete cascade,
  display_name text not null default '',
  memory_enabled boolean not null default false,
  memory_summary text not null default '',
  created_at timestamptz not null default now(),
  updated_at timestamptz not null default now()
);

create table if not exists public.mindheal_turns (
  id bigint generated always as identity primary key,
  user_id uuid not null references auth.users(id) on delete cascade,
  role text not null check (role in ('user','assistant')),
  content text not null,
  created_at timestamptz not null default now()
);

create table if not exists public.mindheal_progress (
  id bigint generated always as identity primary key,
  user_id uuid not null references auth.users(id) on delete cascade,
  mood smallint not null check (mood between 1 and 10),
  stress smallint check (stress between 1 and 10),
  note text not null default '',
  created_at timestamptz not null default now()
);

alter table public.mindheal_profiles enable row level security;
alter table public.mindheal_turns enable row level security;
alter table public.mindheal_progress enable row level security;

drop policy if exists "Users manage own profile" on public.mindheal_profiles;
create policy "Users manage own profile" on public.mindheal_profiles
for all to authenticated using (auth.uid() = user_id) with check (auth.uid() = user_id);

drop policy if exists "Users manage own turns" on public.mindheal_turns;
create policy "Users manage own turns" on public.mindheal_turns
for all to authenticated using (auth.uid() = user_id) with check (auth.uid() = user_id);

drop policy if exists "Users manage own progress" on public.mindheal_progress;
create policy "Users manage own progress" on public.mindheal_progress
for all to authenticated using (auth.uid() = user_id) with check (auth.uid() = user_id);

create index if not exists mindheal_turns_user_created_idx on public.mindheal_turns(user_id, created_at desc);
create index if not exists mindheal_progress_user_created_idx on public.mindheal_progress(user_id, created_at desc);
