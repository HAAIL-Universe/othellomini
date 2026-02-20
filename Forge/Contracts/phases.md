════════════════════════════════════════════════════════════════════════════════
PHASES CONTRACT — OthelloMini
════════════════════════════════════════════════════════════════════════════════

Project: OthelloMini
Type: Mini Build (2-Phase Delivery)
Architecture: Multi-agent AI platform with Python backend, React frontend

────────────────────────────────────────────────────────────────────────────────
Phase 0 — Backend Scaffold
────────────────────────────────────────────────────────────────────────────────

OBJECTIVE:
Build the complete backend system from scratch: project scaffold, database schema,
all API endpoints with authentication, multi-agent AI integration stubs, ethical
filtering logic, and boot/setup scripts. The server must start successfully and
respond to every request defined in the physics contract.

DELIVERABLES:

1. Project Structure & Configuration
   • Python project scaffold with virtual environment setup
   • Requirements.txt with all dependencies (Flask/FastAPI, SQLAlchemy, JWT,
     bcrypt, python-dotenv, psycopg2, pytest)
   • Environment configuration (.env.example with all required variables)
   • Config module for environment-specific settings (dev, prod)
   • Logging configuration with structured output
   • CORS configuration for frontend integration

2. Database Schema & Migrations
   • Database connection setup with connection pooling
   • SQLAlchemy ORM models for all tables:
     - users (user_id, email, password_hash, full_name, consent_tier, timezone,
       language, notification_preferences, created_at, last_active)
     - conversations (conversation_id, user_id, title, archived, message_count,
       last_message_at, created_at, updated_at)
     - messages (message_id, conversation_id, role, content, metadata,
       created_at)
     - message_reactions (reaction_id, message_id, user_id, reaction_type,
       feedback_text, created_at)
     - consent_prompts (prompt_id, user_id, action_type, action_description,
       action_details, rationale, urgency, status, alternatives, expires_at,
       created_at, decided_at)
     - actions (action_id, user_id, action_type, action_description,
       action_details, status, consent_prompt_id, execution_log, result,
       proposed_at, executed_at)
     - ethical_validations (validation_id, related_entity_type,
       related_entity_id, passed, severity, issues, modifications, reasoning,
       validated_at)
     - ethical_validation_logs (log_id, user_id, validation_type,
       content_summary, passed, severity, issues_detected, actions_taken,
       reasoning, created_at)
     - ethical_guidelines (guideline_id, category, title, description,
       rule_text, severity, active, created_at)
     - digital_shadow (shadow_id, user_id, summary, interests, values,
       confidence_score, last_updated)
     - personality_traits (trait_id, user_id, trait_name, trait_category,
       score, confidence, evidence, first_detected, last_updated)
     - behavior_patterns (pattern_id, user_id, pattern_type, description,
       frequency, strength, triggers, contexts, first_detected, last_observed,
       observation_count)
     - goals (goal_id, user_id, title, description, goal_type, status,
       target_date, metrics, coaching_preferences, created_at, updated_at)
     - goal_progress (progress_id, goal_id, metrics, notes, mood, ai_feedback,
       created_at)
     - mood_entries (mood_id, user_id, mood_level, mood_score, mood_tags,
       notes, activities, context, created_at)
     - reasoning_traces (trace_id, agent_type, conversation_id, message_id,
       reasoning_steps, final_decision, confidence_score, created_at)
     - notifications (notification_id, user_id, notification_type, title,
       message, read, action_url, metadata, created_at)
     - feedback (feedback_id, user_id, feedback_type, content, severity,
       context, status, created_at)
     - data_exports (export_id, user_id, status, download_url, expires_at,
       created_at, completed_at)
     - refresh_tokens (token_id, user_id, token_hash, expires_at, created_at,
       revoked)
   • Foreign key constraints and indexes for performance
   • Migration scripts (init_db.py) to create all tables
   • Seed script for default ethical guidelines

3. Authentication & Authorization
   • User registration endpoint with email validation and password hashing
   • Login endpoint with JWT token generation (access + refresh tokens)
   • Token refresh endpoint
   • Logout endpoint with token invalidation
   • Password validation (min 8 chars, letter + number requirement)
   • JWT middleware for protected routes
   • Token blacklist/revocation mechanism using refresh_tokens table
   • User session management

4. Core API Endpoints — User & Profile
   • GET /user/profile — retrieve user profile with all preferences
   • PATCH /user/profile — update profile, timezone, language, notifications
   • DELETE /user/account — account deletion with confirmation
   • POST /user/data-export — GDPR export request
   • GET /user/data-export/{export_id} — check export status

