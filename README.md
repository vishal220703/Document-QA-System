# DocQuest – AI Document Q&A System

DocQuest is a simple and interactive web application that allows you to ask questions about your uploaded documents and get accurate, source-grounded answers using AI.

## 🎯 What It Does

- Upload PDF, DOCX, or TXT documents
- Ask natural language questions about your documents
- Get answers grounded in your actual document content (not generic AI knowledge)
- View your conversation history
- Secure login with JWT authentication

## 🛠️ Tech Stack

- **Backend**: FastAPI + SQLAlchemy + SQLite/PostgreSQL
- **Frontend**: Next.js 14 + React + Tailwind CSS
- **LLM**: Google Gemini (embedding + text generation)
- **Storage**: Local file system for documents

## 📁Project Structure

```
.
├── api.py                      # FastAPI backend entrypoint
├── QAWithPDF/
│   ├── auth.py                # JWT authentication
│   ├── config.py              # Configuration from .env
│   ├── data_ingestion.py      # PDF/DOCX/TXT parsing
│   ├── embedding.py           # Document embedding & retrieval
│   ├── model_api.py           # LLM response generation
│   ├── service.py             # Business logic
│   ├── db_models.py           # Database models
│   ├── db.py                  # Database setup
│   └── schemas.py             # Request/response schemas
├── frontend/                  # Next.js web app
│   ├── app/
│   │   ├── login/page.tsx    # Login/signup page
│   │   └── dashboard/        # Main app interface
│   └── lib/api.ts            # API client
├── requirements.txt           # Python dependencies
├── .env.example              # Environment template
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

## 🚀 Quick Start

### 1. Install Dependencies

**Python**:
```bash
pip install -r requirements.txt
```

**Node.js (Frontend)**:
```bash
cd frontend
npm install
cd ..
```

### 2. Setup Environment

Copy `.env.example` to `.env`:
```bash
cp .env.example .env
```

Get your free Google API key from https://aistudio.google.com/app/apikeys and add it:
```env
GOOGLE_API_KEY=your_key_here
```

### 3. Run the App

**Terminal 1 - Backend** (port 8000):
```bash
uvicorn api:app --reload --host 127.0.0.1 --port 8000
```

**Terminal 2 - Frontend** (port 3000):
```bash
cd frontend
npm run dev
```

### 4. Open in Browser

Go to: **http://localhost:3000**

**Default login credentials**:
- Username: `admin`
- Password: `admin123`

### 5. Use the App

1. Click **Upload Document** and select a PDF, DOCX, or TXT file
2. Ask questions about your document
3. View conversation history

## 📝 Environment Variables

See `.env.example` for all options. Key variables:

| Variable | Default | Purpose |
|----------|---------|---------|
| `GOOGLE_API_KEY` | (required) | Gemini API key |
| `AUTH_USERNAME` | `admin` | Login username |
| `AUTH_PASSWORD` | `admin123` | Login password |
| `TOP_K` | `5` | Number of document chunks to retrieve |
| `CHUNK_SIZE` | `800` | Size of each document chunk |

## 🐛 Troubleshooting

**Backend won't start**:
- Ensure Python 3.10+ is installed: `python --version`
- Try reinstalling dependencies: `pip install --upgrade -r requirements.txt`

**Frontend won't start**:
- Ensure Node 18+ is installed: `node --version`
- Clear node_modules: `cd frontend && rm -rf node_modules && npm install`

**"Login failed" error**:
- Restart the backend: `Ctrl+C` and run `uvicorn api:app --reload`
- Check your credentials match `.env` file

**"Cannot find documents" or upload fails**:
- Ensure `uploads/` folder exists: `mkdir -p uploads`
- Check backend console for error details

**CORS errors**:
- Usually fixed by restarting both backend and frontend

## 🔐 Security Notes

- **Default credentials are for local dev only** – change `AUTH_PASSWORD` and `AUTH_SECRET_KEY` in `.env` if running on a network
- Never commit `.env` to version control
- `GOOGLE_API_KEY` is required to run the app

## 📄 License

MIT

## 👤 Author

Vishal (vishal220703)

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
