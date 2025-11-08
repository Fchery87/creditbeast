'use client';

import { useState, useEffect } from 'react';
import { Button } from '@/components/ui/button';
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '@/components/ui/card';

interface BrandingConfig {
  company_name: string;
  company_tagline: string;
  primary_color: string;
  secondary_color: string;
  accent_color: string;
  background_color: string;
  font_family: string;
  logo_url: string;
  show_creditbeast_branding: boolean;
}

export default function BrandingPage() {
  const [branding, setBranding] = useState<BrandingConfig>({
    company_name: 'CreditBeast',
    company_tagline: 'Credit repair management platform',
    primary_color: '#2563eb',
    secondary_color: '#64748b',
    accent_color: '#0ea5e9',
    background_color: '#ffffff',
    font_family: 'Inter',
    logo_url: '',
    show_creditbeast_branding: true
  });
  
  const [saving, setSaving] = useState(false);
  const [previewMode, setPreviewMode] = useState<'dashboard' | 'email' | 'document'>('dashboard');

  const handleInputChange = (field: keyof BrandingConfig, value: string | boolean) => {
    setBranding(prev => ({ ...prev, [field]: value }));
  };

  const handleSave = async () => {
    setSaving(true);
    try {
      // Mock save - in real implementation, call API
      await new Promise(resolve => setTimeout(resolve, 1000));
      alert('Branding settings saved successfully!');
    } catch (error) {
      console.error('Error saving branding:', error);
      alert('Failed to save branding settings');
    } finally {
      setSaving(false);
    }
  };

  const resetToDefault = () => {
    setBranding({
      company_name: 'CreditBeast',
      company_tagline: 'Credit repair management platform',
      primary_color: '#2563eb',
      secondary_color: '#64748b',
      accent_color: '#0ea5e9',
      background_color: '#ffffff',
      font_family: 'Inter',
      logo_url: '',
      show_creditbeast_branding: true
    });
  };

  const availableFonts = [
    'Inter',
    'Roboto',
    'Open Sans',
    'Lato',
    'Montserrat',
    'Source Sans Pro',
    'Nunito',
    'Poppins'
  ];

  return (
    <div className="space-y-6">
      {/* Header */}
      <div className="flex justify-between items-center">
        <div>
          <h1 className="text-3xl font-bold text-gray-900">Branding & White-Label</h1>
          <p className="text-gray-600 mt-2">Customize your organization's branding and appearance</p>
        </div>
        <div className="flex gap-2">
          <Button variant="outline" onClick={resetToDefault}>
            Reset to Default
          </Button>
          <Button onClick={handleSave} disabled={saving}>
            {saving ? 'Saving...' : 'Save Changes'}
          </Button>
        </div>
      </div>

      <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
        {/* Branding Configuration */}
        <div className="space-y-6">
          {/* Company Information */}
          <Card>
            <CardHeader>
              <CardTitle>Company Information</CardTitle>
              <CardDescription>Basic company details and branding</CardDescription>
            </CardHeader>
            <CardContent className="space-y-4">
              <div>
                <label className="block text-sm font-medium text-gray-700 mb-2">
                  Company Name
                </label>
                <input
                  type="text"
                  value={branding.company_name}
                  onChange={(e) => handleInputChange('company_name', e.target.value)}
                  className="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500"
                  placeholder="Your Company Name"
                />
              </div>
              
              <div>
                <label className="block text-sm font-medium text-gray-700 mb-2">
                  Company Tagline
                </label>
                <input
                  type="text"
                  value={branding.company_tagline}
                  onChange={(e) => handleInputChange('company_tagline', e.target.value)}
                  className="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500"
                  placeholder="Your company tagline"
                />
              </div>

              <div>
                <label className="block text-sm font-medium text-gray-700 mb-2">
                  Logo URL
                </label>
                <input
                  type="url"
                  value={branding.logo_url}
                  onChange={(e) => handleInputChange('logo_url', e.target.value)}
                  className="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500"
                  placeholder="https://example.com/logo.png"
                />
              </div>
            </CardContent>
          </Card>

          {/* Color Scheme */}
          <Card>
            <CardHeader>
              <CardTitle>Color Scheme</CardTitle>
              <CardDescription>Customize the color palette for your brand</CardDescription>
            </CardHeader>
            <CardContent className="space-y-4">
              <div className="grid grid-cols-2 gap-4">
                <div>
                  <label className="block text-sm font-medium text-gray-700 mb-2">
                    Primary Color
                  </label>
                  <div className="flex gap-2">
                    <input
                      type="color"
                      value={branding.primary_color}
                      onChange={(e) => handleInputChange('primary_color', e.target.value)}
                      className="w-12 h-10 border border-gray-300 rounded cursor-pointer"
                    />
                    <input
                      type="text"
                      value={branding.primary_color}
                      onChange={(e) => handleInputChange('primary_color', e.target.value)}
                      className="flex-1 px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500"
                      placeholder="#2563eb"
                    />
                  </div>
                </div>
                
                <div>
                  <label className="block text-sm font-medium text-gray-700 mb-2">
                    Secondary Color
                  </label>
                  <div className="flex gap-2">
                    <input
                      type="color"
                      value={branding.secondary_color}
                      onChange={(e) => handleInputChange('secondary_color', e.target.value)}
                      className="w-12 h-10 border border-gray-300 rounded cursor-pointer"
                    />
                    <input
                      type="text"
                      value={branding.secondary_color}
                      onChange={(e) => handleInputChange('secondary_color', e.target.value)}
                      className="flex-1 px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500"
                      placeholder="#64748b"
                    />
                  </div>
                </div>
                
                <div>
                  <label className="block text-sm font-medium text-gray-700 mb-2">
                    Accent Color
                  </label>
                  <div className="flex gap-2">
                    <input
                      type="color"
                      value={branding.accent_color}
                      onChange={(e) => handleInputChange('accent_color', e.target.value)}
                      className="w-12 h-10 border border-gray-300 rounded cursor-pointer"
                    />
                    <input
                      type="text"
                      value={branding.accent_color}
                      onChange={(e) => handleInputChange('accent_color', e.target.value)}
                      className="flex-1 px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500"
                      placeholder="#0ea5e9"
                    />
                  </div>
                </div>
                
                <div>
                  <label className="block text-sm font-medium text-gray-700 mb-2">
                    Background Color
                  </label>
                  <div className="flex gap-2">
                    <input
                      type="color"
                      value={branding.background_color}
                      onChange={(e) => handleInputChange('background_color', e.target.value)}
                      className="w-12 h-10 border border-gray-300 rounded cursor-pointer"
                    />
                    <input
                      type="text"
                      value={branding.background_color}
                      onChange={(e) => handleInputChange('background_color', e.target.value)}
                      className="flex-1 px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500"
                      placeholder="#ffffff"
                    />
                  </div>
                </div>
              </div>
            </CardContent>
          </Card>

          {/* Typography */}
          <Card>
            <CardHeader>
              <CardTitle>Typography</CardTitle>
              <CardDescription>Choose fonts for your brand</CardDescription>
            </CardHeader>
            <CardContent>
              <div>
                <label className="block text-sm font-medium text-gray-700 mb-2">
                  Font Family
                </label>
                <select
                  value={branding.font_family}
                  onChange={(e) => handleInputChange('font_family', e.target.value)}
                  className="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500"
                >
                  {availableFonts.map(font => (
                    <option key={font} value={font}>{font}</option>
                  ))}
                </select>
              </div>
            </CardContent>
          </Card>

          {/* Settings */}
          <Card>
            <CardHeader>
              <CardTitle>Display Settings</CardTitle>
              <CardDescription>Control what appears in your branded experience</CardDescription>
            </CardHeader>
            <CardContent>
              <div className="flex items-center space-x-3">
                <input
                  type="checkbox"
                  id="show_creditbeast_branding"
                  checked={branding.show_creditbeast_branding}
                  onChange={(e) => handleInputChange('show_creditbeast_branding', e.target.checked)}
                  className="h-4 w-4 text-blue-600 focus:ring-blue-500 border-gray-300 rounded"
                />
                <label htmlFor="show_creditbeast_branding" className="text-sm text-gray-700">
                  Show "Powered by CreditBeast" attribution
                </label>
              </div>
            </CardContent>
          </Card>
        </div>

        {/* Preview */}
        <div className="space-y-6">
          <Card>
            <CardHeader>
              <CardTitle>Live Preview</CardTitle>
              <CardDescription>See how your branding will look</CardDescription>
            </CardHeader>
            <CardContent>
              {/* Preview Mode Tabs */}
              <div className="flex space-x-1 mb-4">
                {['dashboard', 'email', 'document'].map((mode) => (
                  <button
                    key={mode}
                    onClick={() => setPreviewMode(mode as any)}
                    className={`px-3 py-1 text-sm rounded-md ${
                      previewMode === mode
                        ? 'bg-blue-100 text-blue-700'
                        : 'text-gray-500 hover:text-gray-700'
                    }`}
                  >
                    {mode.charAt(0).toUpperCase() + mode.slice(1)}
                  </button>
                ))}
              </div>

              {/* Preview Content */}
              <div 
                className="border rounded-lg p-4 min-h-96"
                style={{ 
                  backgroundColor: branding.background_color,
                  fontFamily: branding.font_family
                }}
              >
                {previewMode === 'dashboard' && (
                  <div>
                    {/* Header */}
                    <div className="flex items-center justify-between mb-6 pb-4 border-b">
                      <div className="flex items-center gap-3">
                        {branding.logo_url ? (
                          <img src={branding.logo_url} alt="Logo" className="h-8 w-auto" />
                        ) : (
                          <div 
                            className="h-8 w-8 rounded flex items-center justify-center text-white text-sm font-bold"
                            style={{ backgroundColor: branding.primary_color }}
                          >
                            {branding.company_name.charAt(0)}
                          </div>
                        )}
                        <div>
                          <h1 
                            className="text-lg font-semibold"
                            style={{ color: branding.primary_color }}
                          >
                            {branding.company_name}
                          </h1>
                          <p className="text-sm text-gray-600">{branding.company_tagline}</p>
                        </div>
                      </div>
                      <button 
                        className="px-4 py-2 rounded-md text-white text-sm"
                        style={{ backgroundColor: branding.primary_color }}
                      >
                        Sign Out
                      </button>
                    </div>

                    {/* Dashboard Content */}
                    <div className="grid grid-cols-2 gap-4">
                      <div 
                        className="p-4 rounded-lg border"
                        style={{ 
                          borderColor: branding.secondary_color,
                          backgroundColor: 'rgba(0,0,0,0.02)'
                        }}
                      >
                        <h3 className="text-sm font-medium text-gray-600 mb-2">Total Clients</h3>
                        <p className="text-2xl font-bold" style={{ color: branding.primary_color }}>24</p>
                      </div>
                      <div 
                        className="p-4 rounded-lg border"
                        style={{ 
                          borderColor: branding.secondary_color,
                          backgroundColor: 'rgba(0,0,0,0.02)'
                        }}
                      >
                        <h3 className="text-sm font-medium text-gray-600 mb-2">Active Disputes</h3>
                        <p className="text-2xl font-bold" style={{ color: branding.accent_color }}>47</p>
                      </div>
                    </div>

                    {branding.show_creditbeast_branding && (
                      <div className="mt-6 pt-4 border-t text-center text-xs text-gray-500">
                        Powered by CreditBeast
                      </div>
                    )}
                  </div>
                )}

                {previewMode === 'email' && (
                  <div>
                    <div 
                      className="p-4 rounded-t"
                      style={{ backgroundColor: branding.primary_color }}
                    >
                      {branding.logo_url ? (
                        <img src={branding.logo_url} alt="Logo" className="h-8 w-auto" />
                      ) : (
                        <h2 className="text-white text-lg font-semibold">{branding.company_name}</h2>
                      )}
                    </div>
                    <div className="p-4 border-x border-b">
                      <h3 className="text-lg font-semibold mb-2">Email Subject</h3>
                      <p className="text-gray-600 mb-4">
                        This is how your email templates will look with your branding applied.
                        The header, colors, and typography will match your chosen settings.
                      </p>
                      <button 
                        className="px-4 py-2 rounded-md text-white text-sm"
                        style={{ backgroundColor: branding.primary_color }}
                      >
                        Call to Action
                      </button>
                    </div>
                    <div className="p-4 border-x border-b text-center text-sm text-gray-500">
                      {branding.company_name} • {branding.company_tagline}
                    </div>
                  </div>
                )}

                {previewMode === 'document' && (
                  <div>
                    <div className="text-center mb-6 pb-4 border-b">
                      {branding.logo_url ? (
                        <img src={branding.logo_url} alt="Logo" className="h-12 w-auto mx-auto mb-2" />
                      ) : (
                        <h2 
                          className="text-2xl font-bold mb-2"
                          style={{ color: branding.primary_color }}
                        >
                          {branding.company_name}
                        </h2>
                      )}
                      <p className="text-gray-600">{branding.company_tagline}</p>
                    </div>
                    
                    <div className="mb-6">
                      <h3 className="text-lg font-semibold mb-2" style={{ color: branding.primary_color }}>
                        Document Title
                      </h3>
                      <p className="text-gray-600">
                        This preview shows how your letterhead and documents will appear with your 
                        custom branding. All letters and official documents will use this design.
                      </p>
                    </div>

                    <div 
                      className="p-4 rounded"
                      style={{ 
                        backgroundColor: 'rgba(0,0,0,0.02)',
                        borderLeft: `4px solid ${branding.accent_color}`
                      }}
                    >
                      <p className="text-sm text-gray-600">
                        Dispute letter content would appear here with your branding applied...
                      </p>
                    </div>
                  </div>
                )}
              </div>
            </CardContent>
          </Card>
        </div>
      </div>
    </div>
  );
}