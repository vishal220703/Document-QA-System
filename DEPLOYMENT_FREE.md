# Free Deployment Guide: Vercel + Render + Neon

This guide deploys your DocQuest project entirely on free tiers using:
- **Frontend**: Vercel (free)
- **Backend**: Render (free, may sleep when idle)
- **Database**: Neon (free PostgreSQL)
- **LLM**: Google Gemini API (free tier available)

## Prerequisites

1. **GitHub Account** - Push your code there
2. **Google API Key** - For Gemini LLM (get at https://aistudio.google.com/app/apikeys)
3. **Neon Account** - For PostgreSQL (free at https://neon.tech)
4. **Render Account** - For backend (free at https://render.com)
5. **Vercel Account** - For frontend (free at https://vercel.com)

---

## Step 1: Prepare Your GitHub Repo

1. Push all code to GitHub:
   ```bash
   git add .
   git commit -m "Deploy to free tier"
   git push origin main
   ```

2. Make sure your root directory is clean (no node_modules, __pycache__, build/, etc.)

---

## Step 2: Create PostgreSQL Database on Neon

1. Go to https://neon.tech and sign up (free tier).
2. Create a new project.
3. Create a database named `docquest`.
4. Copy the connection string:
   - It looks like: `postgresql://user:password@host/dbname?sslmode=require`
   - **Convert to SQLAlchemy format**: `postgresql+psycopg2://user:password@host/dbname?sslmode=require`
5. Save this; you'll need it in Step 3.

---

## Step 3: Deploy Backend on Render

1. Go to https://render.com and sign up.
2. Click **New +** → **Web Service**.
3. Connect your GitHub repository.
4. Fill in settings:
   - **Name**: `docquest-backend`
   - **Runtime**: Docker
   - **Region**: Oregon (or closest to you)
   - **Plan**: Free
   - **Dockerfile Path**: `./Dockerfile`
5. Click **Advanced** and add environment variables:

| Key | Value |
|-----|-------|
| `APP_ENV` | `production` |
| `LLM_PROVIDER` | `gemini` |
| `GOOGLE_API_KEY` | *Your Gemini API key* |
| `GEMINI_MODEL_NAME` | `gemini-2.0-flash` |
| `GEMINI_EMBEDDING_MODEL_NAME` | `gemini-embedding-001` |
| `DATABASE_URL` | *PostgreSQL+psycopg2 URL from Neon* |
| `TOP_K` | `5` |
| `CHUNK_SIZE` | `800` |
| `CHUNK_OVERLAP` | `100` |
| `CORS_ORIGINS` | `https://your-vercel-url.vercel.app,http://localhost:3000` |
| `DATA_DIR` | `/tmp/data` |
| `STORAGE_DIR` | `/tmp/storage` |
| `UPLOAD_DIR` | `/tmp/uploads` |
| `AUTH_USERNAME` | `admin` |
| `AUTH_PASSWORD` | *Choose a strong password* |
| `AUTH_SECRET_KEY` | *Generate random: `python -c "import secrets; print(secrets.token_urlsafe(32))"` in terminal* |
| `AUTH_ALGORITHM` | `HS256` |
| `AUTH_TOKEN_EXPIRE_MINUTES` | `720` |
| `POSTGRES_SSLMODE` | `require` |

6. Click **Create Web Service** and wait for deployment (~2-3 min).
7. Once deployed, copy your backend URL (e.g., `https://docquest-backend.onrender.com`).
8. Test it: Open `https://docquest-backend.onrender.com/health` in browser; should see `{"status":"ok","version":"2.0.0"}`.

**Note**: Render's free tier may auto-sleep after 15 min of inactivity. First request after sleep takes 10-30 sec.

---

## Step 4: Deploy Frontend on Vercel

1. Go to https://vercel.com and sign up.
2. Click **Add New** → **Project**.
3. Import your GitHub repository.
4. Configure:
   - **Framework Preset**: Next.js (auto-detected)
   - **Root Directory**: `frontend`
   - **Build Command**: `npm run build`
   - **Install Command**: `npm install`
5. Add environment variable:
   - **Name**: `NEXT_PUBLIC_API_BASE_URL`
   - **Value**: `https://docquest-backend.onrender.com` (your Render URL from Step 3)
6. Click **Deploy** and wait (~1-2 min).
7. Once deployed, open your Vercel URL.

---

## Step 5: Update CORS on Backend (if needed)

If you get CORS errors:

1. Go back to Render dashboard → docquest-backend → Settings.
2. Edit environment variable `CORS_ORIGINS`.
3. Add your Vercel URL: `https://your-vercel-url.vercel.app`
4. Save and redeploy.

---

## Step 6: Test the Full Stack

1. Open your Vercel frontend URL.
2. Sign in with default credentials:
   - **Username**: `admin`
   - **Password**: `change_this_to_a_strong_password` (whatever you set in AUTH_PASSWORD)
3. Upload a PDF or text file.
4. Ask a question about the document.

---

## Important Notes

### Free Tier Limitations

| Service | Free Tier Limit |
|---------|-----------------|
| **Render** | Sleep after 15 min idle; 400 build hours/month |
| **Neon** | 5 projects; 3GB storage; limited compute |
| **Vercel** | 100 deployments/month; 6000 build minutes/month |
| **Gemini API** | 60 requests/min free tier; quota limits apply |

### Known Issues & Solutions

**Problem**: "Service down" or timeout after deploy
**Solution**: Render's free tier sleeps. Wait 30 sec and retry.

**Problem**: Upload fails or chat returns empty
**Solution**: Check Render logs for errors; may be cold start or DB connection issue.

**Problem**: CORS error in browser console
**Solution**: Verify CORS_ORIGINS in Render env var includes your Vercel URL.

**Problem**: Files/documents disappear after redeploy
**Solution**: Render's free tier doesn't persist disk. Use Neon (persists) but upload dirs don't. For production, add cloud storage.

---

## Production Improvements (When Ready)

1. **Persistent Storage**: Use AWS S3 or Google Cloud Storage for uploads.
2. **Better Auth**: Add email verification, OAuth (GitHub, Google).
3. **Monitoring**: Add error tracking (Sentry) and logging (Datadog).
4. **Database Backups**: Neon auto-backups; test restore workflows.
5. **Rate Limiting**: Protect API from abuse.
6. **API Keys**: Rotate AUTH_SECRET_KEY every 3-6 months in production.

---

## Redeploy After Code Changes

1. Push updates to GitHub:
   ```bash
   git add .
   git commit -m "Feature update"
   git push origin main
   ```

2. **Render**: Auto-deploys on push (if webhook is configured).
3. **Vercel**: Auto-deploys on push (if connected).

Both services redeploy in ~1-2 min.

---

## Support & Debugging

- **Render Logs**: Dashboard → docquest-backend → Logs
- **Vercel Logs**: Dashboard → Deployments → View logs
- **Neon Dashboard**: Check connections, query count, storage usage
- **Chrome DevTools**: Check network tab for API responses

For issues, check:
1. Network tab in DevTools (is API_BASE_URL correct?)
2. Render logs (backend errors)
3. Backend /health endpoint (is it running?)
4. DATABASE_URL format (must be SQLAlchemy format, not raw psql)

---

## Next Steps (Optional Enhancements)

- Add email notifications for errors
- Set up GitHub Actions for automated testing
- Add custom domain (Vercel + Render both support this)
- Enable HTTPS/SSL (Vercel/Render auto-enable)
- Add analytics dashboard for usage tracking
