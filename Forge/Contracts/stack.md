# OthelloMini Technology Stack

## Overview

OthelloMini is a 2-phase proof-of-concept built with a Python/FastAPI backend, React/TypeScript frontend, and SQLite database. The system is containerized with Docker and orchestrated via single docker-compose configuration for local development. This stack prioritizes rapid iteration, simplicity, and minimal infrastructure overhead while maintaining clean separation between API, database, and UI layers.

---

## Backend Stack

### Language & Runtime
- **Python**: 3.11.9
- **Package Manager**: pip 24.0+ with `requirements.txt`
- **Virtual Environment**: Managed within Docker container

### Framework
- **FastAPI**: 0.109.0
  - ASGI web framework for high-performance async REST APIs
  - Auto-generated OpenAPI documentation (`/docs`, `/redoc`)
  - Built-in request validation via Pydantic
  - Dependency injection for service layer

### Core Libraries

**Web & API**
- `uvicorn[standard]`: 0.27.0 – ASGI server with WebSocket support and auto-reload
- `pydantic`: 2.5.3 – Data validation and settings management
- `pydantic-settings`: 2.1.0 – Environment variable configuration

**Database & ORM**
- `sqlalchemy`: 2.0.25 – SQL toolkit and ORM with async support
- `alembic`: 1.13.1 – Database migration tool
- `aiosqlite`: 0.19.0 – Async SQLite driver for SQLAlchemy

**AI & External Services**
- `openai`: 1.10.0 – Official OpenAI Python client for GPT-4 integration
- `httpx`: 0.26.0 – Async HTTP client (dependency for OpenAI SDK)

**Utilities**
- `python-dotenv`: 1.0.0 – Load environment variables from `.env`
- `python-json-logger`: 2.0.7 – Structured JSON logging
- `tenacity`: 8.2.3 – Retry logic for OpenAI API calls

**Development & Testing**
- `pytest`: 7.4.4 – Testing framework
- `pytest-asyncio`: 0.23.3 – Async test support
- `httpx`: 0.26.0 – API test client (same as production dependency)
- `faker`: 22.0.0 – Generate mock user profile data

---

## Database

### Engine
- **SQLite**: 3.42+ (bundled with Python 3.11)
- **File Location**: `/app/data/othello_mini.db` (mounted volume in Docker)
- **Driver**: `aiosqlite` for async operations via SQLAlchemy 2.0

### Schema Overview

**Tables**
1. `user_profile`
   - `id` (INTEGER PRIMARY KEY)
   - `user_id` (TEXT UNIQUE NOT NULL) – Fixed identifier (single-user MVP)
   - `traits` (JSON) – Psychological traits array
   - `preferences` (JSON) – User preferences object
   - `consent_tier` (TEXT) – Enum: 'Passive' | 'Suggestive' | 'Active' | 'Autonomous'
   - `created_at` (TIMESTAMP)
   - `updated_at` (TIMESTAMP)

2. `conversations`
   - `id` (INTEGER PRIMARY KEY)
   - `user_id` (TEXT, FOREIGN KEY)
   - `role` (TEXT) – 'user' | 'assistant' | 'system'
   - `content` (TEXT) – Message content
   - `timestamp` (TIMESTAMP)

3. `suggestions`
   - `id` (INTEGER PRIMARY KEY)
   - `user_id` (TEXT, FOREIGN KEY)
   - `suggestion_text` (TEXT) – AI-generated action description
   - `consent_tier` (TEXT) – Required tier for action
   - `ethical_reasoning` (TEXT) – Othello gatekeeper justification
   - `status` (TEXT) – 'pending' | 'approved' | 'denied'
   - `created_at` (TIMESTAMP)
   - `resolved_at` (TIMESTAMP NULL)

### Migration Management
- **Tool**: Alembic 1.13.1
- **Migration Path**: `backend/alembic/versions/`
- **Auto-run**: `db-init` service in docker-compose runs `alembic upgrade head` before API starts

---

## Frontend Stack

### Framework & Build
- **React**: 18.2.0 – Component-based UI library
- **TypeScript**: 5.3.3 – Static typing for JavaScript
- **Vite**: 5.0.11 – Fast build tool and dev server with HMR

