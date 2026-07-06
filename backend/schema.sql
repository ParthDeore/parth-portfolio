-- ============================================================
-- Portfolio Database Schema (run this in Supabase SQL Editor)
-- Project > SQL Editor > New query > paste all of this > Run
-- ============================================================

-- 1. Contact messages (from your Contact form)
create table if not exists contact_messages (
  id bigint generated always as identity primary key,
  name text not null,
  email text not null,
  subject text,
  message text not null,
  is_read boolean not null default false,
  created_at timestamptz not null default now()
);

-- 2. Blog / project update posts (shown in the new "Blog" section)
create table if not exists blog_posts (
  id bigint generated always as identity primary key,
  title text not null,
  content text not null,
  cover_image_url text,
  created_at timestamptz not null default now()
);

-- 3. Testimonials (visitors submit, you approve before they appear)
create table if not exists testimonials (
  id bigint generated always as identity primary key,
  name text not null,
  role text,
  message text not null,
  status text not null default 'pending' check (status in ('pending', 'approved', 'rejected')),
  created_at timestamptz not null default now()
);

-- 4. Visitor counter (single row that increments)
create table if not exists page_visits (
  id int primary key default 1,
  count bigint not null default 0
);
insert into page_visits (id, count)
values (1, 0)
on conflict (id) do nothing;

-- ============================================================
-- Row Level Security: lock every table down by default.
-- Your FastAPI backend uses the SERVICE ROLE key, which bypasses
-- RLS entirely, so the backend can still read/write everything.
-- This just prevents anyone from hitting Supabase directly from
-- the browser with the public anon key and reading/writing data
-- without going through your API.
-- ============================================================
alter table contact_messages enable row level security;
alter table blog_posts enable row level security;
alter table testimonials enable row level security;
alter table page_visits enable row level security;