5. Core API Endpoints — Conversations & Messages
   • GET /conversations — list user conversations with pagination
   • POST /conversations — create new conversation thread
   • GET /conversations/{conversation_id} — get conversation with messages
   • PATCH /conversations/{conversation_id} — update title/archive status
   • DELETE /conversations/{conversation_id} — delete conversation
   • GET /conversations/{conversation_id}/messages — paginated messages
   • POST /conversations/{conversation_id}/messages — send message to AI
   • POST /messages/{message_id}/reactions — add reaction to message

6. Core API Endpoints — Consent & Actions
   • GET /consent/tier — get current consent tier setting
   • PUT /consent/tier — update consent tier with confirmation
   • GET /consent/prompts — list pending consent prompts
   • GET /consent/prompts/{prompt_id} — get prompt details
   • POST /consent/prompts/{prompt_id} — approve/deny consent prompt
   • GET /actions — list action history with filters
   • GET /actions/{action_id} — get action details with execution log

7. Core API Endpoints — Digital Shadow & Goals
   • GET /shadow — get digital shadow summary (personality, patterns, goals)
   • GET /shadow/traits — get personality traits
   • GET /shadow/goals — list goals with status filter
   • POST /shadow/goals — create new goal
   • GET /shadow/goals/{goal_id} — get goal details with progress
   • PATCH /shadow/goals/{goal_id} — update goal
   • DELETE /shadow/goals/{goal_id} — delete goal
   • POST /shadow/goals/{goal_id}/progress — log goal progress entry
   • GET /shadow/mood — get mood history with date range
   • POST /shadow/mood — log mood entry
   • GET /shadow/behavior-patterns — get detected behavioral patterns

8. Core API Endpoints — AI Agents & Ethics
   • GET /agents/reasoning — get agent reasoning traces
   • GET /agents/status — health check for all agent systems
   • GET /ethics/validation-logs — ethical validation logs with filters
   • GET /ethics/guidelines — active ethical guidelines

9. Core API Endpoints — Notifications & Feedback
   • GET /notifications — list notifications with filters
   • POST /notifications/{notification_id}/read — mark as read
   • POST /notifications/read-all — mark all read
   • POST /feedback — submit feedback/bug reports

10. Multi-Agent AI Integration Stubs
    • Stub service for FELLO (personalization engine)
    • Stub service for Othello (ethical gate) with basic filtering rules
    • Stub service for RealityAgent (proactive interventions)
    • Stub sub-agents (TraitAgent, BehaviorAgent, AspirationAgent, MoodAgent)
    • Message processing pipeline that routes through agents
    • Mock AI response generation for conversation messages
    • Ethical validation service with rule checking against guidelines
    • Consent prompt generation logic
    • Action proposal and execution framework

11. Middleware & Utilities
    • Request validation middleware
    • Error handling middleware with structured error responses
    • Rate limiting middleware (60 req/min default, 10 req/min for messages)
    • Request logging middleware
    • Database session management middleware
    • Utility functions for password hashing/verification
    • Utility functions for JWT encoding/decoding
    • UUID generation utilities
    • Date/time utilities for timezone handling

12. Testing & Boot Scripts
    • Unit tests for authentication flow
    • Unit tests for database models
    • Integration tests for key endpoints (auth, conversations, consent)
    • Boot script (run.py) to start the server
    • Database setup script (setup_db.py)
    • Health check endpoint (GET /health)
    • API documentation endpoint (GET /docs) with OpenAPI spec

SCHEMA COVERAGE:
All tables created and fully integrated:
users, conversations, messages, message_reactions, consent_prompts, actions,
ethical_validations, ethical_validation_logs, ethical_guidelines, digital_shadow,
personality_traits, behavior_patterns, goals, goal_progress, mood_entries,
reasoning_traces, notifications, feedback, data_exports, refresh_tokens

EXIT CRITERIA:
□ Server starts without errors on `python run.py`
□ Database migrations complete successfully
□ All 40+ API endpoints defined in physics contract return valid responses
□ Authentication flow working: register → login → JWT token → protected endpoints
□ User can register, login, create conversation, send message, receive AI response
□ Consent tier can be retrieved and updated
□ Goal can be created and progress logged
□ Ethical validation logs are created for messages
□ Rate limiting enforces limits (returns 429 when exceeded)
□ All endpoints return proper error codes (400, 401, 404, 409, 429, 500)
□ Health check endpoint returns 200 OK
□ Test suite passes with >80% coverage for core auth/API logic

