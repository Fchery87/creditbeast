# CreditBeast Setup Guide

Complete guide to setting up the CreditBeast platform for local development.

## Table of Contents

1. [System Requirements](#system-requirements)
2. [Initial Setup](#initial-setup)
3. [Database Configuration](#database-configuration)
4. [Backend Setup](#backend-setup)
5. [Frontend Setup](#frontend-setup)
6. [Third-Party Services](#third-party-services)
7. [Running the Application](#running-the-application)
8. [Testing](#testing)
9. [Troubleshooting](#troubleshooting)

---

## System Requirements

- **Node.js:** 18.x or higher
- **Python:** 3.11 or higher
- **pnpm:** 8.x or higher (recommended) or npm
- **Git:** Latest version
- **PostgreSQL:** 14+ (for local development, optional)

### Install Dependencies

**macOS:**
```bash
# Install Homebrew
/bin/bash -c "$(curl -fsSL https://raw.githubusercontent.com/Homebrew/install/HEAD/install.sh)"

# Install Node.js
brew install node@18

# Install Python
brew install python@3.11

# Install pnpm
npm install -g pnpm
```

**Linux (Ubuntu/Debian):**
```bash
# Install Node.js
curl -fsSL https://deb.nodesource.com/setup_18.x | sudo -E bash -
sudo apt-get install -y nodejs

# Install Python
sudo apt-get install python3.11 python3.11-venv python3-pip

# Install pnpm
npm install -g pnpm
```

**Windows:**
- Download and install Node.js from [nodejs.org](https://nodejs.org)
- Download and install Python from [python.org](https://python.org)
- Install pnpm: `npm install -g pnpm`

---

## Initial Setup

### 1. Clone the Repository

```bash
git clone YOUR_REPOSITORY_URL
cd creditbeast
```

### 2. Project Structure Overview

```
creditbeast/
├── apps/
│   ├── web/          # Next.js frontend
│   └── api/          # FastAPI backend
├── packages/
│   └── shared/       # Shared types and utilities
├── docs/             # Documentation
└── scripts/          # Utility scripts
```

---

## Database Configuration

### Option A: Use Supabase (Recommended)

1. **Create Supabase Account:**
   - Go to [supabase.com](https://supabase.com)
   - Sign up for free account
   - Create a new project

2. **Get Credentials:**
   - Project URL: `https://YOUR_PROJECT.supabase.co`
   - Anon Key: Found in Project Settings > API
   - Service Role Key: Found in Project Settings > API (keep secure!)

3. **Run Database Schema:**
   - Open Supabase SQL Editor
   - Copy contents of `docs/DATABASE_SCHEMA.sql`
   - Execute the SQL

4. **Verify Setup:**
   - Check that all tables are created
   - Verify RLS policies are enabled

### Option B: Local PostgreSQL

1. **Install PostgreSQL:**
   ```bash
   # macOS
   brew install postgresql@14
   brew services start postgresql@14
   
   # Linux
   sudo apt-get install postgresql-14
   sudo service postgresql start
   ```

2. **Create Database:**
   ```bash
   createdb creditbeast_dev
   ```

3. **Run Schema:**
   ```bash
   psql -d creditbeast_dev -f docs/DATABASE_SCHEMA.sql
   ```

---

## Backend Setup

### 1. Navigate to API Directory

```bash
cd apps/api
```

### 2. Create Python Virtual Environment

```bash
python3.11 -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
```

### 3. Install Dependencies

```bash
pip install -r requirements.txt
```

### 4. Configure Environment Variables

```bash
# Copy example environment file
cp .env.example .env

# Edit .env with your actual values
nano .env  # or use your preferred editor
```

**Required Environment Variables:**

```bash
# Supabase
SUPABASE_URL=https://YOUR_PROJECT.supabase.co
SUPABASE_KEY=your-anon-key
SUPABASE_SERVICE_ROLE_KEY=your-service-role-key

# Clerk (get from clerk.com after setup)
CLERK_SECRET_KEY=sk_test_...
CLERK_PUBLISHABLE_KEY=pk_test_...

# Stripe (get from stripe.com after setup)
STRIPE_SECRET_KEY=sk_test_...
STRIPE_PUBLISHABLE_KEY=pk_test_...
STRIPE_WEBHOOK_SECRET=whsec_... (setup later for webhooks)

# Email/SMTP
SMTP_HOST=smtp.gmail.com
SMTP_PORT=587
SMTP_USERNAME=your-email@gmail.com
SMTP_PASSWORD=your-app-password

# Security
PII_ENCRYPTION_KEY=generate-a-secure-32-character-key-here
JWT_SECRET_KEY=another-secure-secret-key-for-jwt
```

### 5. Test Backend

```bash
# Run development server
uvicorn main:app --reload

# In another terminal, test the API
curl http://localhost:8000/health
```

Expected response:
```json
{
  "status": "healthy",
  "service": "creditbeast-api",
  "version": "1.0.0"
}
```

---

## Frontend Setup

### 1. Navigate to Web Directory

```bash
cd apps/web
```

### 2. Install Dependencies

```bash
pnpm install
# or
npm install
```

### 3. Configure Environment Variables

```bash
# Copy example environment file
cp .env.example .env.local

# Edit .env.local with your values
nano .env.local
```

**Required Environment Variables:**

```bash
# API Configuration
NEXT_PUBLIC_API_URL=http://localhost:8000

# Clerk
NEXT_PUBLIC_CLERK_PUBLISHABLE_KEY=pk_test_...
CLERK_SECRET_KEY=sk_test_...

# Stripe
NEXT_PUBLIC_STRIPE_PUBLISHABLE_KEY=pk_test_...
```

### 4. Test Frontend

```bash
# Run development server
pnpm dev
# or
npm run dev
```

Visit http://localhost:3000 to see the application.

---

## Third-Party Services

### Clerk Authentication Setup

1. **Create Account:**
   - Go to [clerk.com](https://clerk.com)
   - Sign up for free account

2. **Create Application:**
   - Click "Add Application"
   - Choose "Next.js" as framework
   - Copy API keys

3. **Configure Application:**
   - Enable Email/Password authentication
   - Configure organization settings
   - Set up webhooks (optional)

4. **Add Keys to Environment:**
   - Add to backend `.env`
   - Add to frontend `.env.local`

### Stripe Payment Setup

1. **Create Account:**
   - Go to [stripe.com](https://stripe.com)
   - Sign up for account

2. **Get API Keys:**
   - Go to Developers > API keys
   - Copy Publishable key and Secret key
   - Use TEST mode for development

3. **Set Up Products:**
   - Create products for your subscription tiers
   - Note the price IDs

4. **Configure Webhooks (for local development):**
   ```bash
   # Install Stripe CLI
   brew install stripe/stripe-cli/stripe
   
   # Login
   stripe login
   
   # Forward webhooks to local server
   stripe listen --forward-to localhost:8000/api/webhooks/stripe
   
   # Copy the webhook signing secret to .env
   ```

### Email Configuration

#### Option A: Gmail

1. **Enable 2-Factor Authentication** on your Google account

2. **Create App Password:**
   - Go to Google Account settings
   - Security > 2-Step Verification > App passwords
   - Generate password for "Mail"

3. **Add to .env:**
   ```bash
   SMTP_HOST=smtp.gmail.com
   SMTP_PORT=587
   SMTP_USERNAME=your-email@gmail.com
   SMTP_PASSWORD=your-app-password
   ```

#### Option B: SendGrid

1. **Create Account:** [sendgrid.com](https://sendgrid.com)
2. **Create API Key**
3. **Configure:**
   ```bash
   SMTP_HOST=smtp.sendgrid.net
   SMTP_PORT=587
   SMTP_USERNAME=apikey
   SMTP_PASSWORD=your-sendgrid-api-key
   ```

---

## Running the Application

### Development Mode

**Terminal 1 - Backend:**
```bash
cd apps/api
source venv/bin/activate
uvicorn main:app --reload
```

**Terminal 2 - Frontend:**
```bash
cd apps/web
pnpm dev
```

**Terminal 3 - Stripe Webhooks (optional):**
```bash
stripe listen --forward-to localhost:8000/api/webhooks/stripe
```

### Access the Application

- **Frontend:** http://localhost:3000
- **Backend API:** http://localhost:8000
- **API Docs:** http://localhost:8000/api/docs
- **Supabase Dashboard:** https://app.supabase.com

### Default Credentials

If you loaded sample data, you can use:
- **Email:** admin@democreditrepair.com
- **Password:** Set via Clerk authentication

---

## Testing

### Backend Tests

```bash
cd apps/api
pytest
```

### Frontend Tests

```bash
cd apps/web
pnpm test
```

### End-to-End Testing

1. Create a test account via Clerk
2. Test lead capture flow
3. Test client onboarding
4. Test dispute generation
5. Test payment processing (use Stripe test cards)

**Stripe Test Cards:**
- Success: `4242 4242 4242 4242`
- Decline: `4000 0000 0000 0002`
- 3D Secure: `4000 0025 0000 3155`

---

## Troubleshooting

### Backend Issues

**Problem:** `ModuleNotFoundError: No module named 'fastapi'`
**Solution:**
```bash
# Ensure virtual environment is activated
source venv/bin/activate
pip install -r requirements.txt
```

**Problem:** Database connection errors
**Solution:**
- Verify Supabase credentials in `.env`
- Check internet connection
- Verify Supabase project is active

**Problem:** CORS errors
**Solution:**
- Check `CORS_ORIGINS` in backend `.env`
- Ensure frontend URL is included
- Restart backend server

### Frontend Issues

**Problem:** `Cannot find module` errors
**Solution:**
```bash
# Clear cache and reinstall
rm -rf node_modules .next
pnpm install
```

**Problem:** Clerk authentication not working
**Solution:**
- Verify API keys in `.env.local`
- Check Clerk dashboard for application status
- Ensure keys match (test vs live)

**Problem:** API calls failing
**Solution:**
- Verify `NEXT_PUBLIC_API_URL` is correct
- Check backend is running
- Check browser console for errors

### Database Issues

**Problem:** Tables not found
**Solution:**
- Re-run `DATABASE_SCHEMA.sql`
- Verify connection to correct database

**Problem:** Permission denied errors
**Solution:**
- Check RLS policies in Supabase
- Verify user has correct organization access

---

## Development Tips

### Hot Reload

Both frontend and backend support hot reload:
- Backend: Changes automatically reload with `--reload` flag
- Frontend: Next.js Fast Refresh updates on save

### API Documentation

FastAPI provides automatic interactive docs:
- Swagger UI: http://localhost:8000/api/docs
- ReDoc: http://localhost:8000/api/redoc

### Database Inspection

View data in Supabase:
- Go to Table Editor in Supabase dashboard
- Run SQL queries in SQL Editor
- Monitor logs in Logs Explorer

### Code Quality

```bash
# Backend
black apps/api  # Format code
flake8 apps/api  # Lint code
mypy apps/api  # Type checking

# Frontend
cd apps/web
pnpm lint  # ESLint
pnpm format  # Prettier
```

---

## Next Steps

After successful setup:

1. **Customize branding:**
   - Update logo and colors in `tailwind.config.ts`
   - Modify company name in various files

2. **Configure email templates:**
   - Create templates for client notifications
   - Set up transactional emails

3. **Set up monitoring:**
   - Configure error tracking (Sentry)
   - Set up analytics (Google Analytics)

4. **Create test data:**
   - Add sample clients
   - Create test disputes
   - Test full workflows

5. **Review security:**
   - Change all default keys
   - Enable 2FA on all services
   - Review RLS policies

---

## Getting Help

- **Documentation:** Check `/docs` folder
- **API Issues:** Review FastAPI logs and `/api/docs`
- **Frontend Issues:** Check browser console
- **Database Issues:** Check Supabase logs

**Need more help?** Contact your team lead or consult the following:
- Supabase docs: https://supabase.com/docs
- Clerk docs: https://clerk.com/docs
- Stripe docs: https://stripe.com/docs
- Next.js docs: https://nextjs.org/docs

---

**Congratulations! Your CreditBeast development environment is ready.**
