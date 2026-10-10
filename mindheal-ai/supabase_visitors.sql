-- MindHeal AI visitor counter setup.
-- Safe to re-run: existing policies are replaced rather than causing duplicate-policy errors.

create table if not exists public.visitors (
    visitor_id uuid primary key,
    visited_at timestamptz not null default now()
);

alter table public.visitors enable row level security;

grant select, insert on table public.visitors to anon;

drop policy if exists "visitor insert" on public.visitors;
create policy "visitor insert"
    on public.visitors
    for insert
    to anon
    with check (true);

drop policy if exists "visitor count" on public.visitors;
create policy "visitor count"
    on public.visitors
    for select
    to anon
    using (true);

create index if not exists visitors_visited_at_idx
    on public.visitors(visited_at);
