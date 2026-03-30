# DocQuest v2

DocQuest is upgraded to an API-first architecture with a modern web frontend.

## What changed

- Streamlit flow removed and replaced by FastAPI backend (`api.py`)
- New Next.js frontend (`frontend/`)
- Upload, index, and citation-based question answering endpoints
- Persistent conversation memory with conversation history APIs
- Configurable model and chunk settings via environment variables

## Project structure

- `api.py`: FastAPI server entrypoint
- `QAWithPDF/`: Core ingestion, embedding, model, and service logic
- `frontend/`: Next.js web app

## New APIs

- `POST /api/v1/auth/login`
- `POST /api/v1/documents/upload`
- `POST /api/v1/chat/query`
- `POST /api/v1/conversations`
- `GET /api/v1/conversations`
- `GET /api/v1/conversations/{conversation_id}`

## Login and authentication

- App now has a dedicated login page at `/login`.
- Backend issues JWT bearer tokens from `POST /api/v1/auth/login`.
- All document/chat APIs require a valid bearer token.

Set these in `.env`:

```env
AUTH_USERNAME=admin
AUTH_PASSWORD=change_this_password
AUTH_SECRET_KEY=replace_with_a_long_random_secret
AUTH_ALGORITHM=HS256
AUTH_TOKEN_EXPIRE_MINUTES=720
```

## Run locally

### Backend

```bash
pip install -r requirements.txt
uvicorn api:app --reload
```

### Frontend

```bash
cd frontend
npm install
npm run dev
```

Open:

- Frontend: `http://localhost:3000` (or the next free port)
- Login page: `http://localhost:3000/login`

## Environment setup

Copy `.env.example` to `.env` and set `GOOGLE_API_KEY`.

Copy `frontend/.env.local.example` to `frontend/.env.local`.

## PostgreSQL setup (detailed)

Use this if you want conversation memory in PostgreSQL.

### Option A: Setup with pgAdmin (recommended)

1. Open pgAdmin and connect to your local PostgreSQL server.

2. Create database:
- Right-click Databases -> Create -> Database.
- Database name: `docquest`
- Owner: `postgres` (or your preferred user)
- Save.

3. Create login role/user:
- Expand `Login/Group Roles`.
- Right-click -> Create -> Login/Group Role.
- General tab: Name = `docquest_user`
- Definition tab: set password.
- Privileges tab: enable `Can login?`.
- Save.

4. Grant privileges in Query Tool:
- Select the `docquest` database.
- Open Query Tool and run:

```sql
GRANT ALL PRIVILEGES ON DATABASE docquest TO docquest_user;
GRANT ALL ON SCHEMA public TO docquest_user;
ALTER DEFAULT PRIVILEGES IN SCHEMA public GRANT ALL ON TABLES TO docquest_user;
ALTER DEFAULT PRIVILEGES IN SCHEMA public GRANT ALL ON SEQUENCES TO docquest_user;
```

5. Update `.env` with these values:

```env
POSTGRES_HOST=localhost
POSTGRES_PORT=5432
POSTGRES_DB=docquest
POSTGRES_USER=docquest_user
POSTGRES_PASSWORD=your_password
POSTGRES_SSLMODE=disable
```

6. Start backend. Tables are auto-created on startup.

7. Verify tables in pgAdmin:
- Databases -> docquest -> Schemas -> public -> Tables.
- You should see `conversations` and `messages` after backend starts.

8. Verify data inserts:
- Ask a question in UI.
- In Query Tool run:

```sql
SELECT id, title, created_at, updated_at FROM conversations ORDER BY updated_at DESC;
SELECT conversation_id, role, LEFT(content, 120) FROM messages ORDER BY created_at DESC;
```

### Option B: Setup with psql CLI

1. Start PostgreSQL service

Windows service name is often `postgresql-x64-XX`.

```powershell
Get-Service | Where-Object { $_.Name -like "postgres*" }
Start-Service postgresql-x64-17
```

2. Open `psql` as postgres superuser

```powershell
psql -U postgres -h localhost
```

If `psql` is not on PATH, use full path from PostgreSQL install, for example:

```powershell
"C:\Program Files\PostgreSQL\17\bin\psql.exe" -U postgres -h localhost
```

3. Create database and user

```sql
CREATE DATABASE docquest;
CREATE USER docquest_user WITH ENCRYPTED PASSWORD 'strong_password_here';
GRANT ALL PRIVILEGES ON DATABASE docquest TO docquest_user;
```

