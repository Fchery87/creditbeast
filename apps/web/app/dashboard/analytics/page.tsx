'use client';

import { useState, useEffect } from 'react';
import { Button } from '@/components/ui/button';

export default function AnalyticsPage() {
  const [data, setData] = useState<any>(null);
  const [loading, setLoading] = useState(true);
  const [timeframe, setTimeframe] = useState('30');
  const [activeTab, setActiveTab] = useState('overview');

  const fetchAnalytics = async () => {
    try {
      setLoading(true);
      // Mock data for now - replace with real API call
      setTimeout(() => {
        setData({
          revenue: {
            monthly_recurring_revenue: 12500,
            total_revenue_30d: 42300,
            revenue_growth_rate: 12.5,
            currency: 'USD',
          },
          disputes: {
            success_rate_overall: 68.5,
            total_disputes: 47,
            successful_disputes: 32,
            by_bureau: [
              { bureau: 'Equifax', total: 15, successful: 11, success_rate: 73.3 },
              { bureau: 'Experian', total: 18, successful: 12, success_rate: 66.7 },
              { bureau: 'TransUnion', total: 14, successful: 9, success_rate: 64.3 }
            ]
          },
          client_ltv: {
            average_ltv: 850,
            total_clients: 24,
            paying_clients: 20,
          },
          churn: {
            churn_rate_90d: 8.3,
            churned_clients_90d: 2,
            total_clients_at_risk: 3,
            high_risk_clients: 1,
            retention_score: 91.7
          },
          operational: {
            onboarding: {
              total_leads_30d: 12,
              completed_onboarding_30d: 10,
              onboarding_rate: 83.3
            },
            system_usage: {
              total_users: 4,
              active_subscriptions: 1,
              avg_clients_per_user: 6.0
            },
            performance_score: 85
          }
        });
        setLoading(false);
      }, 1000);
    } catch (error) {
      console.error('Failed to fetch analytics:', error);
      setLoading(false);
    }
  };

  useEffect(() => {
    fetchAnalytics();
  }, [timeframe]);

  const formatCurrency = (amount: number) => {
    return new Intl.NumberFormat('en-US', {
      style: 'currency',
      currency: 'USD',
      minimumFractionDigits: 0,
      maximumFractionDigits: 0,
    }).format(amount);
  };

  const formatPercentage = (value: number) => {
    return `${value.toFixed(1)}%`;
  };

  if (loading) {
    return (
      <div className="flex items-center justify-center min-h-screen">
        <div className="text-center">
          <div className="h-8 w-8 animate-spin rounded-full border-4 border-primary-600 border-t-transparent mx-auto mb-4"></div>
          <p className="text-gray-600">Loading analytics...</p>
        </div>
      </div>
    );
  }

  if (!data) {
    return (
      <div className="text-center py-12">
        <div className="h-12 w-12 mx-auto mb-4 text-amber-500">
          <svg fill="currentColor" viewBox="0 0 20 20">
            <path fillRule="evenodd" d="M8.257 3.099c.765-1.36 2.722-1.36 3.486 0l5.58 9.92c.75 1.334-.213 2.98-1.742 2.98H4.42c-1.53 0-2.493-1.646-1.743-2.98l5.58-9.92zM11 13a1 1 0 11-2 0 1 1 0 012 0zm-1-8a1 1 0 00-1 1v3a1 1 0 002 0V6a1 1 0 00-1-1z" clipRule="evenodd" />
          </svg>
        </div>
        <h3 className="text-lg font-semibold text-gray-900 mb-2">No Analytics Data</h3>
        <p className="text-gray-600 mb-4">Unable to load analytics data. Please try again.</p>
        <Button onClick={fetchAnalytics}>
          <svg className="h-4 w-4 mr-2" fill="none" stroke="currentColor" viewBox="0 0 24 24">
            <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M4 4v5h.582m15.356 2A8.001 8.001 0 004.582 9m0 0H9m11 11v-5h-.581m0 0a8.003 8.003 0 01-15.357-2m15.357 2H15" />
          </svg>
          Retry
        </Button>
      </div>
    );
  }

  return (
    <div className="space-y-6">
      {/* Header */}
      <div className="flex flex-col md:flex-row justify-between items-start md:items-center gap-4">
        <div>
          <h1 className="text-3xl font-bold text-gray-900">Analytics & Reporting</h1>
          <p className="text-gray-600">Business intelligence and performance insights</p>
        </div>
        <div className="flex items-center gap-2">
          <select
            value={timeframe}
            onChange={(e) => setTimeframe(e.target.value)}
            className="px-4 py-2 border border-gray-300 rounded-md bg-white"
          >
            <option value="7">Last 7 days</option>
            <option value="30">Last 30 days</option>
            <option value="90">Last 90 days</option>
            <option value="365">Last year</option>
          </select>
          <Button variant="outline" onClick={fetchAnalytics}>
            <svg className="h-4 w-4 mr-2" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M4 4v5h.582m15.356 2A8.001 8.001 0 004.582 9m0 0H9m11 11v-5h-.581m0 0a8.003 8.003 0 01-15.357-2m15.357 2H15" />
            </svg>
            Refresh
          </Button>
          <Button variant="outline">
            <svg className="h-4 w-4 mr-2" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M12 10v6m0 0l-3-3m3 3l3-3m2 8H7a2 2 0 01-2-2V5a2 2 0 012-2h5.586a1 1 0 01.707.293l5.414 5.414a1 1 0 01.293.707V19a2 2 0 01-2 2z" />
            </svg>
            Export
          </Button>
        </div>
      </div>

      {/* Key Metrics Cards */}
      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-6">
        <div className="bg-white rounded-lg border p-6">
          <div className="flex items-center justify-between mb-4">
            <span className="text-gray-600 text-sm font-medium">Monthly Revenue</span>
            <div className="text-gray-400">
              <svg className="w-4 h-4" fill="currentColor" viewBox="0 0 20 20">
                <path d="M8.433 7.418c.155-.103.346-.196.567-.267v1.698a2.305 2.305 0 01-.567-.267C8.07 8.34 8 8.114 8 8c0-.114.07-.34.433-.582zM11 12.849v-1.698c.22.071.412.164.567.267.364.243.433.468.433.582 0 .114-.07.34-.433.582a2.305 2.305 0 01-.567.267z" />
                <path fillRule="evenodd" d="M10 18a8 8 0 100-16 8 8 0 000 16zm1-13a1 1 0 10-2 0v.092a4.535 4.535 0 00-1.676.662C6.602 6.234 6 7.009 6 8c0 .99.602 1.765 1.324 2.246.48.32 1.054.545 1.676.662v1.941c-.391-.127-.68-.317-.843-.504a1 1 0 10-1.51 1.31c.562.649 1.413 1.076 2.353 1.253V15a1 1 0 102 0v-.092a4.535 4.535 0 001.676-.662C13.398 13.766 14 12.991 14 12c0-.99-.602-1.765-1.324-2.246A4.535 4.535 0 0011 9.092V7.151c.391.127.68.317.843.504a1 1 0 101.511-1.31c-.563-.649-1.413-1.076-2.354-1.253V5z" clipRule="evenodd" />
              </svg>
            </div>
          </div>
          <div className="text-2xl font-bold">{formatCurrency(data.revenue.monthly_recurring_revenue)}</div>
          <div className="text-xs text-gray-500 flex items-center">
            {data.revenue.revenue_growth_rate >= 0 ? (
              <svg className="h-3 w-3 mr-1 text-green-600" fill="currentColor" viewBox="0 0 20 20">
                <path fillRule="evenodd" d="M5.293 9.707a1 1 0 010-1.414l4-4a1 1 0 011.414 0l4 4a1 1 0 01-1.414 1.414L11 7.414V15a1 1 0 11-2 0V7.414L6.707 9.707a1 1 0 01-1.414 0z" clipRule="evenodd" />
              </svg>
            ) : (
              <svg className="h-3 w-3 mr-1 text-red-600" fill="currentColor" viewBox="0 0 20 20">
                <path fillRule="evenodd" d="M14.707 10.293a1 1 0 010 1.414l-4 4a1 1 0 01-1.414 0l-4-4a1 1 0 111.414-1.414L9 12.586V5a1 1 0 012 0v7.586l2.293-2.293a1 1 0 011.414 0z" clipRule="evenodd" />
              </svg>
            )}
            {formatPercentage(Math.abs(data.revenue.revenue_growth_rate))} from last month
          </div>
        </div>

        <div className="bg-white rounded-lg border p-6">
          <div className="flex items-center justify-between mb-4">
            <span className="text-gray-600 text-sm font-medium">Dispute Success Rate</span>
            <div className="text-gray-400">
              <svg className="w-4 h-4" fill="currentColor" viewBox="0 0 20 20">
                <path fillRule="evenodd" d="M3 4a1 1 0 011-1h12a1 1 0 110 2H4a1 1 0 01-1-1zm0 4a1 1 0 011-1h12a1 1 0 110 2H4a1 1 0 01-1-1zm0 4a1 1 0 011-1h12a1 1 0 110 2H4a1 1 0 01-1-1zm0 4a1 1 0 011-1h12a1 1 0 110 2H4a1 1 0 01-1-1z" clipRule="evenodd" />
              </svg>
            </div>
          </div>
          <div className="text-2xl font-bold">{formatPercentage(data.disputes.success_rate_overall)}</div>
          <div className="text-xs text-gray-500">
            {data.disputes.successful_disputes} of {data.disputes.total_disputes} disputes
          </div>
        </div>

        <div className="bg-white rounded-lg border p-6">
          <div className="flex items-center justify-between mb-4">
            <span className="text-gray-600 text-sm font-medium">Average LTV</span>
            <div className="text-gray-400">
              <svg className="w-4 h-4" fill="currentColor" viewBox="0 0 20 20">
                <path d="M9 6a3 3 0 11-6 0 3 3 0 016 0zM17 6a3 3 0 11-6 0 3 3 0 016 0zM12.93 17c.046-.327.07-.66.07-1a6.97 6.97 0 00-1.5-4.33A5 5 0 0119 16v1h-6.07zM6 11a5 5 0 015 5v1H1v-1a5 5 0 015-5z" />
              </svg>
            </div>
          </div>
          <div className="text-2xl font-bold">{formatCurrency(data.client_ltv.average_ltv)}</div>
          <div className="text-xs text-gray-500">
            {data.client_ltv.paying_clients} of {data.client_ltv.total_clients} clients
          </div>
        </div>

        <div className="bg-white rounded-lg border p-6">
          <div className="flex items-center justify-between mb-4">
            <span className="text-gray-600 text-sm font-medium">Retention Score</span>
            <div className="text-gray-400">
              <svg className="w-4 h-4" fill="currentColor" viewBox="0 0 20 20">
                <path fillRule="evenodd" d="M10 18a8 8 0 100-16 8 8 0 000 16zm3.707-9.293a1 1 0 00-1.414-1.414L9 10.586 7.707 9.293a1 1 0 00-1.414 1.414l2 2a1 1 0 001.414 0l4-4z" clipRule="evenodd" />
              </svg>
            </div>
          </div>
          <div className="text-2xl font-bold">{Math.round(data.churn.retention_score)}/100</div>
          <div className="text-xs text-gray-500">
            {data.churn.churn_rate_90d.toFixed(1)}% churn rate
          </div>
        </div>
      </div>

      {/* Detailed Analytics Tabs */}
      <div className="bg-white rounded-lg border">
        <div className="border-b">
          <nav className="flex space-x-8 px-6">
            {['overview', 'revenue', 'disputes', 'clients', 'operational'].map((tab) => (
              <button
                key={tab}
                onClick={() => setActiveTab(tab)}
                className={`py-4 px-1 border-b-2 font-medium text-sm ${
                  activeTab === tab
                    ? 'border-primary-500 text-primary-600'
                    : 'border-transparent text-gray-500 hover:text-gray-700 hover:border-gray-300'
                }`}
              >
                {tab.charAt(0).toUpperCase() + tab.slice(1)}
              </button>
            ))}
          </nav>
        </div>

        <div className="p-6">
          {activeTab === 'overview' && (
            <div className="space-y-6">
              <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
                <div>
                  <h3 className="text-lg font-semibold mb-4">Revenue Trends</h3>
                  <div className="h-64 flex items-center justify-center bg-gray-50 rounded-lg">
                    <div className="text-center">
                      <svg className="h-12 w-12 mx-auto mb-2 text-gray-400" fill="currentColor" viewBox="0 0 20 20">
                        <path d="M2 11a1 1 0 011-1h2a1 1 0 011 1v5a1 1 0 01-1 1H3a1 1 0 01-1-1v-5zM8 7a1 1 0 011-1h2a1 1 0 011 1v9a1 1 0 01-1 1H9a1 1 0 01-1-1V7zM14 4a1 1 0 011-1h2a1 1 0 011 1v12a1 1 0 01-1 1h-2a1 1 0 01-1-1V4z" />
                      </svg>
                      <p className="text-gray-500">Revenue chart would be here</p>
                      <p className="text-sm text-gray-400">Integrate with a charting library</p>
                    </div>
                  </div>
                </div>

                <div>
                  <h3 className="text-lg font-semibold mb-4">Dispute Success by Bureau</h3>
                  <div className="space-y-4">
                    {data.disputes.by_bureau.map((bureau: any) => (
                      <div key={bureau.bureau} className="flex items-center justify-between">
                        <div className="font-medium">{bureau.bureau}</div>
                        <div className="flex items-center gap-2">
                          <div className="text-sm text-gray-600">
                            {bureau.successful}/{bureau.total}
                          </div>
                          <span className={`px-3 py-1 rounded-full text-xs font-medium ${
                            bureau.success_rate >= 70 ? 'bg-green-100 text-green-800' : 'bg-gray-100 text-gray-800'
                          }`}>
                            {formatPercentage(bureau.success_rate)}
                          </span>
                        </div>
                      </div>
                    ))}
                  </div>
                </div>
              </div>
            </div>
          )}

          {activeTab === 'revenue' && (
            <div className="space-y-6">
              <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
                <div className="lg:col-span-2">
                  <h3 className="text-lg font-semibold mb-4">Revenue Breakdown</h3>
                  <div className="space-y-4">
                    <div className="flex justify-between">
                      <span>Total Revenue (30 days)</span>
                      <span className="font-semibold">{formatCurrency(data.revenue.total_revenue_30d)}</span>
                    </div>
                    <div className="flex justify-between">
                      <span>Monthly Recurring Revenue</span>
                      <span className="font-semibold">{formatCurrency(data.revenue.monthly_recurring_revenue)}</span>
                    </div>
                    <div className="flex justify-between">
                      <span>Growth Rate</span>
                      <span className={`font-semibold ${data.revenue.revenue_growth_rate >= 0 ? 'text-green-600' : 'text-red-600'}`}>
                        {formatPercentage(data.revenue.revenue_growth_rate)}
                      </span>
                    </div>
                  </div>
                </div>

                <div>
                  <h3 className="text-lg font-semibold mb-4">Client LTV Analysis</h3>
                  <div className="space-y-4">
                    <div className="flex justify-between">
                      <span>Average LTV</span>
                      <span className="font-semibold">{formatCurrency(data.client_ltv.average_ltv)}</span>
                    </div>
                    <div className="flex justify-between">
                      <span>Total Clients</span>
                      <span className="font-semibold">{data.client_ltv.total_clients}</span>
                    </div>
                    <div className="flex justify-between">
                      <span>Paying Clients</span>
                      <span className="font-semibold">{data.client_ltv.paying_clients}</span>
                    </div>
                    <div className="flex justify-between">
                      <span>Conversion Rate</span>
                      <span className="font-semibold">
                        {formatPercentage((data.client_ltv.paying_clients / data.client_ltv.total_clients) * 100)}
                      </span>
                    </div>
                  </div>
                </div>
              </div>
            </div>
          )}

          {activeTab === 'disputes' && (
            <div className="space-y-6">
              <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
                <div>
                  <h3 className="text-lg font-semibold mb-4">Dispute Performance</h3>
                  <div className="space-y-4">
                    <div className="flex justify-between">
                      <span>Success Rate</span>
                      <span className="font-semibold text-2xl">{formatPercentage(data.disputes.success_rate_overall)}</span>
                    </div>
                    <div className="flex justify-between">
                      <span>Total Disputes</span>
                      <span className="font-semibold">{data.disputes.total_disputes}</span>
                    </div>
                    <div className="flex justify-between">
                      <span>Successful</span>
                      <span className="font-semibold text-green-600">{data.disputes.successful_disputes}</span>
                    </div>
                  </div>
                </div>

                <div>
                  <h3 className="text-lg font-semibold mb-4">Churn Analysis</h3>
                  <div className="space-y-4">
                    <div className="flex justify-between">
                      <span>Churn Rate (90d)</span>
                      <span className="font-semibold text-red-600">{formatPercentage(data.churn.churn_rate_90d)}</span>
                    </div>
                    <div className="flex justify-between">
                      <span>At-Risk Clients</span>
                      <span className="font-semibold">{data.churn.total_clients_at_risk}</span>
                    </div>
                    <div className="flex justify-between">
                      <span>High-Risk Clients</span>
                      <span className="font-semibold">{data.churn.high_risk_clients}</span>
                    </div>
                    <div className="flex justify-between">
                      <span>Retention Score</span>
                      <span className="font-semibold">{Math.round(data.churn.retention_score)}/100</span>
                    </div>
                  </div>
                </div>
              </div>
            </div>
          )}

          {activeTab === 'clients' && (
            <div className="space-y-6">
              <h3 className="text-lg font-semibold mb-4">Client Analytics</h3>
              <div className="grid grid-cols-1 md:grid-cols-3 gap-6">
                <div className="text-center">
                  <div className="text-3xl font-bold text-blue-600">{data.client_ltv.total_clients}</div>
                  <div className="text-gray-600">Total Clients</div>
                </div>
                <div className="text-center">
                  <div className="text-3xl font-bold text-green-600">{data.client_ltv.paying_clients}</div>
                  <div className="text-gray-600">Paying Clients</div>
                </div>
                <div className="text-center">
                  <div className="text-3xl font-bold text-purple-600">{formatCurrency(data.client_ltv.average_ltv)}</div>
                  <div className="text-gray-600">Average LTV</div>
                </div>
              </div>
            </div>
          )}

          {activeTab === 'operational' && (
            <div className="space-y-6">
              <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
                <div>
                  <h3 className="text-lg font-semibold mb-4">Onboarding Performance</h3>
                  <div className="space-y-4">
                    <div className="flex justify-between">
                      <span>Total Leads (30d)</span>
                      <span className="font-semibold">{data.operational.onboarding.total_leads_30d}</span>
                    </div>
                    <div className="flex justify-between">
                      <span>Completed Onboarding (30d)</span>
                      <span className="font-semibold">{data.operational.onboarding.completed_onboarding_30d}</span>
                    </div>
                    <div className="flex justify-between">
                      <span>Onboarding Rate</span>
                      <span className="font-semibold">{formatPercentage(data.operational.onboarding.onboarding_rate)}</span>
                    </div>
                  </div>
                </div>

                <div>
                  <h3 className="text-lg font-semibold mb-4">System Usage</h3>
                  <div className="space-y-4">
                    <div className="flex justify-between">
                      <span>Total Users</span>
                      <span className="font-semibold">{data.operational.system_usage.total_users}</span>
                    </div>
                    <div className="flex justify-between">
                      <span>Active Subscriptions</span>
                      <span className="font-semibold">{data.operational.system_usage.active_subscriptions}</span>
                    </div>
                    <div className="flex justify-between">
                      <span>Avg Clients per User</span>
                      <span className="font-semibold">{data.operational.system_usage.avg_clients_per_user}</span>
                    </div>
                    <div className="flex justify-between">
                      <span>Performance Score</span>
                      <span className="font-semibold">{data.operational.performance_score}/100</span>
                    </div>
                  </div>
                </div>
              </div>
            </div>
          )}
        </div>
      </div>
    </div>
  );
}