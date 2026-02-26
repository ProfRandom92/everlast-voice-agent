-- Everlast Voice Agent - Supabase Database Schema
-- DSGVO-konform, EU-Region (Frankfurt)

-- Enable required extensions
CREATE EXTENSION IF NOT EXISTS "uuid-ossp";
CREATE EXTENSION IF NOT EXISTS "pgcrypto";

-- ============================================================================
-- CALLS TABLE
-- ============================================================================
CREATE TABLE IF NOT EXISTS calls (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    conversation_id TEXT NOT NULL UNIQUE,
    phone_number TEXT NOT NULL,
    vapi_call_id TEXT,

    -- Timestamps
    started_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    ended_at TIMESTAMP WITH TIME ZONE,
    duration_seconds INTEGER,

    -- Media URLs
    recording_url TEXT,
    transcript_url TEXT,

    -- Call metadata
    call_status TEXT CHECK (call_status IN ('in_progress', 'completed', 'failed', 'missed')),

    -- GDPR
    consent_recording BOOLEAN DEFAULT FALSE,
    consent_data_processing BOOLEAN DEFAULT FALSE,
    consent_timestamp TIMESTAMP WITH TIME ZONE,

    -- Created/Updated
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

-- Index for performance
CREATE INDEX idx_calls_phone ON calls(phone_number);
CREATE INDEX idx_calls_started ON calls(started_at DESC);
CREATE INDEX idx_calls_conversation ON calls(conversation_id);

-- ============================================================================
-- LEADS TABLE
-- ============================================================================
CREATE TABLE IF NOT EXISTS leads (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    conversation_id TEXT REFERENCES calls(conversation_id),
    phone_number TEXT NOT NULL,

    -- Company Info
    company_name TEXT,
    company_size TEXT CHECK (company_size IN ('1-10', '11-50', '51-200', '201-500', '500+')),
    industry TEXT,
    website TEXT,

    -- Contact Info
    contact_name TEXT,
    contact_email TEXT,
    contact_phone TEXT,

    -- BANT Qualification
    budget TEXT CHECK (budget IN ('Ja', 'Nein', 'Unklar')),
    authority TEXT CHECK (authority IN ('Entscheider', 'Einfluss', 'Keine Entscheidungsbefugnis')),
    need TEXT CHECK (need IN ('Hoch', 'Mittel', 'Niedrig', 'Kein Bedarf')),
    timeline TEXT CHECK (timeline IN ('Sofort', '1-3 Monate', '3-6 Monate', '> 6 Monate', 'Unklar')),

    -- Current tools
    current_tools TEXT,
    specific_need TEXT,

    -- Scoring
    lead_score TEXT CHECK (lead_score IN ('A', 'B', 'C', 'N')),
    lead_score_reason TEXT,

    -- Status
    status TEXT DEFAULT 'new' CHECK (status IN ('new', 'qualified', 'contacted', 'converted', 'lost', 'archived')),

    -- GDPR consent
    marketing_consent BOOLEAN DEFAULT FALSE,

    -- Created/Updated
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),

    -- Notes
    notes TEXT
);

CREATE INDEX idx_leads_score ON leads(lead_score);
CREATE INDEX idx_leads_status ON leads(status);
CREATE INDEX idx_leads_created ON leads(created_at DESC);
CREATE INDEX idx_leads_phone ON leads(phone_number);

