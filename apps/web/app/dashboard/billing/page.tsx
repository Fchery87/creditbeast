'use client';

import { useState } from 'react';
import { useQuery, useMutation, useQueryClient } from '@tanstack/react-query';
import { CreditCard, Download, AlertCircle, CheckCircle2, XCircle, Loader2 } from 'lucide-react';
import { loadStripe, StripeElementsOptions } from '@stripe/stripe-js';
import { Elements, PaymentElement, useStripe, useElements } from '@stripe/react-stripe-js';
import { billingApi } from '@/lib/api';
import { Button } from '@/components/ui/button';
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '@/components/ui/card';
import {
  Table,
  TableBody,
  TableCell,
  TableHead,
  TableHeader,
  TableRow,
} from '@/components/ui/table';
import { Dialog, DialogContent, DialogDescription, DialogFooter, DialogHeader, DialogTitle } from '@/components/ui/dialog';

// Initialize Stripe
const stripePromise = loadStripe(process.env.NEXT_PUBLIC_STRIPE_PUBLISHABLE_KEY || '');

interface PlanDetails {
  id: string;
  name: string;
  price: number;
  interval: string;
  features: string[];
  recommended?: boolean;
}

const plans: PlanDetails[] = [
  {
    id: 'starter',
    name: 'Starter',
    price: 99,
    interval: 'month',
    features: [
      'Up to 25 clients',
      'Basic dispute templates',
      'Email support',
      'Standard compliance reporting',
    ],
  },
  {
    id: 'professional',
    name: 'Professional',
    price: 299,
    interval: 'month',
    features: [
      'Up to 100 clients',
      'Advanced dispute templates',
      'Priority support',
      'Advanced analytics',
      'Custom branding',
      'API access',
    ],
    recommended: true,
  },
  {
    id: 'enterprise',
    name: 'Enterprise',
    price: 999,
    interval: 'month',
    features: [
      'Unlimited clients',
      'All templates + custom',
      '24/7 dedicated support',
      'White-label solution',
      'Custom integrations',
      'Dedicated account manager',
    ],
  },
];

// Stripe Payment Form Component
function StripePaymentForm({ 
  clientSecret,
  planName,
  onSuccess, 
  onCancel 
}: { 
  clientSecret: string;
  planName: string;
  onSuccess: () => void; 
  onCancel: () => void;
}) {
  const stripe = useStripe();
  const elements = useElements();
  const [isProcessing, setIsProcessing] = useState(false);
  const [errorMessage, setErrorMessage] = useState<string | null>(null);

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();

    if (!stripe || !elements) {
      setErrorMessage('Stripe has not loaded yet. Please wait a moment and try again.');
      return;
    }

    setIsProcessing(true);
    setErrorMessage(null);

    try {
      // Validate payment element
      const { error: submitError } = await elements.submit();
      if (submitError) {
        setErrorMessage(submitError.message || 'Payment validation failed');
        setIsProcessing(false);
        return;
      }

      // Confirm payment with Stripe
      const { error: confirmError } = await stripe.confirmPayment({
        elements,
        clientSecret,
        confirmParams: {
          return_url: `${window.location.origin}/dashboard/billing?success=true`,
        },
        redirect: 'if_required', // Only redirect if 3D Secure is required
      });

      if (confirmError) {
        setErrorMessage(confirmError.message || 'Payment failed. Please try again.');
        setIsProcessing(false);
        return;
      }

      // Success!
      onSuccess();
    } catch (error: any) {
      const message = error.response?.data?.detail || 
                     error.message || 
                     'An unexpected error occurred. Please try again.';
      setErrorMessage(message);
      setIsProcessing(false);
    }
  };

  return (
    <form onSubmit={handleSubmit}>
      <div className="py-4 space-y-4">
        <div className="space-y-2">
          <PaymentElement 
            options={{
              layout: 'tabs',
              fields: {
                billingDetails: {
                  email: 'auto',
                }
              }
            }}
          />
        </div>

        {errorMessage && (
          <div className="bg-red-50 border border-red-200 rounded-md p-3 flex items-start gap-2">
            <AlertCircle className="w-5 h-5 text-red-600 flex-shrink-0 mt-0.5" />
            <p className="text-sm text-red-800">{errorMessage}</p>
          </div>
        )}

        <p className="text-xs text-gray-500">
          Your payment information is encrypted and secure. We use Stripe for processing.
        </p>
      </div>

      <DialogFooter>
        <Button 
          type="button"
          variant="outline" 
          onClick={onCancel}
          disabled={isProcessing}
        >
          Cancel
        </Button>
        <Button 
          type="submit"
          disabled={!stripe || isProcessing}
        >
          {isProcessing ? (
            <>
              <Loader2 className="w-4 h-4 mr-2 animate-spin" />
              Processing...
            </>
          ) : (
            <>Complete Subscription</>
          )}
        </Button>
      </DialogFooter>
    </form>
  );
}

