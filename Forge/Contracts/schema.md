# OthelloMini – Database Schema Contract

## 1. Conventions

### 1.1 Naming Conventions
- **Tables**: lowercase, plural nouns with underscores (`users`, `agent_activities`, `consent_logs`)
- **Primary keys**: `id` (BIGSERIAL)
- **Foreign keys**: `{referenced_table_singular}_id` (e.g., `user_id`, `conversation_id`)
- **Timestamps**: `created_at`, `updated_at` (TIMESTAMPTZ)
- **Soft deletes**: `deleted_at` (TIMESTAMPTZ, nullable)
- **Boolean fields**: prefix with `is_` or `has_` (e.g., `is_active`, `has_consented`)
- **JSONB fields**: `_data` or `_metadata` suffix (e.g., `trait_data`, `reasoning_metadata`)

### 1.2 Common Columns
All tables include:
- `id BIGSERIAL PRIMARY KEY`
- `created_at TIMESTAMPTZ NOT NULL DEFAULT NOW()`
- `updated_at TIMESTAMPTZ NOT NULL DEFAULT NOW()`

Tables supporting soft deletes additionally include:
- `deleted_at TIMESTAMPTZ`

### 1.3 Data Type Standards
- **Timestamps**: `TIMESTAMPTZ` (timezone-aware)
- **Text**: `TEXT` for unlimited length; `VARCHAR(n)` only when strict limits required
- **JSON**: `JSONB` for indexable, queryable structured data
- **Enums**: Use PostgreSQL `ENUM` types or `VARCHAR` with `CHECK` constraints
- **UUIDs**: `UUID` type where external identifiers needed

### 1.4 Indexing Strategy
- Primary keys automatically indexed
- Foreign keys indexed for join performance
- Add composite indexes for common query patterns
- JSONB fields use GIN indexes for efficient querying
- Unique constraints where business logic requires uniqueness

---

## 2. Schema Definition

### 2.1 Users

```sql
CREATE TABLE users (
    id BIGSERIAL PRIMARY KEY,
    external_id UUID UNIQUE NOT NULL DEFAULT gen_random_uuid(),
    email VARCHAR(255) UNIQUE NOT NULL,
    username VARCHAR(100) UNIQUE,
    password_hash TEXT NOT NULL,
    full_name VARCHAR(255),
    timezone VARCHAR(50) DEFAULT 'UTC',
    is_active BOOLEAN NOT NULL DEFAULT true,
    created_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    updated_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    deleted_at TIMESTAMPTZ
);

CREATE INDEX idx_users_email ON users(email) WHERE deleted_at IS NULL;
CREATE INDEX idx_users_external_id ON users(external_id);
CREATE INDEX idx_users_active ON users(is_active) WHERE deleted_at IS NULL;
```

### 2.2 Consent Tiers

```sql
CREATE TYPE consent_tier_level AS ENUM ('passive', 'suggestive', 'active', 'autonomous');

CREATE TABLE consent_tiers (
    id BIGSERIAL PRIMARY KEY,
    user_id BIGINT NOT NULL REFERENCES users(id) ON DELETE CASCADE,
    tier_level consent_tier_level NOT NULL DEFAULT 'passive',
    scope VARCHAR(100) NOT NULL, -- 'global', 'scheduling', 'communication', 'health', etc.
    is_active BOOLEAN NOT NULL DEFAULT true,
    settings_data JSONB, -- tier-specific configuration
    created_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    updated_at TIMESTAMPTZ NOT NULL DEFAULT NOW()
);

CREATE INDEX idx_consent_tiers_user ON consent_tiers(user_id);
CREATE INDEX idx_consent_tiers_scope ON consent_tiers(scope);
CREATE INDEX idx_consent_tiers_active ON consent_tiers(user_id, is_active);
CREATE UNIQUE INDEX idx_consent_tiers_user_scope ON consent_tiers(user_id, scope) WHERE is_active = true;
```

### 2.3 Conversations

```sql
CREATE TABLE conversations (
    id BIGSERIAL PRIMARY KEY,
    user_id BIGINT NOT NULL REFERENCES users(id) ON DELETE CASCADE,
    title VARCHAR(500),
    is_archived BOOLEAN NOT NULL DEFAULT false,
    metadata JSONB, -- context, tags, summary
    created_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    updated_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    deleted_at TIMESTAMPTZ
);

CREATE INDEX idx_conversations_user ON conversations(user_id) WHERE deleted_at IS NULL;
CREATE INDEX idx_conversations_archived ON conversations(user_id, is_archived) WHERE deleted_at IS NULL;
CREATE INDEX idx_conversations_created ON conversations(created_at);
```

### 2.4 Messages

