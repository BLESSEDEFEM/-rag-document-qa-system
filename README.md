RAG Document Q&A System

A production-grade Retrieval-Augmented Generation system that lets users upload documents (PDF, DOCX, TXT) and query them using natural language. Returns AI-generated answers with source citations and relevance scores.

Built with FastAPI, React, Pinecone, PostgreSQL, and Google Gemini.

Blog post: I Built a Production RAG System in 3 Weeks — Here's What Actually Broke


Architecture
```
┌─────────────┐
│   Browser   │
└──────┬──────┘
       │ HTTPS
       ▼
┌──────────────────────┐
│  React + TypeScript  │  (Vercel)
│  Clerk Auth          │
└────────┬─────────────┘
         │ REST API + JWT
         ▼
┌──────────────────────┐
│  FastAPI Backend     │  (Railway)
│  + Background Tasks  │
└────┬──────┬──────┬───┘
     │      │      │
     ▼      ▼      ▼
┌─────────┐┌──────────┐┌──────────┐
│Pinecone ││PostgreSQL││VirusTotal│
│(Vectors)││(Metadata)││  (Scan)  │
└────┬────┘└──────────┘└──────────┘
     │
     ▼
┌──────────────────────┐
│ Gemini (primary)     │
│ Cohere (fallback)    │
└──────────────────────┘
```
How a query flows:


User uploads a document → backend extracts text → splits into 1000-char chunks with 100-char overlap
Each chunk is embedded using Gemini's text-embedding-004 model (768 dimensions), with automatic Cohere fallback if Gemini's rate limit is hit
Embeddings are stored in Pinecone with metadata (filename, chunk index, user ID)
User asks a question → question is embedded → Pinecone returns top-k most similar chunks via cosine similarity
Retrieved chunks + question are sent to Gemini 2.0 Flash → generates an answer with source citations



Tech Stack

LayerTechnologyWhyFrontendReact 18 + TypeScript, Vite, Tailwind + shadcn/uiType safety, fast builds, consistent UI componentsBackendFastAPI (Python 3.11)Async support, automatic OpenAPI docs, Pydantic validationDatabasePostgreSQL + SQLAlchemyRelational integrity for document metadata, user isolationVector DBPineconeManaged vector search — no infrastructure to maintain, cosine similarity at scaleEmbeddingsGemini text-embedding-004 (primary), Cohere embed-v3 (fallback)Dual-provider resilience against rate limitsLLMGemini 2.0 FlashFast inference, strong instruction-following, generous free tierAuthClerkJWT-based, handles signup/login/session out of the boxSecurityVirusTotalScans every uploaded file before processingDeploymentRailway (backend) + Vercel (frontend)Zero-config deploys, GitHub push-to-deploy


Performance

MetricValueDocument list response~50ms (cache hit: ~2ms)Upload + processing2–5 seconds (extraction → chunking → embedding → Pinecone upsert)Query → Answer3–5 seconds (embedding ~500ms + Pinecone ~100ms + LLM generation ~2–3s)Max file size10 MBMax chunks per document200 (quota protection)Embedding dimensions768 (Gemini) / 1024 (Cohere)Document capacityHundreds comfortably; thousands with paid Gemini tier


Key Technical Decisions

Why dual embedding providers?
Gemini's free tier caps at 15,000 requests/month. At 5 chunks per document, that's ~3,000 uploads/month. Rather than hitting a wall, the system automatically falls back to Cohere (100 additional requests/month) when Gemini is rate-limited. This required maintaining two separate Pinecone namespaces with different dimensions (768 vs 1024).

Why chunking with overlap?
Fixed-size chunks (1000 chars, 100 overlap) balance retrieval precision against context completeness. The overlap prevents relevant information from being split across chunk boundaries. I tested without overlap and saw a measurable drop in answer relevance for questions spanning paragraph breaks.

Why background processing?
Large documents can take 10+ seconds to chunk and embed. Synchronous processing would block the API and risk timeouts. Background tasks let the API return immediately with a processing status while the document pipeline runs asynchronously.

Why VirusTotal scanning?
Any system accepting file uploads needs a security layer. VirusTotal catches malicious files before they enter the processing pipeline. The system runs in fail-closed mode — if the scan fails, the upload is rejected.


Security


Authentication: Clerk JWT verification with user isolation — users can only access their own documents
File scanning: VirusTotal integration, fail-closed mode
Rate limiting: 200 requests/minute per IP
Input validation: File type, size, and content sanitization
SQL injection prevention: SQLAlchemy ORM with parameterized queries
CORS: Whitelist-based origin validation



API Reference

Upload Document

POST /api/documents/upload
Authorization: Bearer <clerk_jwt_token>
Content-Type: multipart/form-data

file: <binary>

Ask Question

POST /api/documents/answer
Authorization: Bearer <clerk_jwt_token>
Content-Type: application/json

{
  "query": "What is machine learning?",
  "top_k": 5,
  "min_score": 0.3,
  "document_id": 123  // optional — omit to search all documents
}

List Documents

GET /api/documents/list?skip=0&limit=100
Authorization: Bearer <clerk_jwt_token>

Delete Document

DELETE /api/documents/{document_id}
Authorization: Bearer <clerk_jwt_token>

Full interactive API docs available at /api/docs when running locally.


Local Development

Prerequisites


Python 3.11+
Node.js 18+
PostgreSQL 14+
API keys: Gemini, Pinecone, Cohere, VirusTotal, Clerk


Backend

bashcd backend
python -m venv venv
source venv/bin/activate  # Windows: venv\Scripts\activate
pip install -r requirements.txt
cp .env.example .env      # Add your API keys
uvicorn app.main:app --reload --port 8000

Frontend

bashcd frontend
npm install
echo "VITE_API_URL=http://localhost:8000" > .env
echo "VITE_CLERK_PUBLISHABLE_KEY=your_clerk_key" >> .env
npm run dev

Pinecone Setup


Create a Pinecone account → create index named rag-documents
Dimensions: 768 (Gemini) or 1024 (Cohere), metric: cosine
Add PINECONE_API_KEY to your .env



Tests

bashcd backend
pytest tests/ -v --cov=app

18 tests covering authentication, document upload/list/delete, question answering, background processing, and error handling. 63% code coverage.


Known Limitations


Documents exceeding 200 chunks are truncated (quota protection)
Scanned PDFs without embedded text are not supported (no OCR)
No conversation memory across sessions — each query is independent
VirusTotal free tier: 4 scans/minute



Project Structure

```
rag-document-qa-system/
├── backend/
│   ├── app/
│   │   ├── router/         # API endpoints
│   │   ├── services/       # Chunking, embedding, Q&A logic
│   │   ├── models/         # SQLAlchemy models
│   │   ├── middleware/      # Rate limiting, CORS
│   │   └── main.py         # FastAPI entry point
│   ├── tests/              # pytest suite
│   └── requirements.txt
├── frontend/
│   ├── src/
│   │   ├── components/     # React components
│   │   ├── pages/          # Route pages
│   │   └── services/       # API client
│   └── package.json
└── README.md
```


License

MIT
