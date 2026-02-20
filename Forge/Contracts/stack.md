# OthelloMini Technology Stack Contract

## 1. Overview

OthelloMini is a multi-agent, ethics-first AI life intelligence platform requiring sophisticated multi-agent orchestration, real-time chat, persistent psychological modeling, and consent-tiered ethical filtering. This stack prioritizes:

- **Python-native AI/ML workflow** for multi-agent coordination and LLM integration
- **Real-time conversational interface** with inline consent controls
- **Persistent user modeling** with structured psychological profile storage
- **Transparent ethical logging** and agent reasoning traces
- **Single-compose deployment** for rapid 2-phase proof-of-concept iteration

## 2. Backend Stack

### Language & Runtime
- **Python 3.11+**
  - Native support for modern async/await patterns
  - Type hints for agent interface contracts
  - Rich ecosystem for AI/ML libraries

### Core Framework
- **FastAPI 0.109+**
  - High-performance async API framework
  - Automatic OpenAPI documentation
  - WebSocket support for real-time chat
  - Built-in validation via Pydantic v2
  - Native async request handling for multi-agent coordination

### Key Backend Libraries

#### AI & LLM Integration
- **openai 1.10+** - GPT-4/GPT-3.5-turbo integration for agent reasoning
- **langchain 0.1+** - Multi-agent orchestration, prompt templates, memory management
- **tiktoken 0.5+** - Token counting and context window management

#### Agent Framework & Orchestration
- **pydantic 2.5+** - Agent message schemas, validation, settings management
- **pydantic-settings 2.1+** - Environment-based configuration
- **celery 5.3+** - Asynchronous task queue for proactive agent background jobs (RealityAgent scheduling nudges)
- **redis 5.0+** (Python client) - Celery broker, session state, agent working memory cache

#### API & WebSocket
- **uvicorn 0.27+** - ASGI server with WebSocket support
- **websockets 12.0+** - WebSocket protocol handling for real-time chat
- **python-multipart 0.0.6+** - File upload handling (future voice/image input)

#### Authentication & Security
- **python-jose[cryptography] 3.3+** - JWT token generation and validation
- **passlib[bcrypt] 1.7+** - Password hashing
- **python-dotenv 1.0+** - Environment variable management

#### Data & Serialization
- **sqlalchemy 2.0+** - Async ORM for PostgreSQL
- **alembic 1.13+** - Database migrations
- **psycopg2-binary 2.9+** - PostgreSQL adapter
- **orjson 3.9+** - High-performance JSON serialization for agent message logs

#### Observability & Logging
- **structlog 24.1+** - Structured logging for agent reasoning traces
- **prometheus-fastapi-instrumentator 6.1+** - Metrics for agent performance monitoring

## 3. Database Stack

### Primary Database
- **PostgreSQL 16**
  - Robust JSONB support for flexible psychological profile schemas
  - Advanced indexing (GIN, B-tree) for agent query patterns
  - ACID guarantees for consent tier changes and ethical filter logs
  - Native array and full-text search for conversation history

### Schema Design Patterns
- **Users table** - Authentication, consent tier settings, autonomy preferences
- **Conversations table** - Chat sessions with timestamp and context metadata
- **Messages table** - Individual messages with agent attribution and ethical filter results
- **DigitalShadow table** - JSONB psychological profile (traits, behavior patterns, aspirations, mood logs)
- **ConsentLog table** - Audit trail for all user consent decisions and tier changes
- **EthicalFilterLog table** - Othello gatekeeper decisions with reasoning traces
- **AgentActions table** - Proactive interventions proposed by RealityAgent (status: pending/approved/denied/executed)

### Cache & Session Store
- **Redis 7.2+**
  - Session state (active conversation context, agent working memory)
  - Celery task broker for asynchronous proactive agent jobs
  - Rate limiting for API endpoints
  - Ephemeral agent scratch space (short-term reasoning chains)

## 4. Frontend Stack

### Framework
- **React 18.2+**
  - Component-based architecture for chat UI and consent cards
  - Hooks for WebSocket connection management
  - Concurrent rendering for smooth inline consent interactions

### Build Tooling
- **Vite 5.0+**
  - Fast HMR for rapid UI iteration
  - Optimized production builds
  - Native ESM support

