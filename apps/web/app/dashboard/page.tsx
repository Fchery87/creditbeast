import { Users, FileText, Mail, TrendingUp } from 'lucide-react';

export default function DashboardPage() {
  return (
    <div>
      <div className="mb-8">
        <h1 className="text-3xl font-bold text-gray-900">Dashboard</h1>
        <p className="text-gray-600 mt-2">Welcome to your CreditBeast control center</p>
      </div>

      {/* Stats Grid */}
      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-6 mb-8">
        <StatCard
          title="Total Clients"
          value="24"
          change="+12%"
          icon={<Users className="w-6 h-6" />}
          trend="up"
        />
        <StatCard
          title="Active Disputes"
          value="47"
          change="+8%"
          icon={<FileText className="w-6 h-6" />}
          trend="up"
        />
        <StatCard
          title="Letters Sent"
          value="138"
          change="+23%"
          icon={<Mail className="w-6 h-6" />}
          trend="up"
        />
        <StatCard
          title="Success Rate"
          value="68%"
          change="+5%"
          icon={<TrendingUp className="w-6 h-6" />}
          trend="up"
        />
      </div>

      {/* Recent Activity */}
      <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
        <div className="bg-white rounded-lg border p-6">
          <h2 className="text-xl font-semibold mb-4">Recent Clients</h2>
          <div className="space-y-4">
            <ClientRow name="John Smith" status="active" date="2 days ago" />
            <ClientRow name="Sarah Johnson" status="onboarding" date="3 days ago" />
            <ClientRow name="Michael Brown" status="active" date="5 days ago" />
            <ClientRow name="Emma Davis" status="lead" date="1 week ago" />
          </div>
        </div>

        <div className="bg-white rounded-lg border p-6">
          <h2 className="text-xl font-semibold mb-4">Recent Disputes</h2>
          <div className="space-y-4">
            <DisputeRow
              account="Chase Credit Card"
              type="Late Payment"
              status="sent"
              date="1 day ago"
            />
            <DisputeRow
              account="Capital One"
              type="Inquiry"
              status="investigating"
              date="3 days ago"
            />
            <DisputeRow
              account="Discover"
              type="Charge Off"
              status="pending"
              date="5 days ago"
            />
            <DisputeRow
              account="Amex"
              type="Collection"
              status="resolved"
              date="1 week ago"
            />
          </div>
        </div>
      </div>
    </div>
  );
}

function StatCard({
  title,
  value,
  change,
  icon,
  trend,
}: {
  title: string;
  value: string;
  change: string;
  icon: React.ReactNode;
  trend: 'up' | 'down';
}) {
  return (
    <div className="bg-white rounded-lg border p-6">
      <div className="flex items-center justify-between mb-4">
        <span className="text-gray-600 text-sm font-medium">{title}</span>
        <div className="text-primary-600">{icon}</div>
      </div>
      <div className="flex items-baseline justify-between">
        <div className="text-3xl font-bold text-gray-900">{value}</div>
        <span
          className={`text-sm font-medium ${
            trend === 'up' ? 'text-green-600' : 'text-red-600'
          }`}
        >
          {change}
        </span>
      </div>
    </div>
  );
}

function ClientRow({
  name,
  status,
  date,
}: {
  name: string;
  status: string;
  date: string;
}) {
  const statusColors = {
    lead: 'bg-gray-100 text-gray-800',
    onboarding: 'bg-blue-100 text-blue-800',
    active: 'bg-green-100 text-green-800',
    inactive: 'bg-yellow-100 text-yellow-800',
  };

  return (
    <div className="flex items-center justify-between py-3 border-b last:border-0">
      <div>
        <div className="font-medium text-gray-900">{name}</div>
        <div className="text-sm text-gray-500">{date}</div>
      </div>
      <span
        className={`px-3 py-1 rounded-full text-xs font-medium ${
          statusColors[status as keyof typeof statusColors]
        }`}
      >
        {status}
      </span>
    </div>
  );
}

function DisputeRow({
  account,
  type,
  status,
  date,
}: {
  account: string;
  type: string;
  status: string;
  date: string;
}) {
  const statusColors = {
    draft: 'bg-gray-100 text-gray-800',
    pending: 'bg-yellow-100 text-yellow-800',
    sent: 'bg-blue-100 text-blue-800',
    investigating: 'bg-purple-100 text-purple-800',
    resolved: 'bg-green-100 text-green-800',
    failed: 'bg-red-100 text-red-800',
  };

  return (
    <div className="flex items-center justify-between py-3 border-b last:border-0">
      <div>
        <div className="font-medium text-gray-900">{account}</div>
        <div className="text-sm text-gray-500">
          {type} · {date}
        </div>
      </div>
      <span
        className={`px-3 py-1 rounded-full text-xs font-medium ${
          statusColors[status as keyof typeof statusColors]
        }`}
      >
        {status}
      </span>
    </div>
  );
}
