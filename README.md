tests/            # Test suite

# AI Chatbot API

This project is a REST API for an AI-powered chatbot service, built with FastAPI (Python). It provides secure user registration, authentication (JWT), and a chat endpoint for interacting with an AI bot. The API is designed for extensibility, maintainability, and follows industry best practices.

## Purpose

Enable users to:
- Register and create an account
- Log in and obtain a JWT token
- Send chat messages to an AI bot (authentication required)

See [`user-stories.md`](user-stories.md) for detailed requirements and acceptance criteria.

## Features

- User registration: `POST /users/register`
- User login (JWT): `POST /users/login`
- Authenticated chat: `POST /chat`
- Modular, production-ready FastAPI structure
- Pydantic for data validation
- JWT authentication (using `python-jose`)
- Password hashing (using `passlib[bcrypt]`)

## Project Structure

```
app/
  main.py         # FastAPI app entrypoint
  api/            # API route definitions (users, chat)
  models/         # Data models (in-memory user model)
  schemas/        # Pydantic schemas (request/response validation)
  services/       # Business logic (user, chat)
  core/           # Core utilities (auth, security)
tests/            # Test suite (to be added)
requirements.txt  # Python dependencies
Dockerfile        # Production-ready multistage Dockerfile
user-stories.md   # User stories and acceptance criteria
```

## Quickstart (Local Development)

1. Install dependencies:
   ```bash
   pip install -r requirements.txt
   ```
2. Run the server:
   ```bash
   uvicorn app.main:app --reload
   ```
3. Visit the interactive docs: [http://localhost:8000/docs](http://localhost:8000/docs)

## Running with Docker

Build and run the app in a container:

```bash
docker build -t ai-chatbot-api .
docker run -p 8000:8000 ai-chatbot-api
```

## API Overview

- **POST /users/register** — Register a new user (name, email, password)
- **POST /users/login** — Log in and receive a JWT token
- **POST /chat** — Send a chat message (requires JWT in Authorization header)

See the OpenAPI docs at `/docs` for full details and try out the endpoints interactively.

## Security Notes

- Passwords are hashed using bcrypt before storage (in-memory demo only)
- JWT tokens are used for authentication; keep your `SECRET_KEY` safe in production
- The provided Dockerfile runs the app as a non-root user for security

## Extending the App

- Replace the in-memory user store with a real database for production
- Add more endpoints, business logic, or AI integrations as needed
- Write tests in the `tests/` folder

## Requirements

- Python 3.8+
- FastAPI
- Uvicorn
- passlib[bcrypt]
- python-jose
- pydantic

## License

MIT
