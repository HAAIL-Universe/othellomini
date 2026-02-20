# Builder Directive — OthelloMini

**Project Summary**  
OthelloMini is an ethics-first multi-agent AI life intelligence platform delivering deeply personalized assistance through consent-tiered interaction, persistent user modeling, and proactive reality-shaping suggestions.

---

## Execution Flow

The AI builder SHALL execute the following sequence to completion:

### 1. Contract Ingestion
- Read and parse ALL contract files in `/contracts/`:
  - `tech_stack.md` — technology selections, framework versions, architecture decisions
  - `phase_manifest.md` — deliverables, acceptance criteria, file structure per phase
  - `frontend_specification.md` — UI requirements, component hierarchy, interaction patterns
  - `backend_specification.md` — API design, data models, agent architecture, business logic
  - `deployment_plan.md` — environment configuration, CI/CD pipeline, hosting setup
  - `builder_directive.md` (this file) — operational procedures

### 2. Phase 0 — Backend Scaffold
**Objective:** Establish the multi-agent Python backend with ethical filtering, user modeling, and core API.

**Execution Steps:**
1. Initialize Python project structure with virtual environment and dependency management
2. Implement five-layer agent architecture:
   - OutputGate (ethical filtering and consent enforcement)
   - FELLO core agent (orchestration and reasoning)
   - Sub-agents (psychological modeling: traits, behavior, aspirations, mood)
   - RealityAgent (proactive intervention planning)
3. Build data persistence layer for:
   - User digital shadow (persistent psychological profile)
   - Consent tier settings (Passive → Suggestive → Active → Autonomous)
   - Conversation history and ethical audit logs
4. Expose REST or WebSocket API endpoints for:
   - Chat message handling (natural language input/output)
   - Consent approval/denial actions
   - Autonomy tier configuration
   - Agent reasoning trace retrieval
5. Implement ethical validation pipeline:
   - All agent outputs filtered through OutputGate
   - Consent tier enforcement before action execution
   - Audit logging for transparency
6. Write unit tests for core agent logic and ethical filtering
7. Document API contract and agent interaction patterns

**Acceptance:**
- Backend server runs and responds to health checks
- Chat endpoint accepts messages and returns agent-filtered responses
- Consent system blocks/allows actions per configured tier
- All Phase 0 deliverables per `phase_manifest.md` satisfied

### 3. Phase 1 — Frontend & Ship
**Objective:** Build the chat-first UI with inline consent controls, deploy the integrated application.

**Execution Steps:**
1. Initialize frontend project (framework per `tech_stack.md`)
2. Implement primary chat interface:
   - Fullscreen conversational UI with dark theme (navy/charcoal base)
   - Message input/output with warm, journal-like aesthetic
   - Real-time streaming of agent responses
3. Build inline consent prompt components:
   - Action approval/denial cards within chat flow
   - Muted accent colors (soft teal/amber) for prompts
   - Touch-optimized controls for mobile
4. Create optional transparency panel (collapsible side drawer):
   - Agent reasoning trace viewer
   - Ethical validation logs
   - Digital shadow summary (user profile insights)
5. Implement settings/autonomy tier control page:
   - Consent tier selector (Passive → Suggestive → Active → Autonomous)
   - User preferences and privacy controls
   - Accessible but non-intrusive placement
6. Integrate frontend with backend API:
   - Connect chat interface to message endpoints
   - Wire consent actions to backend approval system
   - Fetch and display agent traces and audit logs
7. Apply responsive design and accessibility standards
8. Write integration tests for critical user flows
9. Configure deployment pipeline per `deployment_plan.md`:
   - Environment variables and secrets management
   - CI/CD automation (build, test, deploy)
   - Production hosting setup
10. Deploy integrated application to target environment
11. Verify production readiness:
    - End-to-end chat flow operational
    - Consent system enforced in production
    - Ethical filtering active
    - Monitoring and logging functional

**Acceptance:**
- Frontend accessible via web browser
- Users can chat with FELLO and receive ethically filtered responses
- Consent prompts appear inline; approvals/denials processed correctly
- Transparency panel reveals agent reasoning and audit trail
- All Phase 1 deliverables per `phase_manifest.md` satisfied
- Application deployed and operational in production environment

### 4. Commit & Finalize
- Commit all source code, configuration, and documentation to repository
- Tag release version
- Generate final build report summarizing:
  - Features implemented
  - Tests passed
  - Deployment URL and status
  - Known limitations or future work

---

## Phase List

| Phase | Name                     | Focus                                      |
|-------|--------------------------|--------------------------------------------|
| 0     | Backend Scaffold         | Multi-agent architecture, API, ethics core |
| 1     | Frontend & Ship          | Chat UI, consent controls, deploy          |

---

## Boot Script

**boot_script_required:** `false`

No custom boot script needed. Application launches via standard framework commands (e.g., `python app.py` for backend, `npm start` for frontend, or equivalent per tech stack).

---

## Build Directives

**CRITICAL REQUIREMENTS:**
- The builder MUST complete BOTH Phase 0 and Phase 1 in sequence.
- Ethical filtering (OutputGate) must be functional and enforced before ANY agent output reaches users.
- Consent tier system must be operational and respected by all agents.
- Digital shadow (persistent user model) must persist across sessions.
- Chat interface must be the primary interaction surface; all other UI elements secondary.
- Transparency features (reasoning trace, audit logs) must be accessible on demand.
- All code must be production-quality: tested, documented, and deployable.

**MINI BUILD CONSTRAINTS:**
- Prioritize core functionality over extended features.
- Use minimal viable implementations for sub-agents (can be expanded post-MVP).
- Focus on demonstrating ethical filtering and consent tiers end-to-end.
- Ensure chat + consent approval flow is fully operational.

---

**End of Builder Directive**