────────────────────────────────────────────────────────────────────────────────
Phase 1 — Frontend & Ship
────────────────────────────────────────────────────────────────────────────────

OBJECTIVE:
Build the complete frontend from scratch and ship: React project scaffold, all
pages/routes, components, full backend API integration, styling with the dark
conversational theme, and comprehensive README with setup instructions. User must
be able to interact with the full application end-to-end.

DELIVERABLES:

1. Project Structure & Configuration
   • React project scaffold (using Vite or Create React App)
   • Package.json with dependencies (React, React Router, Axios, date-fns,
     recharts for mood graphs, TailwindCSS or styled-components)
   • Environment configuration (.env.example with API base URL)
   • ESLint and Prettier configuration
   • Build and dev scripts in package.json
   • Public assets (favicon, logo, manifest)

2. Routing & Navigation
   • React Router setup with protected routes
   • Route definitions:
     - /login — login page
     - /register — registration page
     - /chat — main chat interface (default after login)
     - /chat/:conversationId — specific conversation view
     - /consent — consent dashboard with pending prompts
     - /goals — goals overview and management
     - /goals/:goalId — specific goal detail view
     - /shadow — digital shadow dashboard
     - /settings — user settings and preferences
     - /notifications — notifications center
   • Navigation guard/wrapper for authenticated routes
   • Redirect to /login if not authenticated
   • Persistent navigation sidebar (collapsible on mobile)

3. Authentication Pages & Flow
   • Login page component
     - Email and password form with validation
     - Error display for invalid credentials
     - "Remember me" checkbox
     - Link to registration page
   • Registration page component
     - Full name, email, password fields with validation
     - Password strength indicator
     - Terms acceptance checkbox
     - Success message and redirect to chat on registration
   • Logout functionality in navigation
   • Token storage in localStorage/sessionStorage
   • Axios interceptor to attach JWT to requests
   • Token refresh logic when access token expires
   • Redirect to login on 401 responses

4. Main Chat Interface (Chat-First Design)
   • Full-screen conversational chat component
   • Conversation list sidebar (collapsible)
     - List of conversations with titles and timestamps
     - "New conversation" button
     - Archive toggle
     - Search/filter conversations
   • Active conversation view
     - Message list with auto-scroll to bottom
     - User messages right-aligned, AI messages left-aligned
     - Message timestamps
     - Message reactions (like, dislike, flag) inline
     - Loading indicator while AI is responding
   • Message input area
     - Text input (multiline, auto-expanding)
     - Send button (disabled while sending)
     - Character count or guidance
   • Conversation header
     - Conversation title (editable inline)
     - Archive/delete conversation actions
     - "Show reasoning" toggle for transparency panel
   • Optional transparency side panel (collapsible)
     - Agent reasoning traces for current conversation
     - Ethical validation details
     - Digital shadow summary
     - Consent prompts related to conversation
   • Integration with backend:
     - Fetch conversations on mount
     - Create new conversation
     - Send message and display AI response
     - Add reactions to messages
     - Update conversation title
     - Archive/delete conversations

5. Consent Dashboard
   • Consent tier control
     - Current tier display (Passive/Suggestive/Active/Autonomous)
     - Tier selector with descriptions
     - Confirmation modal for tier changes
   • Pending consent prompts list
     - Card for each pending prompt
     - Action type and description
     - Urgency indicator (color-coded)
     - Ethical validation summary
     - Approve/Deny buttons
     - "View details" expands full reasoning and alternatives
   • Consent prompt detail modal
     - Full action details
     - AI rationale
     - Ethical validation details
     - Alternative actions
     - Approve/Deny/Modify actions
   • Action history view
     - Filter by status (proposed, approved, denied, executed)
     - Filter by action type
     - Timeline view of past actions
   • Integration with backend:
     - Fetch current consent tier
     - Update consent tier
     - Fetch pending prompts
     - Respond to prompts (approve/deny)
     - Fetch action history

