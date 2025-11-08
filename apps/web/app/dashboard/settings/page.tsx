'use client';

import { useState } from 'react';
import { useQuery, useMutation, useQueryClient } from '@tanstack/react-query';
import { 
  Settings, 
  Users, 
  Mail, 
  Shield, 
  Database,
  Bell,
  Key,
  Building,
  Save,
  Plus,
  Edit,
  Trash2,
  Eye,
  EyeOff
} from 'lucide-react';
import { Button } from '@/components/ui/button';
import { Input } from '@/components/ui/input';
import { Label } from '@/components/ui/label';
import { Textarea } from '@/components/ui/textarea';
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '@/components/ui/card';
import { Badge } from '@/components/ui/badge';
import { Tabs, TabsContent, TabsList, TabsTrigger } from '@/components/ui/tabs';
import { Switch } from '@/components/ui/switch';
import {
  Table,
  TableBody,
  TableCell,
  TableHead,
  TableHeader,
  TableRow,
} from '@/components/ui/table';
import { Dialog, DialogContent, DialogDescription, DialogFooter, DialogHeader, DialogTitle } from '@/components/ui/dialog';

// Mock data for organization settings
const mockOrgSettings = {
  name: 'Credit Repair Pro LLC',
  slug: 'credit-repair-pro',
  email: 'admin@creditrepairpro.com',
  phone: '+1 (555) 123-4567',
  address: '123 Business Ave, Suite 100, City, State 12345',
  website: 'https://creditrepairpro.com',
  supportEmail: 'support@creditrepairpro.com',
  timezone: 'America/New_York',
  dateFormat: 'MM/dd/yyyy',
  businessHours: {
    start: '09:00',
    end: '17:00',
  },
  compliance: {
    gdprCompliant: true,
    soc2Compliant: true,
    hipaaCompliant: false,
    dataRetention: 2555, // days
    encryptionLevel: 'AES-256',
  },
};

const mockUsers = [
  {
    id: '1',
    name: 'John Doe',
    email: 'john.doe@creditrepairpro.com',
    role: 'admin',
    status: 'active',
    lastLogin: '2025-11-06T10:30:00Z',
    createdAt: '2025-01-15T00:00:00Z',
  },
  {
    id: '2',
    name: 'Jane Smith',
    email: 'jane.smith@creditrepairpro.com',
    role: 'member',
    status: 'active',
    lastLogin: '2025-11-05T14:20:00Z',
    createdAt: '2025-03-20T00:00:00Z',
  },
  {
    id: '3',
    name: 'Bob Wilson',
    email: 'bob.wilson@creditrepairpro.com',
    role: 'viewer',
    status: 'inactive',
    lastLogin: '2025-10-28T09:15:00Z',
    createdAt: '2025-06-10T00:00:00Z',
  },
];

const mockEmailTemplates = [
  {
    id: '1',
    name: 'Client Onboarding',
    category: 'client_communication',
    subject: 'Welcome to CreditBeast - Next Steps',
    isActive: true,
    lastModified: '2025-11-01T00:00:00Z',
  },
  {
    id: '2',
    name: 'Dispute Update',
    category: 'client_communication',
    subject: 'Your Credit Dispute Status Update',
    isActive: true,
    lastModified: '2025-10-28T00:00:00Z',
  },
  {
    id: '3',
    name: 'Payment Reminder',
    category: 'billing',
    subject: 'Payment Due - Action Required',
    isActive: false,
    lastModified: '2025-10-25T00:00:00Z',
  },
];

