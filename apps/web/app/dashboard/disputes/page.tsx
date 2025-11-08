'use client';

import { useState } from 'react';
import { useQuery, useMutation, useQueryClient } from '@tanstack/react-query';
import { ArrowRight, ArrowLeft, FileText, CheckCircle, Send } from 'lucide-react';
import { clientsApi, disputesApi } from '@/lib/api';
import { Client, DisputeCreateInput } from '@/types';
import { Button } from '@/components/ui/button';
import { Input } from '@/components/ui/input';
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '@/components/ui/card';
import { Label } from '@/components/ui/label';
import { Textarea } from '@/components/ui/textarea';
import {
  Table,
  TableBody,
  TableCell,
  TableHead,
  TableHeader,
  TableRow,
} from '@/components/ui/table';

export default function DisputesPage() {
  const [currentStep, setCurrentStep] = useState(1);
  const [selectedClient, setSelectedClient] = useState<Client | null>(null);
  const [disputeData, setDisputeData] = useState<Partial<DisputeCreateInput>>({
    dispute_type: 'late_payment',
    bureau: 'all',
  });
  const [generatedLetter, setGeneratedLetter] = useState<string>('');

  const queryClient = useQueryClient();

  // Fetch clients for step 1
  const { data: clientsData } = useQuery({
    queryKey: ['clients'],
    queryFn: async () => {
      const response = await clientsApi.list({ page: 1, page_size: 100 });
      return response.data;
    },
  });

  // Fetch disputes
  const { data: disputesData, isLoading: disputesLoading } = useQuery({
    queryKey: ['disputes'],
    queryFn: async () => {
      const response = await disputesApi.list({ page: 1, page_size: 50 });
      return response.data;
    },
  });

  // Create dispute mutation
  const createDisputeMutation = useMutation({
    mutationFn: (data: DisputeCreateInput) => disputesApi.create(data),
    onSuccess: async (response) => {
      queryClient.invalidateQueries({ queryKey: ['disputes'] });
      // Generate letter
      const letterResponse = await disputesApi.generateLetter(response.data.id);
      setGeneratedLetter(letterResponse.data.letter_content);
      setCurrentStep(4);
    },
  });

  const handleClientSelect = (client: Client) => {
    setSelectedClient(client);
    setDisputeData(prev => ({ ...prev, client_id: client.id }));
    setCurrentStep(2);
  };

  const handleDisputeTypeSubmit = () => {
    if (!disputeData.dispute_reason || !disputeData.account_name) {
      alert('Please fill in all required fields');
      return;
    }
    setCurrentStep(3);
  };

  const handleGenerateLetter = () => {
    if (!selectedClient || !disputeData.client_id) {
      alert('Please select a client');
      return;
    }

    const fullDisputeData: DisputeCreateInput = {
      client_id: disputeData.client_id,
      dispute_type: disputeData.dispute_type || 'late_payment',
      bureau: disputeData.bureau || 'all',
      account_name: disputeData.account_name || '',
      account_number: disputeData.account_number,
      dispute_reason: disputeData.dispute_reason || '',
      letter_template_id: disputeData.letter_template_id,
    };

    createDisputeMutation.mutate(fullDisputeData);
  };

  const resetWizard = () => {
    setCurrentStep(1);
    setSelectedClient(null);
    setDisputeData({ dispute_type: 'late_payment', bureau: 'all' });
    setGeneratedLetter('');
  };

  return (
    <div className="space-y-6">
      {/* Header */}
      <div>
        <h1 className="text-3xl font-bold">Dispute Management</h1>
        <p className="text-gray-600 mt-2">Generate and manage credit dispute letters</p>
      </div>

      {/* Progress Steps */}
      <div className="flex items-center justify-between max-w-3xl mx-auto">
        {[
          { number: 1, title: 'Select Client' },
          { number: 2, title: 'Dispute Details' },
          { number: 3, title: 'Review' },
          { number: 4, title: 'Generate Letter' },
        ].map((step, index) => (
          <div key={step.number} className="flex items-center">
            <div className="flex flex-col items-center">
              <div
                className={`w-10 h-10 rounded-full flex items-center justify-center font-semibold ${
                  currentStep >= step.number
                    ? 'bg-primary-600 text-white'
                    : 'bg-gray-200 text-gray-600'
                }`}
              >
                {currentStep > step.number ? (
                  <CheckCircle className="w-6 h-6" />
                ) : (
                  step.number
                )}
              </div>
              <span className="text-sm mt-2 font-medium">{step.title}</span>
            </div>
            {index < 3 && (
              <div
                className={`h-1 w-24 mx-4 ${
                  currentStep > step.number ? 'bg-primary-600' : 'bg-gray-200'
                }`}
              />
            )}
          </div>
        ))}
      </div>

      {/* Step Content */}
      <div className="max-w-4xl mx-auto">
        {currentStep === 1 && (
          <Card>
            <CardHeader>
              <CardTitle>Step 1: Select Client</CardTitle>
              <CardDescription>Choose the client for this dispute</CardDescription>
            </CardHeader>
            <CardContent>
              {clientsData && clientsData.items.length > 0 ? (
                <Table>
                  <TableHeader>
                    <TableRow>
                      <TableHead>Name</TableHead>
                      <TableHead>Email</TableHead>
                      <TableHead>Status</TableHead>
                      <TableHead className="text-right">Action</TableHead>
                    </TableRow>
                  </TableHeader>
                  <TableBody>
                    {clientsData.items
                      .filter((c: Client) => c.status === 'active')
                      .map((client: Client) => (
                        <TableRow key={client.id}>
                          <TableCell className="font-medium">
                            {client.first_name} {client.last_name}
                          </TableCell>
                          <TableCell>{client.email}</TableCell>
                          <TableCell>
                            <span className="px-3 py-1 rounded-full text-xs font-medium bg-green-100 text-green-800">
                              {client.status}
                            </span>
                          </TableCell>
                          <TableCell className="text-right">
                            <Button
                              size="sm"
                              onClick={() => handleClientSelect(client)}
                            >
                              Select
                            </Button>
                          </TableCell>
                        </TableRow>
                      ))}
                  </TableBody>
                </Table>
              ) : (
                <div className="text-center py-8 text-gray-500">
                  No active clients found. Please add clients first.
                </div>
              )}
            </CardContent>
          </Card>
        )}

        {currentStep === 2 && selectedClient && (
          <Card>
            <CardHeader>
              <CardTitle>Step 2: Dispute Details</CardTitle>
              <CardDescription>
                Entering dispute information for {selectedClient.first_name}{' '}
                {selectedClient.last_name}
              </CardDescription>
            </CardHeader>
            <CardContent>
              <div className="space-y-4">
                <div className="space-y-2">
                  <Label htmlFor="dispute_type">Dispute Type *</Label>
                  <select
                    id="dispute_type"
                    className="w-full px-4 py-2 border border-gray-300 rounded-md"
                    value={disputeData.dispute_type}
                    onChange={(e) =>
                      setDisputeData({ ...disputeData, dispute_type: e.target.value })
                    }
                  >
                    <option value="inquiry">Hard Inquiry</option>
                    <option value="late_payment">Late Payment</option>
                    <option value="charge_off">Charge Off</option>
                    <option value="collection">Collection Account</option>
                    <option value="bankruptcy">Bankruptcy</option>
                    <option value="foreclosure">Foreclosure</option>
                    <option value="other">Other</option>
                  </select>
                </div>

                <div className="space-y-2">
                  <Label htmlFor="bureau">Credit Bureau *</Label>
                  <select
                    id="bureau"
                    className="w-full px-4 py-2 border border-gray-300 rounded-md"
                    value={disputeData.bureau}
                    onChange={(e) =>
                      setDisputeData({ ...disputeData, bureau: e.target.value as any })
                    }
                  >
                    <option value="all">All Bureaus</option>
                    <option value="equifax">Equifax</option>
                    <option value="experian">Experian</option>
                    <option value="transunion">TransUnion</option>
                  </select>
                </div>

                <div className="space-y-2">
                  <Label htmlFor="account_name">Account/Creditor Name *</Label>
                  <Input
                    id="account_name"
                    value={disputeData.account_name || ''}
                    onChange={(e) =>
                      setDisputeData({ ...disputeData, account_name: e.target.value })
                    }
                    placeholder="e.g., Chase Credit Card, Capital One"
                  />
                </div>

                <div className="space-y-2">
                  <Label htmlFor="account_number">Account Number (Optional)</Label>
                  <Input
                    id="account_number"
                    value={disputeData.account_number || ''}
                    onChange={(e) =>
                      setDisputeData({ ...disputeData, account_number: e.target.value })
                    }
                    placeholder="Last 4 digits or partial account number"
                  />
                </div>

                <div className="space-y-2">
                  <Label htmlFor="dispute_reason">Dispute Reason *</Label>
                  <Textarea
                    id="dispute_reason"
                    value={disputeData.dispute_reason || ''}
                    onChange={(e) =>
                      setDisputeData({ ...disputeData, dispute_reason: e.target.value })
                    }
                    placeholder="Explain why this item should be removed or updated..."
                    rows={6}
                  />
                </div>

                <div className="flex justify-between pt-4">
                  <Button variant="outline" onClick={() => setCurrentStep(1)}>
                    <ArrowLeft className="w-4 h-4 mr-2" />
                    Back
                  </Button>
                  <Button onClick={handleDisputeTypeSubmit}>
                    Next
                    <ArrowRight className="w-4 h-4 ml-2" />
                  </Button>
                </div>
              </div>
            </CardContent>
          </Card>
        )}

        {currentStep === 3 && selectedClient && (
          <Card>
            <CardHeader>
              <CardTitle>Step 3: Review & Confirm</CardTitle>
              <CardDescription>
                Review the dispute details before generating the letter
              </CardDescription>
            </CardHeader>
            <CardContent>
              <div className="space-y-6">
                <div>
                  <h3 className="font-semibold mb-2">Client Information</h3>
                  <div className="bg-gray-50 p-4 rounded-md space-y-1">
                    <p>
                      <span className="font-medium">Name:</span> {selectedClient.first_name}{' '}
                      {selectedClient.last_name}
                    </p>
                    <p>
                      <span className="font-medium">Email:</span> {selectedClient.email}
                    </p>
                    <p>
                      <span className="font-medium">Address:</span>{' '}
                      {selectedClient.street_address}, {selectedClient.city},{' '}
                      {selectedClient.state} {selectedClient.zip_code}
                    </p>
                  </div>
                </div>

                <div>
                  <h3 className="font-semibold mb-2">Dispute Details</h3>
                  <div className="bg-gray-50 p-4 rounded-md space-y-1">
                    <p>
                      <span className="font-medium">Type:</span> {disputeData.dispute_type}
                    </p>
                    <p>
                      <span className="font-medium">Bureau:</span> {disputeData.bureau}
                    </p>
                    <p>
                      <span className="font-medium">Account:</span> {disputeData.account_name}
                    </p>
                    <p>
                      <span className="font-medium">Reason:</span> {disputeData.dispute_reason}
                    </p>
                  </div>
                </div>

                <div className="flex justify-between pt-4">
                  <Button variant="outline" onClick={() => setCurrentStep(2)}>
                    <ArrowLeft className="w-4 h-4 mr-2" />
                    Back
                  </Button>
                  <Button
                    onClick={handleGenerateLetter}
                    disabled={createDisputeMutation.isPending}
                  >
                    {createDisputeMutation.isPending ? (
                      'Generating...'
                    ) : (
                      <>
                        <FileText className="w-4 h-4 mr-2" />
                        Generate Letter
                      </>
                    )}
                  </Button>
                </div>
              </div>
            </CardContent>
          </Card>
        )}

        {currentStep === 4 && generatedLetter && (
          <Card>
            <CardHeader>
              <CardTitle>Step 4: Dispute Letter Generated</CardTitle>
              <CardDescription>Your dispute letter is ready to send</CardDescription>
            </CardHeader>
            <CardContent>
              <div className="space-y-6">
                <div className="bg-white border border-gray-300 p-6 rounded-md max-h-96 overflow-y-auto">
                  <pre className="whitespace-pre-wrap font-mono text-sm">
                    {generatedLetter}
                  </pre>
                </div>

                <div className="flex justify-between items-center pt-4 border-t">
                  <Button variant="outline" onClick={resetWizard}>
                    Create Another Dispute
                  </Button>
                  <div className="flex gap-2">
                    <Button variant="outline">
                      <FileText className="w-4 h-4 mr-2" />
                      Download PDF
                    </Button>
                    <Button>
                      <Send className="w-4 h-4 mr-2" />
                      Send to Client
                    </Button>
                  </div>
                </div>
              </div>
            </CardContent>
          </Card>
        )}
      </div>

      {/* Recent Disputes */}
      <div className="max-w-6xl mx-auto mt-12">
        <Card>
          <CardHeader>
            <CardTitle>Recent Disputes</CardTitle>
            <CardDescription>View and manage all created disputes</CardDescription>
          </CardHeader>
          <CardContent>
            {disputesLoading ? (
              <div className="text-center py-8 text-gray-500">Loading disputes...</div>
            ) : disputesData && disputesData.items.length > 0 ? (
              <Table>
                <TableHeader>
                  <TableRow>
                    <TableHead>Client</TableHead>
                    <TableHead>Type</TableHead>
                    <TableHead>Bureau</TableHead>
                    <TableHead>Account</TableHead>
                    <TableHead>Status</TableHead>
                    <TableHead>Created</TableHead>
                  </TableRow>
                </TableHeader>
                <TableBody>
                  {disputesData.items.slice(0, 10).map((dispute: any) => (
                    <TableRow key={dispute.id}>
                      <TableCell className="font-medium">Client ID: {dispute.client_id.slice(0, 8)}</TableCell>
                      <TableCell>{dispute.dispute_type}</TableCell>
                      <TableCell>{dispute.bureau}</TableCell>
                      <TableCell>{dispute.account_name || 'N/A'}</TableCell>
                      <TableCell>
                        <StatusBadge status={dispute.status} />
                      </TableCell>
                      <TableCell>
                        {new Date(dispute.created_at).toLocaleDateString()}
                      </TableCell>
                    </TableRow>
                  ))}
                </TableBody>
              </Table>
            ) : (
              <div className="text-center py-8 text-gray-500">
                No disputes created yet. Use the wizard above to create your first dispute.
              </div>
            )}
          </CardContent>
        </Card>
      </div>
    </div>
  );
}

function StatusBadge({ status }: { status: string }) {
  const colors: Record<string, string> = {
    draft: 'bg-gray-100 text-gray-800',
    pending: 'bg-yellow-100 text-yellow-800',
    sent: 'bg-blue-100 text-blue-800',
    investigating: 'bg-purple-100 text-purple-800',
    resolved: 'bg-green-100 text-green-800',
    failed: 'bg-red-100 text-red-800',
  };

  return (
    <span className={`px-3 py-1 rounded-full text-xs font-medium ${colors[status] || colors.draft}`}>
      {status}
    </span>
  );
}
