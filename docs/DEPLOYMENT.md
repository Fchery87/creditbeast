# CreditBeast Deployment Guide

This guide provides comprehensive instructions for deploying the CreditBeast platform to various cloud providers.

## Table of Contents

1. [Prerequisites](#prerequisites)
2. [Database Setup (Supabase)](#database-setup)
3. [Backend Deployment](#backend-deployment)
   - [Railway](#deploy-backend-to-railway)
   - [AWS (EC2 + RDS)](#deploy-backend-to-aws)
   - [Google Cloud Platform](#deploy-backend-to-gcp)
   - [Azure](#deploy-backend-to-azure)
4. [Frontend Deployment](#frontend-deployment)
   - [Vercel (Recommended)](#deploy-frontend-to-vercel)
   - [Netlify](#deploy-frontend-to-netlify)
   - [AWS Amplify](#deploy-frontend-to-aws-amplify)
5. [Environment Variables](#environment-variables)
6. [Post-Deployment](#post-deployment)
7. [Monitoring & Maintenance](#monitoring--maintenance)

---

## Prerequisites

Before deploying, ensure you have:

- [x] Supabase account and project created
- [x] Clerk account for authentication
- [x] Stripe account for payments
- [x] SMTP credentials for email (Gmail, SendGrid, etc.)
- [x] Git repository for your code
- [x] Domain name (optional but recommended)

---

## Database Setup

### 1. Create Supabase Project

1. Go to [supabase.com](https://supabase.com)
2. Create a new project
3. Save your project URL and API keys

### 2. Run Database Migration

```bash
# Install Supabase CLI
npm install -g supabase

# Login to Supabase
supabase login

# Link your project
supabase link --project-ref YOUR_PROJECT_REF

# Run the schema migration
psql -h db.YOUR_PROJECT_REF.supabase.co -U postgres -d postgres -f docs/DATABASE_SCHEMA.sql
```

Or manually run the SQL in the Supabase SQL editor:
1. Go to your Supabase project dashboard
2. Click "SQL Editor"
3. Copy and paste the contents of `docs/DATABASE_SCHEMA.sql`
4. Click "Run"

### 3. Configure RLS Policies

The schema includes Row Level Security policies. Ensure they are enabled in your Supabase project.

---

## Backend Deployment

### Deploy Backend to Railway

**Recommended for quick deployment**

1. **Install Railway CLI:**
   ```bash
   npm install -g @railway/cli
   ```

2. **Login and initialize:**
   ```bash
   railway login
   cd apps/api
   railway init
   ```

3. **Create railway.json:**
   ```json
   {
     "$schema": "https://railway.app/railway.schema.json",
     "build": {
       "builder": "NIXPACKS"
     },
     "deploy": {
       "startCommand": "uvicorn main:app --host 0.0.0.0 --port $PORT",
       "restartPolicyType": "ON_FAILURE",
       "restartPolicyMaxRetries": 10
     }
   }
   ```

4. **Set environment variables:**
   ```bash
   railway variables set SUPABASE_URL=your-supabase-url
   railway variables set SUPABASE_KEY=your-supabase-key
   railway variables set CLERK_SECRET_KEY=your-clerk-secret
   railway variables set STRIPE_SECRET_KEY=your-stripe-secret
   # ... add all other environment variables
   ```

5. **Deploy:**
   ```bash
   railway up
   ```

6. **Get your deployment URL:**
   ```bash
   railway status
   ```

### Deploy Backend to AWS

**For production-grade deployment**

#### Option A: EC2 + Application Load Balancer

1. **Create EC2 Instance:**
   - Launch Ubuntu 22.04 LTS
   - Instance type: t3.small or larger
   - Configure security group (open ports 80, 443, 22)

2. **SSH into instance and setup:**
   ```bash
   # Update system
   sudo apt update && sudo apt upgrade -y
   
   # Install Python 3.11
   sudo apt install python3.11 python3.11-venv python3-pip -y
   
   # Install Nginx
   sudo apt install nginx -y
   
   # Clone repository
   git clone YOUR_REPO_URL
   cd creditbeast/apps/api
   
   # Create virtual environment
   python3.11 -m venv venv
   source venv/bin/activate
   
   # Install dependencies
   pip install -r requirements.txt
   
   # Create .env file
   nano .env
   # Paste your environment variables
   ```

3. **Create systemd service:**
   ```bash
   sudo nano /etc/systemd/system/creditbeast-api.service
   ```
   
   ```ini
   [Unit]
   Description=CreditBeast API
   After=network.target
   
   [Service]
   User=ubuntu
   WorkingDirectory=/home/ubuntu/creditbeast/apps/api
   Environment="PATH=/home/ubuntu/creditbeast/apps/api/venv/bin"
   ExecStart=/home/ubuntu/creditbeast/apps/api/venv/bin/uvicorn main:app --host 0.0.0.0 --port 8000
   Restart=always
   
   [Install]
   WantedBy=multi-user.target
   ```

4. **Configure Nginx:**
   ```bash
   sudo nano /etc/nginx/sites-available/creditbeast-api
   ```
   
   ```nginx
   server {
       listen 80;
       server_name api.yourdomain.com;
       
       location / {
           proxy_pass http://127.0.0.1:8000;
           proxy_set_header Host $host;
           proxy_set_header X-Real-IP $remote_addr;
           proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
           proxy_set_header X-Forwarded-Proto $scheme;
       }
   }
   ```

5. **Enable and start:**
   ```bash
   sudo ln -s /etc/nginx/sites-available/creditbeast-api /etc/nginx/sites-enabled/
   sudo systemctl enable creditbeast-api
   sudo systemctl start creditbeast-api
   sudo systemctl restart nginx
   
   # Install SSL certificate with Let's Encrypt
   sudo apt install certbot python3-certbot-nginx -y
   sudo certbot --nginx -d api.yourdomain.com
   ```

#### Option B: AWS Elastic Beanstalk

1. **Install EB CLI:**
   ```bash
   pip install awsebcli
   ```

2. **Initialize:**
   ```bash
   cd apps/api
   eb init -p python-3.11 creditbeast-api
   ```

3. **Create environment:**
   ```bash
   eb create creditbeast-api-prod
   ```

4. **Set environment variables:**
   ```bash
   eb setenv SUPABASE_URL=your-url CLERK_SECRET_KEY=your-key ...
   ```

5. **Deploy:**
   ```bash
   eb deploy
   ```

### Deploy Backend to GCP

1. **Install Google Cloud SDK**

2. **Create App Engine app:**
   ```bash
   cd apps/api
   gcloud app create --region=us-central
   ```

3. **Create app.yaml:**
   ```yaml
   runtime: python311
   entrypoint: uvicorn main:app --host 0.0.0.0 --port $PORT
   
   env_variables:
     SUPABASE_URL: "your-supabase-url"
     SUPABASE_KEY: "your-supabase-key"
     # Add all environment variables
   ```

4. **Deploy:**
   ```bash
   gcloud app deploy
   ```

### Deploy Backend to Azure

1. **Install Azure CLI**

2. **Create Web App:**
   ```bash
   az webapp up --runtime PYTHON:3.11 --name creditbeast-api --resource-group creditbeast-rg
   ```

3. **Configure environment:**
   ```bash
   az webapp config appsettings set --name creditbeast-api --resource-group creditbeast-rg --settings SUPABASE_URL=your-url
   ```

---

## Frontend Deployment

### Deploy Frontend to Vercel

**Recommended - Zero configuration**

1. **Install Vercel CLI:**
   ```bash
   npm install -g vercel
   ```

2. **Deploy:**
   ```bash
   cd apps/web
   vercel
   ```

3. **Set environment variables in Vercel dashboard:**
   - Go to your project settings
   - Add all environment variables from `.env.example`

4. **Deploy to production:**
   ```bash
   vercel --prod
   ```

### Deploy Frontend to Netlify

1. **Install Netlify CLI:**
   ```bash
   npm install -g netlify-cli
   ```

2. **Build the app:**
   ```bash
   cd apps/web
   npm run build
   ```

3. **Deploy:**
   ```bash
   netlify deploy --prod
   ```

4. **Set environment variables:**
   - Go to Netlify dashboard > Site settings > Environment variables
   - Add all required variables

### Deploy Frontend to AWS Amplify

1. **Connect Git repository:**
   - Go to AWS Amplify Console
   - Connect your GitHub/GitLab repository
   - Select the `apps/web` folder as build root

2. **Configure build settings:**
   ```yaml
   version: 1
   applications:
     - frontend:
         phases:
           preBuild:
             commands:
               - cd apps/web
               - npm install
           build:
             commands:
               - npm run build
         artifacts:
           baseDirectory: .next
           files:
             - '**/*'
         cache:
           paths:
             - node_modules/**/*
   ```

3. **Add environment variables in Amplify console**

---

## Environment Variables

### Backend (.env)
```bash
# Supabase
SUPABASE_URL=https://your-project.supabase.co
SUPABASE_KEY=your-anon-key
SUPABASE_SERVICE_ROLE_KEY=your-service-role-key

# Clerk
CLERK_SECRET_KEY=sk_live_your-clerk-secret

# Stripe
STRIPE_SECRET_KEY=sk_live_your-stripe-secret
STRIPE_WEBHOOK_SECRET=whsec_your-webhook-secret

# Email
SMTP_HOST=smtp.gmail.com
SMTP_PORT=587
SMTP_USERNAME=your-email@gmail.com
SMTP_PASSWORD=your-app-password

# Security
PII_ENCRYPTION_KEY=your-32-char-encryption-key
JWT_SECRET_KEY=your-jwt-secret-key
```

### Frontend (.env.local)
```bash
# API
NEXT_PUBLIC_API_URL=https://api.yourdomain.com

# Clerk
NEXT_PUBLIC_CLERK_PUBLISHABLE_KEY=pk_live_your-clerk-key
CLERK_SECRET_KEY=sk_live_your-clerk-secret

# Stripe
NEXT_PUBLIC_STRIPE_PUBLISHABLE_KEY=pk_live_your-stripe-key
```

---

## Post-Deployment

### 1. Test Deployment

```bash
# Test backend health
curl https://api.yourdomain.com/health

# Test frontend
curl https://yourdomain.com
```

### 2. Configure Webhooks

**Stripe Webhooks:**
1. Go to Stripe Dashboard > Developers > Webhooks
2. Add endpoint: `https://api.yourdomain.com/api/webhooks/stripe`
3. Select events: `payment_intent.*`, `invoice.*`, `customer.subscription.*`
4. Copy webhook secret to your backend environment

### 3. Set up Custom Domains

- Configure DNS A/CNAME records for your domain
- Enable SSL certificates
- Update CORS settings in backend to allow your domain

### 4. Initial Data Setup

```bash
# Create your organization
curl -X POST https://api.yourdomain.com/api/auth/organizations \
  -H "Authorization: Bearer YOUR_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{"name": "Your Company", "slug": "your-company"}'
```

---

## Monitoring & Maintenance

### Application Monitoring

1. **Set up logging:**
   - Use cloud provider's logging service
   - Configure log aggregation
   - Set up error alerts

2. **Performance monitoring:**
   - Backend: Use New Relic, Datadog, or cloud-native monitoring
   - Frontend: Use Vercel Analytics, Google Analytics, or Sentry

3. **Uptime monitoring:**
   - Use UptimeRobot, Pingdom, or StatusCake
   - Monitor both frontend and backend endpoints

### Database Maintenance

1. **Regular backups:**
   - Supabase provides automatic backups
   - Configure additional backup policies if needed

2. **Monitor database performance:**
   - Check Supabase dashboard for slow queries
   - Optimize indexes as needed

### Security

1. **Keep dependencies updated:**
   ```bash
   # Backend
   pip list --outdated
   
   # Frontend
   npm outdated
   ```

2. **Regular security audits:**
   ```bash
   # Frontend
   npm audit
   
   # Backend
   pip-audit
   ```

3. **SSL certificate renewal:**
   - Most platforms auto-renew
   - Verify certificates are valid

### Scaling

**Backend Scaling:**
- Horizontal: Add more instances/containers
- Vertical: Increase instance size
- Database: Upgrade Supabase plan as needed

**Frontend Scaling:**
- Vercel/Netlify: Auto-scales
- Add CDN for static assets

---

## Troubleshooting

### Common Issues

1. **Database connection errors:**
   - Verify Supabase credentials
   - Check firewall rules
   - Ensure RLS policies are configured

2. **Authentication failures:**
   - Verify Clerk keys
   - Check CORS settings
   - Ensure JWT configuration matches

3. **Payment processing errors:**
   - Verify Stripe API keys
   - Check webhook signatures
   - Review Stripe dashboard for events

### Getting Help

- Check application logs
- Review Supabase logs
- Consult documentation
- Contact support teams for third-party services

---

## Cost Estimates

### Minimum Production Setup

- **Supabase:** Free tier or Pro ($25/month)
- **Clerk:** Free tier or Pro ($25/month)
- **Stripe:** Pay as you go (2.9% + 30¢ per transaction)
- **Backend Hosting:** $5-20/month (Railway/AWS)
- **Frontend Hosting:** Free (Vercel) or $20/month
- **Domain:** $10-15/year

**Total:** ~$50-100/month for initial deployment

---

## Next Steps

1. Complete deployment checklist
2. Test all features end-to-end
3. Set up monitoring and alerts
4. Configure automated backups
5. Document your specific deployment configuration
6. Create runbook for common operations

**Congratulations! Your CreditBeast platform is now deployed and ready for production use.**