4. Connect to `docquest` and grant schema permissions

```sql
\c docquest
GRANT ALL ON SCHEMA public TO docquest_user;
ALTER DEFAULT PRIVILEGES IN SCHEMA public GRANT ALL ON TABLES TO docquest_user;
ALTER DEFAULT PRIVILEGES IN SCHEMA public GRANT ALL ON SEQUENCES TO docquest_user;
```

5. Set PostgreSQL env values in `.env`

```env
POSTGRES_HOST=localhost
POSTGRES_PORT=5432
POSTGRES_DB=docquest
POSTGRES_USER=docquest_user
POSTGRES_PASSWORD=strong_password_here
POSTGRES_SSLMODE=disable
```

6. Install dependencies (if not already)

```bash
pip install -r requirements.txt
```

7. Start backend

```bash
uvicorn api:app --reload
```

8. Validate DB connection

- Start frontend and ask a question.
- A conversation row and message rows should appear in PostgreSQL:

```sql
SELECT id, title, created_at, updated_at FROM conversations ORDER BY updated_at DESC;
SELECT conversation_id, role, LEFT(content, 80) FROM messages ORDER BY created_at DESC;
```

9. Troubleshooting

- If PostgreSQL is unavailable at startup, backend falls back to `sqlite:///./docquest_memory.db`.
- Fix `DATABASE_URL` and restart backend to return to PostgreSQL.

## Docker deployment (step-by-step)

This repository now includes:

- `Dockerfile` for backend
- `frontend/Dockerfile` for frontend
- `docker-compose.yml` with `postgres`, `pgadmin`, `backend`, and `frontend`

### 1. Prerequisites

- Install Docker Desktop
- Ensure Docker is running
- Ensure ports are free or change them in `docker-compose.yml`:
  - `3000` (frontend)
  - `8000` (backend)
  - `5432` (postgres)
  - `5050` (pgAdmin)

### 2. Set required environment values

From project root, create/update `.env` and add at least:

```env
GOOGLE_API_KEY=your_real_google_api_key
```

The compose file already wires database and auth defaults. For production, change these values in `docker-compose.yml`:

- `POSTGRES_PASSWORD`
- `AUTH_PASSWORD`
- `AUTH_SECRET_KEY`
- `PGADMIN_DEFAULT_PASSWORD`

### 3. Build and start all services

Run from project root:

```bash
docker compose up -d --build
```

Check status:

```bash
docker compose ps
```

### 4. Access services

- Frontend: `http://localhost:3000`
- Backend health: `http://localhost:8000/health`
- pgAdmin4: `http://localhost:5050`

### 5. Login to your app

Use the app credentials configured for backend:

- Username: `AUTH_USERNAME` (default `admin`)
- Password: `AUTH_PASSWORD` (set your own value)

### 6. Connect pgAdmin4 to PostgreSQL container

1. Open pgAdmin: `http://localhost:5050`
2. Login with:
	- Email: `admin@docquest.local`
	- Password: `PGADMIN_DEFAULT_PASSWORD`
3. Right-click **Servers** -> **Register** -> **Server...**
4. In **General** tab:
	- Name: `DocQuest PostgreSQL`
5. In **Connection** tab:
	- Host: `postgres`
	- Port: `5432`
	- Maintenance DB: `docquest`
	- Username: `docquest_user`
	- Password: `strong_password_here` (or your updated value)
6. Save.

### 7. Verify tables and chat data in pgAdmin4

Open Query Tool and run:

```sql
SELECT id, title, created_at, updated_at FROM conversations ORDER BY updated_at DESC;
SELECT conversation_id, role, LEFT(content, 120) FROM messages ORDER BY created_at DESC;
```

### 8. Common Docker commands

Stop all services:

```bash
docker compose down
```

Stop and remove volumes (destroys DB data):

```bash
docker compose down -v
```

View logs:

```bash
docker compose logs -f backend
docker compose logs -f frontend
docker compose logs -f postgres
```

### 9. Production notes

- Use strong secrets and passwords.
- Put a reverse proxy (Nginx/Traefik) in front with HTTPS.
- Restrict exposed ports and firewall access.
- Back up PostgreSQL volumes regularly.
- Avoid committing `.env` files with secrets.

## Frontend + backend integration

- Frontend calls backend via `/api/backend/*` proxy route.
- Next.js rewrites proxy to `BACKEND_INTERNAL_URL`.
- Backend CORS is controlled via `CORS_ORIGINS` in `.env`.