### Core Libraries

**UI & State**
- `react-dom`: 18.2.0 – React rendering for web
- `zustand`: 4.4.7 – Lightweight state management (chat messages, user profile, suggestions)

**HTTP & API**
- `axios`: 1.6.5 – HTTP client for API calls to FastAPI backend

**Styling**
- `tailwindcss`: 3.4.1 – Utility-first CSS framework
- `postcss`: 8.4.33 – CSS processing (required by Tailwind)
- `autoprefixer`: 10.4.16 – Vendor prefix automation

**UI Components**
- `react-markdown`: 9.0.1 – Render AI responses with markdown support
- `lucide-react`: 0.312.0 – Icon library (consent badges, expand/collapse icons)

**Development**
- `@vitejs/plugin-react`: 4.2.1 – Vite plugin for React Fast Refresh
- `eslint`: 8.56.0 – Code linting
- `@typescript-eslint/parser`: 6.19.0 – TypeScript ESLint parser
- `@typescript-eslint/eslint-plugin`: 6.19.0 – TypeScript-specific lint rules

### Build Output
- **Development**: Vite dev server on port 3000 with hot module replacement
- **Production**: Static bundle served from `frontend/dist` (not used in MVP, Docker runs dev server)

---

## Deployment

### Containerization

**Docker**
- Docker Engine: 24.0+
- Docker Compose: 2.23+

**Backend Dockerfile** (`backend/Dockerfile`)
```dockerfile
FROM python:3.11.9-slim

WORKDIR /app

# Install dependencies
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy application code
COPY . .

# Expose API port
EXPOSE 8000

# Run FastAPI with uvicorn
CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000", "--reload"]
```

**Frontend Dockerfile** (`frontend/Dockerfile`)
```dockerfile
FROM node:20-alpine

WORKDIR /app

# Install dependencies
COPY package.json package-lock.json ./
RUN npm ci

# Copy source code
COPY . .

# Expose dev server port
EXPOSE 3000

# Run Vite dev server
CMD ["npm", "run", "dev", "--", "--host", "0.0.0.0"]
```

### Orchestration

**docker-compose.yml**
```yaml
version: '3.9'

services:
  db-init:
    image: python:3.11.9-slim
    volumes:
      - ./backend:/app
      - db-data:/app/data
    working_dir: /app
    environment:
      - DATABASE_URL=sqlite:///data/othello_mini.db
    command: >
      sh -c "pip install -q alembic sqlalchemy aiosqlite &&
             alembic upgrade head"

  api:
    build:
      context: ./backend
      dockerfile: Dockerfile
    ports:
      - "8000:8000"
    environment:
      - DATABASE_URL=sqlite:///data/othello_mini.db
      - OPENAI_API_KEY=${OPENAI_API_KEY}
      - LOG_LEVEL=INFO
      - CORS_ORIGINS=http://localhost:3000
    volumes:
      - ./backend:/app
      - db-data:/app/data
    depends_on:
      db-init:
        condition: service_completed_successfully
    restart: unless-stopped

  frontend:
    build:
      context: ./frontend
      dockerfile: Dockerfile
    ports:
      - "3000:3000"
    environment:
      - VITE_API_BASE_URL=http://localhost:8000
    volumes:
      - ./frontend:/app
      - /app/node_modules
    depends_on:
      - api
    restart: unless-stopped

volumes:
  db-data:
    driver: local
```

### Environment Setup

**Root `.env` file** (not committed to Git)
```env
OPENAI_API_KEY=sk-proj-...
```

**Startup Commands**
```bash
# First-time setup
docker-compose up --build

# Subsequent runs
docker-compose up

# Shutdown
docker-compose down

# Reset database
docker-compose down -v
```

---

## Environment Variables

