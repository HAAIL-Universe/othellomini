# OthelloMini Database Schema

## Conventions

**Naming Standards**
- Table names: lowercase snake_case, plural nouns (e.g., `user_profiles`, `conversations`, `suggestions`)
- Column names: lowercase snake_case
- Primary keys: `id` (SERIAL or UUID)
- Foreign keys: `{referenced_table_singular}_id` (e.g., `user_profile_id`)
- Timestamps: `created_at`, `updated_at` (TIMESTAMP WITH TIME ZONE)
- Soft delete: `deleted_at` (TIMESTAMP WITH TIME ZONE, NULL by default)

**Common Columns**
All tables include:
- `id`: Primary key (SERIAL)
- `created_at`: Record creation timestamp (TIMESTAMP WITH TIME ZONE, NOT NULL, DEFAULT NOW())
- `updated_at`: Record last modification timestamp (TIMESTAMP WITH TIME ZONE, NOT NULL, DEFAULT NOW())

**Data Types**
- Text content: TEXT (no arbitrary length limits)
- Enums: VARCHAR with CHECK constraints
- JSON data: JSONB (for flexible structured data like traits, preferences)
- Timestamps: TIMESTAMP WITH TIME ZONE (for proper timezone handling)
- Boolean flags: BOOLEAN (NOT NULL with explicit defaults)

**Indexes**
- Primary keys automatically indexed
- Foreign keys indexed for join performance
- Timestamp columns indexed for time-based queries
- Unique constraints on natural keys where applicable

---

## Schema Definition

### user_profiles

Stores persistent user model including psychological traits, preferences, behavioral patterns, and consent tier settings. Single-user scope (one row expected for MVP).

```sql
CREATE TABLE user_profiles (
    id SERIAL PRIMARY KEY,
    user_id VARCHAR(255) NOT NULL UNIQUE,
    display_name VARCHAR(255),
    consent_tier VARCHAR(50) NOT NULL DEFAULT 'Passive',
    traits JSONB DEFAULT '{}'::JSONB,
    preferences JSONB DEFAULT '{}'::JSONB,
    behavioral_patterns JSONB DEFAULT '{}'::JSONB,
    context_summary TEXT,
    profile_version INTEGER NOT NULL DEFAULT 1,
    created_at TIMESTAMP WITH TIME ZONE NOT NULL DEFAULT NOW(),
    updated_at TIMESTAMP WITH TIME ZONE NOT NULL DEFAULT NOW(),
    
    CONSTRAINT consent_tier_check CHECK (
        consent_tier IN ('Passive', 'Suggestive', 'Active', 'Autonomous')
    )
);

CREATE INDEX idx_user_profiles_user_id ON user_profiles(user_id);
CREATE INDEX idx_user_profiles_updated_at ON user_profiles(updated_at DESC);

COMMENT ON TABLE user_profiles IS 'Persistent user psychological model and consent settings';
COMMENT ON COLUMN user_profiles.user_id IS 'Unique identifier for user (fixed for single-user MVP)';
COMMENT ON COLUMN user_profiles.consent_tier IS 'Current consent level: Passive/Suggestive/Active/Autonomous';
COMMENT ON COLUMN user_profiles.traits IS 'JSON object storing psychological traits (e.g., {"openness": 0.8, "conscientiousness": 0.7})';
COMMENT ON COLUMN user_profiles.preferences IS 'JSON object storing user preferences (e.g., {"communication_style": "direct", "priority_areas": ["health", "productivity"]})';
COMMENT ON COLUMN user_profiles.behavioral_patterns IS 'JSON object storing observed patterns (e.g., {"morning_routine": "exercise", "work_hours": "9-17"})';
COMMENT ON COLUMN user_profiles.context_summary IS 'Narrative summary of current user context for AI reference';
COMMENT ON COLUMN user_profiles.profile_version IS 'Incremented on each update for auditability';
```

---

### conversations

Stores chat message log with user/assistant roles. Provides conversation history for context and audit trail.

```sql
CREATE TABLE conversations (
    id SERIAL PRIMARY KEY,
    user_profile_id INTEGER NOT NULL,
    role VARCHAR(50) NOT NULL,
    content TEXT NOT NULL,
    metadata JSONB DEFAULT '{}'::JSONB,
    created_at TIMESTAMP WITH TIME ZONE NOT NULL DEFAULT NOW(),
    updated_at TIMESTAMP WITH TIME ZONE NOT NULL DEFAULT NOW(),
    
    CONSTRAINT role_check CHECK (role IN ('user', 'assistant', 'system')),
    CONSTRAINT fk_conversations_user_profile 
        FOREIGN KEY (user_profile_id) 
        REFERENCES user_profiles(id) 
        ON DELETE CASCADE
);

CREATE INDEX idx_conversations_user_profile_id ON conversations(user_profile_id);
CREATE INDEX idx_conversations_created_at ON conversations(created_at DESC);
CREATE INDEX idx_conversations_role ON conversations(role);

COMMENT ON TABLE conversations IS 'Chat message history for user interactions';
COMMENT ON COLUMN conversations.role IS 'Message author: user (human), assistant (AI), system (internal)';
COMMENT ON COLUMN conversations.content IS 'Full message text';
COMMENT ON COLUMN conversations.metadata IS 'Optional JSON metadata (e.g., token count, model version, processing time)';
```

