# OthelloMini — Build Phases

## Phase 0 — Backend Scaffold

**Objective:**  
Build the complete backend system from scratch including project scaffold, database schema, all API endpoints, business logic services, Othello ethical gatekeeper, OpenAI integration, and Docker configuration. By the end of this phase, the API server must be fully operational and capable of handling all chat, profile, and suggestion requests defined in the physics contract.

**Deliverables:**

- **Project Structure & Configuration**
  - Python 3.11+ FastAPI project scaffold with standard directory layout (`app/`, `tests/`, `alembic/`, `docker/`)
  - `pyproject.toml` or `requirements.txt` with all dependencies: FastAPI, Uvicorn, SQLAlchemy, Alembic, Pydantic, OpenAI SDK, python-dotenv
  - Environment configuration loader (`.env` support) for `DATABASE_URL`, `OPENAI_API_KEY`, `API_VERSION`
  - Docker configuration: `Dockerfile` for API service, `docker-compose.yml` with `api`, `db-init`, and `frontend` service definitions
  - `.gitignore`, `.dockerignore`, basic project `README.md` stub

- **Database Schema & Migrations**
  - Alembic initialized with migration folder structure
  - Initial migration creating three tables:
    - `user_profile`: `user_id` (PK, string, default "default_user"), `consent_tier` (enum: passive/suggestive/active/autonomous, default "suggestive"), `traits` (JSON), `preferences` (JSON), `context_summary` (JSON), `created_at`, `updated_at`
    - `conversations`: `conversation_id` (PK, UUID), `user_id` (FK), `user_message` (text), `ai_response` (text), `context` (JSON), `suggestions_count` (int), `timestamp` (datetime), indexed on `user_id` + `timestamp`
    - `suggestions`: `suggestion_id` (PK, UUID), `conversation_id` (FK), `user_id` (FK), `text` (text), `action_type` (enum), `consent_tier` (enum), `ethical_reasoning` (JSON), `risk_level` (enum), `status` (enum: pending/approved/denied/expired), `created_at`, `expires_at`, indexed on `user_id` + `status`
  - SQLAlchemy ORM models matching schema with proper relationships (User → Conversations 1:N, Conversation → Suggestions 1:N)
  - Database initialization script that runs migrations and seeds default user profile with mock trait data

- **Repository Layer**
  - `ProfileRepository`: CRUD methods for user profile (get_profile, update_consent_tier, update_preferences, clear_profile)
  - `ConversationRepository`: create_conversation, get_conversations_paginated, get_conversation_by_id
  - `SuggestionRepository`: create_suggestion, get_suggestions_by_user, get_suggestion_by_id, update_suggestion_status, expire_old_suggestions
  - All repositories use SQLAlchemy sessions with proper transaction handling
  - Repository base class with session management and error handling

- **Service Layer**
  - `AIService`: OpenAI GPT-4 integration wrapper
    - `generate_response(user_message, conversation_history, user_profile)` → AI response string
    - `extract_suggestions(ai_response, conversation_context)` → list of raw suggestion objects
    - Error handling for OpenAI API failures with retry logic (exponential backoff)
    - Token usage tracking and logging
  - `OthelloService`: Ethical gatekeeper logic
    - `gate_suggestions(suggestions, user_profile)` → filtered suggestions with ethical reasoning
    - Rule-based ethical validation: check for harmful content, privacy violations, excessive commitment, manipulation patterns
    - Assign consent tier to each suggestion based on risk assessment
    - Generate human-readable ethical justification for each suggestion
    - Confidence scoring (0.0-1.0) for ethical assessments
  - `ProfileService`: User profile business logic
    - `get_profile()` → UserProfile object
    - `update_consent_tier(new_tier)` → updated profile
    - `update_preferences(preferences_dict)` → updated profile
    - `update_traits_from_conversation(conversation)` → profile with updated traits (mock implementation: static traits for MVP)
    - `clear_profile()` → reset to default state
  - `ChatService`: Orchestrate conversation flow
    - `process_message(user_message, context_dict)` → ChatResponse with AI response + gated suggestions
    - Flow: retrieve profile → call AIService → extract suggestions → call OthelloService → filter by consent tier → persist conversation + suggestions → return response
    - Update conversation context and profile state
    - Handle suggestion expiration (mark pending suggestions >24h old as expired)
  - All services use dependency injection pattern with FastAPI's `Depends()`

