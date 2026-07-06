# Portfolio Backend — Setup Guide

This adds a real database to your portfolio: contact messages, a blog you can
post to without touching HTML, visitor-approved testimonials, and a visit
counter. Stack: **FastAPI + Supabase** (same as your RAG project).

## 1. Create the database (Supabase)

1. Go to https://supabase.com → create a free project (or reuse your existing one).
2. Open **SQL Editor** → paste everything from `schema.sql` → Run.
3. Go to **Project Settings → API** and copy:
   - `Project URL` → this is `https://snvmfhlanrczldqiltky.supabase.co/rest/v1/`
   - `service_role` key (NOT the `anon` key — the service role key bypasses
     row-level security so your backend can read/write everything) → this is
     `eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJzdXBhYmFzZSIsInJlZiI6InNudm1maGxhbnJjemxkcWlsdGt5Iiwicm9sZSI6InNlcnZpY2Vfcm9sZSIsImlhdCI6MTc4MzMxODA2NSwiZXhwIjoyMDk4ODk0MDY1fQ.nAgSTJULxkSOnZ1_gxqAX5oL4MKKlGzuPuMez4bv3q4`

## 2. Run the backend locally

```bash
cd backendpython -m venv venv
python -m venv venv
source venv/bin/activate        # Windows: venv\Scripts\activate
pip install -r requirements.txt
cp .env.example .env
```

Edit `.env` and fill in `SUPABASE_URL`, `SUPABASE_SERVICE_KEY`, and make up an
`ADMIN_KEY` (this is your admin password — keep it secret, don't reuse a real
password).

```bash
uvicorn main:app --reload --port 8000
```

Visit http://127.0.0.1:8000/docs — you'll see interactive API docs and can
test every endpoint from the browser.

## 3. Point the frontend at your backend

In two files, change the `API_BASE_URL` constant:
- `assets/js/api.js`
- `admin.html`

While testing locally, leave it as `http://127.0.0.1:8000`. Open `index.html`
in your browser (or use a tool like VS Code's Live Server) and try the
contact form, testimonials, and visitor counter.

Open `admin.html` in your browser and log in with your `ADMIN_KEY` to publish
a blog post and approve testimonials.

## 4. Deploy the backend (Render — free tier)

1. Push this project to GitHub.
2. Go to https://render.com → New → Web Service → connect your repo.
3. Root directory: `backend`
4. Build command: `pip install -r requirements.txt`
5. Start command: `uvicorn main:app --host 0.0.0.0 --port $PORT`
6. Add environment variables: `SUPABASE_URL`, `SUPABASE_SERVICE_KEY`,
   `ADMIN_KEY`, and `ALLOWED_ORIGINS` (set this to your deployed site's URL,
   e.g. `https://your-username.github.io`).
7. Deploy. Render gives you a URL like `https://your-api.onrender.com`.

## 5. Point the live site at the deployed backend

Update `API_BASE_URL` in `assets/js/api.js` and `admin.html` to your Render
URL, then redeploy your frontend (GitHub Pages, Vercel, Netlify — wherever
you're hosting it now).

## Notes on security

- `admin.html` uses a single shared secret (`ADMIN_KEY`), not real user
  accounts. That's fine for a personal site only you manage. If this ever
  needs more than one admin, swap it for real authentication (e.g. Supabase
  Auth with email/password).
- The database's row-level security is on by default, so nobody can read or
  write your data directly from the browser using Supabase's public key —
  all access goes through your API, which uses the service-role key.
- Note in `main.py` that the free Render tier "spins down" after inactivity,
  so the first request after a while can take ~30–50 seconds to wake up.
  This is normal and matches what you'll see with your RAG project's backend
  too.
