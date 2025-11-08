-- CreditBeast Email Notification System Schema
-- Extension to existing database for comprehensive email functionality

-- ==========================================
-- EMAIL TEMPLATES TABLE
-- ==========================================

CREATE TABLE email_templates (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    organization_id UUID NOT NULL REFERENCES organizations(id) ON DELETE CASCADE,
    
    -- Template Details
    name VARCHAR(255) NOT NULL,
    template_key VARCHAR(100) NOT NULL, -- onboarding_welcome, dispute_created, payment_reminder, etc.
    description TEXT,
    category VARCHAR(50) NOT NULL, -- client_communication, internal_notification, billing
    
    -- Email Content
    subject VARCHAR(500) NOT NULL,
    body_html TEXT NOT NULL,
    body_text TEXT,
    
    -- Template Variables
    variables JSONB DEFAULT '[]', -- Array of variable names like ["client_name", "dispute_count"]
    
    -- Status
    is_active BOOLEAN DEFAULT true,
    is_system_template BOOLEAN DEFAULT false, -- System templates cannot be deleted
    
    -- Metadata
    created_by_user_id UUID REFERENCES users(id),
    last_modified_by_user_id UUID REFERENCES users(id),
    
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    
    CONSTRAINT unique_template_key_per_org UNIQUE(organization_id, template_key)
);

-- ==========================================
-- EMAIL LOGS TABLE
-- ==========================================