### State Management & Data Fetching
- **TanStack Query (React Query) 5.17+** - Server state management, caching, optimistic updates
- **Zustand 4.4+** - Lightweight client state (UI toggles, transparency panel visibility, agent filter settings)

### Real-Time Communication
- **Socket.IO Client 4.6+** - WebSocket connection to FastAPI backend for chat streaming
- **@microsoft/fetch-event-source 2.0+** - SSE fallback for agent response streaming

### UI Components & Styling
- **Tailwind CSS 3.4+** - Utility-first styling for dark navy/charcoal theme with muted teal/amber accents
- **Headless UI 1.7+** - Accessible unstyled components (modals, dropdowns, consent dialogs)
- **Radix UI Primitives 1.0+** - Collapsible panels for agent reasoning traces, ethical logs
- **Lucide React 0.309+** - Icon system (consent checkmarks, agent avatars, ethical warning indicators)

### Chat Interface
- **react-markdown 9.0+** - Render formatted agent responses
- **react-syntax-highlighter 15.5+** - Code block rendering in chat (if agent suggests technical solutions)
- **date-fns 3.2+** - Timestamp formatting for conversation history

### Form Handling & Validation
- **React Hook Form 7.49+** - Performant forms for settings, consent tier adjustments
- **Zod 3.22+** - Frontend validation schema matching Pydantic backend contracts

### Routing
- **React Router 6.21+** - Client-side routing (chat, settings, transparency logs, digital shadow summary)

## 5. Deployment Stack

### Containerization
- **Docker 24+**
  - Multi-stage builds for optimized image sizes
  - Separate containers: `backend`, `frontend-nginx`, `postgres`, `redis`, `celery-worker`

### Orchestration
- **Docker Compose v2.24+**
  - Single-compose deployment for 2-phase proof-of-concept
  - Named volumes for persistent data (PostgreSQL, Redis)
  - Health checks for service dependencies
  - Unified network for inter-service communication

### Web Server
- **Nginx 1.25+** (frontend container)
  - Serve static React build
  - Reverse proxy to FastAPI backend
  - WebSocket upgrade handling
  - Gzip compression for assets

### Process Management
- **Uvicorn workers** (managed by Docker entrypoint)
  - Multi-worker FastAPI deployment for concurrency
  - Graceful reload support

### Background Workers
- **Celery worker container**
  - Separate container for asynchronous agent tasks
  - Proactive RealityAgent interventions (scheduled nudges, goal check-ins)
  - Periodic digital shadow refinement jobs

## 6. Environment Variables

