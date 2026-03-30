# DocQuest v2 – Production-Ready Document Intelligence Platform

DocQuest is an API-first, full-stack document Q&A system with secure authentication, workspace management, and advanced RAG capabilities.

## 🎯 What It Does

- **Private Document QA**: Answers questions grounded in your uploaded documents, not generic LLM knowledge
- **Traceable Answers**: Each response includes source citations and verification scores
- **Enterprise Ready**: Authentication, workspaces, API keys, deployment-ready with Docker
- **Advanced Retrieval**: Multiple retrieval strategies, structured response modes, verification scoring
- **Production Features**: Memory graphs, query automation, evaluation telemetry, webhooks

## 🏗️ Architecture

- **Backend**: FastAPI + SQLAlchemy + PostgreSQL
- **Frontend**: Next.js 14 + React + Tailwind CSS
- **LLM**: Google Gemini (embedding + generation)
- **Storage**: PostgreSQL for conversations/metadata; local disk for documents
- **Deployment**: Docker + Render (backend) + Vercel (frontend) + Neon (PostgreSQL)

## 📦 Project Structure

```
.
├── api.py                          # FastAPI entrypoint
├── QAWithPDF/
│   ├── __init__.py
│   ├── auth.py                    # JWT + API key authentication
│   ├── config.py                  # Settings from environment
│   ├── data_ingestion.py          # PDF/DOCX/TXT parsing & chunking
│   ├── embedding.py               # Query engine setup with retrieval modes
│   ├── model_api.py               # LLM response generation
│   ├── service.py                 # Business logic (retrieval, output modes, verification, graphs)
│   ├── db_models.py               # SQLAlchemy ORM entities
│   ├── schemas.py                 # Pydantic request/response models
│   ├── db.py                      # Database initialization
│   ├── exception.py               # Custom exceptions
│   └── __pycache__/
├── frontend/                       # Next.js web app
│   ├── app/
│   │   ├── login/page.tsx         # Auth + landing page
│   │   ├── dashboard/page.tsx     # Main app interface
│   │   └── ...
│   ├── lib/api.ts                 # API client with auth headers
│   ├── next.config.mjs            # Rewrite backend proxy
│   ├── Dockerfile
│   └── package.json
├── Dockerfile                      # Backend Python container
├── docker-compose.yml             # Local dev stack
├── requirements.txt               # Python dependencies
├── .env.example                   # Environment template
├── .env.production                # Production env template
├── render.yaml                    # Render deployment config
├── vercel.json                    # Vercel deployment config
├── DEPLOYMENT_FREE.md             # Free tier deployment guide
└── README.md
```

## 🚀 Quick Start

### 1. Install Dependencies

```bash
pip install -r requirements.txt
cd frontend && npm install && cd ..
```

### 2. Setup Environment

Copy `.env.example` to `.env`:

```bash
cp .env.example .env
```

