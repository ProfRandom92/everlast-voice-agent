-- Additional RLS Policies for Everlast Voice Agent
-- DSGVO-compliant data access controls

-- ============================================================================
-- SERVICE ROLE BYPASS POLICIES
-- ============================================================================

-- Service role can do everything
CREATE POLICY service_role_all_calls ON calls
    FOR ALL TO service_role USING (true) WITH CHECK (true);

CREATE POLICY service_role_all_leads ON leads
    FOR ALL TO service_role USING (true) WITH CHECK (true);

CREATE POLICY service_role_all_appointments ON appointments
    FOR ALL TO service_role USING (true) WITH CHECK (true);

CREATE POLICY service_role_all_objections ON objections
    FOR ALL TO service_role USING (true) WITH CHECK (true);

CREATE POLICY service_role_all_consent ON consent_logs
    FOR ALL TO service_role USING (true) WITH CHECK (true);

CREATE POLICY service_role_all_summaries ON call_summaries
    FOR ALL TO service_role USING (true) WITH CHECK (true);

-- ============================================================================
-- ANONYMOUS POLICIES (Read-only for public stats)
-- ============================================================================

-- Anonymous users can only read aggregated KPIs
CREATE POLICY anonymous_kpi_read ON kpi_daily_stats
    FOR SELECT TO anon USING (true);

-- ============================================================================
-- AUTHENTICATED USER POLICIES
-- ============================================================================

-- Sales team can view and update leads
CREATE POLICY sales_leads_access ON leads
    FOR ALL TO authenticated
    USING (auth.jwt() ->> 'role' = 'sales')
    WITH CHECK (auth.jwt() ->> 'role' = 'sales');

-- Sales can view appointments
CREATE POLICY sales_appointments_access ON appointments
    FOR SELECT TO authenticated
    USING (auth.jwt() ->> 'role' = 'sales');

-- Admins can do everything
CREATE POLICY admin_all_access ON calls
    FOR ALL TO authenticated
    USING (auth.jwt() ->> 'role' = 'admin')
    WITH CHECK (auth.jwt() ->> 'role' = 'admin');

CREATE POLICY admin_all_leads ON leads
    FOR ALL TO authenticated
    USING (auth.jwt() ->> 'role' = 'admin')
    WITH CHECK (auth.jwt() ->> 'role' = 'admin');

CREATE POLICY admin_all_appointments ON appointments
    FOR ALL TO authenticated
    USING (auth.jwt() ->> 'role' = 'admin')
    WITH CHECK (auth.jwt() ->> 'role' = 'admin');

-- ============================================================================
-- GDPR COMPLIANCE FUNCTIONS
-- ============================================================================

-- Function to handle data deletion request
CREATE OR REPLACE FUNCTION handle_data_deletion_request(phone_number TEXT)
RETURNS void AS $$
DECLARE
    affected_rows INTEGER := 0;
BEGIN
    -- Log the deletion request
    INSERT INTO gdpr_deletion_requests (
        phone_number,
        request_type,
        status,
        processed_at,
        processed_by
    ) VALUES (
        phone_number,
        'deletion',
        'completed',
        NOW(),
        'system'
    );

    -- Delete from tables (in correct order for FK constraints)
    DELETE FROM objections WHERE conversation_id IN (
        SELECT conversation_id FROM calls WHERE phone_number = handle_data_deletion_request.phone_number
    );
    GET DIAGNOSTICS affected_rows = ROW_COUNT;
    RAISE NOTICE 'Deleted % objections', affected_rows;

    DELETE FROM call_summaries WHERE conversation_id IN (
        SELECT conversation_id FROM calls WHERE phone_number = handle_data_deletion_request.phone_number
    );

    DELETE FROM appointments WHERE conversation_id IN (
        SELECT conversation_id FROM calls WHERE phone_number = handle_data_deletion_request.phone_number
    );

    DELETE FROM leads WHERE phone_number = handle_data_deletion_request.phone_number;

    DELETE FROM consent_logs WHERE phone_number = handle_data_deletion_request.phone_number;

    DELETE FROM calls WHERE phone_number = handle_data_deletion_request.phone_number;

END;
$$ LANGUAGE plpgsql SECURITY DEFINER;

-- Function to export user data (GDPR portability)
CREATE OR REPLACE FUNCTION export_user_data(phone_number TEXT)
RETURNS JSONB AS $$
DECLARE
    result JSONB;
