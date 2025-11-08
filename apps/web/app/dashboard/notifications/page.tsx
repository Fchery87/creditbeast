'use client';

import { useState } from 'react';
import { useQuery, useMutation, useQueryClient } from '@tanstack/react-query';
import { 
  Mail, 
  Bell, 
  Send, 
  Eye, 
  Settings, 
  Plus,
  Edit,
  Trash2,
  Filter,
  Search,
  Download,
  TrendingUp,
  Users,
  AlertTriangle,
  CheckCircle2,
  Clock,
  XCircle
} from 'lucide-react';
import { Button } from '@/components/ui/button';
import { Input } from '@/components/ui/input';
import { Label } from '@/components/ui/label';
import { Textarea } from '@/components/ui/textarea';
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '@/components/ui/card';
import { Badge } from '@/components/ui/badge';
import { Tabs, TabsContent, TabsList, TabsTrigger } from '@/components/ui/tabs';
import {
  Table,
  TableBody,
  TableCell,
  TableHead,
  TableHeader,
  TableRow,
} from '@/components/ui/table';
import { Dialog, DialogContent, DialogDescription, DialogFooter, DialogHeader, DialogTitle } from '@/components/ui/dialog';
import { Switch } from '@/components/ui/switch';

// Mock email templates
const mockEmailTemplates = [
  {
    id: '1',
    name: 'Client Onboarding Welcome',
    category: 'client_communication',
    subject: 'Welcome to CreditBeast - Getting Started',
    description: 'Sent to new clients after account creation',
    isActive: true,
    lastModified: '2025-11-01T10:30:00Z',
    variables: ['client_name', 'organization_name', 'login_link'],
    usage: 45,
  },
  {
    id: '2',
    name: 'Dispute Status Update',
    category: 'client_communication',
    subject: 'Your Credit Dispute Update - {{dispute_type}}',
    description: 'Sent when dispute status changes',
    isActive: true,
    lastModified: '2025-10-28T14:20:00Z',
    variables: ['client_name', 'dispute_type', 'status', 'next_steps'],
    usage: 128,
  },
  {
    id: '3',
    name: 'Payment Reminder',
    category: 'billing',
    subject: 'Payment Due - Action Required',
    description: 'Sent when payment is overdue',
    isActive: true,
    lastModified: '2025-10-25T09:15:00Z',
    variables: ['client_name', 'amount_due', 'due_date', 'payment_link'],
    usage: 23,
  },
  {
    id: '4',
    name: 'New Client Alert',
    category: 'internal_notification',
    subject: 'New Client Added - {{client_name}}',
    description: 'Alert sent to admin when new client signs up',
    isActive: true,
    lastModified: '2025-10-20T16:45:00Z',
    variables: ['client_name', 'client_email', 'signup_date'],
    usage: 67,
  },
  {
    id: '5',
    name: 'Payment Failed',
    category: 'billing',
    subject: 'Payment Failed - Immediate Action Required',
    description: 'Alert sent when payment fails',
    isActive: false,
    lastModified: '2025-10-15T11:30:00Z',
    variables: ['client_name', 'amount', 'failure_reason'],
    usage: 8,
  },
];

