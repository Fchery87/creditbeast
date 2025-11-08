'use client';

import { useState, useRef } from 'react';
import { useQuery, useMutation, useQueryClient } from '@tanstack/react-query';
import { 
  Upload, 
  File, 
  FileText, 
  Image, 
  Download, 
  Eye, 
  Trash2, 
  Search, 
  Filter,
  FolderOpen,
  Clock,
  User,
  Shield,
  CheckCircle2,
  XCircle,
  AlertTriangle,
  Plus,
  Grid,
  List,
  SortAsc,
  SortDesc
} from 'lucide-react';
import { Button } from '@/components/ui/button';
import { Input } from '@/components/ui/input';
import { Label } from '@/components/ui/label';
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

// Mock document data
const mockDocuments = [
  {
    id: '1',
    name: 'Credit Report - Equifax.pdf',
    clientId: 'client_1',
    clientName: 'John Doe',
    category: 'credit_report',
    fileType: 'pdf',
    fileSize: 2847123, // bytes
    status: 'verified',
    uploadedAt: '2025-11-06T10:30:00Z',
    uploadedBy: 'admin@creditrepairpro.com',
    tags: ['equifax', 'monthly'],
    encryptionStatus: 'encrypted',
    retentionUntil: '2028-11-06T00:00:00Z',
    downloadCount: 5,
    accessLog: [
      { user: 'admin@creditrepairpro.com', action: 'view', timestamp: '2025-11-06T15:30:00Z' },
      { user: 'user@creditrepairpro.com', action: 'download', timestamp: '2025-11-05T14:20:00Z' },
    ],
  },
  {
    id: '2',
    name: 'Driver License - Front.jpg',
    clientId: 'client_1',
    clientName: 'John Doe',
    category: 'identification',
    fileType: 'image',
    fileSize: 1248756,
    status: 'verified',
    uploadedAt: '2025-11-05T09:15:00Z',
    uploadedBy: 'admin@creditrepairpro.com',
    tags: ['id', 'government'],
    encryptionStatus: 'encrypted',
    retentionUntil: '2028-11-05T00:00:00Z',
    downloadCount: 2,
    accessLog: [
      { user: 'admin@creditrepairpro.com', action: 'upload', timestamp: '2025-11-05T09:15:00Z' },
    ],
  },
  {
    id: '3',
    name: 'Chase Bank Statement - Oct 2025.pdf',
    clientId: 'client_2',
    clientName: 'Jane Smith',
    category: 'bank_statement',
    fileType: 'pdf',
    fileSize: 1562340,
    status: 'pending_review',
    uploadedAt: '2025-11-04T16:45:00Z',
    uploadedBy: 'jane.smith@client.com',
    tags: ['bank', 'chase', 'monthly'],
    encryptionStatus: 'encrypted',
    retentionUntil: '2027-11-04T00:00:00Z',
    downloadCount: 1,
    accessLog: [
      { user: 'jane.smith@client.com', action: 'upload', timestamp: '2025-11-04T16:45:00Z' },
    ],
  },
  {
    id: '4',
    name: 'Medical Records - Dr. Johnson.pdf',
    clientId: 'client_2',
    clientName: 'Jane Smith',
    category: 'medical_record',
    fileType: 'pdf',
    fileSize: 3456789,
    status: 'flagged',
    uploadedAt: '2025-11-03T11:20:00Z',
    uploadedBy: 'admin@creditrepairpro.com',
    tags: ['medical', 'hipaa'],
    encryptionStatus: 'encrypted',
    retentionUntil: '2027-11-03T00:00:00Z',
    downloadCount: 8,
    accessLog: [
      { user: 'admin@creditrepairpro.com', action: 'upload', timestamp: '2025-11-03T11:20:00Z' },
      { user: 'admin@creditrepairpro.com', action: 'flag', timestamp: '2025-11-03T11:25:00Z' },
    ],
  },
  {
    id: '5',
    name: 'Letter - Equifax Response.pdf',
    clientId: 'client_3',
    clientName: 'Bob Wilson',
    category: 'correspondence',
    fileType: 'pdf',
    fileSize: 987654,
    status: 'verified',
    uploadedAt: '2025-11-02T14:10:00Z',
    uploadedBy: 'admin@creditrepairpro.com',
    tags: ['equifax', 'response'],
    encryptionStatus: 'encrypted',
    retentionUntil: '2028-11-02T00:00:00Z',
    downloadCount: 3,
    accessLog: [
      { user: 'admin@creditrepairpro.com', action: 'upload', timestamp: '2025-11-02T14:10:00Z' },
    ],
  },
];