export default function SettingsPage() {
  const [activeTab, setActiveTab] = useState('organization');
  const [isAddUserDialogOpen, setIsAddUserDialogOpen] = useState(false);
  const [isEditTemplateDialogOpen, setIsEditTemplateDialogOpen] = useState(false);
  const [selectedTemplate, setSelectedTemplate] = useState<any>(null);
  const [showApiKey, setShowApiKey] = useState(false);

  const queryClient = useQueryClient();

  // Organization settings mutation
  const updateOrgSettingsMutation = useMutation({
    mutationFn: async (data: any) => {
      // Mock API call
      console.log('Updating organization settings:', data);
      return { success: true };
    },
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['org-settings'] });
    },
  });

  // User management mutations
  const inviteUserMutation = useMutation({
    mutationFn: async (data: any) => {
      // Mock API call
      console.log('Inviting user:', data);
      return { success: true };
    },
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['users'] });
      setIsAddUserDialogOpen(false);
    },
  });

  const updateUserMutation = useMutation({
    mutationFn: async ({ id, data }: any) => {
      // Mock API call
      console.log('Updating user:', id, data);
      return { success: true };
    },
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['users'] });
    },
  });

  const deleteUserMutation = useMutation({
    mutationFn: async (id: string) => {
      // Mock API call
      console.log('Deleting user:', id);
      return { success: true };
    },
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['users'] });
    },
  });

  const handleInviteUser = (e: React.FormEvent<HTMLFormElement>) => {
    e.preventDefault();
    const formData = new FormData(e.currentTarget);
    const data = {
      email: formData.get('email') as string,
      role: formData.get('role') as string,
      name: formData.get('name') as string,
    };
    inviteUserMutation.mutate(data);
  };

  return (
    <div className="space-y-6">
      {/* Header */}
      <div>
        <h1 className="text-3xl font-bold">Settings & Administration</h1>
        <p className="text-gray-600 mt-2">Manage your organization, users, and system preferences</p>
      </div>

      {/* Settings Tabs */}
      <Tabs value={activeTab} onValueChange={setActiveTab} className="space-y-4">
        <TabsList className="grid w-full grid-cols-6">
          <TabsTrigger value="organization">Organization</TabsTrigger>
          <TabsTrigger value="users">Users</TabsTrigger>
          <TabsTrigger value="email">Email Templates</TabsTrigger>
          <TabsTrigger value="security">Security</TabsTrigger>
          <TabsTrigger value="integrations">Integrations</TabsTrigger>
          <TabsTrigger value="backup">Backup</TabsTrigger>
        </TabsList>

        {/* Organization Settings */}
        <TabsContent value="organization" className="space-y-6">
          <Card>
            <CardHeader>
              <CardTitle className="flex items-center gap-2">
                <Building className="w-5 h-5" />
                Organization Information
              </CardTitle>
              <CardDescription>Basic information about your organization</CardDescription>
            </CardHeader>
            <CardContent className="space-y-4">
              <div className="grid grid-cols-2 gap-4">
                <div className="space-y-2">
                  <Label htmlFor="org-name">Organization Name</Label>
                  <Input
                    id="org-name"
                    defaultValue={mockOrgSettings.name}
                    placeholder="Your organization name"
                  />
                </div>
                <div className="space-y-2">
                  <Label htmlFor="org-slug">Organization Slug</Label>
                  <Input
                    id="org-slug"
                    defaultValue={mockOrgSettings.slug}
                    placeholder="organization-slug"
                  />
                </div>
              </div>

              <div className="grid grid-cols-2 gap-4">
                <div className="space-y-2">
                  <Label htmlFor="org-email">Primary Email</Label>
                  <Input
                    id="org-email"
                    type="email"
                    defaultValue={mockOrgSettings.email}
                    placeholder="admin@organization.com"
                  />
                </div>
                <div className="space-y-2">
                  <Label htmlFor="org-phone">Phone Number</Label>
                  <Input
                    id="org-phone"
                    defaultValue={mockOrgSettings.phone}
                    placeholder="+1 (555) 123-4567"
                  />
                </div>
              </div>

              <div className="space-y-2">
                <Label htmlFor="org-address">Business Address</Label>
                <Textarea
                  id="org-address"
                  defaultValue={mockOrgSettings.address}
                  placeholder="123 Business Ave, Suite 100, City, State 12345"
                  rows={3}
                />
              </div>

              <div className="grid grid-cols-2 gap-4">
                <div className="space-y-2">
                  <Label htmlFor="org-website">Website</Label>
                  <Input
                    id="org-website"
                    defaultValue={mockOrgSettings.website}
                    placeholder="https://your-website.com"
                  />
                </div>
                <div className="space-y-2">
                  <Label htmlFor="org-support-email">Support Email</Label>
                  <Input
                    id="org-support-email"
                    type="email"
                    defaultValue={mockOrgSettings.supportEmail}
                    placeholder="support@organization.com"
                  />
                </div>
              </div>

              <div className="grid grid-cols-2 gap-4">
                <div className="space-y-2">
                  <Label htmlFor="org-timezone">Timezone</Label>
                  <select
                    id="org-timezone"
                    defaultValue={mockOrgSettings.timezone}
                    className="w-full px-4 py-2 border border-gray-300 rounded-md"
                  >
                    <option value="America/New_York">Eastern Time (ET)</option>
                    <option value="America/Chicago">Central Time (CT)</option>
                    <option value="America/Denver">Mountain Time (MT)</option>
                    <option value="America/Los_Angeles">Pacific Time (PT)</option>
                  </select>
                </div>
                <div className="space-y-2">
                  <Label htmlFor="org-date-format">Date Format</Label>
                  <select
                    id="org-date-format"
                    defaultValue={mockOrgSettings.dateFormat}
                    className="w-full px-4 py-2 border border-gray-300 rounded-md"
                  >
                    <option value="MM/dd/yyyy">MM/dd/yyyy</option>
                    <option value="dd/MM/yyyy">dd/MM/yyyy</option>
                    <option value="yyyy-MM-dd">yyyy-MM-dd</option>
                  </select>
                </div>
              </div>

              <div className="flex justify-end">
                <Button
                  onClick={() => updateOrgSettingsMutation.mutate({})}
                  disabled={updateOrgSettingsMutation.isPending}
                >
                  <Save className="w-4 h-4 mr-2" />
                  {updateOrgSettingsMutation.isPending ? 'Saving...' : 'Save Changes'}
                </Button>
              </div>
            </CardContent>
          </Card>
        </TabsContent>

        {/* User Management */}
        <TabsContent value="users" className="space-y-6">
          <div className="flex justify-between items-center">
            <h3 className="text-lg font-semibold">User Management</h3>
            <Button onClick={() => setIsAddUserDialogOpen(true)}>
              <Plus className="w-4 h-4 mr-2" />
              Invite User
            </Button>
          </div>

          <Card>
            <CardContent className="p-0">
              <Table>
                <TableHeader>
                  <TableRow>
                    <TableHead>Name</TableHead>
                    <TableHead>Email</TableHead>
                    <TableHead>Role</TableHead>
                    <TableHead>Status</TableHead>
                    <TableHead>Last Login</TableHead>
                    <TableHead className="text-right">Actions</TableHead>
                  </TableRow>
                </TableHeader>
                <TableBody>
                  {mockUsers.map((user) => (
                    <TableRow key={user.id}>
                      <TableCell className="font-medium">{user.name}</TableCell>
                      <TableCell>{user.email}</TableCell>
                      <TableCell>
                        <Badge variant="outline">{user.role}</Badge>
                      </TableCell>
                      <TableCell>
                        <Badge
                          variant={user.status === 'active' ? 'success' : 'secondary'}
                        >
                          {user.status}
                        </Badge>
                      </TableCell>
                      <TableCell>
                        {new Date(user.lastLogin).toLocaleDateString()}
                      </TableCell>
                      <TableCell className="text-right">
                        <div className="flex justify-end gap-2">
                          <Button variant="ghost" size="sm">
                            <Edit className="w-4 h-4" />
                          </Button>
                          <Button
                            variant="ghost"
                            size="sm"
                            onClick={() => {
                              if (confirm('Are you sure you want to remove this user?')) {
                                deleteUserMutation.mutate(user.id);
                              }
                            }}
                          >
                            <Trash2 className="w-4 h-4 text-red-600" />
                          </Button>
                        </div>
                      </TableCell>
                    </TableRow>
                  ))}
                </TableBody>
              </Table>
            </CardContent>
          </Card>
        </TabsContent>

        {/* Email Templates */}
        <TabsContent value="email" className="space-y-6">
          <div className="flex justify-between items-center">
            <h3 className="text-lg font-semibold">Email Templates</h3>
            <Button>
              <Plus className="w-4 h-4 mr-2" />
              New Template
            </Button>
          </div>

          <div className="grid gap-6">
            {mockEmailTemplates.map((template) => (
              <Card key={template.id}>
                <CardHeader>
                  <div className="flex justify-between items-start">
                    <div>
                      <CardTitle className="text-lg">{template.name}</CardTitle>
                      <CardDescription className="mt-1">
                        {template.subject}
                      </CardDescription>
                    </div>
                    <div className="flex items-center gap-2">
                      <Badge
                        variant={template.isActive ? 'success' : 'secondary'}
                      >
                        {template.isActive ? 'Active' : 'Inactive'}
                      </Badge>
                      <Button
                        variant="ghost"
                        size="sm"
                        onClick={() => {
                          setSelectedTemplate(template);
                          setIsEditTemplateDialogOpen(true);
                        }}
                      >
                        <Edit className="w-4 h-4" />
                      </Button>
                    </div>
                  </div>
                </CardHeader>
                <CardContent>
                  <div className="flex justify-between items-center text-sm text-gray-600">
                    <span>Category: {template.category}</span>
                    <span>Last modified: {new Date(template.lastModified).toLocaleDateString()}</span>
                  </div>
                </CardContent>
              </Card>
            ))}
          </div>
        </TabsContent>

        {/* Security Settings */}
        <TabsContent value="security" className="space-y-6">
          <Card>
            <CardHeader>
              <CardTitle className="flex items-center gap-2">
                <Shield className="w-5 h-5" />
                Security & Privacy
              </CardTitle>
              <CardDescription>Manage security settings and compliance</CardDescription>
            </CardHeader>
            <CardContent className="space-y-6">
              <div className="space-y-4">
                <h4 className="font-semibold">API Keys</h4>
                <div className="space-y-3">
                  <div className="flex items-center justify-between p-3 border rounded-md">
                    <div>
                      <p className="font-medium">Production API Key</p>
                      <p className="text-sm text-gray-600">sk_live_xxxxxxxxxxxxxxxxx</p>
                    </div>
                    <div className="flex items-center gap-2">
                      <Button
                        variant="ghost"
                        size="sm"
                        onClick={() => setShowApiKey(!showApiKey)}
                      >
                        {showApiKey ? <EyeOff className="w-4 h-4" /> : <Eye className="w-4 h-4" />}
                      </Button>
                      <Button variant="outline" size="sm">
                        Regenerate
                      </Button>
                    </div>
                  </div>
                </div>
              </div>

              <div className="space-y-4">
                <h4 className="font-semibold">Compliance Settings</h4>
                <div className="space-y-3">
                  <div className="flex items-center justify-between">
                    <div>
                      <Label htmlFor="gdpr-compliance">GDPR Compliance</Label>
                      <p className="text-sm text-gray-600">Enable GDPR compliance features</p>
                    </div>
                    <Switch id="gdpr-compliance" defaultChecked />
                  </div>
                  <div className="flex items-center justify-between">
                    <div>
                      <Label htmlFor="soc2-compliance">SOC 2 Compliance</Label>
                      <p className="text-sm text-gray-600">Enable SOC 2 compliance features</p>
                    </div>
                    <Switch id="soc2-compliance" defaultChecked />
                  </div>
                  <div className="flex items-center justify-between">
                    <div>
                      <Label htmlFor="hipaa-compliance">HIPAA Compliance</Label>
                      <p className="text-sm text-gray-600">Enable HIPAA compliance features</p>
                    </div>
                    <Switch id="hipaa-compliance" />
                  </div>
                </div>
              </div>

              <div className="space-y-4">
                <h4 className="font-semibold">Data Retention</h4>
                <div className="space-y-2">
                  <Label htmlFor="data-retention">Data Retention Period (days)</Label>
                  <Input
                    id="data-retention"
                    type="number"
                    defaultValue={mockOrgSettings.compliance.dataRetention}
                    min="1"
                    max="3650"
                  />
                  <p className="text-sm text-gray-600">
                    How long to keep client data before automatic deletion
                  </p>
                </div>
              </div>
            </CardContent>
          </Card>
        </TabsContent>

        {/* Integrations */}
        <TabsContent value="integrations" className="space-y-6">
          <Card>
            <CardHeader>
              <CardTitle>Third-party Integrations</CardTitle>
              <CardDescription>Manage external service connections</CardDescription>
            </CardHeader>
            <CardContent className="space-y-6">
              {[
                {
                  name: 'Stripe',
                  description: 'Payment processing and billing',
                  status: 'connected',
                  config: 'Active since Jan 2025',
                },
                {
                  name: 'CloudMail',
                  description: 'Email delivery service',
                  status: 'connected',
                  config: 'Active since Feb 2025',
                },
                {
                  name: 'Clerk Auth',
                  description: 'User authentication',
                  status: 'connected',
                  config: 'Active since Jan 2025',
                },
                {
                  name: 'Supabase',
                  description: 'Database and storage',
                  status: 'connected',
                  config: 'Active since Jan 2025',
                },
              ].map((integration, index) => (
                <div key={index} className="flex items-center justify-between p-4 border rounded-md">
                  <div>
                    <h4 className="font-medium">{integration.name}</h4>
                    <p className="text-sm text-gray-600">{integration.description}</p>
                    <p className="text-xs text-gray-500">{integration.config}</p>
                  </div>
                  <div className="flex items-center gap-2">
                    <Badge variant="success">Connected</Badge>
                    <Button variant="outline" size="sm">
                      Configure
                    </Button>
                  </div>
                </div>
              ))}
            </CardContent>
          </Card>
        </TabsContent>

        {/* Backup Settings */}
        <TabsContent value="backup" className="space-y-6">
          <Card>
            <CardHeader>
              <CardTitle className="flex items-center gap-2">
                <Database className="w-5 h-5" />
                Backup & Data Management
              </CardTitle>
              <CardDescription>Configure automated backups and data exports</CardDescription>
            </CardHeader>
            <CardContent className="space-y-6">
              <div className="space-y-4">
                <h4 className="font-semibold">Automated Backups</h4>
                <div className="space-y-3">
                  <div className="flex items-center justify-between">
                    <div>
                      <Label htmlFor="auto-backup">Enable Automated Backups</Label>
                      <p className="text-sm text-gray-600">Daily backups at 2:00 AM</p>
                    </div>
                    <Switch id="auto-backup" defaultChecked />
                  </div>
                  <div className="flex items-center justify-between">
                    <div>
                      <Label htmlFor="retention-backup">Backup Retention (days)</Label>
                      <p className="text-sm text-gray-600">How long to keep backups</p>
                    </div>
                    <Input
                      id="retention-backup"
                      type="number"
                      defaultValue="30"
                      min="1"
                      max="365"
                      className="w-20"
                    />
                  </div>
                </div>
              </div>

              <div className="space-y-4">
                <h4 className="font-semibold">Manual Actions</h4>
                <div className="flex gap-2">
                  <Button variant="outline">
                    <Database className="w-4 h-4 mr-2" />
                    Create Backup Now
                  </Button>
                  <Button variant="outline">
                    <Key className="w-4 h-4 mr-2" />
                    Export All Data
                  </Button>
                </div>
              </div>

              <div className="space-y-4">
                <h4 className="font-semibold">Recent Backups</h4>
                <div className="space-y-2">
                  {[
                    { date: '2025-11-06 02:00 AM', size: '2.3 GB', status: 'Completed' },
                    { date: '2025-11-05 02:00 AM', size: '2.1 GB', status: 'Completed' },
                    { date: '2025-11-04 02:00 AM', size: '2.0 GB', status: 'Completed' },
                  ].map((backup, index) => (
                    <div key={index} className="flex items-center justify-between p-3 border rounded-md">
                      <div>
                        <p className="font-medium">{backup.date}</p>
                        <p className="text-sm text-gray-600">Size: {backup.size}</p>
                      </div>
                      <div className="flex items-center gap-2">
                        <Badge variant="success">{backup.status}</Badge>
                        <Button variant="ghost" size="sm">
                          Download
                        </Button>
                      </div>
                    </div>
                  ))}
                </div>
              </div>
            </CardContent>
          </Card>
        </TabsContent>
      </Tabs>

      {/* Invite User Dialog */}
      <Dialog open={isAddUserDialogOpen} onOpenChange={setIsAddUserDialogOpen}>
        <DialogContent>
          <form onSubmit={handleInviteUser}>
            <DialogHeader>
              <DialogTitle>Invite New User</DialogTitle>
              <DialogDescription>
                Send an invitation to join your organization
              </DialogDescription>
            </DialogHeader>
            <div className="grid gap-4 py-4">
              <div className="space-y-2">
                <Label htmlFor="name">Full Name</Label>
                <Input id="name" name="name" required />
              </div>
              <div className="space-y-2">
                <Label htmlFor="email">Email Address</Label>
                <Input id="email" name="email" type="email" required />
              </div>
              <div className="space-y-2">
                <Label htmlFor="role">Role</Label>
                <select
                  id="role"
                  name="role"
                  className="w-full px-4 py-2 border border-gray-300 rounded-md"
                  required
                >
                  <option value="member">Member</option>
                  <option value="admin">Admin</option>
                  <option value="viewer">Viewer</option>
                </select>
              </div>
            </div>
            <DialogFooter>
              <Button type="button" variant="outline" onClick={() => setIsAddUserDialogOpen(false)}>
                Cancel
              </Button>
              <Button type="submit" disabled={inviteUserMutation.isPending}>
                {inviteUserMutation.isPending ? 'Sending...' : 'Send Invitation'}
              </Button>
            </DialogFooter>
          </form>
        </DialogContent>
      </Dialog>

      {/* Edit Template Dialog */}
      <Dialog open={isEditTemplateDialogOpen} onOpenChange={setIsEditTemplateDialogOpen}>
        <DialogContent className="sm:max-w-2xl">
          <DialogHeader>
            <DialogTitle>Edit Email Template</DialogTitle>
            <DialogDescription>
              Customize the email template content and settings
            </DialogDescription>
          </DialogHeader>
          {selectedTemplate && (
            <div className="grid gap-4 py-4">
              <div className="space-y-2">
                <Label htmlFor="template-name">Template Name</Label>
                <Input
                  id="template-name"
                  defaultValue={selectedTemplate.name}
                />
              </div>
              <div className="space-y-2">
                <Label htmlFor="template-subject">Subject Line</Label>
                <Input
                  id="template-subject"
                  defaultValue={selectedTemplate.subject}
                />
              </div>
              <div className="space-y-2">
                <Label htmlFor="template-content">Email Content</Label>
                <Textarea
                  id="template-content"
                  rows={10}
                  placeholder="Enter your email template content here..."
                />
              </div>
              <div className="flex items-center space-x-2">
                <Switch id="template-active" defaultChecked={selectedTemplate.isActive} />
                <Label htmlFor="template-active">Active</Label>
              </div>
            </div>
          )}
          <DialogFooter>
            <Button type="button" variant="outline" onClick={() => setIsEditTemplateDialogOpen(false)}>
              Cancel
            </Button>
            <Button>Save Changes</Button>
          </DialogFooter>
        </DialogContent>
      </Dialog>
    </div>
  );
}