```sql
CREATE TYPE message_role AS ENUM ('user', 'assistant', 'system');

CREATE TABLE messages (
    id BIGSERIAL PRIMARY KEY,
    conversation_id BIGINT NOT NULL REFERENCES conversations(id) ON DELETE CASCADE,
    user_id BIGINT NOT NULL REFERENCES users(id) ON DELETE CASCADE,
    role message_role NOT NULL,
    content TEXT NOT NULL,
    agent_name VARCHAR(100), -- which agent generated this (FELLO, RealityAgent, etc.)
    reasoning_trace JSONB, -- sub-agent thoughts, chain-of-reasoning
    ethical_validation JSONB, -- Othello validation metadata
    token_count INTEGER,
    created_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    updated_at TIMESTAMPTZ NOT NULL DEFAULT NOW()
);

CREATE INDEX idx_messages_conversation ON messages(conversation_id, created_at);
CREATE INDEX idx_messages_user ON messages(user_id);
CREATE INDEX idx_messages_agent ON messages(agent_name) WHERE agent_name IS NOT NULL;
CREATE INDEX idx_messages_role ON messages(role);
```

### 2.5 Psychological Profiles

```sql
CREATE TABLE psychological_profiles (
    id BIGSERIAL PRIMARY KEY,
    user_id BIGINT NOT NULL REFERENCES users(id) ON DELETE CASCADE,
    trait_data JSONB NOT NULL DEFAULT '{}', -- personality traits, preferences
    behavior_patterns JSONB NOT NULL DEFAULT '{}', -- observed behaviors, habits
    aspirations JSONB NOT NULL DEFAULT '{}', -- goals, desires, long-term plans
    mood_history JSONB NOT NULL DEFAULT '[]', -- timestamped mood entries
    confidence_scores JSONB NOT NULL DEFAULT '{}', -- confidence per tracked dimension
    last_analyzed_at TIMESTAMPTZ,
    created_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    updated_at TIMESTAMPTZ NOT NULL DEFAULT NOW()
);

CREATE UNIQUE INDEX idx_psychological_profiles_user ON psychological_profiles(user_id);
CREATE INDEX idx_psychological_profiles_analyzed ON psychological_profiles(last_analyzed_at);
CREATE INDEX idx_psychological_profiles_traits ON psychological_profiles USING GIN(trait_data);
CREATE INDEX idx_psychological_profiles_behaviors ON psychological_profiles USING GIN(behavior_patterns);
```

### 2.6 Agent Activities

```sql
CREATE TYPE agent_activity_type AS ENUM ('observation', 'analysis', 'suggestion', 'intervention', 'validation');
CREATE TYPE agent_activity_status AS ENUM ('proposed', 'pending_consent', 'approved', 'rejected', 'executed', 'failed');

CREATE TABLE agent_activities (
    id BIGSERIAL PRIMARY KEY,
    user_id BIGINT NOT NULL REFERENCES users(id) ON DELETE CASCADE,
    agent_name VARCHAR(100) NOT NULL, -- FELLO, RealityAgent, Othello, sub-agents
    activity_type agent_activity_type NOT NULL,
    status agent_activity_status NOT NULL DEFAULT 'proposed',
    title VARCHAR(500) NOT NULL,
    description TEXT,
    reasoning TEXT, -- why the agent proposed this
    consent_required BOOLEAN NOT NULL DEFAULT false,
    consent_tier_required consent_tier_level, -- minimum tier needed
    payload JSONB, -- action-specific data
    result JSONB, -- execution outcome
    executed_at TIMESTAMPTZ,
    created_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    updated_at TIMESTAMPTZ NOT NULL DEFAULT NOW()
);

CREATE INDEX idx_agent_activities_user ON agent_activities(user_id, created_at DESC);
CREATE INDEX idx_agent_activities_agent ON agent_activities(agent_name);
CREATE INDEX idx_agent_activities_status ON agent_activities(status);
CREATE INDEX idx_agent_activities_type ON agent_activities(activity_type);
CREATE INDEX idx_agent_activities_consent ON agent_activities(user_id, consent_required) WHERE consent_required = true;
```

### 2.7 Consent Logs

```sql
CREATE TYPE consent_action AS ENUM ('approved', 'denied', 'deferred', 'tier_changed', 'settings_updated');

CREATE TABLE consent_logs (
    id BIGSERIAL PRIMARY KEY,
    user_id BIGINT NOT NULL REFERENCES users(id) ON DELETE CASCADE,
    agent_activity_id BIGINT REFERENCES agent_activities(id) ON DELETE SET NULL,
    consent_tier_id BIGINT REFERENCES consent_tiers(id) ON DELETE SET NULL,
    action consent_action NOT NULL,
    scope VARCHAR(100), -- what area this consent applies to
    previous_value TEXT, -- for tier changes
    new_value TEXT, -- for tier changes
    reason TEXT, -- user-provided reason (optional)
    metadata JSONB, -- additional context
    created_at TIMESTAMPTZ NOT NULL DEFAULT NOW()
);

CREATE INDEX idx_consent_logs_user ON consent_logs(user_id, created_at DESC);
CREATE INDEX idx_consent_logs_activity ON consent_logs(agent_activity_id);
CREATE INDEX idx_consent_logs_action ON consent_logs(action);
CREATE INDEX idx_consent_logs_scope ON consent_logs(scope);
```

