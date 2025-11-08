// ==========================================
// CLIENT TYPES
// ==========================================

export interface Client {
  id: string;
  organization_id: string;
  first_name: string;
  last_name: string;
  email: string;
  phone?: string;
  date_of_birth?: string;
  street_address?: string;
  city?: string;
  state?: string;
  zip_code?: string;
  status: 'lead' | 'onboarding' | 'active' | 'inactive' | 'churned';
  tags: string[];
  notes?: string;
  onboarding_completed_at?: string;
  created_at: string;
  updated_at: string;
}

export interface ClientCreateInput {
  first_name: string;
  last_name: string;
  email: string;
  phone?: string;
  ssn?: string;
  date_of_birth?: string;
  street_address?: string;
  city?: string;
  state?: string;
  zip_code?: string;
  tags?: string[];
  notes?: string;
}

// ==========================================
// DISPUTE TYPES
// ==========================================

export interface Dispute {
  id: string;
  organization_id: string;
  client_id: string;
  dispute_type: string;
  bureau: 'equifax' | 'experian' | 'transunion' | 'all';
  account_name?: string;
  dispute_reason: string;
  status: 'draft' | 'pending' | 'sent' | 'investigating' | 'resolved' | 'failed';
  round_number: number;
  letter_template_id?: string;
  letter_content?: string;
  generated_at?: string;
  sent_at?: string;
  result?: string;
  result_date?: string;
  result_notes?: string;
  created_at: string;
  updated_at: string;
}

export interface DisputeCreateInput {
  client_id: string;
  dispute_type: string;
  bureau: 'equifax' | 'experian' | 'transunion' | 'all';
  account_name?: string;
  account_number?: string;
  dispute_reason: string;
  letter_template_id?: string;
}

// ==========================================
// LETTER TYPES
// ==========================================

export interface Letter {
  id: string;
  organization_id: string;
  client_id: string;
  dispute_id?: string;
  letter_type: 'dispute' | 'followup' | 'confirmation' | 'general';
  template_id?: string;
  status: 'draft' | 'queued' | 'sent' | 'delivered' | 'failed' | 'returned';
  recipient_name: string;
  mail_provider?: string;
  tracking_number?: string;
  sent_at?: string;
  delivered_at?: string;
  expected_delivery_date?: string;
  cost_cents?: number;
  created_at: string;
}

// ==========================================
// AGREEMENT TYPES
// ==========================================

export interface Agreement {
  id: string;
  organization_id: string;
  client_id: string;
  agreement_type: 'service_agreement' | 'authorization' | 'terms_of_service';
  agreement_version: string;
  status: 'pending' | 'signed' | 'expired' | 'terminated';
  signed_at?: string;
  signed_by_name?: string;
  signed_by_email?: string;
  created_at: string;
}

// ==========================================
// BILLING TYPES
// ==========================================

export interface Subscription {
  id: string;
  organization_id: string;
  stripe_subscription_id?: string;
  plan_name: string;
  plan_price_cents: number;
  billing_interval: 'month' | 'year';
  status: 'active' | 'past_due' | 'canceled' | 'incomplete';
  current_period_start?: string;
  current_period_end?: string;
  cancel_at_period_end: boolean;
  created_at: string;
}

export interface Invoice {
  id: string;
  organization_id: string;
  stripe_invoice_id?: string;
  amount_cents: number;
  amount_paid_cents: number;
  currency: string;
  status: 'draft' | 'open' | 'paid' | 'uncollectible' | 'void';
  invoice_date: string;
  due_date?: string;
  paid_at?: string;
  description?: string;
  invoice_pdf_url?: string;
  attempt_count: number;
  created_at: string;
}

// ==========================================
// ORGANIZATION TYPES
// ==========================================

export interface Organization {
  id: string;
  name: string;
  slug: string;
  subscription_tier: string;
  subscription_status: string;
  created_at: string;
}

