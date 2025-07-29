# chat-api

A REST API project scaffolded with FastAPI (Python).

## Features
- FastAPI application structure
- Sample route: `/hello`
- Ready for extension with models, schemas, and services

## Quickstart

1. Install dependencies:
   ```bash
   pip install fastapi uvicorn
   ```
2. Run the server:
   ```bash
   uvicorn app.main:app --reload
   ```
3. Visit [http://localhost:8000/hello](http://localhost:8000/hello)

## Project Structure

```
app/
  main.py         # FastAPI app entrypoint
  api/            # API route definitions
  models/         # Database models (to be added)
  schemas/        # Pydantic schemas (to be added)
  services/       # Business logic (to be added)
  core/           # Core utilities/config (to be added)
tests/            # Test suite
```