---

### suggestions

Stores AI-generated action suggestions with ethical gating metadata. Tracks pending, approved, and denied suggestions with full audit trail.

```sql
CREATE TABLE suggestions (
    id SERIAL PRIMARY KEY,
    user_profile_id INTEGER NOT NULL,
    conversation_id INTEGER,
    suggestion_text TEXT NOT NULL,
    consent_tier VARCHAR(50) NOT NULL,
    ethical_reasoning TEXT NOT NULL,
    status VARCHAR(50) NOT NULL DEFAULT 'pending',
    action_type VARCHAR(100),
    action_payload JSONB DEFAULT '{}'::JSONB,
    user_response TEXT,
    responded_at TIMESTAMP WITH TIME ZONE,
    created_at TIMESTAMP WITH TIME ZONE NOT NULL DEFAULT NOW(),
    updated_at TIMESTAMP WITH TIME ZONE NOT NULL DEFAULT NOW(),
    
    CONSTRAINT consent_tier_check CHECK (
        consent_tier IN ('Passive', 'Suggestive', 'Active', 'Autonomous')
    ),
    CONSTRAINT status_check CHECK (
        status IN ('pending', 'approved', 'denied', 'expired')
    ),
    CONSTRAINT fk_suggestions_user_profile 
        FOREIGN KEY (user_profile_id) 
        REFERENCES user_profiles(id) 
        ON DELETE CASCADE,
    CONSTRAINT fk_suggestions_conversation 
        FOREIGN KEY (conversation_id) 
        REFERENCES conversations(id) 
        ON DELETE SET NULL
);

CREATE INDEX idx_suggestions_user_profile_id ON suggestions(user_profile_id);
CREATE INDEX idx_suggestions_status ON suggestions(status);
CREATE INDEX idx_suggestions_consent_tier ON suggestions(consent_tier);
CREATE INDEX idx_suggestions_created_at ON suggestions(created_at DESC);
CREATE INDEX idx_suggestions_conversation_id ON suggestions(conversation_id);

COMMENT ON TABLE suggestions IS 'AI-generated action suggestions with ethical gating and user responses';
COMMENT ON COLUMN suggestions.suggestion_text IS 'Human-readable suggestion presented to user';
COMMENT ON COLUMN suggestions.consent_tier IS 'Othello-assigned consent tier for this suggestion';
COMMENT ON COLUMN suggestions.ethical_reasoning IS 'Othello gatekeeper justification for consent tier assignment';
COMMENT ON COLUMN suggestions.status IS 'Current state: pending (awaiting user), approved, denied, expired';
COMMENT ON COLUMN suggestions.action_type IS 'Optional: type of action suggested (e.g., "schedule_reminder", "send_email")';
COMMENT ON COLUMN suggestions.action_payload IS 'Optional: structured data for action execution (e.g., {"time": "09:00", "task": "morning exercise"})';
COMMENT ON COLUMN suggestions.user_response IS 'Optional: user feedback/comment when approving or denying';
COMMENT ON COLUMN suggestions.responded_at IS 'Timestamp when user approved/denied suggestion';
COMMENT ON COLUMN suggestions.conversation_id IS 'Optional: link to conversation message that generated this suggestion';
```

---

## Initialization Data

For MVP single-user setup, seed with default user profile:

```sql
INSERT INTO user_profiles (
    user_id, 
    display_name, 
    consent_tier, 
    traits, 
    preferences, 
    context_summary
) VALUES (
    'default_user',
    'User',
    'Suggestive',
    '{"openness": 0.7, "conscientiousness": 0.6, "extraversion": 0.5}'::JSONB,
    '{"communication_style": "conversational", "priority_areas": ["productivity", "wellness"]}'::JSONB,
    'New user exploring AI life companion features.'
)
ON CONFLICT (user_id) DO NOTHING;
```

---

## Migration Notes

**Alembic Integration**
- Initial migration creates all three tables with indexes and constraints
- `updated_at` triggers should be added via SQLAlchemy event listeners or database triggers
- Profile version increment handled in application logic (optimistic locking)

**Performance Considerations**
- JSONB columns indexed with GIN for nested key searches if query patterns require (deferred for MVP)
- Conversation table may grow large: consider partitioning by date in production (out of scope for MVP)
- Suggestions table cleanup job to expire old pending suggestions (application-level cron, not schema)

**Extensibility Hooks**
- `metadata` JSONB columns in conversations allow adding fields without migrations
- `action_payload` JSONB in suggestions supports future action types without schema changes
- Profile `traits`, `preferences`, `behavioral_patterns` are JSONB for flexible user modeling evolution

---

**End of Schema Contract**