// ==========================================
// USER TYPES
// ==========================================

export interface User {
  id: string;
  clerk_user_id: string;
  email: string;
  full_name?: string;
  role: 'admin' | 'member' | 'viewer';
  organization_id?: string;
  created_at: string;
}

// ==========================================
// API RESPONSE TYPES
// ==========================================

export interface PaginatedResponse<T> {
  items: T[];
  total: number;
  page: number;
  page_size: number;
  total_pages: number;
}

export interface ApiError {
  success: false;
  error: string;
  message: string;
  details?: any;
}

export interface ApiSuccess {
  success: true;
  message?: string;
}


// ==========================================
// EMAIL NOTIFICATION TYPES
// ==========================================

export interface EmailTemplate {
  id: string;
  organization_id: string;
  name: string;
  template_key: string;
  description?: string;
  category: 'client_communication' | 'internal_notification' | 'billing';
  subject: string;
  body_html: string;
  body_text?: string;
  variables: string[];
  is_active: boolean;
  is_system_template: boolean;
  created_at: string;
  updated_at: string;
}

export interface EmailTemplateCreateInput {
  name: string;
  template_key: string;
  description?: string;
  category: 'client_communication' | 'internal_notification' | 'billing';
  subject: string;
  body_html: string;
  body_text?: string;
  is_active?: boolean;
}

export interface EmailTemplateUpdateInput {
  name?: string;
  description?: string;
  subject?: string;
  body_html?: string;
  body_text?: string;
  is_active?: boolean;
}

export interface EmailLog {
  id: string;
  organization_id: string;
  client_id?: string;
  dispute_id?: string;
  template_id?: string;
  template_key?: string;
  to_email: string;
  to_name?: string;
  subject: string;
  status: 'queued' | 'sending' | 'sent' | 'delivered' | 'bounced' | 'failed' | 'opened' | 'clicked';
  provider?: string;
  provider_message_id?: string;
  queued_at: string;
  sent_at?: string;
  delivered_at?: string;
  opened_at?: string;
  bounce_reason?: string;
  error_message?: string;
  open_count: number;
  click_count: number;
  created_at: string;
}

export interface EmailAnalytics {
  total_sent: number;
  total_delivered: number;
  total_bounced: number;
  total_opened: number;
  total_clicked: number;
  delivery_rate: number;
  open_rate: number;
  click_rate: number;
  bounce_rate: number;
}

export interface NotificationSettings {
  id: string;
  organization_id: string;
  client_onboarding_enabled: boolean;
  client_dispute_updates_enabled: boolean;
  client_payment_reminders_enabled: boolean;
  client_monthly_reports_enabled: boolean;
  admin_new_client_alert: boolean;
  admin_payment_failed_alert: boolean;
  admin_dispute_milestone_alert: boolean;
  admin_system_alerts_enabled: boolean;
  admin_emails: string[];
  daily_digest_enabled: boolean;
  max_emails_per_day: number;
  max_emails_per_client_per_day: number;
  created_at: string;
  updated_at: string;
}

export interface NotificationSettingsUpdate {
  client_onboarding_enabled?: boolean;
  client_dispute_updates_enabled?: boolean;
  client_payment_reminders_enabled?: boolean;
  client_monthly_reports_enabled?: boolean;
  admin_new_client_alert?: boolean;
  admin_payment_failed_alert?: boolean;
  admin_dispute_milestone_alert?: boolean;
  admin_system_alerts_enabled?: boolean;
  admin_emails?: string[];
  daily_digest_enabled?: boolean;
  max_emails_per_day?: number;
  max_emails_per_client_per_day?: number;
}

export interface EmailSendRequest {
  template_key: string;
  to_email: string;
  to_name?: string;
  variables?: Record<string, any>;
  cc_emails?: string[];
  bcc_emails?: string[];
  client_id?: string;
  dispute_id?: string;
}
