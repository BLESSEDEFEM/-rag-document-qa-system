# 🤖 RAG Document Q&A System

A production-ready Retrieval-Augmented Generation (RAG) system that allows users to upload documents and ask questions, receiving accurate AI-generated answers with source citations.

![RAG System Demo](https://via.placeholder.com/800x400?text=Add+Screenshot+Here)

## 🌟 Features

- 📄 **Document Upload** - Support for PDF, DOCX, and TXT files (up to 10MB)
- 🔍 **Semantic Search** - Uses Cohere embeddings for intelligent document retrieval
- 💬 **AI-Powered Q&A** - Google Gemini 2.0 Flash generates contextual answers
- 📚 **Source Citations** - Every answer includes document sources and relevance scores
- 💾 **Database Storage** - PostgreSQL stores document metadata
- 🔢 **Vector Search** - Pinecone handles embeddings and similarity search
- 🚀 **Production Deployment** - Deployed on Railway (backend) and Vercel (frontend)
- 🔄 **Chat History** - Track conversation flow within session
- 📱 **Mobile Responsive** - Works seamlessly on all devices

## 🏗️ Architecture
```
┌─────────────┐
│   User      │
└──────┬──────┘
       │
       ▼
┌──────────────────────┐
│  React + TypeScript  │ (Vercel)
│  Tailwind CSS        │
└────────┬─────────────┘
         │ HTTPS
         ▼
┌──────────────────────┐
│  FastAPI Backend     │ (Railway)
└────┬─────────────┬───┘
     │             │
     ▼             ▼
┌──────────┐ ┌────────────┐
│Pinecone  │ │ PostgreSQL │
│(1024-dim)│ │  (Railway) │
└────┬─────┘ └────────────┘
     │
     ▼
┌──────────────┐
│ Cohere API   │ (Embeddings)
└──────────────┘
     │
     ▼
┌──────────────┐
│ Gemini 2.0   │ (Answer Generation)
└──────────────┘
```

## 🛠️ Tech Stack

### Frontend
- **React** 18.3 + **TypeScript** 5.5
- **Vite** for build tooling
- **Tailwind CSS** for styling
- **Vercel** for deployment

### Backend
- **FastAPI** (Python 3.11)
- **SQLAlchemy** + **PostgreSQL** (database)
- **Pinecone** (vector database, 1024 dimensions)
- **Cohere** embed-english-v3.0 (embeddings)
- **Google Gemini 2.0 Flash** (LLM)
- **Railway** for deployment

### Document Processing
- **PyPDF2** (PDF extraction)
- **python-docx** (DOCX extraction)
- **RecursiveCharacterTextSplitter** (chunking: 1000 chars, 100 overlap)

## 🚀 Live Demo

- **Frontend**: https://rag-document-qa-system.vercel.app/
- **API**: https://rag-document-qa-system-production.up.railway.app

**⚠️ Note**: This is a demo project. Documents are currently visible to all users (authentication not implemented).

## 📋 Prerequisites

- Python 3.11+
- Node.js 18+
- Cohere API key (free trial)
- Google Gemini API key (free tier)
- Pinecone account (free tier)
- Railway account (for backend deployment)
- Vercel account (for frontend deployment)

## 🔧 Local Setup

### Backend Setup

1. **Clone the repository**
```bash
git clone https://github.com/BLESSEDEFEM/rag-document-qa-system.git
cd rag-document-qa-system
```

2. **Create virtual environment**
```bash
cd backend
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
```

3. **Install dependencies**
```bash
pip install -r requirements.txt
```

4. **Environment variables**

Create `.env` file in `backend/` directory:
```env
# Database
DATABASE_URL=postgresql://user:password@localhost:5432/rag_db

# Vector Database
PINECONE_API_KEY=your_pinecone_api_key
PINECONE_INDEX_NAME=rag-documents

# AI Services
COHERE_API_KEY=your_cohere_trial_key
GEMINI_API_KEY=your_gemini_api_key

# Optional: Redis (if using caching)
REDIS_URL=redis://localhost:6379
```

5. **Setup database**
```bash
# Create PostgreSQL database
createdb rag_db

# Run migrations (manual table creation)
psql rag_db < schema.sql
```

6. **Create Pinecone index**
- Go to https://app.pinecone.io
- Create new index:
  - Name: `rag-documents`
  - Dimensions: `1024`
  - Metric: `cosine`
  - Type: `Serverless`

7. **Run backend**
```bash
uvicorn app.main:app --reload --port 8000
```

Backend will be available at: `http://localhost:8000`

API docs: `http://localhost:8000/docs`

### Frontend Setup

1. **Navigate to frontend**
```bash
cd ../frontend
```

2. **Install dependencies**
```bash
npm install
```

3. **Environment variables**

Create `.env` file in `frontend/` directory:
```env
VITE_API_URL=http://localhost:8000/api/documents
```

4. **Run frontend**
```bash
npm run dev
```

Frontend will be available at: `http://localhost:5173`

## 📡 API Endpoints

### Upload Document
```http
POST /api/documents/upload
Content-Type: multipart/form-data

file: <PDF/DOCX/TXT file>
```

**Response:**
```json
{
  "message": "Document uploaded and processed successfully",
  "document_id": 1,
  "filename": "example.pdf",
  "chunk_count": 45,
  "truncated": false,
  "status": "ready"
}
```

### Ask Question
```http
POST /api/documents/answer
Content-Type: application/json

{
  "query": "What is machine learning?",
  "top_k": 5,
  "min_score": 0.3
}
```

**Response:**
```json
{
  "success": true,
  "answer": "Machine learning is...",
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

### List Documents
```http
GET /api/documents/list
```

### Delete Document
```http
DELETE /api/documents/{document_id}
```

## 🔒 Security Features

- File type validation (whitelist: PDF, DOCX, TXT)
- File size limits (10 MB max)
- UUID-based filename sanitization
- CORS configuration for production domains
- SQL injection prevention (SQLAlchemy ORM)
- Input validation with Pydantic models

## ⚙️ Configuration

### Chunk Size Limit
Documents are limited to **200 chunks** (max ~100KB text) to protect API quotas. Larger documents are automatically truncated.

To adjust:
```python
# backend/app/router/documents.py
MAX_CHUNKS = 200  # Modify this value
```

### Chunking Strategy
```python
# backend/app/services/chunking_service.py
chunk_size = 1000      # Characters per chunk
overlap = 100          # Character overlap between chunks
```

### Embedding Batch Size
```python
# backend/app/services/embedding_service.py
batch_size = 96        # Cohere trial limit
```

## 🧪 Testing

### Backend Tests
```bash
cd backend
pytest tests/
```

### Frontend Tests
```bash
cd frontend
npm run test
```

### Manual Testing Checklist
- [ ] Upload PDF/DOCX/TXT files
- [ ] Ask questions about uploaded documents
- [ ] Verify source citations
- [ ] Test large file truncation warning
- [ ] Check mobile responsiveness
- [ ] Test error handling (invalid file types, network errors)

## 🚀 Deployment

### Backend (Railway)

1. **Create new project** on Railway
2. **Add PostgreSQL** plugin
3. **Set environment variables** (Cohere, Gemini, Pinecone keys)
4. **Connect GitHub repo** - Railway auto-deploys on push
5. **Database setup**: Connect to Railway Postgres via psql and create tables

### Frontend (Vercel)

1. **Import project** from GitHub
2. **Set environment variable**:
   - `VITE_API_URL=https://your-railway-backend.up.railway.app/api/documents`
3. **Deploy** - Vercel auto-deploys on push

## 📊 Performance

| Metric | Value |
|--------|-------|
| Max File Size | 10 MB |
| Chunk Size | 1000 chars |
| Max Chunks/Doc | 200 (quota protection) |
| Embedding Dimension | 1024 |
| Query Response Time | 2-4 seconds |
| Cohere Monthly Limit | 10,000 requests |
| Gemini Daily Limit | 1,500 requests |

## 🐛 Known Issues

- No user authentication (all documents are public)
- Scanned PDFs return 0 characters (needs OCR)
- Large documents (1000+ chunks) take ~60s to process
- No conversation persistence across sessions
- Chat history clears on page refresh

## 🗺️ Roadmap

- [ ] Add user authentication (Clerk.com)
- [ ] Implement conversation memory
- [ ] Add streaming responses
- [ ] Support Excel/PowerPoint files
- [ ] OCR for scanned PDFs
- [ ] Export conversation to PDF
- [ ] Semantic caching for common queries
- [ ] Advanced search within documents

## 📄 License

MIT License - see [LICENSE](LICENSE) file for details

## 👤 Author

**Blessing Efem**
- GitHub: [@BLESSEDEFEM](https://github.com/BLESSEDEFEM)
- LinkedIn: [Your LinkedIn]
- Location: Lagos, Nigeria

## 🙏 Acknowledgments

- [Cohere](https://cohere.com) for embeddings API
- [Google](https://ai.google.dev) for Gemini API
- [Pinecone](https://www.pinecone.io) for vector database
- ALX Software Engineering Program, 

## 📞 Support

For issues or questions:
- Open an [issue](https://github.com/BLESSEDEFEM/rag-document-qa-system/issues)
- Contact via [LinkedIn]

---

**Built with ❤️ in Lagos, Nigeria**


## 🏗️ Architecture & Tech Stack

### Backend (FastAPI + Python)
- **Framework:** FastAPI 0.104+
- **Database:** PostgreSQL (Railway)
- **Vector DB:** Pinecone (document embeddings)
- **AI Models:** Cohere Embed v3, Google Gemini
- **Authentication:** Clerk JWT
- **Deployment:** Railway (auto-deploy from main)

### Frontend (React + TypeScript)
- **Framework:** React 18 + TypeScript
- **Build Tool:** Vite
- **UI Library:** Tailwind CSS + shadcn/ui
- **State Management:** React Query
- **Authentication:** Clerk React
- **Deployment:** Vercel (auto-deploy from main)

### CI/CD Pipeline
- **Testing:** Pytest (18 tests, 63% coverage)
- **Type Checking:** mypy (backend), TypeScript (frontend)
- **Code Quality:** CodeRabbit AI reviews
- **Deployment:** Automatic on merge to main

---

## 🔒 Security Features

- ✅ JWT-based authentication (Clerk)
- ✅ User-scoped data isolation
- ✅ File upload validation (type, size)
- ✅ SQL injection prevention (SQLAlchemy ORM)
- ✅ CORS configuration
- ✅ Environment variable management
- ✅ Rate limiting on AI API calls

---

## 📊 Code Quality Standards

This project maintains high code quality through:

- **Automated Testing:** 18 comprehensive tests covering upload, query, and document management
- **Type Safety:** Python type hints + TypeScript strict mode
- **Code Coverage:** 63% backend coverage, continuously improving
- **AI Code Review:** CodeRabbit analyzes every PR for security, performance, and best practices
- **CI/CD Checks:** All tests must pass before deployment
- **Error Handling:** Comprehensive error handling with user-friendly messages

---

## 🚀 Production Deployment

### Backend (Railway)
- **URL:** [Your Railway URL]
- **Auto-deploy:** Triggered on push to main
- **Health Check:** `/health` endpoint
- **Environment:** Production-ready with proper logging

### Frontend (Vercel)
- **URL:** [Your Vercel URL]
- **Auto-deploy:** Triggered on push to main
- **Performance:** Optimized build with code splitting
- **CDN:** Global edge network

---

## 📈 Future Enhancements

- [ ] Multi-document cross-referencing
- [ ] Citation tracking for answers
- [ ] Document version history
- [ ] Advanced search filters
- [ ] Collaborative document annotations
- [ ] Export Q&A history
- [ ] Multi-language support
- [ ] Voice-to-text queries

---

## 🤝 Contributing

This project follows professional development practices:

1. **Fork the repository**
2. **Create feature branch** (`git checkout -b feature/amazing-feature`)
3. **Write tests** for new functionality
4. **Ensure all tests pass** (`pytest tests/`)
5. **Commit changes** (`git commit -m 'Add amazing feature'`)
6. **Push to branch** (`git push origin feature/amazing-feature`)
7. **Open Pull Request** (CodeRabbit will review automatically)

---

## 📄 License

This project is part of the ALX Software Engineering program portfolio.

---

## 👨‍💻 Developer

**Blessing Nejo**
- Portfolio: [Your portfolio URL]
- GitHub: [@BLESSEDEFEM](https://github.com/BLESSEDEFEM)
- LinkedIn: [Your LinkedIn]

Built with ❤️ as part of the journey to FAANG

---

## 🙏 Acknowledgments

- ALX Software Engineering Program
- FastAPI and React communities
- CodeRabbit for automated code reviews