# RAG Document Q&A System

A production-grade Retrieval-Augmented Generation system for intelligent document analysis and question answering.

## 🚀 Features

- **Document Processing**: Upload PDF, DOCX, TXT files
- **Intelligent Chunking**: Semantic text splitting with overlap
- **Vector Search**: High-performance similarity search using embeddings
- **Citation Support**: Exact quotes with page numbers
- **Real-time Processing**: Async document handling with progress tracking
- **Production Ready**: Authentication, rate limiting, comprehensive logging

## 🛠️ Tech Stack

### Backend
- **Framework**: FastAPI (Python 3.11+)
- **Vector DB**: Pinecone / PostgreSQL with pgvector
- **LLM**: OpenAI GPT-4 / Anthropic Claude
- **Queue**: Celery with Redis
- **Database**: PostgreSQL

### Frontend
- **Framework**: Next.js 14 with TypeScript
- **Styling**: Tailwind CSS
- **State Management**: Zustand
- **Real-time**: WebSockets

## 📁 Project Structure

rag-document-qa-system/
├── backend/
│   ├── app/
│   ├── tests/
│   └── scripts/
├── frontend/
└── docs/

## 🔧 Setup Instructions

Coming soon...

## 👤 Author

[Blessing Nejo]
- Building production-grade AI systems
- Open to opportunities at innovative AI companies

## 📄 License

MIT

## 🌿 Git Branching Strategy

### Branch Structure

- **`main`** - Production-ready code only
  - Always stable and deployable
  - Never commit directly to main
  - Only merge from `dev` after testing

- **`dev`** - Development branch
  - Default working branch
  - Integrate features here
  - Test before merging to main

- **`feature/*`** - Feature branches (optional)
  - Create from `dev`: `git checkout -b feature/new-feature dev`
  - Work on specific features
  - Merge back to `dev` when complete

### Workflow

1. **Start new work:**
```bash
   git checkout dev
   git pull origin dev
   git checkout -b feature/your-feature-name
```

2. **During development:**
```bash
   git add .
   git commit -m "Descriptive message"
```

3. **Finish feature:**
```bash
   git checkout dev
   git merge feature/your-feature-name
   git branch -d feature/your-feature-name
```

4. **Release to production:**
```bash
   git checkout main
   git merge dev
   git push origin main
```

### Quick Commands
```bash
# See all branches
git branch

# Switch branch
git checkout <branch-name>

# Create and switch to new branch
git checkout -b <new-branch-name>

# Delete branch
git branch -d <branch-name>
```