-- ============================================================================
-- APPOINTMENTS TABLE
-- ============================================================================
CREATE TABLE IF NOT EXISTS appointments (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    conversation_id TEXT REFERENCES calls(conversation_id),
    lead_id UUID REFERENCES leads(id),

    -- Appointment details
    appointment_date DATE NOT NULL,
    appointment_time TIME NOT NULL,
    timezone TEXT DEFAULT 'Europe/Berlin',
    duration_minutes INTEGER DEFAULT 30,

    -- Contact info
    name TEXT NOT NULL,
    email TEXT NOT NULL,
    phone TEXT,
    company TEXT,

    -- Appointment type
    event_type TEXT DEFAULT 'demo' CHECK (event_type IN ('demo', 'consultation', 'callback', 'follow_up')),

    -- Calendly integration
    calendly_event_id TEXT,
    calendly_invitee_id TEXT,
    calendly_link TEXT,

    -- Status
    status TEXT DEFAULT 'scheduled' CHECK (status IN ('scheduled', 'confirmed', 'completed', 'cancelled', 'no_show')),

    -- Notes
    notes TEXT,

    -- Timestamps
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

CREATE INDEX idx_appointments_date ON appointments(appointment_date);
CREATE INDEX idx_appointments_status ON appointments(status);
CREATE INDEX idx_appointments_lead ON appointments(lead_id);

-- ============================================================================
-- OBJECTIONS TABLE
-- ============================================================================
CREATE TABLE IF NOT EXISTS objections (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    conversation_id TEXT REFERENCES calls(conversation_id),

    -- Objection details
    objection_type TEXT NOT NULL CHECK (objection_type IN ('Preis', 'Zeit', 'Nicht-Entscheider', 'Bereits-Lösung', 'Kein-Bedarf', 'Misstrauen', 'Andere')),
    objection_text TEXT,
    response_given TEXT,
    outcome TEXT CHECK (outcome IN ('Überwunden', 'Nicht überwunden', 'Offen')),

    -- Timestamp
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

CREATE INDEX idx_objections_type ON objections(objection_type);
CREATE INDEX idx_objections_conversation ON objections(conversation_id);

-- ============================================================================
-- CONSENT LOGS TABLE (GDPR Audit Trail)
-- ============================================================================
CREATE TABLE IF NOT EXISTS consent_logs (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    conversation_id TEXT REFERENCES calls(conversation_id),
    phone_number TEXT NOT NULL,

    -- Consent details
    consent_given BOOLEAN NOT NULL,
    consent_type TEXT NOT NULL CHECK (consent_type IN ('Aufzeichnung', 'Datenverarbeitung', 'Marketing')),
    consent_method TEXT DEFAULT 'verbal' CHECK (consent_method IN ('verbal', 'written', 'digital')),

    -- Context
    ip_address TEXT,
    user_agent TEXT,

    -- Timestamp
    timestamp TIMESTAMP WITH TIME ZONE DEFAULT NOW(),

    -- GDPR: Right to withdraw
    withdrawn_at TIMESTAMP WITH TIME ZONE,
    withdrawal_method TEXT
);

CREATE INDEX idx_consent_phone ON consent_logs(phone_number);
CREATE INDEX idx_consent_timestamp ON consent_logs(timestamp);

-- ============================================================================
-- CALL SUMMARIES TABLE
-- ============================================================================
CREATE TABLE IF NOT EXISTS call_summaries (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    conversation_id TEXT REFERENCES calls(conversation_id) UNIQUE,

    -- Summary
    call_outcome TEXT CHECK (call_outcome IN ('Termin gebucht', 'Rückruf vereinbart', 'Nicht interessiert', 'Nicht erreicht', 'Abgebrochen')),
    lead_score TEXT CHECK (lead_score IN ('A', 'B', 'C', 'N')),
    summary_text TEXT,
    next_steps TEXT,
    notes TEXT,

    -- BANT snapshot
    bant_budget TEXT,
    bant_authority TEXT,
    bant_need TEXT,
    bant_timeline TEXT,

    -- Metrics
    appointment_booked BOOLEAN DEFAULT FALSE,
    objections_count INTEGER DEFAULT 0,

    -- Timestamps
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

CREATE INDEX idx_summaries_score ON call_summaries(lead_score);
CREATE INDEX idx_summaries_outcome ON call_summaries(call_outcome);

-- ============================================================================
-- GDPR DELETION REQUESTS
-- ============================================================================
CREATE TABLE IF NOT EXISTS gdpr_deletion_requests (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    phone_number TEXT NOT NULL,
    email TEXT,

    -- Request details
    request_type TEXT NOT NULL CHECK (request_type IN ('deletion', 'access', 'correction', 'portability')),
    request_method TEXT CHECK (request_method IN ('phone', 'email', 'form', 'letter')),
    request_details TEXT,

    -- Status
    status TEXT DEFAULT 'pending' CHECK (status IN ('pending', 'in_progress', 'completed', 'rejected')),

    -- Processing
    processed_at TIMESTAMP WITH TIME ZONE,
    processed_by TEXT,
    notes TEXT,

    -- Timestamps
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

CREATE INDEX idx_gdpr_status ON gdpr_deletion_requests(status);
CREATE INDEX idx_gdpr_phone ON gdpr_deletion_requests(phone_number);

-- ============================================================================
-- KPI AGGREGATIONS (Materialized View for Dashboard)
-- ============================================================================
CREATE MATERIALIZED VIEW IF NOT EXISTS kpi_daily_stats AS
SELECT
    DATE_TRUNC('day', created_at) AS date,
    COUNT(*) AS total_calls,
    COUNT(CASE WHEN call_outcome = 'Termin gebucht' THEN 1 END) AS booked_appointments,
    COUNT(CASE WHEN lead_score = 'A' THEN 1 END) AS score_a_count,
    COUNT(CASE WHEN lead_score = 'B' THEN 1 END) AS score_b_count,
    COUNT(CASE WHEN lead_score = 'C' THEN 1 END) AS score_c_count,
    AVG(EXTRACT(EPOCH FROM (ended_at - started_at))) AS avg_duration_seconds
FROM call_summaries cs
JOIN calls c ON cs.conversation_id = c.conversation_id
GROUP BY DATE_TRUNC('day', created_at);

CREATE UNIQUE INDEX idx_kpi_daily ON kpi_daily_stats(date);

-- Refresh function
CREATE OR REPLACE FUNCTION refresh_kpi_stats()
RETURNS void AS $$
BEGIN
    REFRESH MATERIALIZED VIEW CONCURRENTLY kpi_daily_stats;
END;
$$ LANGUAGE plpgsql;

-- ============================================================================
-- ROW LEVEL SECURITY POLICIES
-- ============================================================================

-- Enable RLS on all tables
ALTER TABLE calls ENABLE ROW LEVEL SECURITY;
ALTER TABLE leads ENABLE ROW LEVEL SECURITY;
ALTER TABLE appointments ENABLE ROW LEVEL SECURITY;
ALTER TABLE objections ENABLE ROW LEVEL SECURITY;
ALTER TABLE consent_logs ENABLE ROW LEVEL SECURITY;
ALTER TABLE call_summaries ENABLE ROW LEVEL SECURITY;

-- Create policies for authenticated users
CREATE POLICY calls_select_policy ON calls
    FOR SELECT USING (auth.role() = 'authenticated');

CREATE POLICY calls_insert_policy ON calls
    FOR INSERT WITH CHECK (auth.role() = 'authenticated');

CREATE POLICY calls_update_policy ON calls
    FOR UPDATE USING (auth.role() = 'authenticated');

CREATE POLICY leads_select_policy ON leads
    FOR SELECT USING (auth.role() = 'authenticated');

CREATE POLICY leads_insert_policy ON leads
    FOR INSERT WITH CHECK (auth.role() = 'authenticated');

CREATE POLICY leads_update_policy ON leads
    FOR UPDATE USING (auth.role() = 'authenticated');

CREATE POLICY appointments_select_policy ON appointments
    FOR SELECT USING (auth.role() = 'authenticated');

CREATE POLICY appointments_insert_policy ON appointments
    FOR INSERT WITH CHECK (auth.role() = 'authenticated');

CREATE POLICY appointments_update_policy ON appointments
    FOR UPDATE USING (auth.role() = 'authenticated');

-- Service role bypass (for backend API)
CREATE POLICY service_role_policy ON calls
    FOR ALL USING (auth.role() = 'service_role');

-- ============================================================================
-- TRIGGERS
-- ============================================================================

-- Update timestamp trigger
CREATE OR REPLACE FUNCTION update_updated_at_column()
RETURNS TRIGGER AS $$
BEGIN
    NEW.updated_at = NOW();
    RETURN NEW;
END;
$$ language 'plpgsql';

-- Apply to all tables
CREATE TRIGGER update_calls_updated_at BEFORE UPDATE ON calls
    FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();

CREATE TRIGGER update_leads_updated_at BEFORE UPDATE ON leads
    FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();

CREATE TRIGGER update_appointments_updated_at BEFORE UPDATE ON appointments
    FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();

CREATE TRIGGER update_gdpr_updated_at BEFORE UPDATE ON gdpr_deletion_requests
    FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();

-- ============================================================================
-- DASHBOARD VIEWS
-- ============================================================================

-- View: Recent high-quality leads
CREATE OR REPLACE VIEW v_hot_leads AS
SELECT
    l.*,
    c.started_at as call_date,
    cs.summary_text
FROM leads l
JOIN calls c ON l.conversation_id = c.conversation_id
LEFT JOIN call_summaries cs ON l.conversation_id = cs.conversation_id
WHERE l.lead_score IN ('A', 'B')
AND l.status = 'new'
ORDER BY c.started_at DESC;

-- View: Today's appointments
CREATE OR REPLACE VIEW v_today_appointments AS
SELECT
    a.*,
    l.lead_score,
    l.budget,
    l.need
FROM appointments a
LEFT JOIN leads l ON a.lead_id = l.id
WHERE a.appointment_date = CURRENT_DATE
ORDER BY a.appointment_time;

-- View: Objection analytics
CREATE OR REPLACE VIEW v_objection_analytics AS
SELECT
    objection_type,
    outcome,
    COUNT(*) as count,
    ROUND(COUNT(*) FILTER (WHERE outcome = 'Überwunden') * 100.0 / COUNT(*), 2) as overcome_rate
FROM objections
GROUP BY objection_type, outcome;

-- ============================================================================
-- INITIAL DATA (Optional)
-- ============================================================================

-- Add comment for documentation
COMMENT ON TABLE calls IS 'Voice call records from Vapi integration';
COMMENT ON TABLE leads IS 'Qualified B2B leads with BANT criteria';
COMMENT ON TABLE appointments IS 'Scheduled demo appointments via Calendly';
COMMENT ON TABLE objections IS 'Recorded objections during sales calls';
COMMENT ON TABLE consent_logs IS 'GDPR consent audit trail';
COMMENT ON TABLE call_summaries IS 'AI-generated call summaries and scoring';
