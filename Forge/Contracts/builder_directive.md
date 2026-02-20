# Builder Directive — OthelloMini

## Project Summary
OthelloMini is an ethics-first AI chat companion with consent-gated personalized assistance, featuring a multi-agent architecture with Othello ethical gatekeeper and persistent user profile modeling.

## Build Phases
This project consists of exactly **2 phases** that must be executed sequentially to completion:

- **Phase 0** — Backend Scaffold
- **Phase 1** — Frontend & Ship

## Execution Protocol

### Step 1: Read All Contracts
Before beginning any implementation work, read and internalize the following contracts in order:

1. **physics.md** — Data model, API schemas, database structure, and technical constraints
2. **blueprint.md** — System architecture, component relationships, and integration requirements  
3. **phases.md** — Detailed phase deliverables, exit criteria, and acceptance requirements

Cross-reference these contracts throughout the build to ensure consistency and completeness.

### Step 2: Execute Phase 0 — Backend Scaffold
Build the complete Python/FastAPI backend system including:

- Project scaffold with FastAPI, SQLAlchemy, Alembic
- SQLite database with three tables: `user_profile`, `conversations`, `suggestions`
- Database migrations and initialization script
- Repository layer (ProfileRepository, ConversationRepository, SuggestionRepository)
- Service layer (AIService with OpenAI GPT-4 integration, OthelloService ethical gatekeeper, ProfileService, ChatService)
- Complete REST API with 10+ endpoints (chat, profile, suggestions, conversations, health)
- Pydantic request/response models matching physics contract schemas
- Docker configuration (`Dockerfile`, `docker-compose.yml` with db-init and api services)
- Structured logging, error handling, CORS middleware
- Testing framework setup with pytest

**Phase 0 Exit Criteria:**
- `docker-compose up --build` starts all services successfully
- Database migrations create all three tables with proper relationships
- API health check returns 200 "healthy" status
- Default user profile seeded and retrievable
- Chat endpoint accepts message and returns AI response with gated suggestions (live OpenAI API call)
- Suggestion approve/deny endpoints function correctly
- Profile update endpoint successfully changes consent tier
- All endpoints return proper error responses for invalid input
- SQLite database persists across container restarts
- Logs show structured output with request correlation

**Do not proceed to Phase 1 until all Phase 0 exit criteria are verified.**

### Step 3: Execute Phase 1 — Frontend & Ship
Build the complete React/TypeScript frontend including:

- React 18+ project with Vite, TypeScript, ESLint
- TypeScript interfaces matching physics contract schemas
- API integration layer with Axios client (chat, profile, suggestions, conversations endpoints)
- Custom hooks (useProfile, useChat, useSuggestions, useConversations)
- Core components:
  - ChatView with message list and auto-scroll
  - MessageInput with character count and keyboard shortcuts
  - SuggestionCard with consent tier badge, risk indicator, expandable ethical reasoning
  - ProfilePanel (collapsible) showing user traits and consent tier
  - SettingsModal for consent tier adjustment and profile clear
  - ConversationHistory with pagination
  - HealthIndicator for API status
- Responsive layout (desktop, tablet, mobile with breakpoints)
- Dark theme styling (deep navy/charcoal background, soft teal accents, high-contrast text)
- State management (Context API or Zustand for profile, local state for chat)
- Loading states, error handling, toast notifications, accessibility features
- Docker integration (frontend service in docker-compose.yml, nginx or Node static server)
- Comprehensive README.md with project overview, setup instructions, usage examples, troubleshooting, tech stack, consent tier explanations, limitations

**Phase 1 Exit Criteria:**
- `docker-compose up --build` starts backend + frontend, frontend accessible at http://localhost:3000
- Chat interface loads and displays empty state
- User can send message and receive AI response with suggestion cards
- Suggestion cards display all fields (text, consent tier, ethical reasoning, approve/deny buttons)
- Approve/deny buttons update suggestion status (verified in UI and backend)
- Profile panel displays user data (consent tier, traits, topics)
- Settings modal opens, allows consent tier change, saves successfully, persists after reload
- "Clear Profile Data" resets profile to default
- Conversation history loads with pagination
- Application is fully responsive (mobile, tablet, desktop tested)
- README.md is complete with all sections (description, setup, usage, troubleshooting, environment variables)
- No console errors during normal usage
- Application handles API errors gracefully

**Do not consider the build complete until all Phase 1 exit criteria are verified.**

### Step 4: Final Commit & Verification
After both phases are complete:

1. Verify all exit criteria from both phases are met
2. Run full end-to-end test: start services, send chat message, approve suggestion, change consent tier, verify persistence
3. Confirm README.md completeness and accuracy
4. Verify `.env.example` documents all required environment variables
5. Ensure `.gitignore` excludes sensitive files (`.env`, `node_modules`, database files, build artifacts)
6. Create final commit with message: "Complete OthelloMini MVP - Phase 0 (Backend) + Phase 1 (Frontend)"
7. Verify git repository contains:
   - `/backend` directory with FastAPI application
   - `/frontend` directory with React application
   - `docker-compose.yml` at root
   - `.env.example` at root
   - `README.md` at root
   - `.gitignore` at root

## Critical Requirements

### OpenAI Integration
- Backend must use OpenAI GPT-4 API (requires valid `OPENAI_API_KEY` environment variable)
- AIService must handle API errors gracefully with retry logic
- Token usage should be tracked and logged
- Mock responses are not acceptable for the chat endpoint

### Ethical Gatekeeper
- OthelloService must evaluate all AI-generated suggestions before presentation
- Rule-based validation must check for: harmful content, privacy violations, excessive commitment, manipulation patterns
- Each suggestion must have ethical_reasoning JSON with human-readable justification
- Consent tier assignment based on risk assessment
- Suggestions exceeding user's consent tier must be filtered out

### Data Persistence
- SQLite database must persist in Docker volume (`./data`)
- Database must survive container restarts
- Default user profile must be seeded on first initialization
- Alembic migrations must be version-controlled

### Responsive Design
- Frontend must be usable on mobile devices (320px minimum width)
- Layout must adapt to three breakpoints: mobile (<768px), tablet (768-1024px), desktop (>1024px)
- Touch targets must be appropriately sized for mobile interaction
- Side panel must collapse on mobile, be accessible via drawer or toggle

### Error Handling
- Backend: all endpoints must return consistent error schema (Error model from physics contract)
- Frontend: all API errors must display user-friendly messages (not raw error objects)
- Network failures must not crash the application
- Loading states must be shown during async operations

### Documentation
- README.md must be comprehensive enough for a new developer to set up and run the project
- All environment variables must be documented
- Setup instructions must be step-by-step with exact commands
- Troubleshooting section must address common issues (API key errors, port conflicts, database locks)

## Boot Script Flag
`boot_script_required: false`

The project uses Docker Compose for orchestration. No additional boot script is required beyond `docker-compose up --build`.

## Acceptance Definition
The build is complete when:
1. All Phase 0 exit criteria are met and verified
2. All Phase 1 exit criteria are met and verified
3. End-to-end user flow works: start services → send chat message → view suggestion → approve/deny → change consent tier → verify persistence
4. README.md is complete and accurate
5. Repository is properly structured with all required files
6. No placeholder code or TODO comments remain in critical paths
7. `.env.example` documents all required environment variables

**The builder must execute both phases to completion. Partial delivery is not acceptable.**