6. Goals Management
   • Goals overview page
     - Grid/list of active goals with progress bars
     - Filter by status (active, completed, paused)
     - Filter by goal type (habit, achievement, learning, etc.)
     - "Create new goal" button
   • Create goal modal/form
     - Title, description, goal type
     - Target date picker
     - Metrics definition (add multiple metrics)
     - Coaching preferences (frequency, reminder time)
   • Goal detail page
     - Goal title, description, status
     - Progress visualization (progress bars, charts)
     - Metrics current vs target
     - Progress history timeline
     - AI insights display
     - "Log progress" button
     - Edit goal button
   • Log progress modal
     - Input fields for each metric
     - Notes textarea
     - Mood selector
     - AI feedback displayed after submission
   • Edit goal form
     - Update any goal field
     - Change status (complete, pause, abandon)
   • Integration with backend:
     - Fetch goals list
     - Create new goal
     - Fetch goal details with progress
     - Update goal
     - Delete goal
     - Log progress entry

7. Digital Shadow Dashboard
   • Digital shadow summary section
     - AI-generated summary text
     - Confidence score display
     - Last updated timestamp
   • Personality traits section
     - List/grid of traits with scores
     - Visual representation (bar charts, radar chart)
     - Confidence indicators
     - Evidence snippets (expandable)
   • Behavioral patterns section
     - List of detected patterns
     - Frequency and strength indicators
     - Triggers and contexts
     - Observation count
   • Mood history section
     - Mood timeline graph (line chart or area chart)
     - Average mood stats (7-day, 30-day)
     - Detected trends display
     - "Log mood" button
   • Log mood modal
     - Mood level selector (very negative to very positive)
     - Mood tags (multi-select: anxious, excited, tired, etc.)
     - Notes textarea
     - Recent activities input
   • Interests and values display
     - Tag cloud or list of interests
     - Values list
   • Integration with backend:
     - Fetch digital shadow summary
     - Fetch personality traits
     - Fetch behavioral patterns
     - Fetch mood history with date range
     - Log mood entry

8. Settings Page
   • User profile section
     - Display and edit full name, email
     - Timezone selector
     - Language selector
   • Notification preferences
     - Toggle switches for each preference type
     - Email notifications
     - Push notifications
     - Daily summary
     - Goal reminders
   • Account management
     - Change password form
     - Data export request button with status display
     - Delete account button (with confirmation modal)
   • Integration with backend:
     - Fetch user profile
     - Update profile fields
     - Update notification preferences
     - Request data export
     - Check export status
     - Delete account

9. Notifications Center
   • Notifications list
     - Filter by type (consent_prompt, goal_reminder, system_update, etc.)
     - Filter by read/unread
     - Each notification card with:
       • Icon based on type
       • Title and message
       • Timestamp
       • Action link (if applicable)
       • Mark as read button
   • "Mark all as read" button
   • Unread count badge in navigation
   • Integration with backend:
     - Fetch notifications with filters
     - Mark notification as read
     - Mark all as read

10. Shared Components & UI Elements
    • Button component (primary, secondary, danger variants)
    • Input components (text, email, password, textarea)
    • Select/dropdown component
    • Modal component (generic wrapper)
    • Card component
    • Loading spinner
    • Error message display component
    • Success toast/notification component
    • Date picker component
    • Progress bar component
    • Badge component (for counts, status)
    • Tooltip component
    • Collapsible/accordion component
    • Tabs component
    • Avatar component (user initials or icon)