const documentCategories = [
  { value: 'all', label: 'All Documents', count: mockDocuments.length },
  { value: 'credit_report', label: 'Credit Reports', count: 12 },
  { value: 'identification', label: 'Identification', count: 8 },
  { value: 'bank_statement', label: 'Bank Statements', count: 15 },
  { value: 'medical_record', label: 'Medical Records', count: 6 },
  { value: 'correspondence', label: 'Correspondence', count: 9 },
  { value: 'legal_document', label: 'Legal Documents', count: 4 },
  { value: 'income_verification', label: 'Income Verification', count: 7 },
];

export default function DocumentsPage() {
  const [viewMode, setViewMode] = useState<'grid' | 'list'>('list');
  const [searchQuery, setSearchQuery] = useState('');
  const [categoryFilter, setCategoryFilter] = useState('all');
  const [statusFilter, setStatusFilter] = useState('all');
  const [clientFilter, setClientFilter] = useState('all');
  const [sortBy, setSortBy] = useState<'name' | 'date' | 'size' | 'client'>('date');
  const [sortOrder, setSortOrder] = useState<'asc' | 'desc'>('desc');
  const [isUploadDialogOpen, setIsUploadDialogOpen] = useState(false);
  const [isViewDialogOpen, setIsViewDialogOpen] = useState(false);
  const [selectedDocument, setSelectedDocument] = useState<any>(null);
  const [uploadedFiles, setUploadedFiles] = useState<File[]>([]);
  const fileInputRef = useRef<HTMLInputElement>(null);

  const queryClient = useQueryClient();

  // Upload documents mutation
  const uploadDocumentsMutation = useMutation({
    mutationFn: async (files: File[]) => {
      // Mock upload API call
      console.log('Uploading files:', files);
      return { success: true, uploaded: files.length };
    },
    onSuccess: (result) => {
      queryClient.invalidateQueries({ queryKey: ['documents'] });
      setIsUploadDialogOpen(false);
      setUploadedFiles([]);
      console.log(`Successfully uploaded ${result.uploaded} files`);
    },
  });

  // Delete document mutation
  const deleteDocumentMutation = useMutation({
    mutationFn: async (id: string) => {
      console.log('Deleting document:', id);
      return { success: true };
    },
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['documents'] });
    },
  });

  // Download document mutation
  const downloadDocumentMutation = useMutation({
    mutationFn: async (doc: any) => {
      console.log('Downloading document:', doc.name);
      // Mock download logic
      return { success: true };
    },
  });

  // Filter and sort documents
  const filteredDocuments = mockDocuments
    .filter(doc => {
      const matchesSearch = doc.name.toLowerCase().includes(searchQuery.toLowerCase()) ||
                           doc.clientName.toLowerCase().includes(searchQuery.toLowerCase()) ||
                           doc.tags.some(tag => tag.toLowerCase().includes(searchQuery.toLowerCase()));
      const matchesCategory = categoryFilter === 'all' || doc.category === categoryFilter;
      const matchesStatus = statusFilter === 'all' || doc.status === statusFilter;
      const matchesClient = clientFilter === 'all' || doc.clientId === clientFilter;
      
      return matchesSearch && matchesCategory && matchesStatus && matchesClient;
    })
    .sort((a, b) => {
      let comparison = 0;
      switch (sortBy) {
        case 'name':
          comparison = a.name.localeCompare(b.name);
          break;
        case 'date':
          comparison = new Date(a.uploadedAt).getTime() - new Date(b.uploadedAt).getTime();
          break;
        case 'size':
          comparison = a.fileSize - b.fileSize;
          break;
        case 'client':
          comparison = a.clientName.localeCompare(b.clientName);
          break;
      }
      return sortOrder === 'asc' ? comparison : -comparison;
    });

  // Format file size
  const formatFileSize = (bytes: number) => {
    if (bytes === 0) return '0 Bytes';
    const k = 1024;
    const sizes = ['Bytes', 'KB', 'MB', 'GB'];
    const i = Math.floor(Math.log(bytes) / Math.log(k));
    return parseFloat((bytes / Math.pow(k, i)).toFixed(2)) + ' ' + sizes[i];
  };

  // Get file icon
  const getFileIcon = (fileType: string) => {
    if (fileType === 'image') return <Image className="w-5 h-5" />;
    return <FileText className="w-5 h-5" />;
  };

  // Handle file selection
  const handleFileSelect = (e: React.ChangeEvent<HTMLInputElement>) => {
    const files = Array.from(e.target.files || []);
    setUploadedFiles(prev => [...prev, ...files]);
  };

  // Remove file from upload list
  const removeFile = (index: number) => {
    setUploadedFiles(prev => prev.filter((_, i) => i !== index));
  };

  // Handle upload
  const handleUpload = () => {
    if (uploadedFiles.length === 0) return;
    uploadDocumentsMutation.mutate(uploadedFiles);
  };

  // Document stats
  const documentStats = {
    total: mockDocuments.length,
    verified: mockDocuments.filter(d => d.status === 'verified').length,
    pending: mockDocuments.filter(d => d.status === 'pending_review').length,
    flagged: mockDocuments.filter(d => d.status === 'flagged').length,
    totalSize: mockDocuments.reduce((sum, doc) => sum + doc.fileSize, 0),
  };

  return (
    <div className="space-y-6">
      {/* Header */}
      <div className="flex justify-between items-center">
        <div>
          <h1 className="text-3xl font-bold">Document Management</h1>
          <p className="text-gray-600 mt-2">Securely manage client documents and files</p>
        </div>
        <div className="flex gap-2">
          <Button
            variant="outline"
            onClick={() => setViewMode(viewMode === 'grid' ? 'list' : 'grid')}
          >
            {viewMode === 'grid' ? <List className="w-4 h-4 mr-2" /> : <Grid className="w-4 h-4 mr-2" />}
            {viewMode === 'grid' ? 'List View' : 'Grid View'}
          </Button>
          <Button onClick={() => setIsUploadDialogOpen(true)}>
            <Upload className="w-4 h-4 mr-2" />
            Upload Documents
          </Button>
        </div>
      </div>

      {/* Document Statistics */}
      <div className="grid gap-6 md:grid-cols-2 lg:grid-cols-5">
        <Card>
          <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
            <CardTitle className="text-sm font-medium">Total Documents</CardTitle>
            <File className="h-4 w-4 text-blue-600" />
          </CardHeader>
          <CardContent>
            <div className="text-2xl font-bold">{documentStats.total}</div>
            <p className="text-xs text-gray-600">
              {formatFileSize(documentStats.totalSize)} total
            </p>
          </CardContent>
        </Card>

        <Card>
          <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
            <CardTitle className="text-sm font-medium">Verified</CardTitle>
            <CheckCircle2 className="h-4 w-4 text-green-600" />
          </CardHeader>
          <CardContent>
            <div className="text-2xl font-bold text-green-600">{documentStats.verified}</div>
            <p className="text-xs text-gray-600">
              Ready for processing
            </p>
          </CardContent>
        </Card>

        <Card>
          <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
            <CardTitle className="text-sm font-medium">Pending Review</CardTitle>
            <Clock className="h-4 w-4 text-yellow-600" />
          </CardHeader>
          <CardContent>
            <div className="text-2xl font-bold text-yellow-600">{documentStats.pending}</div>
            <p className="text-xs text-gray-600">
              Needs verification
            </p>
          </CardContent>
        </Card>

        <Card>
          <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
            <CardTitle className="text-sm font-medium">Flagged</CardTitle>
            <AlertTriangle className="h-4 w-4 text-red-600" />
          </CardHeader>
          <CardContent>
            <div className="text-2xl font-bold text-red-600">{documentStats.flagged}</div>
            <p className="text-xs text-gray-600">
              Requires attention
            </p>
          </CardContent>
        </Card>

        <Card>
          <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
            <CardTitle className="text-sm font-medium">Secure Storage</CardTitle>
            <Shield className="h-4 w-4 text-purple-600" />
          </CardHeader>
          <CardContent>
            <div className="text-2xl font-bold text-purple-600">100%</div>
            <p className="text-xs text-gray-600">
              AES-256 encrypted
            </p>
          </CardContent>
        </Card>
      </div>

      {/* Filters and Search */}
      <Card>
        <CardContent className="pt-6">
          <div className="flex gap-4 items-center">
            <div className="flex-1 relative">
              <Search className="absolute left-3 top-3 h-4 w-4 text-gray-400" />
              <Input
                placeholder="Search documents, clients, or tags..."
                value={searchQuery}
                onChange={(e) => setSearchQuery(e.target.value)}
                className="pl-10"
              />
            </div>
            <select
              value={categoryFilter}
              onChange={(e) => setCategoryFilter(e.target.value)}
              className="px-4 py-2 border border-gray-300 rounded-md"
            >
              {documentCategories.map(cat => (
                <option key={cat.value} value={cat.value}>
                  {cat.label} ({cat.count})
                </option>
              ))}
            </select>
            <select
              value={statusFilter}
              onChange={(e) => setStatusFilter(e.target.value)}
              className="px-4 py-2 border border-gray-300 rounded-md"
            >
              <option value="all">All Status</option>
              <option value="verified">Verified</option>
              <option value="pending_review">Pending Review</option>
              <option value="flagged">Flagged</option>
            </select>
            <div className="flex items-center gap-2">
              <select
                value={sortBy}
                onChange={(e) => setSortBy(e.target.value as any)}
                className="px-4 py-2 border border-gray-300 rounded-md"
              >
                <option value="date">Sort by Date</option>
                <option value="name">Sort by Name</option>
                <option value="size">Sort by Size</option>
                <option value="client">Sort by Client</option>
              </select>
              <Button
                variant="outline"
                size="sm"
                onClick={() => setSortOrder(sortOrder === 'asc' ? 'desc' : 'asc')}
              >
                {sortOrder === 'asc' ? <SortAsc className="w-4 h-4" /> : <SortDesc className="w-4 h-4" />}
              </Button>
            </div>
          </div>
        </CardContent>
      </Card>

      {/* Documents List/Grid */}
      <Card>
        <CardHeader>
          <CardTitle>
            Documents ({filteredDocuments.length})
          </CardTitle>
          <CardDescription>
            Manage and review client documents
          </CardDescription>
        </CardHeader>
        <CardContent>
          {viewMode === 'list' ? (
            <Table>
              <TableHeader>
                <TableRow>
                  <TableHead>Document</TableHead>
                  <TableHead>Client</TableHead>
                  <TableHead>Category</TableHead>
                  <TableHead>Size</TableHead>
                  <TableHead>Status</TableHead>
                  <TableHead>Uploaded</TableHead>
                  <TableHead className="text-right">Actions</TableHead>
                </TableRow>
              </TableHeader>
              <TableBody>
                {filteredDocuments.map((doc) => (
                  <TableRow key={doc.id}>
                    <TableCell>
                      <div className="flex items-center gap-3">
                        {getFileIcon(doc.fileType)}
                        <div>
                          <p className="font-medium">{doc.name}</p>
                          <div className="flex gap-1 mt-1">
                            {doc.tags.slice(0, 3).map(tag => (
                              <Badge key={tag} variant="outline" className="text-xs">
                                {tag}
                              </Badge>
                            ))}
                            {doc.tags.length > 3 && (
                              <Badge variant="outline" className="text-xs">
                                +{doc.tags.length - 3}
                              </Badge>
                            )}
                          </div>
                        </div>
                      </div>
                    </TableCell>
                    <TableCell>
                      <div className="flex items-center gap-2">
                        <User className="w-4 h-4 text-gray-400" />
                        {doc.clientName}
                      </div>
                    </TableCell>
                    <TableCell>
                      <Badge variant="secondary">
                        {doc.category.replace('_', ' ')}
                      </Badge>
                    </TableCell>
                    <TableCell className="font-mono text-sm">
                      {formatFileSize(doc.fileSize)}
                    </TableCell>
                    <TableCell>
                      <StatusBadge status={doc.status} />
                    </TableCell>
                    <TableCell className="text-sm">
                      <div>
                        <p>{new Date(doc.uploadedAt).toLocaleDateString()}</p>
                        <p className="text-gray-500 text-xs">
                          by {doc.uploadedBy}
                        </p>
                      </div>
                    </TableCell>
                    <TableCell className="text-right">
                      <div className="flex justify-end gap-2">
                        <Button
                          variant="ghost"
                          size="sm"
                          onClick={() => {
                            setSelectedDocument(doc);
                            setIsViewDialogOpen(true);
                          }}
                        >
                          <Eye className="w-4 h-4" />
                        </Button>
                        <Button
                          variant="ghost"
                          size="sm"
                          onClick={() => downloadDocumentMutation.mutate(doc)}
                        >
                          <Download className="w-4 h-4" />
                        </Button>
                        <Button
                          variant="ghost"
                          size="sm"
                          onClick={() => {
                            if (confirm('Are you sure you want to delete this document?')) {
                              deleteDocumentMutation.mutate(doc.id);
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
          ) : (
            <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 xl:grid-cols-4 gap-4">
              {filteredDocuments.map((doc) => (
                <Card key={doc.id} className="cursor-pointer hover:shadow-md transition-shadow">
                  <CardContent className="p-4">
                    <div className="flex items-start justify-between mb-3">
                      <div className="flex items-center gap-2">
                        {getFileIcon(doc.fileType)}
                        <StatusBadge status={doc.status} />
                      </div>
                      <div className="flex gap-1">
                        <Button
                          variant="ghost"
                          size="sm"
                          onClick={(e) => {
                            e.stopPropagation();
                            setSelectedDocument(doc);
                            setIsViewDialogOpen(true);
                          }}
                        >
                          <Eye className="w-3 h-3" />
                        </Button>
                        <Button
                          variant="ghost"
                          size="sm"
                          onClick={(e) => {
                            e.stopPropagation();
                            downloadDocumentMutation.mutate(doc);
                          }}
                        >
                          <Download className="w-3 h-3" />
                        </Button>
                      </div>
                    </div>
                    <h4 className="font-medium text-sm mb-2 truncate">{doc.name}</h4>
                    <p className="text-xs text-gray-600 mb-2">{doc.clientName}</p>
                    <div className="flex justify-between items-center text-xs text-gray-500">
                      <span>{formatFileSize(doc.fileSize)}</span>
                      <span>{new Date(doc.uploadedAt).toLocaleDateString()}</span>
                    </div>
                    <div className="mt-2 flex flex-wrap gap-1">
                      {doc.tags.slice(0, 2).map(tag => (
                        <Badge key={tag} variant="outline" className="text-xs">
                          {tag}
                        </Badge>
                      ))}
                      {doc.tags.length > 2 && (
                        <Badge variant="outline" className="text-xs">
                          +{doc.tags.length - 2}
                        </Badge>
                      )}
                    </div>
                  </CardContent>
                </Card>
              ))}
            </div>
          )}

          {filteredDocuments.length === 0 && (
            <div className="text-center py-12">
              <FolderOpen className="w-12 h-12 text-gray-400 mx-auto mb-4" />
              <h3 className="text-lg font-medium text-gray-900 mb-2">No documents found</h3>
              <p className="text-gray-600 mb-4">
                {searchQuery || categoryFilter !== 'all' || statusFilter !== 'all'
                  ? 'Try adjusting your filters or search terms.'
                  : 'Upload your first document to get started.'}
              </p>
              <Button onClick={() => setIsUploadDialogOpen(true)}>
                <Upload className="w-4 h-4 mr-2" />
                Upload Documents
              </Button>
            </div>
          )}
        </CardContent>
      </Card>

      {/* Upload Dialog */}
      <Dialog open={isUploadDialogOpen} onOpenChange={setIsUploadDialogOpen}>
        <DialogContent className="sm:max-w-2xl">
          <DialogHeader>
            <DialogTitle>Upload Documents</DialogTitle>
            <DialogDescription>
              Upload client documents securely. All files are encrypted and audit logged.
            </DialogDescription>
          </DialogHeader>
          
          <div className="space-y-4">
            {/* Drag and drop area */}
            <div
              className="border-2 border-dashed border-gray-300 rounded-lg p-8 text-center cursor-pointer hover:border-gray-400 transition-colors"
              onClick={() => fileInputRef.current?.click()}
              onDragOver={(e) => {
                e.preventDefault();
                e.currentTarget.classList.add('border-blue-400', 'bg-blue-50');
              }}
              onDragLeave={(e) => {
                e.preventDefault();
                e.currentTarget.classList.remove('border-blue-400', 'bg-blue-50');
              }}
              onDrop={(e) => {
                e.preventDefault();
                e.currentTarget.classList.remove('border-blue-400', 'bg-blue-50');
                const files = Array.from(e.dataTransfer.files);
                setUploadedFiles(prev => [...prev, ...files]);
              }}
            >
              <Upload className="w-12 h-12 text-gray-400 mx-auto mb-4" />
              <h3 className="text-lg font-medium mb-2">Drop files here or click to browse</h3>
              <p className="text-gray-600">
                Support for PDF, JPG, PNG, DOC, DOCX (max 50MB per file)
              </p>
            </div>

            <input
              ref={fileInputRef}
              type="file"
              multiple
              accept=".pdf,.jpg,.jpeg,.png,.doc,.docx"
              onChange={handleFileSelect}
              className="hidden"
            />

            {/* File list */}
            {uploadedFiles.length > 0 && (
              <div className="space-y-2">
                <Label>Selected Files ({uploadedFiles.length})</Label>
                <div className="max-h-48 overflow-y-auto space-y-2">
                  {uploadedFiles.map((file, index) => (
                    <div key={index} className="flex items-center justify-between p-3 bg-gray-50 rounded-md">
                      <div className="flex items-center gap-3">
                        {getFileIcon(file.type.includes('image') ? 'image' : 'document')}
                        <div>
                          <p className="text-sm font-medium">{file.name}</p>
                          <p className="text-xs text-gray-600">{formatFileSize(file.size)}</p>
                        </div>
                      </div>
                      <Button
                        variant="ghost"
                        size="sm"
                        onClick={() => removeFile(index)}
                      >
                        <XCircle className="w-4 h-4 text-red-600" />
                      </Button>
                    </div>
                  ))}
                </div>
              </div>
            )}

            {/* Client assignment */}
            <div className="space-y-2">
              <Label htmlFor="client-select">Assign to Client</Label>
              <select
                id="client-select"
                className="w-full px-4 py-2 border border-gray-300 rounded-md"
                required
              >
                <option value="">Select a client...</option>
                <option value="client_1">John Doe</option>
                <option value="client_2">Jane Smith</option>
                <option value="client_3">Bob Wilson</option>
              </select>
            </div>

            {/* Document category */}
            <div className="space-y-2">
              <Label htmlFor="category-select">Document Category</Label>
              <select
                id="category-select"
                className="w-full px-4 py-2 border border-gray-300 rounded-md"
                required
              >
                <option value="">Select category...</option>
                <option value="credit_report">Credit Report</option>
                <option value="identification">Identification</option>
                <option value="bank_statement">Bank Statement</option>
                <option value="medical_record">Medical Record</option>
                <option value="correspondence">Correspondence</option>
                <option value="legal_document">Legal Document</option>
                <option value="income_verification">Income Verification</option>
              </select>
            </div>
          </div>

          <DialogFooter>
            <Button type="button" variant="outline" onClick={() => setIsUploadDialogOpen(false)}>
              Cancel
            </Button>
            <Button
              onClick={handleUpload}
              disabled={uploadedFiles.length === 0 || uploadDocumentsMutation.isPending}
            >
              {uploadDocumentsMutation.isPending ? 'Uploading...' : `Upload ${uploadedFiles.length} Files`}
            </Button>
          </DialogFooter>
        </DialogContent>
      </Dialog>

      {/* Document Viewer Dialog */}
      <Dialog open={isViewDialogOpen} onOpenChange={setIsViewDialogOpen}>
        <DialogContent className="sm:max-w-4xl max-h-[90vh] overflow-y-auto">
          <DialogHeader>
            <DialogTitle>Document Details</DialogTitle>
            <DialogDescription>
              View document information and access log
            </DialogDescription>
          </DialogHeader>

          {selectedDocument && (
            <div className="space-y-6">
              {/* Document Info */}
              <div className="grid grid-cols-2 gap-4">
                <div>
                  <Label className="text-sm font-medium text-gray-700">Document Name</Label>
                  <p className="text-sm">{selectedDocument.name}</p>
                </div>
                <div>
                  <Label className="text-sm font-medium text-gray-700">Client</Label>
                  <p className="text-sm">{selectedDocument.clientName}</p>
                </div>
                <div>
                  <Label className="text-sm font-medium text-gray-700">Category</Label>
                  <Badge variant="secondary">{selectedDocument.category.replace('_', ' ')}</Badge>
                </div>
                <div>
                  <Label className="text-sm font-medium text-gray-700">Status</Label>
                  <StatusBadge status={selectedDocument.status} />
                </div>
                <div>
                  <Label className="text-sm font-medium text-gray-700">File Size</Label>
                  <p className="text-sm font-mono">{formatFileSize(selectedDocument.fileSize)}</p>
                </div>
                <div>
                  <Label className="text-sm font-medium text-gray-700">Encryption</Label>
                  <div className="flex items-center gap-1">
                    <Shield className="w-4 h-4 text-green-600" />
                    <span className="text-sm">{selectedDocument.encryptionStatus}</span>
                  </div>
                </div>
              </div>

              {/* Tags */}
              <div>
                <Label className="text-sm font-medium text-gray-700 mb-2 block">Tags</Label>
                <div className="flex flex-wrap gap-1">
                  {selectedDocument.tags.map((tag: string) => (
                    <Badge key={tag} variant="outline" className="text-xs">
                      {tag}
                    </Badge>
                  ))}
                </div>
              </div>

              {/* Access Log */}
              <div>
                <Label className="text-sm font-medium text-gray-700 mb-2 block">Access Log</Label>
                <div className="space-y-2 max-h-48 overflow-y-auto">
                  {selectedDocument.accessLog.map((log: any, index: number) => (
                    <div key={index} className="flex justify-between items-center p-2 bg-gray-50 rounded text-sm">
                      <div className="flex items-center gap-2">
                        <User className="w-3 h-3 text-gray-400" />
                        <span>{log.user}</span>
                        <Badge variant="outline" className="text-xs">{log.action}</Badge>
                      </div>
                      <span className="text-gray-500">{new Date(log.timestamp).toLocaleString()}</span>
                    </div>
                  ))}
                </div>
              </div>
            </div>
          )}

          <DialogFooter>
            <Button variant="outline" onClick={() => setIsViewDialogOpen(false)}>
              Close
            </Button>
            <Button
              onClick={() => selectedDocument && downloadDocumentMutation.mutate(selectedDocument)}
            >
              <Download className="w-4 h-4 mr-2" />
              Download
            </Button>
          </DialogFooter>
        </DialogContent>
      </Dialog>
    </div>
  );
}

function StatusBadge({ status }: { status: string }) {
  const config: Record<string, { label: string; className: string; icon: any }> = {
    verified: {
      label: 'Verified',
      className: 'bg-green-100 text-green-800',
      icon: CheckCircle2,
    },
    pending_review: {
      label: 'Pending Review',
      className: 'bg-yellow-100 text-yellow-800',
      icon: Clock,
    },
    flagged: {
      label: 'Flagged',
      className: 'bg-red-100 text-red-800',
      icon: AlertTriangle,
    },
  };

  const { label, className, icon: Icon } = config[status] || config.pending_review;

  return (
    <span className={`inline-flex items-center gap-1 px-2 py-1 rounded-full text-xs font-medium ${className}`}>
      <Icon className="w-3 h-3" />
      {label}
    </span>
  );
}