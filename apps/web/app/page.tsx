import Link from 'next/link';
import { ArrowRight, CheckCircle, Zap, Shield, Clock } from 'lucide-react';
import { SignUpButton } from '@clerk/nextjs';

export default function HomePage() {
  return (
    <main className="min-h-screen bg-gradient-to-b from-white to-gray-50">
      {/* Navigation */}
      <nav className="border-b bg-white/80 backdrop-blur-sm sticky top-0 z-50">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
          <div className="flex justify-between items-center h-16">
            <div className="flex items-center">
              <span className="text-2xl font-bold text-primary-600">CreditBeast</span>
            </div>
            <div className="flex items-center gap-4">
              <Link
                href="/sign-in"
                className="text-gray-700 hover:text-gray-900 font-medium"
              >
                Sign In
              </Link>
              <SignUpButton mode="modal">
                <button className="bg-primary-600 text-white px-6 py-2 rounded-lg font-medium hover:bg-primary-700 transition-colors">
                  Get Started
                </button>
              </SignUpButton>
            </div>
          </div>
        </div>
      </nav>

      {/* Hero Section */}
      <section className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-20">
        <div className="text-center">
          <h1 className="text-5xl md:text-6xl font-bold text-gray-900 mb-6">
            Transform Your Credit Repair
            <span className="block text-primary-600">Business Operations</span>
          </h1>
          <p className="text-xl text-gray-600 mb-8 max-w-3xl mx-auto">
            Compliance-first platform that automates client onboarding, dispute generation,
            and payment recovery. Reduce manual work by 90%.
          </p>
          <div className="flex flex-col sm:flex-row gap-4 justify-center">
            <SignUpButton mode="modal">
              <button className="bg-primary-600 text-white px-8 py-4 rounded-lg font-semibold text-lg hover:bg-primary-700 transition-colors inline-flex items-center justify-center gap-2">
                Start Free Trial
                <ArrowRight className="w-5 h-5" />
              </button>
            </SignUpButton>
            <Link
              href="#features"
              className="border-2 border-primary-600 text-primary-600 px-8 py-4 rounded-lg font-semibold text-lg hover:bg-primary-50 transition-colors"
            >
              See How It Works
            </Link>
          </div>
        </div>
      </section>

      {/* Stats Section */}
      <section className="bg-primary-600 text-white py-16">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
          <div className="grid grid-cols-1 md:grid-cols-3 gap-8 text-center">
            <div>
              <div className="text-5xl font-bold mb-2">&lt; 24h</div>
              <div className="text-primary-100 text-lg">Client Onboarding Time</div>
            </div>
            <div>
              <div className="text-5xl font-bold mb-2">&lt; 10min</div>
              <div className="text-primary-100 text-lg">Dispute Generation</div>
            </div>
            <div>
              <div className="text-5xl font-bold mb-2">&gt; 40%</div>
              <div className="text-primary-100 text-lg">Payment Recovery Rate</div>
            </div>
          </div>
        </div>
      </section>

      {/* Features Section */}
      <section id="features" className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-20">
        <div className="text-center mb-16">
          <h2 className="text-4xl font-bold text-gray-900 mb-4">
            Everything You Need to Scale Your Business
          </h2>
          <p className="text-xl text-gray-600 max-w-2xl mx-auto">
            Built specifically for credit repair professionals with compliance and automation at the core
          </p>
        </div>

        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-8">
          <FeatureCard
            icon={<Zap className="w-10 h-10 text-primary-600" />}
            title="Automated Workflows"
            description="Automate client onboarding, dispute generation, and letter mailing. Save 20+ hours per week."
          />
          <FeatureCard
            icon={<Shield className="w-10 h-10 text-primary-600" />}
            title="Compliance Built-In"
            description="Complete audit trails, data encryption, and compliance reporting. Sleep better at night."
          />
          <FeatureCard
            icon={<Clock className="w-10 h-10 text-primary-600" />}
            title="Instant Dispute Letters"
            description="Generate professional dispute letters in under 10 minutes with AI-powered templates."
          />
          <FeatureCard
            icon={<CheckCircle className="w-10 h-10 text-primary-600" />}
            title="Payment Recovery"
            description="Intelligent dunning system recovers over 40% of failed payments automatically."
          />
          <FeatureCard
            icon={<CheckCircle className="w-10 h-10 text-primary-600" />}
            title="Client Portal"
            description="Branded client portal for document uploads, agreement signing, and progress tracking."
          />
          <FeatureCard
            icon={<CheckCircle className="w-10 h-10 text-primary-600" />}
            title="Real-time Analytics"
            description="Track business metrics, client progress, and revenue in real-time dashboards."
          />
        </div>
      </section>

      {/* CTA Section */}
      <section className="bg-gray-900 text-white py-20">
        <div className="max-w-4xl mx-auto px-4 sm:px-6 lg:px-8 text-center">
          <h2 className="text-4xl font-bold mb-6">
            Ready to Transform Your Credit Repair Business?
          </h2>
          <p className="text-xl text-gray-300 mb-8">
            Join credit repair professionals who are scaling their businesses with CreditBeast
          </p>
          <SignUpButton mode="modal">
            <button className="bg-white text-gray-900 px-8 py-4 rounded-lg font-semibold text-lg hover:bg-gray-100 transition-colors inline-flex items-center gap-2">
              Start Your Free Trial
              <ArrowRight className="w-5 h-5" />
            </button>
          </SignUpButton>
        </div>
      </section>

      {/* Footer */}
      <footer className="bg-white border-t">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-12">
          <div className="grid grid-cols-1 md:grid-cols-4 gap-8">
            <div className="col-span-1">
              <span className="text-2xl font-bold text-primary-600">CreditBeast</span>
              <p className="text-gray-600 mt-4">
                Compliance-first platform for credit repair professionals.
              </p>
            </div>
            <div>
              <h4 className="font-semibold mb-4">Product</h4>
              <ul className="space-y-2 text-gray-600">
                <li><Link href="#features">Features</Link></li>
                <li><Link href="/pricing">Pricing</Link></li>
                <li><Link href="/docs">Documentation</Link></li>
              </ul>
            </div>
            <div>
              <h4 className="font-semibold mb-4">Company</h4>
              <ul className="space-y-2 text-gray-600">
                <li><Link href="/about">About</Link></li>
                <li><Link href="/blog">Blog</Link></li>
                <li><Link href="/contact">Contact</Link></li>
              </ul>
            </div>
            <div>
              <h4 className="font-semibold mb-4">Legal</h4>
              <ul className="space-y-2 text-gray-600">
                <li><Link href="/privacy">Privacy</Link></li>
                <li><Link href="/terms">Terms</Link></li>
                <li><Link href="/compliance">Compliance</Link></li>
              </ul>
            </div>
          </div>
          <div className="border-t mt-12 pt-8 text-center text-gray-600">
            <p>&copy; 2025 CreditBeast. All rights reserved.</p>
          </div>
        </div>
      </footer>
    </main>
  );
}

function FeatureCard({
  icon,
  title,
  description,
}: {
  icon: React.ReactNode;
  title: string;
  description: string;
}) {
  return (
    <div className="bg-white border border-gray-200 rounded-xl p-6 hover:shadow-lg transition-shadow">
      <div className="mb-4">{icon}</div>
      <h3 className="text-xl font-semibold mb-2">{title}</h3>
      <p className="text-gray-600">{description}</p>
    </div>
  );
}
