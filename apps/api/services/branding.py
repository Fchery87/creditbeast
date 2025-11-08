"""
White-label branding service for multi-tenant customization
"""

import re
import json
from typing import Dict, List, Optional, Any
from datetime import datetime
import logging
from pathlib import Path

from models.branding import (
    OrganizationBranding, BrandingUpdateRequest, BrandingPreviewRequest,
    BrandingValidationRequest, BrandingTemplate, BrandingValidationResponse
)
from services.database import db

logger = logging.getLogger(__name__)


class BrandingService:
    """Service for managing organization branding and white-label features"""

    def __init__(self):
        self.db = None

    async def get_organization_branding(self, org_id: str) -> OrganizationBranding:
        """Get current branding configuration for organization"""
        try:
            # This would query the database in a real implementation
            # For now, return default branding with org_id
            default_branding = OrganizationBranding(
                id=f"branding_{org_id}",
                organization_id=org_id,
                company_name="CreditBeast",
                created_at=datetime.now(),
                updated_at=datetime.now()
            )
            return default_branding
        except Exception as e:
            logger.error(f"Error fetching branding for org {org_id}: {e}")
            raise

    async def update_organization_branding(
        self, 
        org_id: str, 
        updates: BrandingUpdateRequest
    ) -> OrganizationBranding:
        """Update organization branding configuration"""
        try:
            # Validate updates
            validation_response = await self.validate_branding_updates(updates)
            if not validation_response.is_valid:
                raise ValueError(f"Invalid branding updates: {', '.join(validation_response.errors)}")
            
            # In a real implementation, this would update the database
            # For now, return a mock updated branding
            current_branding = await self.get_organization_branding(org_id)
            
            # Apply updates
            update_dict = updates.dict(exclude_unset=True)
            updated_branding = current_branding.copy(update=update_dict)
            updated_branding.updated_at = datetime.now()
            
            logger.info(f"Updated branding for organization {org_id}")
            return updated_branding
        except Exception as e:
            logger.error(f"Error updating branding for org {org_id}: {e}")
            raise

    async def validate_branding_updates(
        self, 
        updates: BrandingValidationRequest | BrandingUpdateRequest
    ) -> BrandingValidationResponse:
        """Validate branding updates for correctness"""
        errors = []
        warnings = []
        suggestions = []
        
        try:
            if isinstance(updates, BrandingUpdateRequest):
                updates_dict = updates.dict(exclude_unset=True)
            else:
                updates_dict = updates.branding_updates.dict(exclude_unset=True)
            
            # Validate colors
            color_fields = ['primary_color', 'secondary_color', 'accent_color', 'background_color']
            for field in color_fields:
                if field in updates_dict:
                    color = updates_dict[field]
                    if not self._is_valid_hex_color(color):
                        errors.append(f"Invalid hex color format for {field}: {color}")
            
            # Validate URLs
            url_fields = ['logo_url', 'favicon_url', 'website_url', 'facebook_url', 'twitter_url']
            for field in url_fields:
                if field in updates_dict and updates_dict[field]:
                    url = updates_dict[field]
                    if not self._is_valid_url(url):
                        errors.append(f"Invalid URL format for {field}: {url}")
            
            # Validate email addresses
            email_fields = ['support_email']
            for field in email_fields:
                if field in updates_dict and updates_dict[field]:
                    email = updates_dict[field]
                    if not self._is_valid_email(email):
                        errors.append(f"Invalid email format for {field}: {email}")
            
            # Validate custom domain
            if 'custom_domain' in updates_dict and updates_dict['custom_domain']:
                domain = updates_dict['custom_domain']
                if not self._is_valid_domain(domain):
                    errors.append(f"Invalid domain format: {domain}")
                if domain and not domain.endswith(('.com', '.net', '.org', '.io', '.co')):
                    warnings.append(f"Domain {domain} uses an unusual TLD")
            
            # Validate font families
            if 'font_family' in updates_dict:
                font = updates_dict['font_family']
                if font and not re.match(r'^[a-zA-Z0-9\s,\-]+$', font):
                    errors.append(f"Invalid font family: {font}")
            
            # Generate suggestions
            if 'primary_color' in updates_dict:
                color = updates_dict['primary_color']
                if color and self._is_valid_hex_color(color):
                    suggestions.append(f"Consider testing {color} with your logo for accessibility")
            
            if not errors and not warnings:
                suggestions.append("Branding configuration looks good!")
            
            return BrandingValidationResponse(
                success=True,
                is_valid=len(errors) == 0,
                errors=errors,
                warnings=warnings,
                suggestions=suggestions
            )
            
        except Exception as e:
            logger.error(f"Error validating branding updates: {e}")
            return BrandingValidationResponse(
                success=False,
                is_valid=False,
                errors=[f"Validation error: {str(e)}"],
                warnings=[],
                suggestions=[]
            )

    async def preview_branding_changes(
        self, 
        org_id: str, 
        request: BrandingPreviewRequest
    ) -> Dict[str, Any]:
        """Generate preview of branding changes"""
        try:
            current_branding = await self.get_organization_branding(org_id)
            updates = request.branding_updates.dict(exclude_unset=True)
            
            # Apply updates to current branding
            preview_branding = current_branding.copy(update=updates)
            
            # Generate preview based on type
            if request.preview_type == "dashboard":
                preview_data = await self._generate_dashboard_preview(preview_branding)
            elif request.preview_type == "email":
                preview_data = await self._generate_email_preview(preview_branding)
            elif request.preview_type == "document":
                preview_data = await self._generate_document_preview(preview_branding)
            elif request.preview_type == "landing":
                preview_data = await self._generate_landing_preview(preview_branding)
            else:
                preview_data = {"message": "Preview not available for this type"}
            
            return {
                "success": True,
                "preview_type": request.preview_type,
                "preview_data": preview_data,
                "branding": preview_branding.dict()
            }
            
        except Exception as e:
            logger.error(f"Error generating branding preview: {e}")
            raise

    async def get_branding_templates(self) -> List[BrandingTemplate]:
        """Get available branding templates"""
        try:
            # Define some default templates
            templates = [
                BrandingTemplate(
                    id="modern-blue",
                    name="Modern Blue",
                    description="Clean, professional blue theme",
                    category="professional",
                    template_data=OrganizationBranding(
                        id="template-modern-blue",
                        organization_id="template",
                        primary_color="#2563eb",
                        secondary_color="#64748b",
                        accent_color="#0ea5e9",
                        background_color="#ffffff",
                        company_name="CreditBeast",
                        created_at=datetime.now(),
                        updated_at=datetime.now()
                    ),
                    is_premium=False,
                    is_active=True,
                    created_at=datetime.now()
                ),
                BrandingTemplate(
                    id="elegant-purple",
                    name="Elegant Purple",
                    description="Sophisticated purple and gray theme",
                    category="professional",
                    template_data=OrganizationBranding(
                        id="template-elegant-purple",
                        organization_id="template",
                        primary_color="#7c3aed",
                        secondary_color="#6b7280",
                        accent_color="#a855f7",
                        background_color="#fafafa",
                        company_name="CreditBeast",
                        created_at=datetime.now(),
                        updated_at=datetime.now()
                    ),
                    is_premium=True,
                    is_active=True,
                    created_at=datetime.now()
                ),
                BrandingTemplate(
                    id="minimalist-green",
                    name="Minimalist Green",
                    description="Clean green theme for modern businesses",
                    category="minimalist",
                    template_data=OrganizationBranding(
                        id="template-minimalist-green",
                        organization_id="template",
                        primary_color="#059669",
                        secondary_color="#374151",
                        accent_color="#10b981",
                        background_color="#ffffff",
                        company_name="CreditBeast",
                        created_at=datetime.now(),
                        updated_at=datetime.now()
                    ),
                    is_premium=False,
                    is_active=True,
                    created_at=datetime.now()
                )
            ]
            
            return templates
            
        except Exception as e:
            logger.error(f"Error fetching branding templates: {e}")
            raise

    async def apply_branding_template(
        self, 
        org_id: str, 
        template_id: str
    ) -> OrganizationBranding:
        """Apply a branding template to organization"""
        try:
            templates = await self.get_branding_templates()
            template = next((t for t in templates if t.id == template_id), None)
            
            if not template:
                raise ValueError(f"Template not found: {template_id}")
            
            if not template.is_active:
                raise ValueError(f"Template is not active: {template_id}")
            
            # Apply template to organization
            template_data = template.template_data.dict()
            template_data['organization_id'] = org_id
            template_data['id'] = f"branding_{org_id}"
            template_data['created_at'] = datetime.now()
            template_data['updated_at'] = datetime.now()
            
            branding = OrganizationBranding(**template_data)
            
            logger.info(f"Applied template {template_id} to organization {org_id}")
            return branding
            
        except Exception as e:
            logger.error(f"Error applying branding template: {e}")
            raise

    async def generate_custom_css(self, branding: OrganizationBranding) -> str:
        """Generate custom CSS from branding configuration"""
        try:
            css_vars = {
                '--color-primary': branding.primary_color,
                '--color-secondary': branding.secondary_color,
                '--color-accent': branding.accent_color,
                '--color-background': branding.background_color,
                '--font-family': branding.font_family,
            }
            
            css = "/* Generated Custom CSS */\n\n"
            
            # Add CSS variables
            css += ":root {\n"
            for var, value in css_vars.items():
                if value:
                    css += f"  {var}: {value};\n"
            css += "}\n\n"
            
            # Add custom CSS if provided
            if branding.custom_css:
                css += "/* Custom CSS */\n"
                css += branding.custom_css + "\n\n"
            
            # Add predefined styles
            css += """
/* Branding Application Styles */
.brand-primary { color: var(--color-primary); }
.brand-primary-bg { background-color: var(--color-primary); }
.brand-secondary { color: var(--color-secondary); }
.brand-secondary-bg { background-color: var(--color-secondary); }
.brand-accent { color: var(--color-accent); }
.brand-accent-bg { background-color: var(--color-accent); }

.button-primary {
  background-color: var(--color-primary);
  border-color: var(--color-primary);
}

.button-primary:hover {
  background-color: var(--color-secondary);
  border-color: var(--color-secondary);
}
"""
            
            return css
            
        except Exception as e:
            logger.error(f"Error generating custom CSS: {e}")
            raise

    # Private helper methods
    def _is_valid_hex_color(self, color: str) -> bool:
        """Validate hex color format"""
        if not color:
            return True
        return bool(re.match(r'^#[0-9A-Fa-f]{6}$', color))

    def _is_valid_url(self, url: str) -> bool:
        """Validate URL format"""
        if not url:
            return True
        return bool(re.match(r'^https?://[^\s/$.?#].[^\s]*$', url))

    def _is_valid_email(self, email: str) -> bool:
        """Validate email format"""
        if not email:
            return True
        return bool(re.match(r'^[^\s@]+@[^\s@]+\.[^\s@]+$', email))

    def _is_valid_domain(self, domain: str) -> bool:
        """Validate domain format"""
        if not domain:
            return True
        return bool(re.match(r'^[a-zA-Z0-9]([a-zA-Z0-9-]{0,61}[a-zA-Z0-9])?(\.[a-zA-Z0-9]([a-zA-Z0-9-]{0,61}[a-zA-Z0-9])?)*$', domain))

    async def _generate_dashboard_preview(self, branding: OrganizationBranding) -> Dict[str, Any]:
        """Generate dashboard preview data"""
        return {
            "type": "dashboard",
            "colors": {
                "primary": branding.primary_color,
                "secondary": branding.secondary_color,
                "accent": branding.accent_color,
                "background": branding.background_color
            },
            "logo": branding.logo_url,
            "company_name": branding.company_name
        }

    async def _generate_email_preview(self, branding: OrganizationBranding) -> Dict[str, Any]:
        """Generate email template preview data"""
        return {
            "type": "email",
            "header_logo": branding.email_header_logo_url or branding.logo_url,
            "footer_text": branding.email_footer_text,
            "primary_color": branding.email_primary_color or branding.primary_color,
            "company_name": branding.company_name
        }

    async def _generate_document_preview(self, branding: OrganizationBranding) -> Dict[str, Any]:
        """Generate document preview data"""
        return {
            "type": "document",
            "header_text": branding.document_header_text,
            "footer_text": branding.document_footer_text,
            "logo": branding.document_logo_url or branding.logo_url,
            "company_name": branding.company_name
        }

    async def _generate_landing_preview(self, branding: OrganizationBranding) -> Dict[str, Any]:
        """Generate landing page preview data"""
        return {
            "type": "landing",
            "company_name": branding.company_name,
            "company_tagline": branding.company_tagline,
            "logo": branding.logo_url,
            "primary_color": branding.primary_color,
            "background_color": branding.background_color
        }


# Global branding service instance
branding_service = BrandingService()