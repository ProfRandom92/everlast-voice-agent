-- Checkpoints table for LangGraph state persistence
-- Thread-ID = Caller Phone Number for session continuity

CREATE TABLE IF NOT EXISTS checkpoints (
    thread_id TEXT PRIMARY KEY,
    state JSONB NOT NULL,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),

    -- Metadata
    phone_number TEXT NOT NULL,
    conversation_id TEXT,

    -- Expiration (optional - auto-cleanup old sessions)
    expires_at TIMESTAMP WITH TIME ZONE DEFAULT (NOW() + INTERVAL '24 hours')
);

-- Index for quick lookups by phone number
CREATE INDEX IF NOT EXISTS idx_checkpoints_phone ON checkpoints(phone_number);

-- Index for expiration cleanup
CREATE INDEX IF NOT EXISTS idx_checkpoints_expires ON checkpoints(expires_at);

-- Trigger to update updated_at
CREATE OR REPLACE FUNCTION update_checkpoint_timestamp()
RETURNS TRIGGER AS $$
BEGIN
    NEW.updated_at = NOW();
    RETURN NEW;
END;
$$ LANGUAGE plpgsql;

CREATE TRIGGER update_checkpoint_timestamp
    BEFORE UPDATE ON checkpoints
    FOR EACH ROW
    EXECUTE FUNCTION update_checkpoint_timestamp();

-- RLS Policies
ALTER TABLE checkpoints ENABLE ROW LEVEL SECURITY;

CREATE POLICY checkpoints_select ON checkpoints
    FOR SELECT TO authenticated USING (true);

CREATE POLICY checkpoints_insert ON checkpoints
    FOR INSERT TO authenticated WITH CHECK (true);

CREATE POLICY checkpoints_update ON checkpoints
    FOR UPDATE TO authenticated USING (true);

CREATE POLICY checkpoints_delete ON checkpoints
    FOR DELETE TO authenticated USING (true);

-- Service role bypass
CREATE POLICY service_role_all ON checkpoints
    FOR ALL TO service_role USING (true) WITH CHECK (true);

-- Cleanup function for expired checkpoints
CREATE OR REPLACE FUNCTION cleanup_expired_checkpoints()
RETURNS INTEGER AS $$
DECLARE
    deleted_count INTEGER;
BEGIN
    DELETE FROM checkpoints
    WHERE expires_at < NOW();

    GET DIAGNOSTICS deleted_count = ROW_COUNT;
    RETURN deleted_count;
END;
$$ LANGUAGE plpgsql;

-- View for active sessions (last 24 hours)
CREATE OR REPLACE VIEW v_active_sessions AS
SELECT
    thread_id,
    phone_number,
    conversation_id,
    updated_at,
    state->>'current_agent' as current_agent,
    state->'bant'->>'need' as need_level,
    state->'caller_sentiment'->>'current_sentiment' as sentiment
FROM checkpoints
WHERE updated_at > NOW() - INTERVAL '24 hours'
ORDER BY updated_at DESC;