CREATE TABLE email_logs (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    organization_id UUID NOT NULL REFERENCES organizations(id) ON DELETE CASCADE,
    
    -- Reference to source entities
    client_id UUID REFERENCES clients(id) ON DELETE SET NULL,
    dispute_id UUID REFERENCES disputes(id) ON DELETE SET NULL,
    invoice_id UUID REFERENCES billing_invoices(id) ON DELETE SET NULL,
    
    -- Email Details
    template_id UUID REFERENCES email_templates(id) ON DELETE SET NULL,
    template_key VARCHAR(100),
    
    -- Recipients
    to_email VARCHAR(255) NOT NULL,
    to_name VARCHAR(255),
    cc_emails TEXT[], -- Array of CC email addresses
    bcc_emails TEXT[], -- Array of BCC email addresses
    
    -- Content
    subject VARCHAR(500) NOT NULL,
    body_html TEXT,
    body_text TEXT,
    
    -- Delivery Information
    provider VARCHAR(50), -- cloudmail, smtp, sendgrid, etc.
    provider_message_id VARCHAR(255),
    
    -- Status Tracking
    status VARCHAR(50) DEFAULT 'queued', -- queued, sending, sent, delivered, bounced, failed, opened, clicked
    
    -- Delivery Timestamps
    queued_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    sent_at TIMESTAMP WITH TIME ZONE,
    delivered_at TIMESTAMP WITH TIME ZONE,
    bounced_at TIMESTAMP WITH TIME ZONE,
    opened_at TIMESTAMP WITH TIME ZONE,
    first_clicked_at TIMESTAMP WITH TIME ZONE,
    
    -- Bounce/Error Information
    bounce_reason TEXT,
    error_message TEXT,
    
    -- Engagement Metrics
    open_count INTEGER DEFAULT 0,
    click_count INTEGER DEFAULT 0,
    
    -- Metadata
    metadata JSONB DEFAULT '{}', -- Additional tracking data
    
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

-- ==========================================
-- NOTIFICATION SETTINGS TABLE
-- ==========================================

CREATE TABLE notification_settings (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    organization_id UUID NOT NULL REFERENCES organizations(id) ON DELETE CASCADE,
    
    -- Client Communication Settings
    client_onboarding_enabled BOOLEAN DEFAULT true,
    client_dispute_updates_enabled BOOLEAN DEFAULT true,
    client_payment_reminders_enabled BOOLEAN DEFAULT true,
    client_monthly_reports_enabled BOOLEAN DEFAULT false,
    
    -- Internal Admin Notifications
    admin_new_client_alert BOOLEAN DEFAULT true,
    admin_payment_failed_alert BOOLEAN DEFAULT true,
    admin_dispute_milestone_alert BOOLEAN DEFAULT true,
    admin_system_alerts_enabled BOOLEAN DEFAULT true,
    
    -- Admin Email Recipients
    admin_emails TEXT[] DEFAULT '{}', -- Array of admin email addresses
    
    -- Notification Frequency
    daily_digest_enabled BOOLEAN DEFAULT false,
    daily_digest_time TIME DEFAULT '09:00:00',
    
    -- Email Rate Limiting
    max_emails_per_day INTEGER DEFAULT 100,
    max_emails_per_client_per_day INTEGER DEFAULT 5,
    
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    
    CONSTRAINT one_setting_per_org UNIQUE(organization_id)
);

-- ==========================================
-- EMAIL QUEUE TABLE (for asynchronous processing)
-- ==========================================

CREATE TABLE email_queue (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    organization_id UUID NOT NULL REFERENCES organizations(id) ON DELETE CASCADE,
    
    -- Email Details
    template_key VARCHAR(100),
    to_email VARCHAR(255) NOT NULL,
    to_name VARCHAR(255),
    subject VARCHAR(500) NOT NULL,
    body_html TEXT NOT NULL,
    body_text TEXT,
    
    -- Template Variables (for retry)
    template_variables JSONB DEFAULT '{}',
    
    -- References
    client_id UUID REFERENCES clients(id) ON DELETE CASCADE,
    dispute_id UUID REFERENCES disputes(id) ON DELETE CASCADE,
    
    -- Processing Status
    status VARCHAR(50) DEFAULT 'pending', -- pending, processing, sent, failed
    priority INTEGER DEFAULT 5, -- 1-10, lower is higher priority
    
    -- Retry Logic
    attempt_count INTEGER DEFAULT 0,
    max_attempts INTEGER DEFAULT 3,
    next_retry_at TIMESTAMP WITH TIME ZONE,
    last_error TEXT,
    
    -- Scheduling
    scheduled_for TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    processed_at TIMESTAMP WITH TIME ZONE,
    
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

-- ==========================================
-- INDEXES
-- ==========================================

CREATE INDEX idx_email_templates_org ON email_templates(organization_id);
CREATE INDEX idx_email_templates_key ON email_templates(template_key);
CREATE INDEX idx_email_templates_active ON email_templates(is_active);

CREATE INDEX idx_email_logs_org ON email_logs(organization_id);
CREATE INDEX idx_email_logs_client ON email_logs(client_id);
CREATE INDEX idx_email_logs_status ON email_logs(status);
CREATE INDEX idx_email_logs_created ON email_logs(created_at DESC);
CREATE INDEX idx_email_logs_to_email ON email_logs(to_email);

CREATE INDEX idx_notification_settings_org ON notification_settings(organization_id);

CREATE INDEX idx_email_queue_status ON email_queue(status);
CREATE INDEX idx_email_queue_scheduled ON email_queue(scheduled_for);
CREATE INDEX idx_email_queue_org ON email_queue(organization_id);

-- ==========================================
-- ROW LEVEL SECURITY POLICIES
-- ==========================================

ALTER TABLE email_templates ENABLE ROW LEVEL SECURITY;
ALTER TABLE email_logs ENABLE ROW LEVEL SECURITY;
ALTER TABLE notification_settings ENABLE ROW LEVEL SECURITY;
ALTER TABLE email_queue ENABLE ROW LEVEL SECURITY;

CREATE POLICY email_template_org_isolation ON email_templates
    FOR ALL
    USING (organization_id = current_setting('app.current_org_id', true)::uuid);

CREATE POLICY email_logs_org_isolation ON email_logs
    FOR ALL
    USING (organization_id = current_setting('app.current_org_id', true)::uuid);

CREATE POLICY notification_settings_org_isolation ON notification_settings
    FOR ALL
    USING (organization_id = current_setting('app.current_org_id', true)::uuid);

CREATE POLICY email_queue_org_isolation ON email_queue
    FOR ALL
    USING (organization_id = current_setting('app.current_org_id', true)::uuid);

-- ==========================================
-- TRIGGERS
-- ==========================================

CREATE TRIGGER update_email_templates_updated_at BEFORE UPDATE ON email_templates
    FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();

CREATE TRIGGER update_email_logs_updated_at BEFORE UPDATE ON email_logs
    FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();

CREATE TRIGGER update_notification_settings_updated_at BEFORE UPDATE ON notification_settings
    FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();

CREATE TRIGGER update_email_queue_updated_at BEFORE UPDATE ON email_queue
    FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();

-- ==========================================
-- DEFAULT EMAIL TEMPLATES
-- ==========================================

-- Insert default templates for the demo organization
INSERT INTO email_templates (organization_id, name, template_key, description, category, subject, body_html, body_text, variables, is_system_template)
VALUES 
    -- Client Onboarding
    ('00000000-0000-0000-0000-000000000001', 
     'Welcome Onboarding Email', 
     'onboarding_welcome',
     'Sent when a new client completes onboarding',
     'client_communication',
     'Welcome to CreditBeast - Let''s Start Your Credit Repair Journey',
     '<h2>Welcome {{client_name}}!</h2><p>We''re excited to help you improve your credit score. Our team will review your credit report and start disputing inaccurate items within 24 hours.</p><p>You can track your progress anytime in your client portal.</p>',
     'Welcome {{client_name}}! We''re excited to help you improve your credit score.',
     '["client_name", "organization_name"]',
     true),
    
    -- Dispute Created
    ('00000000-0000-0000-0000-000000000001',
     'Dispute Created Notification',
     'dispute_created',
     'Sent when a new dispute is created for a client',
     'client_communication',
     'New Dispute Filed on Your Behalf',
     '<h2>Good News, {{client_name}}!</h2><p>We''ve filed a new dispute with {{bureau}} regarding {{account_name}}.</p><p>Dispute Type: {{dispute_type}}</p><p>We''ll notify you as soon as we receive a response, typically within 30-45 days.</p>',
     'Good news, {{client_name}}! We''ve filed a new dispute with {{bureau}}.',
     '["client_name", "bureau", "account_name", "dispute_type"]',
     true),
    
    -- Payment Reminder
    ('00000000-0000-0000-0000-000000000001',
     'Payment Reminder',
     'payment_reminder',
     'Sent when payment is due',
     'billing',
     'Payment Reminder - Invoice Due',
     '<h2>Payment Reminder</h2><p>Hi {{client_name}},</p><p>This is a friendly reminder that your payment of ${{amount}} is due on {{due_date}}.</p><p>Please make your payment to avoid service interruption.</p>',
     'Payment reminder: ${{amount}} due on {{due_date}}',
     '["client_name", "amount", "due_date"]',
     true),
    
    -- Internal: New Client Alert
    ('00000000-0000-0000-0000-000000000001',
     'Admin New Client Alert',
     'admin_new_client',
     'Internal notification when a new client signs up',
     'internal_notification',
     'New Client Signup: {{client_name}}',
     '<h3>New Client Alert</h3><p>{{client_name}} ({{client_email}}) just completed onboarding.</p><p>Status: {{status}}</p><p>Review the client in your dashboard.</p>',
     'New client: {{client_name}} ({{client_email}})',
     '["client_name", "client_email", "status"]',
     true),
    
    -- Internal: Payment Failed
    ('00000000-0000-0000-0000-000000000001',
     'Admin Payment Failed Alert',
     'admin_payment_failed',
     'Internal notification when payment fails',
     'internal_notification',
     'Payment Failed: {{client_name}}',
     '<h3>Payment Failed Alert</h3><p>Payment failed for {{client_name}}.</p><p>Amount: ${{amount}}</p><p>Reason: {{reason}}</p>',
     'Payment failed for {{client_name}} - ${{amount}}',
     '["client_name", "amount", "reason"]',
     true);

-- Insert default notification settings for demo organization
INSERT INTO notification_settings (organization_id)
VALUES ('00000000-0000-0000-0000-000000000001');
