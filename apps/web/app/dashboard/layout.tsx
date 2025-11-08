'use client';

import { usePathname } from 'next/navigation';
import { UserButton } from '@clerk/nextjs';
import Link from 'next/link';
import { Home, Users, FileText, Mail, CreditCard, Settings, Bell } from 'lucide-react';

export default function DashboardLayout({
  children,
}: {
  children: React.ReactNode;
}) {
  const pathname = usePathname();

  return (
    <div className="min-h-screen bg-gray-50">
      {/* Top Navigation */}
      <nav className="bg-white border-b">
        <div className="max-w-full px-6">
          <div className="flex items-center justify-between h-16">
            <div className="flex items-center gap-8">
              <Link href="/dashboard" className="flex items-center gap-2">
                <span className="text-2xl font-bold text-primary-600">CreditBeast</span>
              </Link>
            </div>
            <div className="flex items-center gap-4">
              <span className="text-sm text-gray-600">Welcome back!</span>
              <UserButton afterSignOutUrl="/" />
            </div>
          </div>
        </div>
      </nav>

      <div className="flex">
        {/* Sidebar */}
        <aside className="w-64 bg-white border-r min-h-[calc(100vh-4rem)] p-6">
          <nav className="space-y-2">
            <NavLink href="/dashboard" icon={<Home />} active={pathname === '/dashboard'}>
              Dashboard
            </NavLink>
            <NavLink href="/dashboard/clients" icon={<Users />} active={pathname === '/dashboard/clients'}>
              Clients
            </NavLink>
            <NavLink href="/dashboard/disputes" icon={<FileText />} active={pathname === '/dashboard/disputes'}>
              Disputes
            </NavLink>
            <NavLink href="/dashboard/letters" icon={<Mail />} active={pathname === '/dashboard/letters'}>
              Letters
            </NavLink>
            <NavLink href="/dashboard/notifications" icon={<Bell />} active={pathname === '/dashboard/notifications'}>
              Notifications
            </NavLink>
            <NavLink href="/dashboard/billing" icon={<CreditCard />} active={pathname === '/dashboard/billing'}>
              Billing
            </NavLink>
            <NavLink href="/dashboard/settings" icon={<Settings />} active={pathname === '/dashboard/settings'}>
              Settings
            </NavLink>
          </nav>
        </aside>

        {/* Main Content */}
        <main className="flex-1 p-8">{children}</main>
      </div>
    </div>
  );
}

function NavLink({
  href,
  icon,
  children,
  active = false,
}: {
  href: string;
  icon: React.ReactNode;
  children: React.ReactNode;
  active?: boolean;
}) {
  return (
    <Link
      href={href}
      className={`flex items-center gap-3 px-4 py-3 rounded-lg transition-colors ${
        active
          ? 'bg-primary-50 text-primary-600 font-semibold'
          : 'text-gray-700 hover:bg-gray-100 hover:text-gray-900'
      }`}
    >
      <span className="w-5 h-5">{icon}</span>
      <span className="font-medium">{children}</span>
    </Link>
  );
}