- **API Routes (FastAPI)**
  - `/api/v1/chat` POST: accept user message, return AI response with gated suggestions
    - Request validation via Pydantic model (ChatRequest)
    - Response model (ChatResponse) with conversation_id, message, response, suggestions array, profile_updated flag, metadata
    - Error handling: 400 for validation errors, 500 for OpenAI/DB failures
  - `/api/v1/profile` GET: return UserProfile schema
  - `/api/v1/profile` PATCH: update consent tier and preferences
    - Request validation (ProfileUpdateRequest)
    - Response: updated UserProfile
  - `/api/v1/profile/clear` POST: reset profile to default
  - `/api/v1/suggestions` GET: list suggestions with pagination and status filter
    - Query params: `status` (pending/approved/denied/all), `limit`, `offset`
    - Response: suggestions array, total count, pagination metadata
  - `/api/v1/suggestions/{suggestion_id}/approve` POST: mark suggestion approved
    - Optional feedback in request body
    - Response: suggestion_id, status, approved_at timestamp
  - `/api/v1/suggestions/{suggestion_id}/deny` POST: mark suggestion denied
    - Optional reason in request body
    - Response: suggestion_id, status, denied_at timestamp
  - `/api/v1/conversations` GET: paginated conversation history
    - Query params: `limit`, `offset`, `since` (date filter)
    - Response: conversations array, total count, pagination metadata
  - `/api/v1/health` GET: health check endpoint
    - Check database connectivity (ping query)
    - Check OpenAI API status (lightweight check or cached status)
    - Return overall status (healthy/degraded/unhealthy), service statuses, version info
  - All routes use consistent error response schema (Error model)
  - CORS middleware configured to allow frontend origin (http://localhost:3000)

- **Pydantic Models (Request/Response Schemas)**
  - Request models: `ChatRequest`, `ProfileUpdateRequest`, `SuggestionActionRequest`
  - Response models: `ChatResponse`, `UserProfile`, `Suggestion`, `Conversation`, `Error`, `HealthResponse`, `PaginatedSuggestionsResponse`, `PaginatedConversationsResponse`
  - All models match physics contract schemas exactly
  - Field validation with Pydantic validators (min/max length, enum validation, format checks)

- **Application Bootstrap**
  - FastAPI app initialization with metadata (title, version, description)
  - Lifespan event handlers: startup (DB connection check, seed default profile if missing) and shutdown (cleanup)
  - Router registration for all endpoint groups
  - Exception handlers for common errors (ValidationError, DatabaseError, OpenAIError)
  - Structured logging configuration (JSON logs with request ID correlation)
  - API versioning strategy (prefix `/api/v1`)

- **Docker & Local Development**
  - `Dockerfile` for backend: multi-stage build (dependencies → app copy → production image)
  - `docker-compose.yml` orchestration:
    - `db-init` service: runs Alembic migrations before API starts
    - `api` service: runs Uvicorn server on port 8000, mounts `./data` volume for SQLite persistence
    - Environment variables passed from `.env` file
    - Health checks configured for API service
  - `.env.example` file documenting required environment variables
  - Local development instructions in README stub

- **Testing Setup**
  - `pytest` configured with basic test structure
  - Test fixtures for database session (in-memory SQLite), mock OpenAI client
  - Placeholder test files: `tests/test_services.py`, `tests/test_routes.py`, `tests/test_repositories.py`
  - No full test coverage required for Phase 0, but framework must be in place

**Schema Coverage:**
- Full implementation of `user_profile` table with all columns (user_id, consent_tier, traits, preferences, context_summary, timestamps)
- Full implementation of `conversations` table with all columns (conversation_id, user_id, messages, context, metadata, timestamp)
- Full implementation of `suggestions` table with all columns (suggestion_id, conversation_id, user_id, text, action_type, consent_tier, ethical_reasoning, risk_level, status, timestamps)
- All relationships (FKs) and indexes defined
- Seed data: default user profile with mock Big Five traits

**Exit Criteria:**
1. `docker-compose up --build` starts all services without errors
2. Database migrations run successfully, all three tables created
3. API health check (`GET /api/v1/health`) returns 200 with "healthy" status
4. Default user profile seeded and retrievable via `GET /api/v1/profile`
5. Chat endpoint (`POST /api/v1/chat`) accepts message and returns AI response with at least one gated suggestion (using real OpenAI API)
6. Suggestion approval/denial endpoints function correctly (update status in database)
7. Profile update endpoint (`PATCH /api/v1/profile`) successfully changes consent tier
8. All API endpoints return proper error responses for invalid input (validated via manual testing or Postman)
9. SQLite database file persists across container restarts (volume mount working)
10. Logs show structured output with request correlation IDs

---

## Phase 1 — Frontend & Ship

**Objective:**  
Build the complete React frontend from scratch including project scaffold, all UI components, chat interface, suggestion cards, profile panel, settings modal, API integration with backend, styling with dark theme, mobile responsiveness, and comprehensive documentation. By the end of this phase, the user can interact with the full application via browser, send chat messages, view/approve/deny suggestions, adjust consent tier, and understand how to set up and use the system.

**Deliverables:**

- **Project Structure & Configuration**
  - React 18+ project initialized with Vite + TypeScript
  - Project structure: `src/components/`, `src/pages/`, `src/services/`, `src/hooks/`, `src/types/`, `src/styles/`, `src/utils/`
  - TypeScript configuration (`tsconfig.json`) with strict mode
  - ESLint + Prettier configuration for code quality
  - Environment variable configuration: `.env` for `VITE_API_BASE_URL` (default: http://localhost:8000)
  - `package.json` with all dependencies: React, React Router, Axios, date-fns, CSS modules or styled-components
  - `.gitignore` for node_modules, build artifacts

- **Type Definitions**
  - TypeScript interfaces matching physics contract schemas:
    - `UserProfile` type (user_id, consent_tier, traits, preferences, context_summary, timestamps)
    - `Suggestion` type (suggestion_id, text, action_type, consent_tier, ethical_reasoning, risk_level, status, timestamps)
    - `Conversation` type (conversation_id, messages, context, timestamp)
    - `ChatRequest`, `ChatResponse`, `Error` types
  - Enum types for consent tiers, action types, risk levels, status values
  - API response wrapper types for pagination

- **API Integration Layer**
  - `api/client.ts`: Axios client configured with base URL, interceptors for error handling, request/response logging
  - `api/chat.ts`: `sendMessage(message, context?)` → ChatResponse
  - `api/profile.ts`: `getProfile()`, `updateProfile(updates)`, `clearProfile()`
  - `api/suggestions.ts`: `getSuggestions(status?, limit?, offset?)`, `approveSuggestion(id, feedback?)`, `denySuggestion(id, reason?)`
  - `api/conversations.ts`: `getConversations(limit?, offset?, since?)`
  - Error handling: parse API error responses, display user-friendly messages
  - Loading states and retry logic for failed requests

- **Custom Hooks**
  - `useProfile()`: fetch and cache user profile, provide update methods
  - `useChat()`: manage chat state (messages, loading, error), send message function
  - `useSuggestions()`: fetch suggestions with pagination, approve/deny actions
  - `useConversations()`: fetch conversation history with pagination
  - All hooks use React Query or similar for caching and state management

- **Core Components**
  - `ChatView` (main page):
    - Message list container with scrollable area
    - User messages aligned right, AI responses aligned left
    - Message bubbles with sender indicator, timestamp
    - Auto-scroll to bottom on new messages
    - Loading indicator while AI responds
    - Error display for failed requests
  - `MessageInput`:
    - Text area with placeholder "Type your message..."
    - Character count display (max 4000)
    - Send button (disabled while loading or empty)
    - Enter-to-send keyboard shortcut (Shift+Enter for new line)
    - Optional context controls (mood selector, currently hidden/minimal for MVP)
  - `SuggestionCard`:
    - Suggestion text display
    - Consent tier badge with color coding (Passive: gray, Suggestive: teal, Active: amber, Autonomous: red)
    - Risk level indicator (Low/Medium/High)
    - Expandable ethical reasoning section (collapsed by default, click to expand)
    - Approve/Deny button pair (only for pending suggestions)
    - Status indicator for approved/denied suggestions
    - Timestamp (created_at, expires_at countdown)
  - `ProfilePanel` (collapsible side panel):
    - User ID display
    - Current consent tier with color indicator
    - Top 3 psychological traits display (Big Five scores as horizontal bars or percentage)
    - Recent conversation topics (tag cloud or bullet list)
    - Last interaction timestamp
    - "View Full Profile" button → opens profile modal
    - Collapse/expand toggle button
  - `SettingsModal`:
    - Consent tier selector (radio buttons: Passive / Suggestive / Active / Autonomous)
    - Description of each tier's implications
    - Preferences section:
      - Communication style dropdown (Direct / Gentle / Analytical / Motivational)
      - Focus areas multi-select (Productivity, Mental Health, Relationships, etc.)
      - Notification frequency dropdown (Realtime / Hourly / Daily / Weekly)
    - "Clear Profile Data" button with confirmation dialog
    - Save button (calls `updateProfile` API)
    - Cancel/Close button
  - `ConversationHistory` (in side panel or separate view):
    - List of past conversations with timestamps
    - Click to view full conversation details
    - Pagination controls (Load More button or infinite scroll)
  - `HealthIndicator` (status bar or footer):
    - API connectivity status (green/yellow/red dot)
    - Optional: display API version, last health check time

- **Layout & Navigation**
  - `Layout` component:
    - Main content area (chat view)
    - Collapsible side panel (profile + conversation history)
    - Top navigation bar: app title "OthelloMini", settings icon button
    - Footer: minimal attribution or status indicator
  - Responsive layout:
    - Desktop (>1024px): side panel always visible, chat takes 70% width
    - Tablet (768-1024px): side panel collapsible by default, full-width chat when collapsed
    - Mobile (<768px): side panel as slide-over drawer, full-screen chat, floating action button for settings
  - React Router setup with single route `/` for chat view (no complex routing needed for MVP)

- **Styling & Theme**
  - Dark theme implementation:
    - Background: deep navy/charcoal (#1a1d29 or similar)
    - Primary text: high-contrast white/off-white (#f0f0f0)
    - Secondary text: muted gray (#a0a0a0)
    - Accent color for suggestions: soft teal (#5fb3b3)
    - Warning color for high-risk: amber (#f59e0b)
    - Error color: red (#ef4444)
  - Component-specific styles:
    - Chat bubbles: subtle rounded corners, semi-transparent backgrounds
    - Suggestion cards: bordered cards with hover effect
    - Buttons: clear hover/active states, disabled states with reduced opacity
    - Input fields: dark backgrounds with light borders, focus states with accent color glow
  - Typography:
    - Sans-serif font (Inter, Roboto, or system font stack)
    - Clear hierarchy: larger text for messages, smaller for metadata
  - Responsive styles: CSS Grid or Flexbox for layout, media queries for breakpoints
  - CSS Modules or styled-components for component scoping

- **State Management**
  - Global state for user profile (via Context API or Zustand)
  - Local state for chat messages (managed by `useChat` hook)
  - Suggestions state synchronized with backend (fetch on mount, update on approve/deny)
  - Loading/error states for all async operations
  - Optimistic updates for suggestion actions (immediate UI update, rollback on error)

- **User Experience Enhancements**
  - Loading skeletons for profile panel and conversation list
  - Smooth animations for message appearance, suggestion cards
  - Toast notifications for success/error messages (approve/deny confirmation, profile update confirmation)
  - Empty states: "No conversations yet" when history is empty, "No suggestions" when none pending
  - Keyboard shortcuts: Escape to close modal, Enter to send message
  - Accessibility: ARIA labels for interactive elements, keyboard navigation support, focus management

- **Docker Integration**
  - `Dockerfile` for frontend: Node 18+ base, install dependencies, build production bundle with Vite, serve with nginx or Node static server
  - Update `docker-compose.yml` to include frontend service:
    - Port 3000 exposed
    - Environment variable `VITE_API_BASE_URL` passed from `.env`
    - Depends on `api` service
  - Nginx configuration (if used): proxy `/api` requests to backend, serve static files
  - Production build optimization: minification, code splitting, asset caching headers

- **Comprehensive README.md**
  - **Project Overview**:
    - Description: "OthelloMini is an ethics-first AI chat companion with consent-gated personalized assistance. The system maintains a persistent user profile and filters all AI suggestions through an ethical gatekeeper (Othello) before presentation."
    - Purpose: Proof-of-concept demonstrating consent-tiered AI assistance with transparent ethical reasoning
    - Target audience: Individuals exploring trustworthy AI assistance
  - **Features**:
    - Conversational AI chat powered by OpenAI GPT-4
    - Persistent user profile with psychological trait tracking
    - Consent-gated suggestion system (4 tiers: Passive → Suggestive → Active → Autonomous)
    - Transparent ethical reasoning for every suggestion
    - User-controlled autonomy settings
    - Clean, dark-themed responsive UI
  - **Tech Stack**:
    - Backend: Python 3.11+, FastAPI, SQLAlchemy, OpenAI API, SQLite
    - Frontend: React 18+, TypeScript, Vite, Axios
    - Deployment: Docker Compose for local development
  - **Prerequisites**:
    - Docker 24+ and Docker Compose 2.0+
    - OpenAI API key (sign up at platform.openai.com)
    - 2 GB RAM minimum
  - **Setup Instructions**:
    1. Clone repository: `git clone <repo-url> othello-mini && cd othello-mini`
    2. Create `.env` file with `OPENAI_API_KEY=sk-...`
    3. Start services: `docker-compose up --build`
    4. Access frontend at http://localhost:3000
    5. API documentation available at http://localhost:8000/docs
  - **Environment Variables**:
    - `OPENAI_API_KEY` (required): Your OpenAI API key
    - `DATABASE_URL` (optional): SQLite database path, defaults to `sqlite:///data/othello_mini.db`
    - `VITE_API_BASE_URL` (optional): Backend API URL, defaults to `http://localhost:8000`
  - **Usage Examples**:
    - Send a chat message: Type in the input field and press Enter
    - Approve a suggestion: Click "Approve" button on suggestion card
    - Adjust consent tier: Click settings icon, select new tier, save
    - View ethical reasoning: Click suggestion card to expand reasoning section
    - Clear profile: Settings → "Clear Profile Data" → confirm
  - **Project Structure**:
    - `/backend` - FastAPI application
    - `/frontend` - React application
    - `/data` - SQLite database persistence (created by Docker volume)
    - `docker-compose.yml` - Service orchestration
  - **Development**:
    - Backend hot reload: `cd backend && uvicorn app.main:app --reload`
    - Frontend dev server: `cd frontend && npm run dev`
    - Run tests: `pytest` (backend), `npm test` (frontend)
  - **API Documentation**:
    - Interactive Swagger docs: http://localhost:8000/docs
    - Key endpoints: `/api/v1/chat`, `/api/v1/profile`, `/api/v1/suggestions`
  - **Consent Tiers Explained**:
    - **Passive**: Observation only, no action suggestions
    - **Suggestive**: Low-risk suggestions (read articles, reflect on topics)
    - **Active**: Medium-risk suggestions (schedule tasks, draft messages)
    - **Autonomous**: High-risk suggestions (execute actions, make commitments)
  - **Ethical Guardrails**:
    - All suggestions pass through Othello gatekeeper
    - Rule-based validation checks for harm, privacy, manipulation
    - Transparent justification for every suggestion
    - User always has final approval authority
  - **Troubleshooting**:
    - "OpenAI API error": Check API key validity and quota
    - "Database locked": Stop containers and restart `docker-compose up`
    - "Port already in use": Change port mappings in docker-compose.yml
  - **Limitations**:
    - Single-user only (no authentication)
    - Mock psychological traits (not ML-based)
    - Rule-based ethical filtering (not LLM-based)
    - Local deployment only (not production-ready)
  - **Future Roadmap** (out of scope for MVP):
    - Multi-agent sub-system (FELLO sub-agents)
    - Real-world action execution (calendar, email integrations)
    - Advanced ML-based trait extraction
    - Multi-user support with authentication
    - Cloud deployment (AWS/GCP)
  - **License**: MIT (or specify)
  - **Contributing**: Guidelines for contributions (if applicable)
  - **Contact**: Project maintainer information

- **Final Testing & Polish**
  - Manual end-to-end testing:
    - Send chat message → verify AI response appears
    - Verify suggestion cards render with correct data
    - Approve suggestion → verify status updates in UI and backend
    - Deny suggestion → verify status updates
    - Change consent tier → verify new tier persists after page reload
    - Clear profile → verify profile resets to default
    - Test responsive layouts on mobile/tablet/desktop screen sizes
  - Cross-browser testing: Chrome, Firefox, Safari (basic verification)
  - Performance check: ensure chat interface remains responsive with 50+ messages
  - Accessibility audit: keyboard navigation, screen reader compatibility (basic checks)
  - Error handling verification: network errors, API timeouts, invalid inputs

**Schema Coverage:**
- All frontend types/interfaces match backend schemas (UserProfile, Suggestion, Conversation)
- Full representation of `user_profile` data in ProfilePanel and SettingsModal
- Complete conversation history display with all fields (messages, timestamps, context)
- All suggestion fields displayed in SuggestionCard (text, consent_tier, ethical_reasoning, risk_level, status)

**Exit Criteria:**
1. `docker-compose up --build` starts all services (backend + frontend) and frontend is accessible at http://localhost:3000
2. Chat interface loads without errors, displays empty state initially
3. User can send a message and receive AI response with suggestion cards rendered inline
4. Suggestion cards display all required fields (text, consent tier badge, ethical reasoning expandable, approve/deny buttons)
5. Clicking "Approve" on a suggestion updates its status to approved (verified in UI and via backend API)
6. Clicking "Deny" on a suggestion updates its status to denied
7. Profile panel displays user profile data (consent tier, traits, recent topics)
8. Settings modal opens, allows consent tier change, and saves successfully (persists after page reload)
9. "Clear Profile Data" function resets profile to default state
10. Conversation history loads and displays past messages with pagination
11. Application is fully responsive (tested on mobile, tablet, desktop viewports)
12. README.md is complete with all sections filled (description, setup, usage, troubleshooting)
13. All environment variables documented in README and `.env.example`
14. No console errors in browser developer tools during normal usage
15. Application handles API errors gracefully (displays error messages, doesn't crash)

---

**End of Phases Contract**