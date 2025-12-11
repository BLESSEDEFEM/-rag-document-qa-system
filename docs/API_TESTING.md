# API Testing with Postman

## Setup

1. Install Postman from https://www.postman.com/downloads/
2. Import collection: `docs/postman_collection.json`
3. Set environment variables

## Environment Variables

| Variable | Value | Description |
|----------|-------|-------------|
| `base_url` | `http://localhost:8000/api/documents` | API base URL |

## Available Endpoints

### Health Check
- **Method:** GET
- **URL:** `http://localhost:8000/health`
- **Purpose:** Verify server is running

### List Documents
- **Method:** GET
- **URL:** `{{base_url}}/list`
- **Purpose:** Get all uploaded documents

### Upload Document
- **Method:** POST
- **URL:** `{{base_url}}/upload`
- **Body:** form-data with `file` key
- **Purpose:** Upload new document

### Query Documents
- **Method:** POST
- **URL:** `{{base_url}}/query`
- **Body:** 
```json
  {
    "query": "Your question here",
    "top_k": 5,
    "min_score": 0.3
  }
```
- **Purpose:** Search documents without AI answer

### Answer Question
- **Method:** POST
- **URL:** `{{base_url}}/answer`
- **Body:**
```json
  {
    "query": "Your question here",
    "top_k": 5,
    "min_score": 0.3
  }
```
- **Purpose:** Get AI-generated answer with citations

### Delete Document
- **Method:** DELETE
- **URL:** `{{base_url}}/{document_id}`
- **Purpose:** Delete specific document

## Testing Workflow

1. Start backend server: `uvicorn app.main:app --reload`
2. Open Postman
3. Run Health Check (verify server running)
4. Upload a test document
5. Run List Documents (verify upload)
6. Query or Answer questions
7. Delete document if needed

## Troubleshooting

- **Connection refused:** Backend server not running
- **404 errors:** Check URL and base_url variable
- **500 errors:** Check backend logs for details