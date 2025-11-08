'use client';

import { useState } from 'react';
import { useQuery } from '@tanstack/react-query';
import { 
  Shield, 
  FileText, 
  Users, 
  AlertTriangle, 
  CheckCircle2, 
  Download,
  Calendar,
  Filter,
  Search
} from 'lucide-react';
import { Button } from '@/components/ui/button';
import { Input } from '@/components/ui/input';
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '@/components/ui/card';
import {
  Table,
  TableBody,
  TableCell,
  TableHead,
  TableHeader,
  TableRow,
} from '@/components/ui/table';
import { Badge } from '@/components/ui/badge';
import { Tabs, TabsContent, TabsList, TabsTrigger } from '@/components/ui/tabs';
import {
  Select,
  SelectContent,
  SelectItem,
  SelectTrigger,
  SelectValue,
} from '@/components/ui/select';

export default function CompliancePage() {
  const [searchQuery, setSearchQuery] = useState('');
  const [dateRange, setDateRange] = useState('30d');
  const [complianceFilter, setComplianceFilter] = useState('all');

  // Mock compliance data
  const { data: complianceOverview, isLoading } = useQuery({
    queryKey: ['compliance-overview'],
    queryFn: async () => {
      // Mock data for demonstration
      return {
        totalUsers: 156,
        activeClients: 142,
        encryptedData: 100,
        auditLogs: 2847,
        complianceScore: 98,
        dataBreaches: 0,
        lastAudit: '2025-11-01',
        nextAudit: '2025-12-01',
        violations: [
          {
            id: '1',
            type: 'GDPR',
            severity: 'medium',
            description: 'Data retention period exceeded for 3 clients',
            status: 'resolved',
            date: '2025-10-15',
          },
          {
            id: '2', 
            type: 'SOC2',
            severity: 'low',
            description: 'Audit log backup delayed by 2 hours',
            status: 'in_progress',
            date: '2025-10-28',
          }
        ],
        auditLogs: [
          {
            id: '1',
            user: 'john.doe@company.com',
            action: 'client_data_access',
            resource: 'client_12345',
            ipAddress: '192.168.1.100',
            timestamp: '2025-11-06T15:30:22Z',
            status: 'success',
          },
          {
            id: '2',
            user: 'jane.smith@company.com',
            action: 'dispute_create',
            resource: 'dispute_67890',
            ipAddress: '192.168.1.105',
            timestamp: '2025-11-06T14:15:45Z',
            status: 'success',
          },
        ],
        encryptionStatus: {
          dataAtRest: 'AES-256',
          dataInTransit: 'TLS 1.3',
          keyManagement: 'AWS KMS',
          lastRotation: '2025-10-01',
        },
      };
    },
  });

  const filteredLogs = complianceOverview?.auditLogs?.filter(log =>
    log.user.toLowerCase().includes(searchQuery.toLowerCase()) ||
    log.action.toLowerCase().includes(searchQuery.toLowerCase())
  ) || [];

  return (
    <div className="space-y-6">
      {/* Header */}
      <div className="flex justify-between items-center">
        <div>
          <h1 className="text-3xl font-bold">Compliance & Security</h1>
          <p className="text-gray-600 mt-2">Monitor compliance status and security events</p>
        </div>
        <div className="flex gap-2">
          <Button variant="outline">
            <Download className="w-4 h-4 mr-2" />
            Export Report
          </Button>
          <Button>
            <Shield className="w-4 h-4 mr-2" />
            Security Scan
          </Button>
        </div>
      </div>

      {/* Compliance Overview Cards */}
      <div className="grid gap-6 md:grid-cols-2 lg:grid-cols-4">
        <Card>
          <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
            <CardTitle className="text-sm font-medium">Compliance Score</CardTitle>
            <CheckCircle2 className="h-4 w-4 text-green-600" />
          </CardHeader>
          <CardContent>
            <div className="text-2xl font-bold text-green-600">
              {complianceOverview?.complianceScore || 0}%
            </div>
            <p className="text-xs text-gray-600">
              +2% from last month
            </p>
          </CardContent>
        </Card>

        <Card>
          <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
            <CardTitle className="text-sm font-medium">Active Users</CardTitle>
            <Users className="h-4 w-4 text-blue-600" />
          </CardHeader>
          <CardContent>
            <div className="text-2xl font-bold">
              {complianceOverview?.activeClients || 0}
            </div>
            <p className="text-xs text-gray-600">
              of {complianceOverview?.totalUsers || 0} total
            </p>
          </CardContent>
        </Card>

        <Card>
          <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
            <CardTitle className="text-sm font-medium">Data Encrypted</CardTitle>
            <Shield className="h-4 w-4 text-green-600" />
          </CardHeader>
          <CardContent>
            <div className="text-2xl font-bold text-green-600">
              {complianceOverview?.encryptedData || 0}%
            </div>
            <p className="text-xs text-gray-600">
              All PII encrypted
            </p>
          </CardContent>
        </Card>

        <Card>
          <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
            <CardTitle className="text-sm font-medium">Security Incidents</CardTitle>
            <AlertTriangle className="h-4 w-4 text-green-600" />
          </CardHeader>
          <CardContent>
            <div className="text-2xl font-bold text-green-600">
              {complianceOverview?.dataBreaches || 0}
            </div>
            <p className="text-xs text-gray-600">
              Last 30 days
            </p>
          </CardContent>
        </Card>
      </div>

      {/* Compliance Tabs */}
      <Tabs defaultValue="overview" className="space-y-4">
        <TabsList>
          <TabsTrigger value="overview">Overview</TabsTrigger>
          <TabsTrigger value="audit-logs">Audit Logs</TabsTrigger>
          <TabsTrigger value="violations">Violations</TabsTrigger>
          <TabsTrigger value="encryption">Encryption</TabsTrigger>
        </TabsList>

        <TabsContent value="overview" className="space-y-4">
          <div className="grid gap-6 md:grid-cols-2">
            <Card>
              <CardHeader>
                <CardTitle>Recent Compliance Activities</CardTitle>
                <CardDescription>Latest security and compliance events</CardDescription>
              </CardHeader>
              <CardContent>
                <div className="space-y-4">
                  {[
                    { action: 'Data encryption key rotated', time: '2 hours ago', status: 'success' },
                    { action: 'Security scan completed', time: '1 day ago', status: 'success' },
                    { action: 'User access review', time: '3 days ago', status: 'warning' },
                    { action: 'Backup verification', time: '1 week ago', status: 'success' },
                  ].map((activity, index) => (
                    <div key={index} className="flex items-center justify-between">
                      <div className="flex items-center gap-3">
                        <div className={`w-2 h-2 rounded-full ${
                          activity.status === 'success' ? 'bg-green-500' : 'bg-yellow-500'
                        }`} />
                        <div>
                          <p className="text-sm font-medium">{activity.action}</p>
                          <p className="text-xs text-gray-500">{activity.time}</p>
                        </div>
                      </div>
                      <Badge variant={activity.status === 'success' ? 'default' : 'secondary'}>
                        {activity.status}
                      </Badge>
                    </div>
                  ))}
                </div>
              </CardContent>
            </Card>

            <Card>
              <CardHeader>
                <CardTitle>Compliance Deadlines</CardTitle>
                <CardDescription>Upcoming compliance requirements</CardDescription>
              </CardHeader>
              <CardContent>
                <div className="space-y-4">
                  {[
                    { task: 'Annual SOC 2 audit', due: '2025-12-01', type: 'SOC2' },
                    { task: 'Data retention review', due: '2025-11-15', type: 'GDPR' },
                    { task: 'Security training', due: '2025-11-30', type: 'Internal' },
                    { task: 'Penetration testing', due: '2025-12-15', type: 'Security' },
                  ].map((deadline, index) => (
                    <div key={index} className="flex items-center justify-between">
                      <div>
                        <p className="text-sm font-medium">{deadline.task}</p>
                        <p className="text-xs text-gray-500">{deadline.due}</p>
                      </div>
                      <Badge variant="outline">{deadline.type}</Badge>
                    </div>
                  ))}
                </div>
              </CardContent>
            </Card>
          </div>
        </TabsContent>

        <TabsContent value="audit-logs" className="space-y-4">
          <Card>
            <CardHeader>
              <div className="flex justify-between items-center">
                <div>
                  <CardTitle>Audit Log Viewer</CardTitle>
                  <CardDescription>Track all system access and data modifications</CardDescription>
                </div>
                <Button variant="outline" size="sm">
                  <Download className="w-4 h-4 mr-2" />
                  Export Logs
                </Button>
              </div>
            </CardHeader>
            <CardContent>
              {/* Search and Filters */}
              <div className="flex gap-4 mb-6">
                <div className="flex-1 relative">
                  <Search className="absolute left-3 top-3 h-4 w-4 text-gray-400" />
                  <Input
                    placeholder="Search logs by user or action..."
                    value={searchQuery}
                    onChange={(e) => setSearchQuery(e.target.value)}
                    className="pl-10"
                  />
                </div>
                <Select value={dateRange} onValueChange={setDateRange}>
                  <SelectTrigger className="w-32">
                    <SelectValue />
                  </SelectTrigger>
                  <SelectContent>
                    <SelectItem value="7d">Last 7 days</SelectItem>
                    <SelectItem value="30d">Last 30 days</SelectItem>
                    <SelectItem value="90d">Last 90 days</SelectItem>
                  </SelectContent>
                </Select>
              </div>

              {/* Audit Logs Table */}
              <Table>
                <TableHeader>
                  <TableRow>
                    <TableHead>Timestamp</TableHead>
                    <TableHead>User</TableHead>
                    <TableHead>Action</TableHead>
                    <TableHead>Resource</TableHead>
                    <TableHead>IP Address</TableHead>
                    <TableHead>Status</TableHead>
                  </TableRow>
                </TableHeader>
                <TableBody>
                  {filteredLogs.map((log) => (
                    <TableRow key={log.id}>
                      <TableCell className="font-mono text-sm">
                        {new Date(log.timestamp).toLocaleString()}
                      </TableCell>
                      <TableCell className="font-medium">{log.user}</TableCell>
                      <TableCell>
                        <Badge variant="outline">{log.action}</Badge>
                      </TableCell>
                      <TableCell className="font-mono text-sm">
                        {log.resource?.slice(0, 12)}...
                      </TableCell>
                      <TableCell className="font-mono text-sm">{log.ipAddress}</TableCell>
                      <TableCell>
                        <Badge 
                          variant={log.status === 'success' ? 'default' : 'destructive'}
                        >
                          {log.status}
                        </Badge>
                      </TableCell>
                    </TableRow>
                  ))}
                </TableBody>
              </Table>
            </CardContent>
          </Card>
        </TabsContent>

        <TabsContent value="violations" className="space-y-4">
          <Card>
            <CardHeader>
              <CardTitle>Compliance Violations</CardTitle>
              <CardDescription>Track and resolve compliance issues</CardDescription>
            </CardHeader>
            <CardContent>
              <Table>
                <TableHeader>
                  <TableRow>
                    <TableHead>Type</TableHead>
                    <TableHead>Severity</TableHead>
                    <TableHead>Description</TableHead>
                    <TableHead>Status</TableHead>
                    <TableHead>Date</TableHead>
                    <TableHead className="text-right">Actions</TableHead>
                  </TableRow>
                </TableHeader>
                <TableBody>
                  {complianceOverview?.violations?.map((violation) => (
                    <TableRow key={violation.id}>
                      <TableCell>
                        <Badge variant="outline">{violation.type}</Badge>
                      </TableCell>
                      <TableCell>
                        <Badge 
                          variant={violation.severity === 'high' ? 'destructive' : 
                                   violation.severity === 'medium' ? 'secondary' : 'outline'}
                        >
                          {violation.severity}
                        </Badge>
                      </TableCell>
                      <TableCell className="max-w-xs">{violation.description}</TableCell>
                      <TableCell>
                        <Badge 
                          variant={violation.status === 'resolved' ? 'default' : 'secondary'}
                        >
                          {violation.status}
                        </Badge>
                      </TableCell>
                      <TableCell>{new Date(violation.date).toLocaleDateString()}</TableCell>
                      <TableCell className="text-right">
                        <Button variant="ghost" size="sm">
                          Resolve
                        </Button>
                      </TableCell>
                    </TableRow>
                  ))}
                </TableBody>
              </Table>
            </CardContent>
          </Card>
        </TabsContent>

        <TabsContent value="encryption" className="space-y-4">
          <div className="grid gap-6 md:grid-cols-2">
            <Card>
              <CardHeader>
                <CardTitle>Encryption Status</CardTitle>
                <CardDescription>Current encryption configuration</CardDescription>
              </CardHeader>
              <CardContent>
                <div className="space-y-4">
                  <div className="flex justify-between items-center">
                    <span className="text-sm font-medium">Data at Rest</span>
                    <Badge variant="default">{complianceOverview?.encryptionStatus?.dataAtRest}</Badge>
                  </div>
                  <div className="flex justify-between items-center">
                    <span className="text-sm font-medium">Data in Transit</span>
                    <Badge variant="default">{complianceOverview?.encryptionStatus?.dataInTransit}</Badge>
                  </div>
                  <div className="flex justify-between items-center">
                    <span className="text-sm font-medium">Key Management</span>
                    <Badge variant="default">{complianceOverview?.encryptionStatus?.keyManagement}</Badge>
                  </div>
                  <div className="flex justify-between items-center">
                    <span className="text-sm font-medium">Last Rotation</span>
                    <span className="text-sm text-gray-600">
                      {complianceOverview?.encryptionStatus?.lastRotation}
                    </span>
                  </div>
                </div>
              </CardContent>
            </Card>

            <Card>
              <CardHeader>
                <CardTitle>Encryption Health</CardTitle>
                <CardDescription>Encryption system status</CardDescription>
              </CardHeader>
              <CardContent>
                <div className="space-y-4">
                  <div className="flex items-center justify-between">
                    <div className="flex items-center gap-2">
                      <CheckCircle2 className="w-4 h-4 text-green-600" />
                      <span className="text-sm">SSL Certificates Valid</span>
                    </div>
                    <Badge variant="default">Valid</Badge>
                  </div>
                  <div className="flex items-center justify-between">
                    <div className="flex items-center gap-2">
                      <CheckCircle2 className="w-4 h-4 text-green-600" />
                      <span className="text-sm">Database Encryption</span>
                    </div>
                    <Badge variant="default">Active</Badge>
                  </div>
                  <div className="flex items-center justify-between">
                    <div className="flex items-center gap-2">
                      <CheckCircle2 className="w-4 h-4 text-green-600" />
                      <span className="text-sm">Backup Encryption</span>
                    </div>
                    <Badge variant="default">Enabled</Badge>
                  </div>
                  <div className="flex items-center justify-between">
                    <div className="flex items-center gap-2">
                      <AlertTriangle className="w-4 h-4 text-yellow-600" />
                      <span className="text-sm">Key Rotation Due</span>
                    </div>
                    <Badge variant="secondary">30 days</Badge>
                  </div>
                </div>
              </CardContent>
            </Card>
          </div>
        </TabsContent>
      </Tabs>
    </div>
  );
}