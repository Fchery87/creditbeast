"""
CreditBeast FastAPI Application
Main entry point for the backend API server
"""

from fastapi import FastAPI, Request, status
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from contextlib import asynccontextmanager
import time
import logging
from config import settings

# Import routers
from routers import auth, leads, clients, disputes, billing, webhooks, emails, automation, security, analytics, branding, client_portal, integrations

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Application lifespan manager
@asynccontextmanager
async def lifespan(app: FastAPI):
    """Startup and shutdown events"""
    logger.info("Starting CreditBeast API server...")
    
    # Validate required environment variables
    required_vars = [
        ('supabase_url', 'SUPABASE_URL'),
        ('supabase_key', 'SUPABASE_KEY'),
        ('clerk_secret_key', 'CLERK_SECRET_KEY'),
    ]
    
    missing = []
    for attr_name, env_name in required_vars:
        value = getattr(settings, attr_name, None)
        if not value or value.startswith('your-'):
            missing.append(env_name)
    
    if missing:
        logger.error(f"Missing or placeholder environment variables: {', '.join(missing)}")
        logger.error("Please configure these variables in your .env file")
    else:
        logger.info("All required environment variables are configured")
    
    yield
    logger.info("Shutting down CreditBeast API server...")

# Initialize FastAPI app
app = FastAPI(
    title="CreditBeast API",
    description="Compliance-first B2B SaaS platform for credit repair professionals",
    version="1.0.0",
    docs_url="/api/docs",
    redoc_url="/api/redoc",
    openapi_url="/api/openapi.json",
    lifespan=lifespan
)

# CORS Configuration
# Get allowed origins from environment variable or use defaults
import os
cors_origins_str = os.getenv("CORS_ORIGINS", "http://localhost:3000,http://localhost:3001")
allowed_origins = [origin.strip() for origin in cors_origins_str.split(",")]

# Add production frontend URL if specified
frontend_url = os.getenv("FRONTEND_URL")
if frontend_url and frontend_url not in allowed_origins:
    allowed_origins.append(frontend_url)

logger.info(f"CORS allowed origins: {allowed_origins}")

app.add_middleware(
    CORSMiddleware,
    allow_origins=allowed_origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Request timing middleware
@app.middleware("http")
async def add_process_time_header(request: Request, call_next):
    """Add X-Process-Time header to all responses"""
    start_time = time.time()
    response = await call_next(request)
    process_time = time.time() - start_time
    response.headers["X-Process-Time"] = str(process_time)
    return response

# Error handling
@app.exception_handler(Exception)
async def global_exception_handler(request: Request, exc: Exception):
    """Global exception handler"""
    logger.error(f"Global exception: {exc}", exc_info=True)
    return JSONResponse(
        status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
        content={
            "error": "Internal server error",
            "message": str(exc) if app.debug else "An unexpected error occurred"
        }
    )

# Health check endpoint
@app.get("/health", tags=["System"])
async def health_check():
    """Health check endpoint"""
    return {
        "status": "healthy",
        "service": "creditbeast-api",
        "version": "1.0.0"
    }

@app.get("/", tags=["System"])
async def root():
    """Root endpoint"""
    return {
        "message": "CreditBeast API",
        "docs": "/api/docs",
        "version": "1.0.0"
    }

# Include routers
app.include_router(auth.router, prefix="/api/auth", tags=["Authentication"])
app.include_router(leads.router, prefix="/api/leads", tags=["Leads"])
app.include_router(clients.router, prefix="/api/clients", tags=["Clients"])
app.include_router(disputes.router, prefix="/api/disputes", tags=["Disputes"])
app.include_router(billing.router, prefix="/api/billing", tags=["Billing"])
app.include_router(webhooks.router, prefix="/api/webhooks", tags=["Webhooks"])
app.include_router(emails.router, prefix="/api/emails", tags=["Email Notifications"])
app.include_router(automation.router, prefix="/api/automation", tags=["Automation"])
app.include_router(security.router, prefix="/api/security", tags=["Security"])
app.include_router(analytics.router, prefix="/api/analytics", tags=["Analytics"])
app.include_router(branding.router, prefix="/api/branding", tags=["Branding & White-Label"])
app.include_router(client_portal.router, prefix="/api/client-portal", tags=["Client Portal"])
app.include_router(integrations.router, prefix="/api/integrations", tags=["Third-Party Integrations"])

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(
        "main:app",
        host="0.0.0.0",
        port=8000,
        reload=True,
        log_level="info"
    )
