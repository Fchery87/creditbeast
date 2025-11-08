"""
White-label branding models for multi-tenant customization
"""

from pydantic import BaseModel, Field
from typing import Optional, Dict, Any
from datetime import datetime


class OrganizationBranding(BaseModel):
    """Organization branding configuration"""
    id: str
    organization_id: str
    
    # Visual Branding
    primary_color: str = Field(default="#2563eb", description="Primary brand color (hex)")
    secondary_color: str = Field(default="#64748b", description="Secondary brand color (hex)")
    accent_color: str = Field(default="#0ea5e9", description="Accent color (hex)")
    background_color: str = Field(default="#ffffff", description="Background color (hex)")
    
    # Logo and Assets
    logo_url: Optional[str] = None
    favicon_url: Optional[str] = None
    dark_logo_url: Optional[str] = None
    
    # Typography
    font_family: str = Field(default="Inter", description="Primary font family")
    heading_font: Optional[str] = None
    body_font: Optional[str] = None
    
    # Custom CSS
    custom_css: Optional[str] = None
    custom_styles: Dict[str, Any] = Field(default_factory=dict)
    
    # Company Information
    company_name: str = Field(default="CreditBeast")
    company_tagline: Optional[str] = None
    company_description: Optional[str] = None
    support_email: Optional[str] = None
    support_phone: Optional[str] = None
    website_url: Optional[str] = None
    
    # Email Branding
    email_template_enabled: bool = True
    email_header_logo_url: Optional[str] = None
    email_footer_text: Optional[str] = None
    email_primary_color: Optional[str] = None
    
    # Document Branding
    letterhead_enabled: bool = True
    document_header_text: Optional[str] = None
    document_footer_text: Optional[str] = None
    document_logo_url: Optional[str] = None
    
    # Feature Toggles
    show_creditbeast_branding: bool = Field(default=True, description="Show 'Powered by CreditBeast'")
    enable_custom_domain: bool = False
    custom_domain: Optional[str] = None
    
    # Social Links
    facebook_url: Optional[str] = None
    twitter_url: Optional[str] = None
    linkedin_url: Optional[str] = None
    instagram_url: Optional[str] = None
    
    # SEO and Meta
    meta_title: Optional[str] = None
    meta_description: Optional[str] = None
    meta_keywords: Optional[str] = None
    meta_image_url: Optional[str] = None
    
    # Created/Updated timestamps
    created_at: datetime
    updated_at: datetime


class BrandingTemplate(BaseModel):
    """Predefined branding templates"""
    id: str
    name: str
    description: str
    
    # Template Data
    template_data: OrganizationBranding
    
    # Template Metadata
    category: str  # "professional", "modern", "creative", "minimalist"
    preview_image_url: Optional[str] = None
    is_premium: bool = False
    is_active: bool = True
    
    created_at: datetime


class BrandingUpdateRequest(BaseModel):
    """Request model for updating branding"""
    # Visual Updates
    primary_color: Optional[str] = None
    secondary_color: Optional[str] = None
    accent_color: Optional[str] = None
    background_color: Optional[str] = None
    
    # Logo Updates
    logo_url: Optional[str] = None
    favicon_url: Optional[str] = None
    dark_logo_url: Optional[str] = None
    
    # Typography
    font_family: Optional[str] = None
    heading_font: Optional[str] = None
    body_font: Optional[str] = None
    
    # Custom CSS
    custom_css: Optional[str] = None
    custom_styles: Optional[Dict[str, Any]] = None
    
    # Company Info
    company_name: Optional[str] = None
    company_tagline: Optional[str] = None
    company_description: Optional[str] = None
    support_email: Optional[str] = None
    support_phone: Optional[str] = None
    website_url: Optional[str] = None
    
    # Email Settings
    email_header_logo_url: Optional[str] = None
    email_footer_text: Optional[str] = None
    email_primary_color: Optional[str] = None
    
    # Document Settings
    document_header_text: Optional[str] = None
    document_footer_text: Optional[str] = None
    document_logo_url: Optional[str] = None
    
    # Feature Toggles
    show_creditbeast_branding: Optional[bool] = None
    enable_custom_domain: Optional[bool] = None
    custom_domain: Optional[str] = None
    
    # Social Links
    facebook_url: Optional[str] = None
    twitter_url: Optional[str] = None
    linkedin_url: Optional[str] = None
    instagram_url: Optional[str] = None
    
    # SEO
    meta_title: Optional[str] = None
    meta_description: Optional[str] = None
    meta_keywords: Optional[str] = None
    meta_image_url: Optional[str] = None


class BrandingPreviewRequest(BaseModel):
    """Request model for previewing branding changes"""
    branding_updates: BrandingUpdateRequest
    preview_type: str = Field(default="dashboard", description="dashboard|email|document|landing")


class BrandingValidationRequest(BaseModel):
    """Request model for validating branding settings"""
    branding_updates: BrandingUpdateRequest
    validation_type: str = Field(default="colors", description="colors|domains|emails|general")


# Response Models
class BrandingResponse(BaseModel):
    """Response model for branding data"""
    success: bool
    data: OrganizationBranding
    message: Optional[str] = None


class BrandingTemplatesResponse(BaseModel):
    """Response model for branding templates"""
    success: bool
    data: list[BrandingTemplate]
    message: Optional[str] = None


class BrandingValidationResponse(BaseModel):
    """Response model for branding validation"""
    success: bool
    is_valid: bool
    errors: list[str] = []
    warnings: list[str] = []
    suggestions: list[str] = []
    message: Optional[str] = None