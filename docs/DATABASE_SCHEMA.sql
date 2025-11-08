-- CreditBeast Database Schema
-- Designed for Supabase with Row Level Security (RLS) and PII encryption

-- Enable required extensions
CREATE EXTENSION IF NOT EXISTS "uuid-ossp";
CREATE EXTENSION IF NOT EXISTS "pgcrypto";

-- ==========================================
-- CORE TABLES
-- ==========================================

-- Organizations (Multi-tenancy foundation)
CREATE TABLE organizations (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    name VARCHAR(255) NOT NULL,
    slug VARCHAR(100) UNIQUE NOT NULL,
    owner_user_id UUID NOT NULL,
    subscription_tier VARCHAR(50) DEFAULT 'free',
    subscription_status VARCHAR(50) DEFAULT 'active',
    stripe_customer_id VARCHAR(255),
    settings JSONB DEFAULT '{}',
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

-- Users (Authentication)
CREATE TABLE users (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    clerk_user_id VARCHAR(255) UNIQUE NOT NULL,
    email VARCHAR(255) NOT NULL,
    full_name VARCHAR(255),
    role VARCHAR(50) DEFAULT 'member',
    organization_id UUID REFERENCES organizations(id) ON DELETE CASCADE,
    last_login_at TIMESTAMP WITH TIME ZONE,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

-- Clients (Core business entity)
CREATE TABLE clients (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    organization_id UUID NOT NULL REFERENCES organizations(id) ON DELETE CASCADE,
    created_by_user_id UUID REFERENCES users(id),
    
    -- Personal Information (PII - encrypted)
    first_name VARCHAR(255) NOT NULL,
    last_name VARCHAR(255) NOT NULL,
    email VARCHAR(255) NOT NULL,
    phone VARCHAR(50),
    ssn_encrypted TEXT, -- Encrypted SSN
    date_of_birth DATE,
    
    -- Address Information (PII - encrypted)
    street_address TEXT,
    city VARCHAR(100),
    state VARCHAR(50),
    zip_code VARCHAR(20),
    
    -- Status and Metadata
    status VARCHAR(50) DEFAULT 'lead', -- lead, onboarding, active, inactive, churned
    onboarding_completed_at TIMESTAMP WITH TIME ZONE,
    tags VARCHAR(255)[],
    notes TEXT,
    
    -- Credit Information
    credit_report_data JSONB,
    dispute_items JSONB,
    
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    
    CONSTRAINT unique_client_email_per_org UNIQUE(organization_id, email)
);

-- Agreements (Legal compliance)
CREATE TABLE agreements (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    organization_id UUID NOT NULL REFERENCES organizations(id) ON DELETE CASCADE,
    client_id UUID NOT NULL REFERENCES clients(id) ON DELETE CASCADE,
    
    agreement_type VARCHAR(50) NOT NULL, -- service_agreement, authorization, terms_of_service
    agreement_version VARCHAR(20) NOT NULL,
    content TEXT NOT NULL,
    
    signed_at TIMESTAMP WITH TIME ZONE,
    signature_data JSONB, -- IP address, user agent, etc.
    signed_by_name VARCHAR(255),
    signed_by_email VARCHAR(255),
    
    status VARCHAR(50) DEFAULT 'pending', -- pending, signed, expired, terminated
    
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

-- Disputes (Primary business value)
CREATE TABLE disputes (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    organization_id UUID NOT NULL REFERENCES organizations(id) ON DELETE CASCADE,
    client_id UUID NOT NULL REFERENCES clients(id) ON DELETE CASCADE,
    created_by_user_id UUID REFERENCES users(id),
    
    -- Dispute Details
    dispute_type VARCHAR(50) NOT NULL, -- inquiry, charge_off, late_payment, collection, etc.
    bureau VARCHAR(50) NOT NULL, -- equifax, experian, transunion, all
    account_name VARCHAR(255),
    account_number_encrypted TEXT, -- Encrypted account number
    dispute_reason TEXT NOT NULL,
    
    -- Status Tracking
    status VARCHAR(50) DEFAULT 'draft', -- draft, pending, sent, investigating, resolved, failed
    round_number INTEGER DEFAULT 1,
    
    -- Letter Information
    letter_template_id VARCHAR(100),
    letter_content TEXT,
    generated_at TIMESTAMP WITH TIME ZONE,
    sent_at TIMESTAMP WITH TIME ZONE,
    
    -- Results
    result VARCHAR(50), -- deleted, updated, verified, pending
    result_date DATE,
    result_notes TEXT,
    
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

-- Letters (Automated mailing)
CREATE TABLE letters (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    organization_id UUID NOT NULL REFERENCES organizations(id) ON DELETE CASCADE,
    client_id UUID NOT NULL REFERENCES clients(id) ON DELETE CASCADE,
    dispute_id UUID REFERENCES disputes(id) ON DELETE SET NULL,
    
    -- Letter Details
    letter_type VARCHAR(50) NOT NULL, -- dispute, followup, confirmation, general
    template_id VARCHAR(100),
    content TEXT NOT NULL,
    
    -- Recipient Information
    recipient_name VARCHAR(255) NOT NULL,
    recipient_address TEXT NOT NULL,
    
    -- Mailing Status
    status VARCHAR(50) DEFAULT 'draft', -- draft, queued, sent, delivered, failed, returned
    mail_provider VARCHAR(50), -- cloudmail, lob, etc.
    mail_provider_id VARCHAR(255),
    tracking_number VARCHAR(255),
    
    -- Delivery Tracking
    queued_at TIMESTAMP WITH TIME ZONE,
    sent_at TIMESTAMP WITH TIME ZONE,
    delivered_at TIMESTAMP WITH TIME ZONE,
    expected_delivery_date DATE,
    
    cost_cents INTEGER,
    
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

-- Billing (Revenue engine)
CREATE TABLE billing_subscriptions (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    organization_id UUID NOT NULL REFERENCES organizations(id) ON DELETE CASCADE,
    
    stripe_subscription_id VARCHAR(255) UNIQUE,
    stripe_customer_id VARCHAR(255) NOT NULL,
    
    plan_name VARCHAR(100) NOT NULL,
    plan_price_cents INTEGER NOT NULL,
    billing_interval VARCHAR(20) NOT NULL, -- month, year
    
    status VARCHAR(50) DEFAULT 'active', -- active, past_due, canceled, incomplete
    current_period_start TIMESTAMP WITH TIME ZONE,
    current_period_end TIMESTAMP WITH TIME ZONE,
    cancel_at_period_end BOOLEAN DEFAULT FALSE,
    canceled_at TIMESTAMP WITH TIME ZONE,
    
    trial_start TIMESTAMP WITH TIME ZONE,
    trial_end TIMESTAMP WITH TIME ZONE,
    
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

-- Payment Invoices
CREATE TABLE billing_invoices (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    organization_id UUID NOT NULL REFERENCES organizations(id) ON DELETE CASCADE,
    subscription_id UUID REFERENCES billing_subscriptions(id) ON DELETE SET NULL,
    
    stripe_invoice_id VARCHAR(255) UNIQUE,
    stripe_payment_intent_id VARCHAR(255),
    
    amount_cents INTEGER NOT NULL,
    amount_paid_cents INTEGER DEFAULT 0,
    currency VARCHAR(3) DEFAULT 'usd',
    
    status VARCHAR(50) NOT NULL, -- draft, open, paid, uncollectible, void
    
    invoice_date DATE NOT NULL,
    due_date DATE,
    paid_at TIMESTAMP WITH TIME ZONE,
    
    description TEXT,
    invoice_pdf_url TEXT,
    
    -- Dunning management
    attempt_count INTEGER DEFAULT 0,
    next_retry_at TIMESTAMP WITH TIME ZONE,
    
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

-- Audit Logs (Compliance requirement)
CREATE TABLE audit_logs (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    organization_id UUID REFERENCES organizations(id) ON DELETE CASCADE,
    user_id UUID REFERENCES users(id) ON DELETE SET NULL,
    
    -- Action Details
    action VARCHAR(100) NOT NULL, -- create, update, delete, view, export
    resource_type VARCHAR(100) NOT NULL, -- client, dispute, letter, etc.
    resource_id UUID,
    
    -- Change Tracking
    changes JSONB, -- Before/after values
    metadata JSONB, -- IP address, user agent, etc.
    
    -- Compliance
    compliance_category VARCHAR(100), -- data_access, data_modification, export, etc.
    
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

-- ==========================================
-- INDEXES FOR PERFORMANCE
-- ==========================================

CREATE INDEX idx_users_org ON users(organization_id);
CREATE INDEX idx_users_clerk ON users(clerk_user_id);

CREATE INDEX idx_clients_org ON clients(organization_id);
CREATE INDEX idx_clients_status ON clients(status);
CREATE INDEX idx_clients_email ON clients(email);

CREATE INDEX idx_agreements_client ON agreements(client_id);
CREATE INDEX idx_agreements_org ON agreements(organization_id);

CREATE INDEX idx_disputes_client ON disputes(client_id);
CREATE INDEX idx_disputes_org ON disputes(organization_id);
CREATE INDEX idx_disputes_status ON disputes(status);

CREATE INDEX idx_letters_client ON letters(client_id);
CREATE INDEX idx_letters_org ON letters(organization_id);
CREATE INDEX idx_letters_status ON letters(status);

CREATE INDEX idx_billing_subs_org ON billing_subscriptions(organization_id);
CREATE INDEX idx_billing_subs_stripe ON billing_subscriptions(stripe_subscription_id);

CREATE INDEX idx_billing_inv_org ON billing_invoices(organization_id);
CREATE INDEX idx_billing_inv_status ON billing_invoices(status);

CREATE INDEX idx_audit_org ON audit_logs(organization_id);
CREATE INDEX idx_audit_resource ON audit_logs(resource_type, resource_id);
CREATE INDEX idx_audit_created ON audit_logs(created_at);

-- ==========================================
-- ROW LEVEL SECURITY (RLS) POLICIES
-- ==========================================

-- Enable RLS on all tables
ALTER TABLE organizations ENABLE ROW LEVEL SECURITY;
ALTER TABLE users ENABLE ROW LEVEL SECURITY;
ALTER TABLE clients ENABLE ROW LEVEL SECURITY;
ALTER TABLE agreements ENABLE ROW LEVEL SECURITY;
ALTER TABLE disputes ENABLE ROW LEVEL SECURITY;
ALTER TABLE letters ENABLE ROW LEVEL SECURITY;
ALTER TABLE billing_subscriptions ENABLE ROW LEVEL SECURITY;
ALTER TABLE billing_invoices ENABLE ROW LEVEL SECURITY;
ALTER TABLE audit_logs ENABLE ROW LEVEL SECURITY;

-- Organizations: Users can only access their own organization
CREATE POLICY org_isolation ON organizations
    FOR ALL
    USING (id = current_setting('app.current_org_id', true)::uuid);

-- Users: Can only see users in their organization
CREATE POLICY user_org_isolation ON users
    FOR ALL
    USING (organization_id = current_setting('app.current_org_id', true)::uuid);

-- Clients: Organization-scoped access
CREATE POLICY client_org_isolation ON clients
    FOR ALL
    USING (organization_id = current_setting('app.current_org_id', true)::uuid);

-- Agreements: Organization-scoped access
CREATE POLICY agreement_org_isolation ON agreements
    FOR ALL
    USING (organization_id = current_setting('app.current_org_id', true)::uuid);

-- Disputes: Organization-scoped access
CREATE POLICY dispute_org_isolation ON disputes
    FOR ALL
    USING (organization_id = current_setting('app.current_org_id', true)::uuid);

-- Letters: Organization-scoped access
CREATE POLICY letter_org_isolation ON letters
    FOR ALL
    USING (organization_id = current_setting('app.current_org_id', true)::uuid);

-- Billing Subscriptions: Organization-scoped access
CREATE POLICY billing_sub_org_isolation ON billing_subscriptions
    FOR ALL
    USING (organization_id = current_setting('app.current_org_id', true)::uuid);

-- Billing Invoices: Organization-scoped access
CREATE POLICY billing_inv_org_isolation ON billing_invoices
    FOR ALL
    USING (organization_id = current_setting('app.current_org_id', true)::uuid);

-- Audit Logs: Read-only, organization-scoped
CREATE POLICY audit_org_isolation ON audit_logs
    FOR SELECT
    USING (organization_id = current_setting('app.current_org_id', true)::uuid);

-- ==========================================
-- FUNCTIONS AND TRIGGERS
-- ==========================================

-- Function to update updated_at timestamp
CREATE OR REPLACE FUNCTION update_updated_at_column()
RETURNS TRIGGER AS $$
BEGIN
    NEW.updated_at = NOW();
    RETURN NEW;
END;
$$ LANGUAGE plpgsql;

-- Apply updated_at trigger to all relevant tables
CREATE TRIGGER update_organizations_updated_at BEFORE UPDATE ON organizations
    FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();

CREATE TRIGGER update_users_updated_at BEFORE UPDATE ON users
    FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();

CREATE TRIGGER update_clients_updated_at BEFORE UPDATE ON clients
    FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();

CREATE TRIGGER update_agreements_updated_at BEFORE UPDATE ON agreements
    FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();

CREATE TRIGGER update_disputes_updated_at BEFORE UPDATE ON disputes
    FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();

CREATE TRIGGER update_letters_updated_at BEFORE UPDATE ON letters
    FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();

CREATE TRIGGER update_billing_subs_updated_at BEFORE UPDATE ON billing_subscriptions
    FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();

CREATE TRIGGER update_billing_inv_updated_at BEFORE UPDATE ON billing_invoices
    FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();

-- Function to create audit log entry
CREATE OR REPLACE FUNCTION create_audit_log()
RETURNS TRIGGER AS $$
BEGIN
    INSERT INTO audit_logs (
        organization_id,
        user_id,
        action,
        resource_type,
        resource_id,
        changes,
        metadata
    ) VALUES (
        COALESCE(NEW.organization_id, OLD.organization_id),
        current_setting('app.current_user_id', true)::uuid,
        TG_OP,
        TG_TABLE_NAME,
        COALESCE(NEW.id, OLD.id),
        jsonb_build_object('old', to_jsonb(OLD), 'new', to_jsonb(NEW)),
        jsonb_build_object('timestamp', NOW())
    );
    RETURN NEW;
END;
$$ LANGUAGE plpgsql;

-- Apply audit triggers to sensitive tables
CREATE TRIGGER audit_clients AFTER INSERT OR UPDATE OR DELETE ON clients
    FOR EACH ROW EXECUTE FUNCTION create_audit_log();

CREATE TRIGGER audit_disputes AFTER INSERT OR UPDATE OR DELETE ON disputes
    FOR EACH ROW EXECUTE FUNCTION create_audit_log();

CREATE TRIGGER audit_agreements AFTER INSERT OR UPDATE OR DELETE ON agreements
    FOR EACH ROW EXECUTE FUNCTION create_audit_log();

-- ==========================================
-- ENCRYPTION FUNCTIONS
-- ==========================================

-- Function to encrypt PII data
CREATE OR REPLACE FUNCTION encrypt_pii(data TEXT, key TEXT)
RETURNS TEXT AS $$
BEGIN
    RETURN encode(pgp_sym_encrypt(data, key), 'base64');
END;
$$ LANGUAGE plpgsql SECURITY DEFINER;

-- Function to decrypt PII data
CREATE OR REPLACE FUNCTION decrypt_pii(encrypted_data TEXT, key TEXT)
RETURNS TEXT AS $$
BEGIN
    RETURN pgp_sym_decrypt(decode(encrypted_data, 'base64'), key);
EXCEPTION
    WHEN OTHERS THEN
        RETURN NULL;
END;
$$ LANGUAGE plpgsql SECURITY DEFINER;

-- ==========================================
-- SAMPLE SEED DATA (Development Only)
-- ==========================================

-- Insert sample organization
INSERT INTO organizations (id, name, slug, owner_user_id, subscription_tier)
VALUES 
    ('00000000-0000-0000-0000-000000000001', 'Demo Credit Repair Co', 'demo-credit-repair', '00000000-0000-0000-0000-000000000001', 'professional');

-- Insert sample user
INSERT INTO users (id, clerk_user_id, email, full_name, role, organization_id)
VALUES 
    ('00000000-0000-0000-0000-000000000001', 'user_demo123', 'admin@democreditrepair.com', 'Demo Admin', 'admin', '00000000-0000-0000-0000-000000000001');

-- Note: Do not insert PII sample data in production