// Mock email logs
const mockEmailLogs = [
  {
    id: '1',
    to: 'john.doe@example.com',
    subject: 'Welcome to CreditBeast - Getting Started',
    template: 'Client Onboarding Welcome',
    status: 'delivered',
    sentAt: '2025-11-06T15:30:00Z',
    opened: true,
    clicked: false,
    type: 'client_communication',
  },
  {
    id: '2',
    to: 'jane.smith@example.com',
    subject: 'Your Credit Dispute Update - Late Payment',
    template: 'Dispute Status Update',
    status: 'delivered',
    sentAt: '2025-11-06T14:20:00Z',
    opened: true,
    clicked: true,
    type: 'client_communication',
  },
  {
    id: '3',
    to: 'admin@creditrepairpro.com',
    subject: 'New Client Added - Bob Johnson',
    template: 'New Client Alert',
    status: 'delivered',
    sentAt: '2025-11-06T13:45:00Z',
    opened: false,
    clicked: false,
    type: 'internal_notification',
  },
  {
    id: '4',
    to: 'mike.wilson@example.com',
    subject: 'Payment Due - Action Required',
    template: 'Payment Reminder',
    status: 'bounced',
    sentAt: '2025-11-06T12:15:00Z',
    opened: false,
    clicked: false,
    type: 'billing',
  },
  {
    id: '5',
    to: 'sarah.davis@example.com',
    subject: 'Payment Failed - Immediate Action Required',
    template: 'Payment Failed',
    status: 'failed',
    sentAt: '2025-11-06T11:30:00Z',
    opened: false,
    clicked: false,
    type: 'billing',
  },
];

// Mock notification settings
const mockNotificationSettings = {
  client_onboarding_enabled: true,
  client_dispute_updates_enabled: true,
  client_payment_reminders_enabled: true,
  client_monthly_reports_enabled: true,
  admin_new_client_alert: true,
  admin_payment_failed_alert: true,
  admin_dispute_milestone_alert: true,
  admin_system_alerts_enabled: true,
  admin_emails: ['admin@creditrepairpro.com', 'ops@creditrepairpro.com'],
  daily_digest_enabled: true,
  max_emails_per_day: 1000,
  max_emails_per_client_per_day: 3,
};

