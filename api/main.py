from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from api.core.config import settings
from api.db.database import engine, Base
from api.api import auth, users, content

# Create FastAPI app
app = FastAPI(
    title="Avery API",
    description="AI-powered LinkedIn content generation platform",
    version="1.0.0",
)

# Configure CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        settings.frontend_url,
        "http://localhost:3000",
        "http://localhost:3001",
        "https://www.averycmo.com",  # 生产环境
    ],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.on_event("startup")
async def startup_event():
    """Create database tables on startup"""
    try:
        Base.metadata.create_all(bind=engine)
    except Exception as e:
        # Log error but don't prevent app from starting
        print(f"Warning: Could not create database tables: {e}")
        print("Database tables will be created on first request")


# Root endpoint
@app.get("/")
def read_root():
    """Root endpoint - API health check"""
    return {
        "message": "Avery API is running",
        "version": "1.0.0",
        "environment": settings.environment
    }


@app.get("/health")
def health_check():
    """Health check endpoint"""
    return {"status": "healthy"}


@app.get("/debug/config")
def debug_config():
    """Debug endpoint to check configuration (REMOVE IN PRODUCTION)"""
    return {
        "database_url_prefix": settings.database_url.split("@")[1] if "@" in settings.database_url else settings.database_url,
        "environment": settings.environment,
        "has_secret_key": bool(settings.secret_key),
        "frontend_url": settings.frontend_url,
    }


# Include routers
app.include_router(auth.router, prefix="/api/v1/auth", tags=["Authentication"])
app.include_router(users.router, prefix="/api/v1/users", tags=["Users"])
app.include_router(content.router, prefix="/api/v1/content", tags=["Content"])


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000, reload=True)