11. Styling & Theme Implementation
    • Dark theme base colors:
      - Deep navy/charcoal background (#1a1d29, #252936)
      - Soft teal accent (#4fd1c5, #2c7a7b)
      - Amber accent for urgent items (#f6ad55, #dd6b20)
      - High-contrast text (#ffffff, #e2e8f0)
      - Muted secondary text (#a0aec0)
    • Warm conversational feel:
      - Rounded corners on cards and inputs
      - Soft shadows
      - Smooth transitions and animations
      - Comfortable line spacing
      - Friendly font (Inter, Poppins, or similar)
    • Responsive layout:
      - Mobile-first approach
      - Breakpoints for tablet and desktop
      - Touch-optimized controls (larger tap targets)
      - Collapsible sidebar on mobile
    • Accessibility:
      - ARIA labels where appropriate
      - Keyboard navigation support
      - Focus indicators
      - Sufficient color contrast

12. API Integration Layer
    • Axios instance with base URL configuration
    • API service modules:
      - authService (login, register, refresh, logout)
      - conversationService (CRUD operations, messages)
      - consentService (tier, prompts, actions)
      - goalService (CRUD operations, progress)
      - shadowService (summary, traits, patterns, mood)
      - agentService (reasoning, status)
      - ethicsService (validation logs, guidelines)
      - notificationService (list, read)
      - userService (profile, settings, export, delete)
      - feedbackService (submit feedback)
    • Request interceptor for JWT attachment
    • Response interceptor for token refresh and error handling
    • Loading state management during API calls
    • Error state management and display
    • Success feedback after mutations

13. State Management & Context
    • Auth context for user session and token management
    • Global state for current conversation
    • Notification count state (updates periodically)
    • Theme context (if supporting light/dark toggle in future)
    • Local state in components where appropriate
    • Loading and error states for all data fetching

14. Polish & User Experience
    • Empty states for lists (no conversations, no goals, etc.)
    • Error states with retry options
    • Confirmation modals for destructive actions
    • Optimistic UI updates where appropriate
    • Smooth transitions between pages
    • Loading skeletons for content
    • Inline validation on forms
    • Success toasts after actions
    • Helpful tooltips and guidance text
    • Welcome message for new users
    • Onboarding flow or tutorial (optional tour)

15. Comprehensive README.md
    • Project title and description
      - What OthelloMini is
      - Multi-agent AI life intelligence platform
      - Ethics-first approach with consent tiers
    • Key features list
      - Conversational AI with personalization
      - Consent-tiered ethical filtering
      - Goal tracking and coaching
      - Digital shadow modeling
      - Transparent reasoning traces
    • Tech stack
      - Backend: Python, Flask/FastAPI, SQLAlchemy, PostgreSQL
      - Frontend: React, React Router, TailwindCSS, Axios
      - AI: Multi-agent architecture (FELLO, Othello, sub-agents)
    • Prerequisites
      - Node.js (version)
      - Python (version)
      - PostgreSQL (version)
      - npm or yarn
    • Setup instructions
      - Backend setup:
        • Clone repository
        • Create virtual environment
        • Install Python dependencies
        • Setup PostgreSQL database
        • Configure environment variables
        • Run migrations
        • Start backend server
      - Frontend setup:
        • Install npm dependencies
        • Configure environment variables
        • Start development server
    • Environment variables
      - Backend variables (DATABASE_URL, JWT_SECRET, etc.)
      - Frontend variables (REACT_APP_API_URL)
    • Running the application
      - Development mode
      - Production build
    • Project structure overview
      - Backend folder structure
      - Frontend folder structure
    • API documentation reference (link to /docs endpoint)
    • Usage examples
      - Create account and login
      - Start a conversation
      - Set consent tier
      - Create and track a goal
      - View digital shadow
    • Screenshots or GIFs (optional but helpful)
    • Contributing guidelines (if open source)
    • License information
    • Contact/support information

16. Build & Deployment Preparation
    • Production build script for frontend
    • Environment-specific API URL handling
    • Static file serving configuration
    • Basic deployment guide (suggested platforms: Heroku, Render, Vercel)
    • Docker configuration (optional but recommended)
      - Dockerfile for backend
      - Dockerfile for frontend
      - Docker-compose.yml for full stack

SCHEMA COVERAGE:
All tables utilized through frontend interactions:
users (profile, settings), conversations (chat interface), messages (chat),
consent_prompts (consent dashboard), actions (action history), goals (goal pages),
goal_progress (progress tracking), mood_entries (mood logging), personality_traits
(shadow dashboard), behavior_patterns (shadow dashboard), notifications
(notifications center), digital_shadow (shadow summary)

EXIT CRITERIA:
□ Frontend builds successfully (`npm run build`)
□ Development server starts without errors (`npm run dev`)
□ User can register new account through UI
□ User can login and receive authentication token
□ Protected routes redirect to login when not authenticated
□ Main chat interface loads with conversation list
□ User can create new conversation and send messages
□ AI responses appear in conversation (from backend mock/stub)
□ User can view and update consent tier
□ Pending consent prompts display in consent dashboard
□ User can approve/deny consent prompts
□ User can create, view, update, and delete goals
□ User can log progress for a goal
□ Digital shadow dashboard displays personality traits and mood history
□ User can log mood entries
□ Behavioral patterns display in shadow dashboard
□ Agent reasoning traces can be viewed (if available)
□ Notifications list displays and can be marked as read
□ Settings page allows profile updates
□ User can request data export
□ User can delete account with confirmation
□ Logout functionality works and clears session
□ All pages are styled consistently with dark theme
□ Mobile responsive layout works on small screens
□ README.md is complete with all sections filled
□ Application is visually polished (no obvious bugs, smooth UX)
□ End-to-end flow works: register → login → chat → create goal → log progress
  → view shadow → adjust consent tier → logout