| Variable Name       | Description                                                                 | Required | Default Value              | Used By         |
|---------------------|-----------------------------------------------------------------------------|----------|----------------------------|-----------------|
| `OPENAI_API_KEY`    | OpenAI API key for GPT-4 chat completion and suggestion generation          | Yes      | (none)                     | Backend (API)   |
| `DATABASE_URL`      | SQLite database connection string                                           | Yes      | `sqlite:///data/othello_mini.db` | Backend (API, db-init) |
| `LOG_LEVEL`         | Logging verbosity level                                                     | No       | `INFO`                     | Backend (API)   |
| `CORS_ORIGINS`      | Allowed origins for CORS requests (comma-separated)                         | No       | `http://localhost:3000`    | Backend (API)   |
| `VITE_API_BASE_URL` | Base URL for FastAPI backend (used by frontend Axios client)                | Yes      | `http://localhost:8000`    | Frontend        |
| `DEFAULT_USER_ID`   | Fixed user identifier for single-user MVP                                   | No       | `user_001`                 | Backend (API)   |
| `MAX_CONVERSATION_HISTORY` | Number of recent messages to include in AI context window            | No       | `20`                       | Backend (API)   |
| `OPENAI_MODEL`      | OpenAI model identifier for chat completions                                | No       | `gpt-4-turbo-preview`      | Backend (API)   |
| `OPENAI_TIMEOUT`    | Timeout in seconds for OpenAI API requests                                  | No       | `30`                       | Backend (API)   |

### Notes on Environment Variables

- **Secrets Management**: `OPENAI_API_KEY` must be set in `.env` file (excluded via `.gitignore`). No secrets in code or Dockerfiles.
- **Frontend Environment**: Vite requires `VITE_` prefix for environment variables exposed to browser. `VITE_API_BASE_URL` is injected at build time.
- **Database Persistence**: `DATABASE_URL` points to `/app/data/othello_mini.db` inside container, mounted to `db-data` named volume for persistence across restarts.
- **CORS Configuration**: `CORS_ORIGINS` allows frontend at `http://localhost:3000` to call API at `http://localhost:8000`. Adjust for production domains.

---

## Development Workflow

### Prerequisites
- Docker Desktop 24+ (Windows/Mac) or Docker Engine + Compose plugin (Linux)
- OpenAI API key with GPT-4 access
- 4 GB available RAM
- Git

### Local Setup
1. Clone repository: `git clone <repo-url> othello-mini && cd othello-mini`
2. Create `.env`: `echo "OPENAI_API_KEY=sk-..." > .env`
3. Start services: `docker-compose up --build`
4. Access frontend: `http://localhost:3000`
5. Access API docs: `http://localhost:8000/docs`

### Hot Reload
- **Backend**: Uvicorn auto-reloads on file changes in `backend/` (volume-mounted)
- **Frontend**: Vite HMR updates browser on file changes in `frontend/src/` (volume-mounted)

### Database Inspection
```bash
# Access SQLite shell
docker-compose exec api sqlite3 /app/data/othello_mini.db

# View tables
.tables

# Query user profile
SELECT * FROM user_profile;
```

### Testing
```bash
# Backend unit tests
docker-compose exec api pytest tests/

# Frontend (manual testing via browser for MVP)
# Automated frontend tests deferred to post-MVP
```

---

## Dependency Rationale

### Why FastAPI?
- Auto-generated OpenAPI docs reduce API documentation overhead
- Native async support for concurrent OpenAI API calls
- Pydantic validation eliminates manual request parsing errors
- Mature ecosystem with 70k+ GitHub stars

### Why SQLite?
- Zero-configuration database (no separate DB container)
- Sufficient for single-user MVP (<10k records)
- File-based persistence simplifies Docker volume management
- Easy migration to PostgreSQL if scaling to multi-user in full build

### Why Vite over Create React App?
- 10-20x faster cold start (esbuild vs Webpack)
- Native ES modules = instant HMR
- Optimized production builds with Rollup
- CRA is deprecated; Vite is React team's recommended tooling

### Why Zustand over Redux?
- 90% less boilerplate (no actions/reducers/providers)
- Hooks-first API matches React mental model
- 3 KB bundle size vs 45 KB for Redux Toolkit
- Sufficient for chat state + profile + suggestions (no complex middleware needed)

### Why Tailwind CSS?
- Utility-first enables rapid UI iteration without CSS file sprawl
- Purges unused styles in production (minimal bundle size)
- Design tokens (colors, spacing) enforce visual consistency
- JIT compiler generates only used classes (fast rebuilds)

---

**End of Stack Contract**