| Variable Name | Description | Required | Default | Example |
|--------------|-------------|----------|---------|---------|
| **Backend - Core** |
| `ENVIRONMENT` | Deployment environment | Yes | - | `development`, `production` |
| `SECRET_KEY` | JWT signing key and app secret | Yes | - | `your-256-bit-secret-key-here` |
| `API_HOST` | Backend API host | No | `0.0.0.0` | `0.0.0.0` |
| `API_PORT` | Backend API port | No | `8000` | `8000` |
| `CORS_ORIGINS` | Allowed CORS origins (comma-separated) | Yes | - | `http://localhost:3000,http://localhost:8080` |
| **Database** |
| `DATABASE_URL` | PostgreSQL connection string | Yes | - | `postgresql+asyncpg://user:pass@postgres:5432/othellomini` |
| `POSTGRES_USER` | PostgreSQL username | Yes | - | `othello` |
| `POSTGRES_PASSWORD` | PostgreSQL password | Yes | - | `secure_password_here` |
| `POSTGRES_DB` | PostgreSQL database name | Yes | - | `othellomini` |
| `DB_POOL_SIZE` | Connection pool size | No | `10` | `10` |
| `DB_MAX_OVERFLOW` | Max overflow connections | No | `20` | `20` |
| **Redis** |
| `REDIS_URL` | Redis connection string | Yes | - | `redis://redis:6379/0` |
| `REDIS_PASSWORD` | Redis password (if enabled) | No | - | `redis_secure_pass` |
| **Celery** |
| `CELERY_BROKER_URL` | Celery broker URL | Yes | - | `redis://redis:6379/1` |
| `CELERY_RESULT_BACKEND` | Celery result backend URL | Yes | - | `redis://redis:6379/2` |
| **AI/LLM Integration** |
| `OPENAI_API_KEY` | OpenAI API key for GPT models | Yes | - | `sk-proj-...` |
| `OPENAI_MODEL_DEFAULT` | Default GPT model for agents | No | `gpt-4-turbo-preview` | `gpt-4-turbo-preview`, `gpt-3.5-turbo` |
| `OPENAI_MODEL_ETHICS` | Model for Othello ethical filtering | No | `gpt-4-turbo-preview` | `gpt-4-turbo-preview` |
| `OPENAI_MAX_TOKENS` | Max tokens per agent response | No | `1500` | `1500` |
| `OPENAI_TEMPERATURE` | Temperature for agent responses | No | `0.7` | `0.7` |
| **Agent Configuration** |
| `AGENT_REASONING_LOG_ENABLED` | Enable detailed agent reasoning logs | No | `true` | `true`, `false` |
| `AGENT_TRANSPARENCY_MODE` | Expose reasoning traces to frontend | No | `true` | `true`, `false` |
| `ETHICAL_FILTER_STRICT_MODE` | Strict ethical filtering (reject ambiguous) | No | `false` | `true`, `false` |
| `DEFAULT_CONSENT_TIER` | Default consent tier for new users | No | `Passive` | `Passive`, `Suggestive`, `Active`, `Autonomous` |
| **Session & Auth** |
| `JWT_SECRET_KEY` | JWT token signing key | Yes | - | `jwt-secret-256-bit-key` |
| `JWT_ALGORITHM` | JWT signing algorithm | No | `HS256` | `HS256` |
| `JWT_EXPIRATION_HOURS` | JWT token expiration in hours | No | `168` | `168` (7 days) |
| `SESSION_TIMEOUT_MINUTES` | Inactive session timeout | No | `60` | `60` |
| **Frontend** |
| `VITE_API_BASE_URL` | Backend API base URL | Yes | - | `http://localhost:8000` |
| `VITE_WS_URL` | WebSocket URL for real-time chat | Yes | - | `ws://localhost:8000/ws` |
| `VITE_APP_NAME` | Application display name | No | `OthelloMini` | `OthelloMini` |
| `VITE_ENABLE_TRANSPARENCY_PANEL` | Show agent reasoning panel | No | `true` | `true`, `false` |
| **Logging & Monitoring** |
| `LOG_LEVEL` | Application log level | No | `INFO` | `DEBUG`, `INFO`, `WARNING`, `ERROR` |
| `LOG_FORMAT` | Log output format | No | `json` | `json`, `console` |
| `ENABLE_METRICS` | Enable Prometheus metrics endpoint | No | `true` | `true`, `false` |
| **Rate Limiting** |
| `RATE_LIMIT_ENABLED` | Enable API rate limiting | No | `true` | `true`, `false` |
| `RATE_LIMIT_PER_MINUTE` | Max requests per minute per user | No | `60` | `60` |

## 7. Development Tools

### Code Quality
- **black 24.1+** - Python code formatting
- **ruff 0.1+** - Fast Python linter (replaces flake8, isort)
- **mypy 1.8+** - Static type checking
- **pytest 8.0+** - Backend testing framework
- **pytest-asyncio 0.23+** - Async test support
- **httpx 0.26+** - Async HTTP client for API tests

### Frontend Development
- **ESLint 8.56+** - JavaScript/TypeScript linting
- **Prettier 3.2+** - Code formatting
- **TypeScript 5.3+** - Static typing for React components
- **Vitest 1.2+** - Unit testing for React components
- **@testing-library/react 14.1+** - Component testing utilities

### Development Workflow
- **pre-commit 3.6+** - Git hooks for code quality checks
- **Docker Compose (dev override)** - Hot-reload volumes for local development

## 8. Deployment Architecture

