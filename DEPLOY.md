# Deploying for free (Render + Vercel)

This app is **read-only** and ships its data as a committed SQLite file
(`backend/app/data/fifa.db`), so there is **no database to host or pay for**. You deploy two
free pieces:

- **Backend** (FastAPI) → **Render** free web service (Docker). Data is baked into the image.
- **Frontend** (React) → **Vercel** free static hosting.

> The data is **not** taken from your local PostgreSQL. It lives in the repo (the SQLite file)
> and is regenerated from the CC0 source with `python scripts/build_sqlite.py`. Your local
> Postgres is only for development and is not used in production.

Total cost: **$0**. Only caveat: Render's free backend **sleeps after ~15 min idle** and takes
~50s to wake on the next request (the frontend shows loading states meanwhile).

---

## 0. One-time: put the code on GitHub

From the project root:

```bash
git init
git add -A
git commit -m "FIFA World Cup platform"
```

Create an empty repo on GitHub (github.com → New repository), then:

```bash
git remote add origin https://github.com/<your-username>/<repo>.git
git branch -M main
git push -u origin main
```

> The `.gitignore` already excludes `backend/.env` (your API key) and `node_modules/`, and
> **includes** the baked-in `backend/app/data/fifa.db`.

---

## 1. Backend → Render (free)

1. Sign in at https://render.com with your GitHub account.
2. **New → Blueprint** → select your repo. Render reads [`render.yaml`](render.yaml) and creates a
   free Docker web service named `fifa-wc-api`.
   - *(Manual alternative: New → Web Service → your repo → Root Directory `backend`, Runtime
     `Docker`, Instance type `Free`, Health Check Path `/api/health`.)*
3. Click **Apply / Create**. First build takes a few minutes.
4. When it's live, copy the URL, e.g. `https://fifa-wc-api.onrender.com`.
5. Test it: open `https://<your-backend>/api/health` → should show `{"status":"ok",...}`, and
   `https://<your-backend>/docs` for the API docs.

Leave `CORS_ORIGINS` empty for now — you'll set it in step 3.

## 2. Frontend → Vercel (free)

1. Sign in at https://vercel.com with GitHub → **Add New → Project** → import the same repo.
2. Set **Root Directory** to `frontend`. Vercel auto-detects Vite (build `npm run build`,
   output `dist`); [`vercel.json`](frontend/vercel.json) handles client-side routing.
3. Under **Environment Variables**, add:
   - `VITE_API_BASE` = `https://<your-backend>.onrender.com/api`  ← your Render URL **+ `/api`**
4. **Deploy**. Copy the resulting URL, e.g. `https://fifa-wc.vercel.app`.

## 3. Connect them (CORS)

1. Back in Render → your service → **Environment** → add:
   - `CORS_ORIGINS` = `https://<your-frontend>.vercel.app`  (your Vercel URL, no trailing slash)
2. Save — Render redeploys automatically. (`CORS_ORIGIN_REGEX` is already set to allow Vercel
   preview URLs.)

Open your Vercel URL — the dashboard loads live from the deployed API. Done. 🎉

---

## Updating the data later

```bash
cd backend
venv\Scripts\python scripts\build_sqlite.py   # rebuilds app/data/fifa.db from martj42 (CC0)
cd ..
git add backend/app/data/fifa.db && git commit -m "Refresh data" && git push
```

Render and Vercel redeploy automatically on push.

## Alternatives (all free)

- **One container (Hugging Face Space or Fly.io):** the same `backend/Dockerfile` runs anywhere.
  You can also build the frontend and serve it from the backend to get a single URL.
- **Netlify instead of Vercel:** import the repo, base directory `frontend`; `netlify.toml`
  already configures the build + SPA redirect. Set `VITE_API_BASE` in Netlify's env settings.
- **Backend elsewhere:** Fly.io (`fly launch` with the Dockerfile) and Koyeb also have free tiers.

## Troubleshooting

- **Frontend loads but no data / CORS error in console:** `VITE_API_BASE` (Vercel) must be your
  backend URL **+ `/api`**; `CORS_ORIGINS` (Render) must be your exact frontend origin.
- **First request is slow (~50s):** Render free tier was asleep; it's warm after that.
- **`/api/health` fails on Render:** check the service logs; ensure Root Directory is `backend`
  and Runtime is `Docker`.
