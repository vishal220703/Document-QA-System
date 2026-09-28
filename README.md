# DocQuest – AI Document Q&A System

DocQuest is a simple and interactive web application that allows you to ask questions about your uploaded documents and get accurate, source-grounded answers using AI.

## 🎯 What It Does

- Upload PDF, DOCX, or TXT documents
- Ask natural language questions about your documents
- Get answers grounded in your actual document content (not generic AI knowledge)
- View your conversation history
- Secure login with JWT authentication

## 🛠️ Tech Stack

- **Backend**: FastAPI + SQLAlchemy + PostgreSQL
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

**Python**:
```bash
pip install -r requirements.txt
```

**Node.js**:
```bash
npm install
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

**Frontend + backend**:
```bash
npm run dev
```

This starts the backend on port 8000 and the frontend on port 3000.

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

- Authenticated users can access only their own uploaded documents and chat history.
- **Default credentials are for local dev only** – change `AUTH_PASSWORD` and `AUTH_SECRET_KEY` in `.env` if running on a network
- Never commit `.env` to version control
- `GOOGLE_API_KEY` is required to run the app

## 📄 License

MIT

## 👤 Author

Vishal (vishal220703)
