create table if not exists public.articles (
 id text primary key, title text not null, url text not null unique,
 source text, published_at timestamptz, collected_at timestamptz not null default now(),
 description text, origin text not null default 'unknown'
);
create index if not exists articles_published_at_idx on public.articles(published_at desc);
alter table public.articles enable row level security;
-- Prototype policy for public-source research data. Tighten before production.
create policy "public can read articles" on public.articles for select using (true);
create policy "public can insert articles" on public.articles for insert with check (true);
create policy "public can update articles" on public.articles for update using (true) with check (true);