```
┌─────────────────────────────────────────────────────────┐
│  Docker Compose Single-Host Deployment                  │
├─────────────────────────────────────────────────────────┤
│                                                           │
│  ┌─────────────┐      ┌──────────────────────────┐      │
│  │   Nginx     │◄─────┤   Frontend (React)       │      │
│  │   :80       │      │   Static Build           │      │
│  └──────┬──────┘      └──────────────────────────┘      │
│         │                                                │
│         │ /api/*  (reverse proxy)                       │
│         │ /ws     (WebSocket upgrade)                   │
│         ▼                                                │
│  ┌──────────────────────────────────────────────┐       │
│  │   FastAPI Backend (Uvicorn)                  │       │
│  │   :8000                                      │       │
│  │   - REST API                                 │       │
│  │   - WebSocket chat endpoint                  │       │
│  │   - Multi-agent orchestration                │       │
│  └───────┬─────────────────────┬────────────────┘       │
│          │                     │                        │
│          ▼                     ▼                        │
│  ┌──────────────┐      ┌─────────────────────┐         │
│  │ PostgreSQL   │      │  Redis :6379        │         │
│  │ :5432        │      │  - Session store    │         │
│  │ - User data  │      │  - Celery broker    │         │
│  │ - Profiles   │      │  - Agent cache      │         │
│  │ - Logs       │      └─────────┬───────────┘         │
│  └──────────────┘                │                      │
│                                   │                      │
│                            ┌──────▼──────────────┐      │
│                            │  Celery Worker      │      │
│                            │  - Background tasks │      │
│                            │  - RealityAgent     │      │
│                            └─────────────────────┘      │
│                                                           │
└─────────────────────────────────────────────────────────┘
```

### Container Services

1. **frontend-nginx** (Nginx + React build)
   - Serves static assets
   - Reverse proxies `/api/*` to backend
   - WebSocket upgrade for `/ws`

2. **backend** (FastAPI + Uvicorn)
   - Multi-worker async API
   - WebSocket endpoint for real-time chat
   - Multi-agent coordination (FELLO, Othello, RealityAgent)
   - Ethical filtering and consent validation

3. **postgres** (PostgreSQL 16)
   - Persistent user data, conversations, digital shadows
   - Ethical filter logs, consent audit trail

4. **redis** (Redis 7.2)
   - Session state and agent working memory
   - Celery broker and result backend
   - Rate limiting store

5. **celery-worker** (Celery + Python backend code)
   - Asynchronous proactive agent tasks
   - Scheduled nudges and goal check-ins
   - Periodic digital shadow refinement

### Volume Strategy
- **postgres-data** - PostgreSQL data directory (persistent)
- **redis-data** - Redis dump.rdb (persistent, optional for POC)
- **backend-logs** - Structured agent reasoning logs (bind mount for dev, named volume for prod)

### Network
- Single Docker bridge network `othellomini-network` for inter-service communication
- Services reference each other by service name (e.g., `postgres`, `redis`)

## 9. Proof-of-Concept Constraints

This stack is optimized for a **2-phase proof-of-concept**:

- **Single-host deployment** via Docker Compose (no Kubernetes, no distributed orchestration)
- **Vertical scaling only** (increase container resources, not replica count)
- **Simple secrets management** (environment variables, no Vault or external secret stores)
- **File-based logging** (no ELK stack or centralized log aggregation)
- **Basic monitoring** (Prometheus metrics endpoint exposed, no Grafana deployment in compose)
- **No CDN or edge caching** (Nginx serves static assets directly)
- **Local HTTPS termination** (optional self-signed cert for development, not production-grade TLS)

### Phase 1 (Core Functionality)
Focus: Conversational interface + ethical filtering + basic digital shadow
- Backend API with OpenAI integration
- WebSocket chat
- Othello ethical filter (consent tier: Passive only)
- Basic React chat UI
- PostgreSQL user/conversation/message tables

### Phase 2 (Multi-Agent Intelligence)
Focus: Multi-agent coordination + proactive interventions + transparency
- FELLO multi-agent orchestration with sub-agents
- RealityAgent proactive suggestions
- Celery background worker for scheduled actions
- Digital shadow JSONB schema with psychological modeling
- Transparency panel (agent reasoning traces, ethical logs)
- Consent tier progression (Passive → Suggestive → Active)

---

**Document Version:** 1.0  
**Last Updated:** 2025-01-24  
**Target Deployment:** Docker Compose single-host proof-of-concept  
**Production Readiness:** Not production-ready; suitable for 2-phase MVP demonstration and validation