### 2.8 Interventions

```sql
CREATE TYPE intervention_category AS ENUM ('routine', 'scheduling', 'goal_coaching', 'health_nudge', 'communication', 'other');
CREATE TYPE intervention_status AS ENUM ('scheduled', 'delivered', 'acknowledged', 'completed', 'dismissed', 'failed');

CREATE TABLE interventions (
    id BIGSERIAL PRIMARY KEY,
    user_id BIGINT NOT NULL REFERENCES users(id) ON DELETE CASCADE,
    agent_activity_id BIGINT REFERENCES agent_activities(id) ON DELETE SET NULL,
    category intervention_category NOT NULL,
    status intervention_status NOT NULL DEFAULT 'scheduled',
    title VARCHAR(500) NOT NULL,
    message TEXT NOT NULL,
    scheduled_for TIMESTAMPTZ NOT NULL,
    delivered_at TIMESTAMPTZ,
    acknowledged_at TIMESTAMPTZ,
    completed_at TIMESTAMPTZ,
    user_feedback TEXT,
    effectiveness_score INTEGER CHECK (effectiveness_score BETWEEN 1 AND 5),
    metadata JSONB,
    created_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    updated_at TIMESTAMPTZ NOT NULL DEFAULT NOW()
);

CREATE INDEX idx_interventions_user ON interventions(user_id, scheduled_for);
CREATE INDEX idx_interventions_status ON interventions(status);
CREATE INDEX idx_interventions_category ON interventions(category);
CREATE INDEX idx_interventions_scheduled ON interventions(scheduled_for) WHERE status = 'scheduled';
CREATE INDEX idx_interventions_activity ON interventions(agent_activity_id);
```

### 2.9 Ethical Validations

```sql
CREATE TYPE validation_result AS ENUM ('passed', 'flagged', 'blocked', 'escalated');

CREATE TABLE ethical_validations (
    id BIGSERIAL PRIMARY KEY,
    user_id BIGINT NOT NULL REFERENCES users(id) ON DELETE CASCADE,
    message_id BIGINT REFERENCES messages(id) ON DELETE CASCADE,
    agent_activity_id BIGINT REFERENCES agent_activities(id) ON DELETE CASCADE,
    validator VARCHAR(100) NOT NULL DEFAULT 'Othello', -- which component validated
    result validation_result NOT NULL,
    rules_applied TEXT[], -- list of ethical rules checked
    concerns TEXT[], -- identified ethical concerns
    reasoning TEXT, -- why this result was reached
    override_allowed BOOLEAN NOT NULL DEFAULT false,
    overridden_by_user BOOLEAN NOT NULL DEFAULT false,
    metadata JSONB,
    created_at TIMESTAMPTZ NOT NULL DEFAULT NOW()
);

CREATE INDEX idx_ethical_validations_user ON ethical_validations(user_id, created_at DESC);
CREATE INDEX idx_ethical_validations_message ON ethical_validations(message_id);
CREATE INDEX idx_ethical_validations_activity ON ethical_validations(agent_activity_id);
CREATE INDEX idx_ethical_validations_result ON ethical_validations(result);
CREATE INDEX idx_ethical_validations_flagged ON ethical_validations(user_id, result) WHERE result IN ('flagged', 'blocked');
```

### 2.10 User Preferences

```sql
CREATE TABLE user_preferences (
    id BIGSERIAL PRIMARY KEY,
    user_id BIGINT NOT NULL REFERENCES users(id) ON DELETE CASCADE,
    preference_key VARCHAR(100) NOT NULL,
    preference_value TEXT,
    value_type VARCHAR(20) NOT NULL DEFAULT 'string', -- string, number, boolean, json
    category VARCHAR(50), -- ui, notifications, agents, privacy
    is_sensitive BOOLEAN NOT NULL DEFAULT false,
    created_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    updated_at TIMESTAMPTZ NOT NULL DEFAULT NOW()
);

CREATE UNIQUE INDEX idx_user_preferences_key ON user_preferences(user_id, preference_key);
CREATE INDEX idx_user_preferences_category ON user_preferences(user_id, category);
```

### 2.11 Session Logs