export default function NotificationsPage() {
  const [activeTab, setActiveTab] = useState('overview');
  const [searchQuery, setSearchQuery] = useState('');
  const [statusFilter, setStatusFilter] = useState('all');
  const [categoryFilter, setCategoryFilter] = useState('all');
  const [isTemplateDialogOpen, setIsTemplateDialogOpen] = useState(false);
  const [isSettingsDialogOpen, setIsSettingsDialogOpen] = useState(false);
  const [selectedTemplate, setSelectedTemplate] = useState<any>(null);
  const [notificationSettings, setNotificationSettings] = useState(mockNotificationSettings);

  const queryClient = useQueryClient();

  // Email template mutations
  const createTemplateMutation = useMutation({
    mutationFn: async (data: any) => {
      console.log('Creating template:', data);
      return { success: true };
    },
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['email-templates'] });
      setIsTemplateDialogOpen(false);
    },
  });

  const updateTemplateMutation = useMutation({
    mutationFn: async ({ id, data }: any) => {
      console.log('Updating template:', id, data);
      return { success: true };
    },
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['email-templates'] });
    },
  });

  const deleteTemplateMutation = useMutation({
    mutationFn: async (id: string) => {
      console.log('Deleting template:', id);
      return { success: true };
    },
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['email-templates'] });
    },
  });

  const updateSettingsMutation = useMutation({
    mutationFn: async (data: any) => {
      console.log('Updating notification settings:', data);
      return { success: true };
    },
    onSuccess: () => {
      setIsSettingsDialogOpen(false);
    },
  });

  // Email analytics data
  const emailAnalytics = {
    totalSent: 1250,
    totalDelivered: 1180,
    totalOpened: 890,
    totalClicked: 156,
    deliveryRate: 94.4,
    openRate: 75.4,
    clickRate: 17.5,
    bounceRate: 2.8,
  };

  const filteredLogs = mockEmailLogs.filter(log => {
    const matchesSearch = log.to.toLowerCase().includes(searchQuery.toLowerCase()) ||
                         log.subject.toLowerCase().includes(searchQuery.toLowerCase());
    const matchesStatus = statusFilter === 'all' || log.status === statusFilter;
    const matchesCategory = categoryFilter === 'all' || log.type === categoryFilter;
    return matchesSearch && matchesStatus && matchesCategory;
  });

  const handleCreateTemplate = (e: React.FormEvent<HTMLFormElement>) => {
    e.preventDefault();
    const formData = new FormData(e.currentTarget);
    const data = {
      name: formData.get('name') as string,
      category: formData.get('category') as string,
      subject: formData.get('subject') as string,
      description: formData.get('description') as string,
      isActive: formData.get('isActive') === 'on',
    };
    createTemplateMutation.mutate(data);
  };

  return (
    <div className="space-y-6">
      {/* Header */}
      <div className="flex justify-between items-center">
        <div>
          <h1 className="text-3xl font-bold">Email & Notifications</h1>
          <p className="text-gray-600 mt-2">Manage email templates, notifications, and communication settings</p>
        </div>
        <div className="flex gap-2">
          <Button variant="outline" onClick={() => setIsSettingsDialogOpen(true)}>
            <Settings className="w-4 h-4 mr-2" />
            Settings
          </Button>
          <Button onClick={() => setIsTemplateDialogOpen(true)}>
            <Plus className="w-4 h-4 mr-2" />
            New Template
          </Button>
        </div>
      </div>

      {/* Analytics Overview */}
      <div className="grid gap-6 md:grid-cols-2 lg:grid-cols-4">
        <Card>
          <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
            <CardTitle className="text-sm font-medium">Total Sent</CardTitle>
            <Mail className="h-4 w-4 text-blue-600" />
          </CardHeader>
          <CardContent>
            <div className="text-2xl font-bold">{emailAnalytics.totalSent.toLocaleString()}</div>
            <p className="text-xs text-gray-600">
              +12% from last month
            </p>
          </CardContent>
        </Card>

        <Card>
          <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
            <CardTitle className="text-sm font-medium">Delivery Rate</CardTitle>
            <CheckCircle2 className="h-4 w-4 text-green-600" />
          </CardHeader>
          <CardContent>
            <div className="text-2xl font-bold text-green-600">
              {emailAnalytics.deliveryRate}%
            </div>
            <p className="text-xs text-gray-600">
              {emailAnalytics.totalDelivered} delivered
            </p>
          </CardContent>
        </Card>

        <Card>
          <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
            <CardTitle className="text-sm font-medium">Open Rate</CardTitle>
            <Eye className="h-4 w-4 text-orange-600" />
          </CardHeader>
          <CardContent>
            <div className="text-2xl font-bold text-orange-600">
              {emailAnalytics.openRate}%
            </div>
            <p className="text-xs text-gray-600">
              {emailAnalytics.totalOpened} opened
            </p>
          </CardContent>
        </Card>

        <Card>
          <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
            <CardTitle className="text-sm font-medium">Click Rate</CardTitle>
            <TrendingUp className="h-4 w-4 text-purple-600" />
          </CardHeader>
          <CardContent>
            <div className="text-2xl font-bold text-purple-600">
              {emailAnalytics.clickRate}%
            </div>
            <p className="text-xs text-gray-600">
              {emailAnalytics.totalClicked} clicked
            </p>
          </CardContent>
        </Card>
      </div>

      {/* Main Content Tabs */}
      <Tabs value={activeTab} onValueChange={setActiveTab} className="space-y-4">
        <TabsList>
          <TabsTrigger value="overview">Email Logs</TabsTrigger>
          <TabsTrigger value="templates">Templates</TabsTrigger>
          <TabsTrigger value="settings">Notification Settings</TabsTrigger>
          <TabsTrigger value="analytics">Analytics</TabsTrigger>
        </TabsList>

        {/* Email Logs Tab */}
        <TabsContent value="overview" className="space-y-4">
          <Card>
            <CardHeader>
              <div className="flex justify-between items-center">
                <div>
                  <CardTitle>Email Activity Log</CardTitle>
                  <CardDescription>Track all sent emails and their status</CardDescription>
                </div>
                <Button variant="outline" size="sm">
                  <Download className="w-4 h-4 mr-2" />
                  Export Log
                </Button>
              </div>
            </CardHeader>
            <CardContent>
              {/* Filters */}
              <div className="flex gap-4 mb-6">
                <div className="flex-1 relative">
                  <Search className="absolute left-3 top-3 h-4 w-4 text-gray-400" />
                  <Input
                    placeholder="Search by email or subject..."
                    value={searchQuery}
                    onChange={(e) => setSearchQuery(e.target.value)}
                    className="pl-10"
                  />
                </div>
                <select
                  value={statusFilter}
                  onChange={(e) => setStatusFilter(e.target.value)}
                  className="px-4 py-2 border border-gray-300 rounded-md"
                >
                  <option value="all">All Status</option>
                  <option value="delivered">Delivered</option>
                  <option value="bounced">Bounced</option>
                  <option value="failed">Failed</option>
                  <option value="opened">Opened</option>
                </select>
                <select
                  value={categoryFilter}
                  onChange={(e) => setCategoryFilter(e.target.value)}
                  className="px-4 py-2 border border-gray-300 rounded-md"
                >
                  <option value="all">All Categories</option>
                  <option value="client_communication">Client Communication</option>
                  <option value="billing">Billing</option>
                  <option value="internal_notification">Internal</option>
                </select>
              </div>

              {/* Email Logs Table */}
              <Table>
                <TableHeader>
                  <TableRow>
                    <TableHead>Recipient</TableHead>
                    <TableHead>Subject</TableHead>
                    <TableHead>Template</TableHead>
                    <TableHead>Type</TableHead>
                    <TableHead>Status</TableHead>
                    <TableHead>Sent</TableHead>
                    <TableHead>Engagement</TableHead>
                  </TableRow>
                </TableHeader>
                <TableBody>
                  {filteredLogs.map((log) => (
                    <TableRow key={log.id}>
                      <TableCell className="font-medium">{log.to}</TableCell>
                      <TableCell className="max-w-xs truncate">{log.subject}</TableCell>
                      <TableCell>
                        <Badge variant="outline">{log.template}</Badge>
                      </TableCell>
                      <TableCell>
                        <Badge
                          variant={
                            log.type === 'client_communication' ? 'default' :
                            log.type === 'billing' ? 'secondary' : 'outline'
                          }
                        >
                          {log.type.replace('_', ' ')}
                        </Badge>
                      </TableCell>
                      <TableCell>
                        <StatusBadge status={log.status} />
                      </TableCell>
                      <TableCell className="text-sm">
                        {new Date(log.sentAt).toLocaleString()}
                      </TableCell>
                      <TableCell>
                        <div className="flex items-center gap-2">
                          {log.opened && <Eye className="w-4 h-4 text-green-600" />}
                          {log.clicked && <TrendingUp className="w-4 h-4 text-blue-600" />}
                          {!log.opened && !log.clicked && (
                            <span className="text-gray-400 text-sm">No engagement</span>
                          )}
                        </div>
                      </TableCell>
                    </TableRow>
                  ))}
                </TableBody>
              </Table>
            </CardContent>
          </Card>
        </TabsContent>

        {/* Templates Tab */}
        <TabsContent value="templates" className="space-y-4">
          <div className="grid gap-6">
            {mockEmailTemplates.map((template) => (
              <Card key={template.id}>
                <CardHeader>
                  <div className="flex justify-between items-start">
                    <div className="flex-1">
                      <div className="flex items-center gap-3">
                        <CardTitle className="text-lg">{template.name}</CardTitle>
                        <Badge variant={template.isActive ? 'success' : 'secondary'}>
                          {template.isActive ? 'Active' : 'Inactive'}
                        </Badge>
                        <Badge variant="outline">{template.category.replace('_', ' ')}</Badge>
                      </div>
                      <CardDescription className="mt-1">
                        <strong>Subject:</strong> {template.subject}
                      </CardDescription>
                      <CardDescription className="mt-1">
                        {template.description}
                      </CardDescription>
                      <div className="mt-2 flex items-center gap-4 text-sm text-gray-600">
                        <span>Used {template.usage} times</span>
                        <span>Variables: {template.variables.join(', ')}</span>
                        <span>Modified: {new Date(template.lastModified).toLocaleDateString()}</span>
                      </div>
                    </div>
                    <div className="flex items-center gap-2">
                      <Button
                        variant="ghost"
                        size="sm"
                        onClick={() => {
                          setSelectedTemplate(template);
                          setIsTemplateDialogOpen(true);
                        }}
                      >
                        <Edit className="w-4 h-4" />
                      </Button>
                      <Button
                        variant="ghost"
                        size="sm"
                        onClick={() => {
                          if (confirm('Are you sure you want to delete this template?')) {
                            deleteTemplateMutation.mutate(template.id);
                          }
                        }}
                      >
                        <Trash2 className="w-4 h-4 text-red-600" />
                      </Button>
                    </div>
                  </div>
                </CardHeader>
              </Card>
            ))}
          </div>
        </TabsContent>

        {/* Settings Tab */}
        <TabsContent value="settings" className="space-y-4">
          <div className="grid gap-6 md:grid-cols-2">
            <Card>
              <CardHeader>
                <CardTitle>Client Communication</CardTitle>
                <CardDescription>Configure client-facing email notifications</CardDescription>
              </CardHeader>
              <CardContent className="space-y-4">
                <div className="flex items-center justify-between">
                  <div>
                    <Label htmlFor="client-onboarding">Onboarding Emails</Label>
                    <p className="text-sm text-gray-600">Welcome and setup emails for new clients</p>
                  </div>
                  <Switch
                    id="client-onboarding"
                    checked={notificationSettings.client_onboarding_enabled}
                    onChange={(checked) => 
                      setNotificationSettings(prev => ({ ...prev, client_onboarding_enabled: checked }))
                    }
                  />
                </div>
                <div className="flex items-center justify-between">
                  <div>
                    <Label htmlFor="client-disputes">Dispute Updates</Label>
                    <p className="text-sm text-gray-600">Status updates for credit disputes</p>
                  </div>
                  <Switch
                    id="client-disputes"
                    checked={notificationSettings.client_dispute_updates_enabled}
                    onChange={(checked) => 
                      setNotificationSettings(prev => ({ ...prev, client_dispute_updates_enabled: checked }))
                    }
                  />
                </div>
                <div className="flex items-center justify-between">
                  <div>
                    <Label htmlFor="client-payments">Payment Reminders</Label>
                    <p className="text-sm text-gray-600">Due date and overdue payment notifications</p>
                  </div>
                  <Switch
                    id="client-payments"
                    checked={notificationSettings.client_payment_reminders_enabled}
                    onChange={(checked) => 
                      setNotificationSettings(prev => ({ ...prev, client_payment_reminders_enabled: checked }))
                    }
                  />
                </div>
                <div className="flex items-center justify-between">
                  <div>
                    <Label htmlFor="client-reports">Monthly Reports</Label>
                    <p className="text-sm text-gray-600">Summary reports sent to clients</p>
                  </div>
                  <Switch
                    id="client-reports"
                    checked={notificationSettings.client_monthly_reports_enabled}
                    onChange={(checked) => 
                      setNotificationSettings(prev => ({ ...prev, client_monthly_reports_enabled: checked }))
                    }
                  />
                </div>
              </CardContent>
            </Card>

            <Card>
              <CardHeader>
                <CardTitle>Internal Notifications</CardTitle>
                <CardDescription>Alerts and notifications for your team</CardDescription>
              </CardHeader>
              <CardContent className="space-y-4">
                <div className="flex items-center justify-between">
                  <div>
                    <Label htmlFor="admin-clients">New Client Alerts</Label>
                    <p className="text-sm text-gray-600">Notify when new clients sign up</p>
                  </div>
                  <Switch
                    id="admin-clients"
                    checked={notificationSettings.admin_new_client_alert}
                    onChange={(checked) => 
                      setNotificationSettings(prev => ({ ...prev, admin_new_client_alert: checked }))
                    }
                  />
                </div>
                <div className="flex items-center justify-between">
                  <div>
                    <Label htmlFor="admin-payments">Payment Failures</Label>
                    <p className="text-sm text-gray-600">Alerts for failed payment attempts</p>
                  </div>
                  <Switch
                    id="admin-payments"
                    checked={notificationSettings.admin_payment_failed_alert}
                    onChange={(checked) => 
                      setNotificationSettings(prev => ({ ...prev, admin_payment_failed_alert: checked }))
                    }
                  />
                </div>
                <div className="flex items-center justify-between">
                  <div>
                    <Label htmlFor="admin-disputes">Dispute Milestones</Label>
                    <p className="text-sm text-gray-600">Important dispute status changes</p>
                  </div>
                  <Switch
                    id="admin-disputes"
                    checked={notificationSettings.admin_dispute_milestone_alert}
                    onChange={(checked) => 
                      setNotificationSettings(prev => ({ ...prev, admin_dispute_milestone_alert: checked }))
                    }
                  />
                </div>
                <div className="flex items-center justify-between">
                  <div>
                    <Label htmlFor="admin-system">System Alerts</Label>
                    <p className="text-sm text-gray-600">System errors and performance issues</p>
                  </div>
                  <Switch
                    id="admin-system"
                    checked={notificationSettings.admin_system_alerts_enabled}
                    onChange={(checked) => 
                      setNotificationSettings(prev => ({ ...prev, admin_system_alerts_enabled: checked }))
                    }
                  />
                </div>
              </CardContent>
            </Card>
          </div>
        </TabsContent>

        {/* Analytics Tab */}
        <TabsContent value="analytics" className="space-y-4">
          <div className="grid gap-6 md:grid-cols-2">
            <Card>
              <CardHeader>
                <CardTitle>Delivery Performance</CardTitle>
                <CardDescription>Email delivery and bounce metrics</CardDescription>
              </CardHeader>
              <CardContent className="space-y-4">
                <div className="flex justify-between items-center">
                  <span className="text-sm font-medium">Delivery Rate</span>
                  <span className="text-2xl font-bold text-green-600">{emailAnalytics.deliveryRate}%</span>
                </div>
                <div className="flex justify-between items-center">
                  <span className="text-sm font-medium">Bounce Rate</span>
                  <span className="text-2xl font-bold text-red-600">{emailAnalytics.bounceRate}%</span>
                </div>
                <div className="flex justify-between items-center">
                  <span className="text-sm font-medium">Total Delivered</span>
                  <span className="text-lg font-semibold">{emailAnalytics.totalDelivered.toLocaleString()}</span>
                </div>
              </CardContent>
            </Card>

            <Card>
              <CardHeader>
                <CardTitle>Engagement Metrics</CardTitle>
                <CardDescription>Open and click-through rates</CardDescription>
              </CardHeader>
              <CardContent className="space-y-4">
                <div className="flex justify-between items-center">
                  <span className="text-sm font-medium">Open Rate</span>
                  <span className="text-2xl font-bold text-orange-600">{emailAnalytics.openRate}%</span>
                </div>
                <div className="flex justify-between items-center">
                  <span className="text-sm font-medium">Click Rate</span>
                  <span className="text-2xl font-bold text-blue-600">{emailAnalytics.clickRate}%</span>
                </div>
                <div className="flex justify-between items-center">
                  <span className="text-sm font-medium">Total Opens</span>
                  <span className="text-lg font-semibold">{emailAnalytics.totalOpened.toLocaleString()}</span>
                </div>
              </CardContent>
            </Card>
          </div>
        </TabsContent>
      </Tabs>

      {/* Template Dialog */}
      <Dialog open={isTemplateDialogOpen} onOpenChange={setIsTemplateDialogOpen}>
        <DialogContent className="sm:max-w-2xl">
          <form onSubmit={handleCreateTemplate}>
            <DialogHeader>
              <DialogTitle>
                {selectedTemplate ? 'Edit Email Template' : 'Create Email Template'}
              </DialogTitle>
              <DialogDescription>
                Create or modify email templates for automated communications
              </DialogDescription>
            </DialogHeader>
            <div className="grid gap-4 py-4">
              <div className="grid grid-cols-2 gap-4">
                <div className="space-y-2">
                  <Label htmlFor="template-name">Template Name</Label>
                  <Input
                    id="template-name"
                    name="name"
                    defaultValue={selectedTemplate?.name || ''}
                    required
                  />
                </div>
                <div className="space-y-2">
                  <Label htmlFor="template-category">Category</Label>
                  <select
                    id="template-category"
                    name="category"
                    defaultValue={selectedTemplate?.category || 'client_communication'}
                    className="w-full px-4 py-2 border border-gray-300 rounded-md"
                    required
                  >
                    <option value="client_communication">Client Communication</option>
                    <option value="billing">Billing</option>
                    <option value="internal_notification">Internal Notification</option>
                  </select>
                </div>
              </div>
              <div className="space-y-2">
                <Label htmlFor="template-subject">Subject Line</Label>
                <Input
                  id="template-subject"
                  name="subject"
                  defaultValue={selectedTemplate?.subject || ''}
                  placeholder="Use {{variable_name}} for dynamic content"
                  required
                />
              </div>
              <div className="space-y-2">
                <Label htmlFor="template-description">Description</Label>
                <Input
                  id="template-description"
                  name="description"
                  defaultValue={selectedTemplate?.description || ''}
                  placeholder="When and why this template is used"
                />
              </div>
              <div className="space-y-2">
                <Label htmlFor="template-content">Email Content</Label>
                <Textarea
                  id="template-content"
                  name="content"
                  rows={10}
                  placeholder="Enter your email template content here...&#10;&#10;Use {{variable_name}} for dynamic content.&#10;&#10;HTML and plain text versions supported."
                />
              </div>
              <div className="flex items-center space-x-2">
                <input
                  type="checkbox"
                  id="template-active"
                  name="isActive"
                  defaultChecked={selectedTemplate?.isActive ?? true}
                />
                <Label htmlFor="template-active">Active (can be used in automations)</Label>
              </div>
            </div>
            <DialogFooter>
              <Button type="button" variant="outline" onClick={() => setIsTemplateDialogOpen(false)}>
                Cancel
              </Button>
              <Button type="submit" disabled={createTemplateMutation.isPending}>
                {selectedTemplate ? 'Update Template' : 'Create Template'}
              </Button>
            </DialogFooter>
          </form>
        </DialogContent>
      </Dialog>
    </div>
  );
}

function StatusBadge({ status }: { status: string }) {
  const config: Record<string, { label: string; className: string; icon: any }> = {
    delivered: {
      label: 'Delivered',
      className: 'bg-green-100 text-green-800',
      icon: CheckCircle2,
    },
    bounced: {
      label: 'Bounced',
      className: 'bg-red-100 text-red-800',
      icon: XCircle,
    },
    failed: {
      label: 'Failed',
      className: 'bg-red-100 text-red-800',
      icon: XCircle,
    },
    queued: {
      label: 'Queued',
      className: 'bg-yellow-100 text-yellow-800',
      icon: Clock,
    },
    sending: {
      label: 'Sending',
      className: 'bg-blue-100 text-blue-800',
      icon: Send,
    },
  };

  const { label, className, icon: Icon } = config[status] || config.queued;

  return (
    <span className={`inline-flex items-center gap-1 px-3 py-1 rounded-full text-xs font-medium ${className}`}>
      <Icon className="w-3 h-3" />
      {label}
    </span>
  );
}