Set `GOOGLE_API_KEY` (get from https://aistudio.google.com/app/apikeys):

```env
GOOGLE_API_KEY=your_key_here
```

### 3. Database Setup (Optional for local dev; uses SQLite fallback)

For PostgreSQL:

```bash
# Windows (adjust service name as needed)
Start-Service postgresql-x64-17

# Create DB and user
psql -U postgres -h localhost
```

```sql
CREATE DATABASE docquest;
CREATE USER docquest_user WITH ENCRYPTED PASSWORD 'your_password';
GRANT ALL PRIVILEGES ON DATABASE docquest TO docquest_user;
```

Update `.env`:

```env
DATABASE_URL=postgresql+psycopg2://docquest_user:your_password@localhost:5432/docquest
```

### 4. Run Locally

**Terminal 1 (Backend)**:
```bash
uvicorn api:app --reload --host 127.0.0.1 --port 8000
```

**Terminal 2 (Frontend)**:
```bash
cd frontend
npm run dev
```

Open: http://localhost:3000/login

**Default credentials** (from `.env.example`):
- Username: `admin`
- Password: `admin123`

### 5. Test the App

1. Login with default credentials
2. Upload a PDF, DOCX, or TXT file
3. Ask a question about the document
4. View conversation history

## 🌐 Production Deployment

**FASTEST FREE OPTION**: Render (backend) + Neon (database) + Vercel (frontend)

See [DEPLOYMENT_FREE.md](DEPLOYMENT_FREE.md) for step-by-step instructions.

**Or use Docker Compose locally**:

```bash
docker-compose up -d
# Opens on http://localhost:3000
```

## 🔑 Key APIs

### Authentication

```
POST /api/v1/auth/login
POST /api/v1/auth/signup
```

### Documents & Chat

```
POST /api/v1/documents/upload       # Upload PDF/DOCX/TXT
POST /api/v1/chat/query             # Ask a question
GET /api/v1/conversations           # List conversations
GET /api/v1/conversations/{id}      # Get conversation + messages
```

### Advanced Features

```
POST /api/v1/workspaces             # Create workspace
GET /api/v1/workspaces              # List workspaces
GET /api/v1/workspaces/{id}/graph   # Memory graph
POST /api/v1/automations            # Create automation
POST /api/v1/automations/{id}/run   # Run automation
GET /api/v1/monitoring/evaluations  # Evaluation summary
POST /api/v1/api-keys               # Create API key
```

## ⚙️ Configuration

All settings from environment variables (see `.env.example`):

| Variable | Default | Description |
|----------|---------|-------------|
| `GOOGLE_API_KEY` | (required) | Gemini API key |
| `DATABASE_URL` | SQLite | PostgreSQL connection string |
| `AUTH_SECRET_KEY` | (required in prod) | JWT signing key |
| `CORS_ORIGINS` | localhost:3000/3001 | Allowed frontend origins |
| `TOP_K` | 5 | Document chunks to retrieve |
| `CHUNK_SIZE` | 800 | Document chunk size in tokens |

## 🐛 Troubleshooting

**"CORS error" in browser**: 
- Add your frontend URL to `CORS_ORIGINS` in `.env` and restart backend.

**"Connection refused" on API calls**:
- Ensure backend is running: `uvicorn api:app --reload`
- Check `NEXT_PUBLIC_API_BASE_URL` in frontend `.env`

**"PostgreSQL connection failed"**:
- Verify PostgreSQL is running
- Check `DATABASE_URL` format
- Or just use SQLite (auto-fallback in dev)

**Upload fails**:
- Check file size (PDFs/DOCXs should be < 10MB for free tier)
- Verify `UPLOAD_DIR` exists: `mkdir -p uploads`

**Render backend sleeping**:
- Free tier auto-sleeps after 15 min idle; first request takes 10-30 sec
- Upgrade to paid tier if you need always-on

## 📚 Advanced Features

- **Retrieval Modes**: `standard`, `hybrid`, `decompose`, `rerank`
- **Output Modes**: `standard`, `bullet_points`, `executive_brief`, `table`, `json`
- **Verification**: Source-grounded confidence scores
- **Memory Graph**: Knowledge graph extraction from conversations
- **Query Automation**: Schedule recurring questions
- **Evaluation**: Track QA accuracy and user feedback

## 🔐 Security

- **JWT Authentication**: Secure token-based access
- **API Keys**: Alternative key-based auth for integrations
- **Password Hashing**: bcrypt with salt
- **CORS**: Configurable allowed origins
- **Environment Secrets**: Sensitive values in `.env` (not committed)

## 📄 License

MIT

## 👤 Author

Vishal (vishal220703)

## 🤝 Contributing

Pull requests welcome. For major changes, open an issue first.

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
=======
### 3. Run the App

```bash
streamlit run StreamlitApp.py
```

### 📌 Notes

1. You must configure your embedding and LLM API keys in the respective modules (embedding.py, model_api.py).
2. All uploaded documents are processed in memory and are not stored permanently.
3. Logo can be replaced by adding your own logo.png to the root directory.

🧑‍💻 Author- Vishal M
📫 LinkedIn
💻 GitHub
>>>>>>> 150355389e9d53e8ace41b249a3833660ab1dcba
