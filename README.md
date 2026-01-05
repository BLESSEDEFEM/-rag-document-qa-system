# 🤖 RAG Document Q&A System

A production-ready **Retrieval-Augmented Generation (RAG)** system that enables users to upload documents (PDF, DOCX, TXT) and ask questions, receiving accurate AI-generated answers with source citations.

[![Live Demo](https://img.shields.io/badge/demo-live-success)](https://rag-document-qa-system.vercel.app)
[![Backend API](https://img.shields.io/badge/API-Railway-purple)](https://rag-document-qa-system-production.up.railway.app)
[![Tests](https://img.shields.io/badge/tests-18%20passed-brightgreen)](https://github.com/BLESSEDEFEM/rag-document-qa-system)

---

## 🌟 Key Features

- 📄 **Multi-Format Support** - Upload PDF, DOCX, and TXT files (up to 10MB)
- 🔍 **Semantic Search** - Dual embedding models (Gemini + Cohere fallback)
- 💬 **AI-Powered Answers** - Google Gemini 2.0 Flash generates contextual responses
- 📚 **Source Citations** - Every answer includes document sources with relevance scores
- 🔐 **Secure Authentication** - Clerk-based JWT authentication with user isolation
- 🦠 **Virus Scanning** - VirusTotal integration for uploaded files
- ⚡ **Background Processing** - Large documents processed asynchronously
- 🚀 **Production Deployment** - Railway (backend) + Vercel (frontend)
- 📱 **Mobile Responsive** - Optimized for all screen sizes

---

## 🏗️ System Architecture
```
┌─────────────┐
│   User      │ (Browser)
└──────┬──────┘
       │ HTTPS
       ▼
┌──────────────────────┐
│  React + TypeScript  │ ← Vercel
│  Clerk Auth          │
└────────┬─────────────┘
         │ REST API + JWT
         ▼
┌──────────────────────┐
│  FastAPI Backend     │ ← Railway
│  + Background Tasks  │
└────┬──────┬──────┬───┘
     │      │      │
     ▼      ▼      ▼
┌─────────┐┌──────────┐┌──────────┐
│Pinecone ││PostgreSQL││VirusTotal│
│ Vectors ││  (Docs)  ││ (Scan)   │
└─────────┘└──────────┘└──────────┘
     │
     ▼
┌──────────────────────┐
│ Gemini (primary)     │
│ Cohere (fallback)    │
└──────────────────────┘
```

---

## 🛠️ Tech Stack

### Frontend
- **Framework:** React 18.3 + TypeScript 5.5
- **Build Tool:** Vite 5.x
- **UI:** Tailwind CSS + shadcn/ui
- **Auth:** Clerk React
- **State:** React Query
- **Deployment:** Vercel

### Backend
- **Framework:** FastAPI 0.104+
- **Language:** Python 3.11
- **Database:** PostgreSQL (SQLAlchemy ORM)
- **Vector DB:** Pinecone (768-dim for Gemini, 1024-dim for Cohere)
- **Embeddings:** Google Gemini text-embedding-004 (primary), Cohere embed-v3 (fallback)
- **LLM:** Google Gemini 2.0 Flash
- **Auth:** Clerk JWT verification
- **Security:** VirusTotal API, rate limiting
- **Deployment:** Railway

### Document Processing
- **PDF:** PyPDF2
- **DOCX:** python-docx
- **Chunking:** RecursiveCharacterTextSplitter (1000 chars, 100 overlap)
- **Max chunks:** 200 per document (quota protection)

---

## 🚀 Live Demo

- **Frontend:** [https://rag-document-qa-system.vercel.app](https://rag-document-qa-system.vercel.app)
- **API Docs:** [https://rag-document-qa-system-production.up.railway.app/api/docs](https://rag-document-qa-system-production.up.railway.app/api/docs)

**Test Account:** Sign up with any email (Clerk handles authentication)

---

## 📋 Prerequisites

- **Python** 3.11+
- **Node.js** 18+
- **PostgreSQL** 14+ (or Railway database)
- **API Keys:**
  - [Google Gemini API](https://ai.google.dev) (free: 15,000 requests/month)
  - [Cohere API](https://dashboard.cohere.com) (free: 100 requests/month)
  - [Pinecone](https://www.pinecone.io) (free: 1 index)
  - [VirusTotal](https://www.virustotal.com) (free: 4 requests/minute)
  - [Clerk](https://clerk.com) (free: 10,000 MAUs)

---

## 🔧 Local Development Setup

### 1. Clone Repository
```bash
git clone https://github.com/Blessing92/rag-document-qa-system.git
cd rag-document-qa-system
```

### 2. Backend Setup
```bash
cd backend

# Create virtual environment
python -m venv venv
source venv/bin/activate  # Windows: venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt

# Create .env file (copy from .env.example)
cp .env.example .env
# Edit .env and add your API keys

# Run database migrations (if using local PostgreSQL)
# psql -U postgres -c "CREATE DATABASE rag_db;"

# Start server
uvicorn app.main:app --reload --port 8000
```

**Backend will run at:** `http://localhost:8000`  
**API Docs:** `http://localhost:8000/api/docs`

### 3. Frontend Setup
```bash
cd ../frontend

# Install dependencies
npm install

# Create .env file
echo "VITE_API_URL=http://localhost:8000" > .env
echo "VITE_CLERK_PUBLISHABLE_KEY=your_clerk_key" >> .env

# Start development server
npm run dev
```

**Frontend will run at:** `http://localhost:5173`

### 4. Setup Pinecone Index

1. Go to [Pinecone Console](https://app.pinecone.io)
2. Create new index:
   - **Name:** `rag-documents`
   - **Dimensions:** `768` (for Gemini) or `1024` (for Cohere)
   - **Metric:** `cosine`
   - **Cloud:** `AWS` (free tier)

---

## 📡 API Reference

### Upload Document
```http
POST /api/documents/upload
Authorization: Bearer <clerk_jwt_token>
Content-Type: multipart/form-data

file: <binary>
```

**Response:**
```json
{
  "message": "Document uploaded successfully. Processing in background...",
  "document_id": 123,
  "filename": "example.pdf",
  "status": "processing"
}
```

### Ask Question
```http
POST /api/documents/answer
Authorization: Bearer <clerk_jwt_token>
Content-Type: application/json

{
  "query": "What is machine learning?",
  "top_k": 5,
  "min_score": 0.3,
  "document_id": 123  // optional
}
```

**Response:**
```json
{
  "success": true,
  "answer": "Machine learning is a subset of artificial intelligence...",
  "sources": [
    {
      "filename": "ml_guide.pdf",
      "chunk_index": 3,
      "relevance_score": 0.87
    }
  ],
  "chunks_used": 3
}
```

### List Documents (Paginated)
```http
GET /api/documents/list?skip=0&limit=100
Authorization: Bearer <clerk_jwt_token>
```

### Delete Document
```http
DELETE /api/documents/{document_id}
Authorization: Bearer <clerk_jwt_token>
```

---

## 🔒 Security Features

- ✅ **JWT Authentication** - Clerk-based authentication with user isolation
- ✅ **Virus Scanning** - VirusTotal integration (fail-closed mode)
- ✅ **Rate Limiting** - 200 requests/minute per IP
- ✅ **Input Validation** - File type, size, and content sanitization
- ✅ **SQL Injection Prevention** - SQLAlchemy ORM with parameterized queries
- ✅ **CORS Protection** - Whitelist-based origin validation
- ✅ **Background Processing** - Prevents request timeout attacks
- ✅ **User Data Isolation** - Users can only access their own documents

---

## 🧪 Testing

### Run Backend Tests
```bash
cd backend
pytest tests/ -v --cov=app
```

**Test Coverage:** 18 tests, 63% coverage

### Run Frontend Tests
```bash
cd frontend
npm run test
```

### Manual Testing Checklist
- [ ] Upload PDF, DOCX, TXT files
- [ ] Ask questions about uploaded documents
- [ ] Verify source citations and scores
- [ ] Test authentication (login/logout)
- [ ] Check mobile responsiveness
- [ ] Test error handling (invalid files, network errors)
- [ ] Verify background processing status

---

## 🚀 Production Deployment

### Backend (Railway)

1. **Create Railway project:** [railway.app](https://railway.app)
2. **Add PostgreSQL plugin**
3. **Connect GitHub repository**
4. **Set environment variables** (from `.env.example`)
5. **Deploy** (automatic on push to `main`)

**Environment Variables:**
- `DATABASE_URL` (auto-set by Railway PostgreSQL)
- `PINECONE_API_KEY`
- `GEMINI_API_KEY`
- `COHERE_API_KEY`
- `VIRUSTOTAL_API_KEY`
- `CLERK_JWKS_URL`
- `VIRUS_SCAN_REQUIRED=false` (optional)

### Frontend (Vercel)

1. **Import from GitHub:** [vercel.com/new](https://vercel.com/new)
2. **Set environment variables:**
   - `VITE_API_URL=https://your-railway-backend.up.railway.app`
   - `VITE_CLERK_PUBLISHABLE_KEY=your_clerk_key`
3. **Deploy** (automatic on push to `main`)

---

## ⚙️ Configuration

### Adjust Chunk Limits
```python
# backend/app/router/documents.py
MAX_CHUNKS = 200  # Maximum chunks per document
```

### Modify Chunking Strategy
```python
# backend/app/services/chunking_service.py
chunk_size = 1000      # Characters per chunk
overlap = 100          # Character overlap
```

### Configure Virus Scanning
```env
# .env
VIRUS_SCAN_REQUIRED=false  # Set to 'true' to enforce scanning
```

---

## 📊 Performance Metrics

| Metric | Value |
|--------|-------|
| Max File Size | 10 MB |
| Chunk Size | 1000 chars |
| Max Chunks/Doc | 200 (quota protection) |
| Embedding Dimension | 768 (Gemini) / 1024 (Cohere) |
| Query Response Time | 2-4 seconds |
| Gemini Monthly Limit | 15,000 requests (free) |
| Cohere Monthly Limit | 100 requests (free) |
| Background Task Timeout | 60 seconds |

---

## 🐛 Known Limitations

- Large documents (1000+ chunks) truncated to 200 chunks
- Scanned PDFs require OCR (not implemented)
- No conversation memory across sessions
- Document list limited to 1000 documents per user
- VirusTotal free tier: 4 requests/minute

---

## 🗺️ Roadmap

- [ ] Streaming responses (SSE/WebSocket)
- [ ] Multi-document cross-referencing
- [ ] Conversation memory with Redis
- [ ] OCR for scanned PDFs (Tesseract)
- [ ] Excel/PowerPoint support
- [ ] Export conversations to PDF
- [ ] Multi-language support
- [ ] Advanced search filters

---

## 🤝 Contributing

Contributions welcome! This project follows professional development practices:

1. **Fork the repository**
2. **Create feature branch:** `git checkout -b feature/amazing-feature`
3. **Write tests** for new functionality
4. **Ensure tests pass:** `pytest tests/`
5. **Commit changes:** `git commit -m 'Add amazing feature'`
6. **Push to branch:** `git push origin feature/amazing-feature`
7. **Open Pull Request** (CodeRabbit will auto-review)

---

## 📄 License
  
MIT License - see [LICENSE](LICENSE) file for details.

---

## 👨‍💻 Developer

**Blessing Nejo**  
Junior AI Engineer | ALX Software Engineering Graduate  
📍 Lagos, Nigeria

- 🔗 GitHub: [@BLESSEDEFEM](https://github.com/BLESSEDEFEM)
- 💼 LinkedIn: [Blessing Nejo - https://www.linkedin.com/in/blessing-nejo-
195673134]
- 📧 Email: [nejoblessing72@gmail.com]

**Built with ❤️ as part of the journey**

---

## 🙏 Acknowledgments

- **ALX Software Engineering Program** - For the training and mentorship
- **CodeRabbit AI** - For automated code reviews and security audits
- **FastAPI & React Communities** - For excellent documentation
- **Cohere, Google, Pinecone** - For providing free tier APIs

---

## 📞 Support

For issues, questions, or feature requests:
- 🐛 Open an [issue](https://github.com/BLESSEDEFEM/rag-document-qa-system/issues)
- 💬 Contact via [LinkedIn - Blessing Nejo - https://www.linkedin.com/in/blessing-nejo-
195673134]
- 📧 Email: [nejoblessing72@gmail.com]

---

**⭐ If this project helped you, consider giving it a star!**