// Main Billing Page Component
export default function BillingPage() {
  const [isSubscribeDialogOpen, setIsSubscribeDialogOpen] = useState(false);
  const [isCancelDialogOpen, setIsCancelDialogOpen] = useState(false);
  const [selectedPlan, setSelectedPlan] = useState<string>('professional');
  const [clientSecret, setClientSecret] = useState<string | null>(null);

  const queryClient = useQueryClient();

  // Fetch current subscription
  const { data: subscription, isLoading: subscriptionLoading } = useQuery({
    queryKey: ['subscription'],
    queryFn: async () => {
      try {
        const response = await billingApi.getSubscription();
        return response.data;
      } catch (error: any) {
        if (error.response?.status === 404) {
          return null; // No subscription
        }
        throw error;
      }
    },
  });

  // Create subscription mutation
  const createSubscriptionMutation = useMutation({
    mutationFn: async (planId: string) => {
      const response = await billingApi.createSubscription({
        plan_name: planId,
        billing_interval: 'month',
      });
      return response.data;
    },
    onSuccess: (data) => {
      if (data.client_secret) {
        setClientSecret(data.client_secret);
      } else {
        throw new Error('No client secret returned from server');
      }
    },
    onError: (error: any) => {
      console.error('Failed to create subscription:', error);
      const message = error.response?.data?.detail || 'Failed to initialize payment. Please try again.';
      alert(message);
      setIsSubscribeDialogOpen(false);
    },
  });

  // Cancel subscription mutation
  const cancelSubscriptionMutation = useMutation({
    mutationFn: () => billingApi.cancelSubscription(),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['subscription'] });
      setIsCancelDialogOpen(false);
    },
    onError: (error: any) => {
      alert(error.response?.data?.detail || 'Failed to cancel subscription. Please try again.');
    },
  });

  // Handle opening subscribe dialog
  const handleOpenSubscribeDialog = (planId: string) => {
    setSelectedPlan(planId);
    setIsSubscribeDialogOpen(true);
    setClientSecret(null);
    // Create subscription when dialog opens
    createSubscriptionMutation.mutate(planId);
  };

  // Handle successful payment
  const handlePaymentSuccess = () => {
    setIsSubscribeDialogOpen(false);
    setClientSecret(null);
    queryClient.invalidateQueries({ queryKey: ['subscription'] });
  };

  // Handle dialog close
  const handleDialogClose = (open: boolean) => {
    if (!open && !createSubscriptionMutation.isPending) {
      setIsSubscribeDialogOpen(false);
      setClientSecret(null);
    }
  };

  // Stripe Elements options
  const elementsOptions: StripeElementsOptions = {
    clientSecret: clientSecret || undefined,
    appearance: {
      theme: 'stripe',
      variables: {
        colorPrimary: '#2563eb',
        borderRadius: '6px',
      },
    },
  };

  const selectedPlanDetails = plans.find(p => p.id === selectedPlan);

  return (
    <div className="space-y-6">
      {/* Header */}
      <div>
        <h1 className="text-3xl font-bold">Billing & Subscription</h1>
        <p className="text-gray-600 mt-2">Manage your subscription and payment methods</p>
      </div>

      {/* Current Subscription */}
      <div className="grid gap-6 md:grid-cols-2">
        <Card>
          <CardHeader>
            <CardTitle>Current Subscription</CardTitle>
            <CardDescription>Your active plan and billing cycle</CardDescription>
          </CardHeader>
          <CardContent>
            {subscriptionLoading ? (
              <div className="text-center py-8 text-gray-500">
                <Loader2 className="w-6 h-6 animate-spin mx-auto mb-2" />
                Loading...
              </div>
            ) : subscription ? (
              <div className="space-y-4">
                <div className="flex items-center justify-between">
                  <div>
                    <p className="text-2xl font-bold capitalize">{subscription.plan_name}</p>
                    <p className="text-gray-600">
                      ${(subscription.plan_price_cents / 100).toFixed(2)}/{subscription.billing_interval}
                    </p>
                  </div>
                  <SubscriptionStatusBadge status={subscription.status} />
                </div>

                {subscription.current_period_end && (
                  <div className="pt-4 border-t">
                    <p className="text-sm text-gray-600">
                      {subscription.cancel_at_period_end ? (
                        <>
                          <AlertCircle className="inline w-4 h-4 mr-1 text-orange-600" />
                          Cancels on{' '}
                          {new Date(subscription.current_period_end).toLocaleDateString()}
                        </>
                      ) : (
                        <>
                          Next billing date:{' '}
                          {new Date(subscription.current_period_end).toLocaleDateString()}
                        </>
                      )}
                    </p>
                  </div>
                )}

                <div className="flex gap-2 pt-4">
                  <Button variant="outline" size="sm">
                    <CreditCard className="w-4 h-4 mr-2" />
                    Manage Payment Method
                  </Button>
                  {!subscription.cancel_at_period_end && (
                    <Button
                      variant="outline"
                      size="sm"
                      onClick={() => setIsCancelDialogOpen(true)}
                    >
                      Cancel Subscription
                    </Button>
                  )}
                </div>
              </div>
            ) : (
              <div className="text-center py-8">
                <p className="text-gray-500 mb-4">No active subscription</p>
                <Button onClick={() => handleOpenSubscribeDialog('professional')}>
                  Subscribe Now
                </Button>
              </div>
            )}
          </CardContent>
        </Card>

        <Card>
          <CardHeader>
            <CardTitle>Billing Summary</CardTitle>
            <CardDescription>Overview of your billing information</CardDescription>
          </CardHeader>
          <CardContent>
            <div className="space-y-4">
              <div className="flex justify-between">
                <span className="text-gray-600">Total Paid (All Time)</span>
                <span className="font-semibold">$0.00</span>
              </div>
              <div className="flex justify-between">
                <span className="text-gray-600">Current Month</span>
                <span className="font-semibold">
                  ${subscription ? (subscription.plan_price_cents / 100).toFixed(2) : '0.00'}
                </span>
              </div>
              <div className="flex justify-between">
                <span className="text-gray-600">Failed Payments</span>
                <span className="font-semibold text-red-600">0</span>
              </div>
              <div className="flex justify-between pt-4 border-t">
                <span className="text-gray-600">Payment Method</span>
                <span className="font-semibold">
                  {subscription ? 'Card ending in ****' : 'Not set'}
                </span>
              </div>
            </div>
          </CardContent>
        </Card>
      </div>

      {/* Available Plans */}
      {!subscription && (
        <div>
          <h2 className="text-2xl font-bold mb-4">Choose Your Plan</h2>
          <div className="grid gap-6 md:grid-cols-3">
            {plans.map((plan) => (
              <Card
                key={plan.id}
                className={plan.recommended ? 'border-primary-600 border-2' : ''}
              >
                {plan.recommended && (
                  <div className="bg-primary-600 text-white text-center py-1 text-sm font-semibold rounded-t-lg">
                    Recommended
                  </div>
                )}
                <CardHeader>
                  <CardTitle>{plan.name}</CardTitle>
                  <div className="mt-4">
                    <span className="text-4xl font-bold">${plan.price}</span>
                    <span className="text-gray-600">/{plan.interval}</span>
                  </div>
                </CardHeader>
                <CardContent>
                  <ul className="space-y-3 mb-6">
                    {plan.features.map((feature, index) => (
                      <li key={index} className="flex items-start">
                        <CheckCircle2 className="w-5 h-5 text-green-600 mr-2 flex-shrink-0 mt-0.5" />
                        <span className="text-sm">{feature}</span>
                      </li>
                    ))}
                  </ul>
                  <Button
                    className="w-full"
                    variant={plan.recommended ? 'default' : 'outline'}
                    onClick={() => handleOpenSubscribeDialog(plan.id)}
                  >
                    Get Started
                  </Button>
                </CardContent>
              </Card>
            ))}
          </div>
        </div>
      )}

      {/* Payment History */}
      <Card>
        <CardHeader>
          <CardTitle>Payment History</CardTitle>
          <CardDescription>View and download past invoices</CardDescription>
        </CardHeader>
        <CardContent>
          <Table>
            <TableHeader>
              <TableRow>
                <TableHead>Invoice</TableHead>
                <TableHead>Date</TableHead>
                <TableHead>Amount</TableHead>
                <TableHead>Status</TableHead>
                <TableHead className="text-right">Actions</TableHead>
              </TableRow>
            </TableHeader>
            <TableBody>
              <TableRow>
                <TableCell colSpan={5} className="text-center py-8 text-gray-500">
                  No payment history available
                </TableCell>
              </TableRow>
            </TableBody>
          </Table>
        </CardContent>
      </Card>

      {/* Subscribe Dialog with Stripe Elements */}
      <Dialog open={isSubscribeDialogOpen} onOpenChange={handleDialogClose}>
        <DialogContent className="sm:max-w-md">
          <DialogHeader>
            <DialogTitle>Subscribe to {selectedPlanDetails?.name} Plan</DialogTitle>
            <DialogDescription>
              ${selectedPlanDetails?.price}/month - Complete your payment to unlock all features
            </DialogDescription>
          </DialogHeader>

          {createSubscriptionMutation.isPending || !clientSecret ? (
            <div className="py-8 text-center">
              <Loader2 className="w-8 h-8 animate-spin mx-auto mb-2 text-primary-600" />
              <p className="text-gray-600">Initializing secure payment...</p>
            </div>
          ) : (
            <Elements stripe={stripePromise} options={elementsOptions}>
              <StripePaymentForm
                clientSecret={clientSecret}
                planName={selectedPlanDetails?.name || ''}
                onSuccess={handlePaymentSuccess}
                onCancel={() => handleDialogClose(false)}
              />
            </Elements>
          )}
        </DialogContent>
      </Dialog>

      {/* Cancel Confirmation Dialog */}
      <Dialog open={isCancelDialogOpen} onOpenChange={setIsCancelDialogOpen}>
        <DialogContent>
          <DialogHeader>
            <DialogTitle>Cancel Subscription</DialogTitle>
            <DialogDescription>
              Are you sure you want to cancel your subscription?
            </DialogDescription>
          </DialogHeader>
          <div className="py-4">
            <p className="text-sm text-gray-600">
              Your subscription will remain active until the end of your current billing period on{' '}
              <span className="font-semibold">
                {subscription?.current_period_end &&
                  new Date(subscription.current_period_end).toLocaleDateString()}
              </span>
              . After that, you will lose access to premium features.
            </p>
          </div>
          <DialogFooter>
            <Button 
              variant="outline" 
              onClick={() => setIsCancelDialogOpen(false)}
              disabled={cancelSubscriptionMutation.isPending}
            >
              Keep Subscription
            </Button>
            <Button
              variant="destructive"
              onClick={() => cancelSubscriptionMutation.mutate()}
              disabled={cancelSubscriptionMutation.isPending}
            >
              {cancelSubscriptionMutation.isPending ? (
                <>
                  <Loader2 className="w-4 h-4 mr-2 animate-spin" />
                  Canceling...
                </>
              ) : (
                'Cancel Subscription'
              )}
            </Button>
          </DialogFooter>
        </DialogContent>
      </Dialog>
    </div>
  );
}

function SubscriptionStatusBadge({ status }: { status: string }) {
  const config: Record<string, { label: string; className: string; icon: any }> = {
    active: {
      label: 'Active',
      className: 'bg-green-100 text-green-800',
      icon: CheckCircle2,
    },
    past_due: {
      label: 'Past Due',
      className: 'bg-yellow-100 text-yellow-800',
      icon: AlertCircle,
    },
    canceled: {
      label: 'Canceled',
      className: 'bg-red-100 text-red-800',
      icon: XCircle,
    },
    incomplete: {
      label: 'Incomplete',
      className: 'bg-gray-100 text-gray-800',
      icon: AlertCircle,
    },
  };

  const { label, className, icon: Icon } = config[status] || config.incomplete;

  return (
    <span className={`inline-flex items-center gap-1 px-3 py-1 rounded-full text-xs font-medium ${className}`}>
      <Icon className="w-3 h-3" />
      {label}
    </span>
  );
}