BEGIN
    SELECT jsonb_build_object(
        'calls', (
            SELECT jsonb_agg(to_jsonb(c.*))
            FROM calls c WHERE c.phone_number = export_user_data.phone_number
        ),
        'leads', (
            SELECT jsonb_agg(to_jsonb(l.*))
            FROM leads l WHERE l.phone_number = export_user_data.phone_number
        ),
        'consent_logs', (
            SELECT jsonb_agg(to_jsonb(cl.*))
            FROM consent_logs cl WHERE cl.phone_number = export_user_data.phone_number
        ),
        'appointments', (
            SELECT jsonb_agg(to_jsonb(a.*))
            FROM appointments a
            JOIN calls c ON a.conversation_id = c.conversation_id
            WHERE c.phone_number = export_user_data.phone_number
        ),
        'objections', (
            SELECT jsonb_agg(to_jsonb(o.*))
            FROM objections o
            JOIN calls c ON o.conversation_id = c.conversation_id
            WHERE c.phone_number = export_user_data.phone_number
        ),
        'export_date', NOW()
    ) INTO result;

    RETURN result;
END;
$$ LANGUAGE plpgsql SECURITY DEFINER;

-- ============================================================================
-- AUDIT LOGGING
-- ============================================================================

-- Table for audit logs
CREATE TABLE IF NOT EXISTS audit_logs (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    table_name TEXT NOT NULL,
    record_id UUID,
    action TEXT NOT NULL CHECK (action IN ('INSERT', 'UPDATE', 'DELETE')),
    old_data JSONB,
    new_data JSONB,
    performed_by TEXT,
    performed_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    ip_address TEXT
);

-- Trigger function for audit logging
CREATE OR REPLACE FUNCTION audit_trigger()
RETURNS TRIGGER AS $$
BEGIN
    IF TG_OP = 'DELETE' THEN
        INSERT INTO audit_logs (table_name, record_id, action, old_data, performed_by)
        VALUES (TG_TABLE_NAME, OLD.id, TG_OP, to_jsonb(OLD), current_user);
        RETURN OLD;
    ELSIF TG_OP = 'UPDATE' THEN
        INSERT INTO audit_logs (table_name, record_id, action, old_data, new_data, performed_by)
        VALUES (TG_TABLE_NAME, NEW.id, TG_OP, to_jsonb(OLD), to_jsonb(NEW), current_user);
        RETURN NEW;
    ELSIF TG_OP = 'INSERT' THEN
        INSERT INTO audit_logs (table_name, record_id, action, new_data, performed_by)
        VALUES (TG_TABLE_NAME, NEW.id, TG_OP, to_jsonb(NEW), current_user);
        RETURN NEW;
    END IF;
    RETURN NULL;
END;
$$ LANGUAGE plpgsql;

-- Apply audit triggers
CREATE TRIGGER audit_calls_trigger AFTER INSERT OR UPDATE OR DELETE ON calls
    FOR EACH ROW EXECUTE FUNCTION audit_trigger();

CREATE TRIGGER audit_leads_trigger AFTER INSERT OR UPDATE OR DELETE ON leads
    FOR EACH ROW EXECUTE FUNCTION audit_trigger();

CREATE TRIGGER audit_appointments_trigger AFTER INSERT OR UPDATE OR DELETE ON appointments
    FOR EACH ROW EXECUTE FUNCTION audit_trigger();

-- ============================================================================
-- DATA RETENTION POLICY (Automatic cleanup after 2 years)
-- ============================================================================

-- Function to clean up old data
CREATE OR REPLACE FUNCTION cleanup_old_data()
RETURNS INTEGER AS $$
DECLARE
    deleted_count INTEGER := 0;
    cutoff_date TIMESTAMP WITH TIME ZONE := NOW() - INTERVAL '2 years';
BEGIN
    -- Only delete if no active business relationship
    DELETE FROM objections WHERE created_at < cutoff_date;
    GET DIAGNOSTICS deleted_count = ROW_COUNT;

    DELETE FROM call_summaries WHERE created_at < cutoff_date;

    DELETE FROM appointments WHERE created_at < cutoff_date;

    DELETE FROM leads
    WHERE created_at < cutoff_date
    AND status NOT IN ('converted', 'contacted');

    DELETE FROM consent_logs WHERE timestamp < cutoff_date;

    -- Mark calls for deletion
    UPDATE calls
    SET recording_url = NULL, transcript_url = NULL
    WHERE started_at < cutoff_date;

    RETURN deleted_count;
END;
$$ LANGUAGE plpgsql SECURITY DEFINER;
