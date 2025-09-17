# GraphRAG Minimal Service

A minimal end-to-end GraphRAG scaffold: upload documents, ingest into vector and graph stores, and answer queries using dual retrieval (semantic + graph) with FastAPI.

## Features
- User-scoped documents and knowledge graph
- Ingestion: parse files, chunk, embed, extract entities/relations
- Storage: Chroma (local) for vectors, Neo4j for graph
- Query: dual retrieval and grounded LLM answer

## Setup
1. Copy `.env.example` to `.env` and adjust values.
2. Create a virtual environment and install deps:
```bash
python -m venv .venv
. .venv/Scripts/Activate.ps1  # PowerShell
pip install -r requirements.txt
```
3. Ensure Neo4j is running and credentials match `.env`.

## Run
```bash
uvicorn app.main:app --reload --port %PORT%
```
If `%PORT%` is unset, defaults to 8001.

## API
- `POST /auth/login` body `{ "username": "alice" }` → `{ user_id }`
- `POST /documents/upload` form-data: `user_id`, `files` (pdf/docx/txt)
- `POST /query` body `{ user_id, question, k }` → answer + references + evidence

## Notes
- Entity extraction is a simple placeholder; swap with your NLP/LLM.
- Chroma persists under `.chroma`; delete to reset.
- Uploads are temporarily stored under `storage/uploads` during ingestion.
