# OthelloMini Blueprint

## 1. Product Intent

OthelloMini is a proof-of-concept ethics-first AI chat companion that demonstrates consent-gated personalized assistance. The system maintains a simple persistent user profile (psychological traits, preferences, behavioral patterns) and filters all AI-generated suggestions through an explicit ethical consent layer before presentation. The target user is an individual exploring how a trustworthy AI assistant might provide personalized guidance while respecting ethical boundaries and user autonomy. This mini build validates the core interaction loop: user converses → system learns patterns → AI suggests actions → Othello gates suggestions by user-defined consent tier → user approves/denies in-context.

## 2. Core Invariants

1. **Consent-first output**: Every AI-generated suggestion or action MUST pass through the Othello ethical gatekeeper and be tagged with a consent tier (Passive/Suggestive/Active/Autonomous) before reaching the user. No bypass paths.

2. **Persistent user model**: All user interactions MUST update the centralized user profile (traits, preferences, context history). Profile state persists across sessions and is version-controlled for auditability.

3. **Transparent ethical reasoning**: Every gated suggestion MUST include a concise ethical justification visible to the user on demand (inline expandable reasoning). No black-box filtering.

4. **Stateless chat sessions with stateful memory**: Each chat message is processed independently but MUST read from and write to the persistent user profile. Session continuity is derived from profile state, not in-memory chat history.

5. **Single-user scope**: This mini build supports one user only (no multi-tenancy, no user authentication beyond optional environment config). Profile is identified by a fixed user_id.

## 3. MVP Scope

### In Scope (2-phase build)

**Phase 1 – Backend API & Core Logic**
- REST API with FastAPI (Python 3.11+)
- `/chat` endpoint: accepts user message, returns AI response + consent-gated suggestions
- `/profile` endpoints: GET user profile summary, PATCH update consent tier settings
- `/suggestions/{id}/approve` and `/suggestions/{id}/deny`: user action on pending suggestions
- Othello gatekeeper service: rule-based ethical filter with consent tier assignment
- Minimal AI suggestion engine: OpenAI GPT-4 integration for conversational responses and action generation
- Simple user profile store: SQLite database with `user_profile` (traits, preferences, consent_tier), `conversations` (message log), `suggestions` (pending/approved/denied actions with ethical reasoning)
- Docker Compose for local development (API + SQLite)

**Phase 2 – Frontend Chat UI**
- Single-page React application (Vite + TypeScript)
- Fullscreen chat interface: message list, input field, send button
- Inline suggestion cards: display AI-generated actions with consent tier badge, ethical reasoning (expandable), approve/deny buttons
- Collapsible side panel: user profile summary (top 3 traits, current consent tier), recent conversation context
- Settings modal: adjust consent tier (radio buttons: Passive/Suggestive/Active/Autonomous), view/clear profile data
- Dark theme with navy/charcoal base, soft teal accents for suggestions, amber for warnings
- Mobile-responsive layout (flexbox/grid, touch-friendly buttons)

### Explicitly NOT in Scope

- Multi-agent sub-system architecture (FELLO sub-agents, RealityAgent, PlannerAgent) — deferred to full build
- Real-world action execution (calendar API, email sending, external integrations) — suggestions are displayed only
- Advanced psychological modeling (LLM-based trait extraction, mood tracking) — static mock traits for MVP
- User authentication, multi-user support, role-based access control
- Conversation branching, chat history export, advanced search
- LLM fine-tuning, custom embeddings, vector search for context retrieval
- Production-grade observability (structured logging only, no telemetry/metrics)
- Cloud deployment (AWS/GCP) — local Docker only

## 4. Layer Boundaries

```
┌─────────────────────────────────────────────┐
│  Presentation (React SPA)                   │
│  - ChatView, ProfilePanel, SettingsModal    │
└─────────────────────────────────────────────┘
                    ↓ HTTP/JSON
┌─────────────────────────────────────────────┐
│  API Routes (FastAPI)                       │
│  - /chat, /profile, /suggestions/*          │
│  - Request validation (Pydantic models)     │
└─────────────────────────────────────────────┘
                    ↓
┌─────────────────────────────────────────────┐
│  Service Layer                              │
│  - ChatService: orchestrate conversation    │
│  - OthelloService: ethical gating logic     │
│  - ProfileService: user model CRUD          │
│  - AIService: OpenAI API wrapper            │
└─────────────────────────────────────────────┘
                    ↓
┌─────────────────────────────────────────────┐
│  Repository Layer                           │
│  - ProfileRepository (user_profile table)   │
│  - ConversationRepository (conversations)   │
│  - SuggestionRepository (suggestions table) │
│  - SQLite via SQLAlchemy ORM                │
└─────────────────────────────────────────────┘
                    ↓
┌─────────────────────────────────────────────┐
│  Data Store (SQLite)                        │
│  - Single file: othello_mini.db             │
└─────────────────────────────────────────────┘
```

**Dependency Rules:**
- Routes call Service layer only (never Repository directly)
- Services call Repositories and external APIs (OpenAI)
- Repositories encapsulate all SQL/ORM logic
- No circular dependencies: Service → Repository (one-way)
- OthelloService is injected into ChatService (dependency injection via FastAPI)

## 5. Deployment

**Local Development (Docker Compose)**

```yaml
# docker-compose.yml
services:
  api:
    build: ./backend
    ports:
      - "8000:8000"
    environment:
      - DATABASE_URL=sqlite:///data/othello_mini.db
      - OPENAI_API_KEY=${OPENAI_API_KEY}
    volumes:
      - ./data:/app/data
    depends_on:
      - db-init

  frontend:
    build: ./frontend
    ports:
      - "3000:3000"
    environment:
      - VITE_API_BASE_URL=http://localhost:8000
    depends_on:
      - api

  db-init:
    image: python:3.11-slim
    volumes:
      - ./backend:/app
      - ./data:/app/data
    working_dir: /app
    command: python -m alembic upgrade head
```

**Requirements:**
- Docker 24+, Docker Compose 2.0+
- OpenAI API key (provided via `.env` file)
- 2 GB RAM minimum (for API + frontend dev servers)

**Build & Run:**
```bash
# Clone repo
git clone <repo-url> othello-mini && cd othello-mini

# Set OpenAI key
echo "OPENAI_API_KEY=sk-..." > .env

# Start services
docker-compose up --build

# Access frontend: http://localhost:3000
# API docs: http://localhost:8000/docs
```

**Database Migrations:**
- Alembic for schema versioning
- Initial migration creates `user_profile`, `conversations`, `suggestions` tables
- Run migrations automatically in `db-init` service before API starts

**Persistence:**
- SQLite file mounted to `./data/othello_mini.db` for persistence across container restarts
- Profile data survives `docker-compose down` (volumes retained)

---

**End of Blueprint**