```sql
CREATE TABLE session_logs (
    id BIGSERIAL PRIMARY KEY,
    user_id BIGINT NOT NULL REFERENCES users(id) ON DELETE CASCADE,
    session_token VARCHAR(255) UNIQUE NOT NULL,
    ip_address INET,
    user_agent TEXT,
    login_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    last_activity_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    logout_at TIMESTAMPTZ,
    is_active BOOLEAN NOT NULL DEFAULT true
);

CREATE INDEX idx_session_logs_user ON session_logs(user_id, is_active);
CREATE INDEX idx_session_logs_token ON session_logs(session_token) WHERE is_active = true;
CREATE INDEX idx_session_logs_activity ON session_logs(last_activity_at) WHERE is_active = true;
```

---

## 3. Triggers and Functions

### 3.1 Updated At Trigger

```sql
CREATE OR REPLACE FUNCTION update_updated_at_column()
RETURNS TRIGGER AS $$
BEGIN
    NEW.updated_at = NOW();
    RETURN NEW;
END;
$$ LANGUAGE plpgsql;

-- Apply to all tables with updated_at
CREATE TRIGGER update_users_updated_at BEFORE UPDATE ON users
    FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();

CREATE TRIGGER update_consent_tiers_updated_at BEFORE UPDATE ON consent_tiers
    FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();

CREATE TRIGGER update_conversations_updated_at BEFORE UPDATE ON conversations
    FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();

CREATE TRIGGER update_messages_updated_at BEFORE UPDATE ON messages
    FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();

CREATE TRIGGER update_psychological_profiles_updated_at BEFORE UPDATE ON psychological_profiles
    FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();

CREATE TRIGGER update_agent_activities_updated_at BEFORE UPDATE ON agent_activities
    FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();

CREATE TRIGGER update_interventions_updated_at BEFORE UPDATE ON interventions
    FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();

CREATE TRIGGER update_user_preferences_updated_at BEFORE UPDATE ON user_preferences
    FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();
```

---

## 4. Initial Data

### 4.1 Default Consent Scopes

Default consent scopes to be initialized per user upon registration:

- `global` – overall system consent tier
- `scheduling` – calendar and time management interventions
- `communication` – message sending, email drafting
- `health` – wellness nudges, habit tracking
- `finance` – spending insights, budget suggestions
- `social` – social interaction coaching
- `goal_coaching` – aspirations and achievement tracking

---

## 5. Notes

### 5.1 JSONB Schema Examples

**trait_data** (psychological_profiles):
```json
{
  "openness": 0.75,
  "conscientiousness": 0.82,
  "extraversion": 0.45,
  "agreeableness": 0.68,
  "neuroticism": 0.35,
  "preferences": {
    "communication_style": "direct",
    "feedback_tolerance": "high"
  }
}
```

**behavior_patterns** (psychological_profiles):
```json
{
  "sleep_schedule": {
    "avg_bedtime": "23:00",
    "avg_wake": "07:00",
    "consistency_score": 0.78
  },
  "work_patterns": {
    "peak_productivity_hours": [9, 10, 11, 14, 15],
    "break_frequency": "every_90_min"
  }
}
```

**reasoning_trace** (messages):
```json
{
  "sub_agents": [
    {
      "name": "TraitAnalyzer",
      "input": "User expressed frustration about deadline",
      "output": "Elevated stress markers, conscientiousness strain",
      "confidence": 0.82
    },
    {
      "name": "ContextBuilder",
      "input": "Recent conversation history",
      "output": "Work pressure theme across 3 recent sessions",
      "confidence": 0.91
    }
  ],
  "synthesis": "Recommend schedule adjustment with high confidence"
}
```

**ethical_validation** (messages):
```json
{
  "othello_version": "1.0.2",
  "checks_performed": ["consent_tier", "harm_potential", "privacy_boundary"],
  "results": {
    "consent_tier": "pass",
    "harm_potential": "pass",
    "privacy_boundary": "pass"
  },
  "overall": "cleared",
  "timestamp": "2025-01-15T10:30:00Z"
}
```

### 5.2 Performance Considerations

- **JSONB indexes**: GIN indexes on psychological_profiles enable fast querying of nested trait and behavior data
- **Partitioning**: For high-volume deployments, consider partitioning `messages`, `agent_activities`, and `consent_logs` by time range (monthly or quarterly)
- **Archival strategy**: Implement soft deletes for conversations/messages with periodic archival to cold storage for inactive data older than 12 months
- **Connection pooling**: Use PgBouncer or similar for connection management in production

### 5.3 Security Considerations

- All sensitive fields (password_hash, trait_data, behavior_patterns) should be encrypted at rest
- Implement row-level security (RLS) policies to ensure users can only access their own data
- Audit critical operations via consent_logs and ethical_validations
- Regularly rotate session tokens and expire inactive sessions

### 5.4 Migration Strategy

- Use a migration tool (e.g., Alembic, Flyway) to version and manage schema changes
- Test all migrations on staging environment with production-like data volumes
- Create rollback scripts for each migration
- Maintain backwards compatibility for at least one version during rolling deployments