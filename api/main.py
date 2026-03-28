from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
import logging

from api.core.config import settings
from api.core.logging_config import init_app_logging
from api.db.database import engine, Base
from api.api import content as content_router
from api.routes import infographic as infographic_router
from api.routes import auth as auth_router

# Import all models to ensure tables are created
from api.models import user, content, infographic

# 初始化日志
init_app_logging("avery")
logger = logging.getLogger(__name__)

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
        "http://localhost:3002",
        "https://www.averycmo.com",  # 生产环境
    ],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.on_event("startup")
async def startup_event():
    """Create database tables on startup"""
    logger.info("="*60)
    logger.info("🚀 Avery Content Generation API 启动")
    logger.info(f"📡 环境: {settings.environment}")
    logger.info(f"🌐 前端URL: {settings.frontend_url}")
    logger.info(f"🔑 Novita API: {'已配置' if settings.novita_api_key else '未配置'}")
    logger.info(f"🔑 Tavily API: {'已配置' if settings.tavily_api_key else '未配置'}")
    logger.info("="*60)

    try:
        Base.metadata.create_all(bind=engine)
        logger.info("✅ 数据库表初始化成功")
    except Exception as e:
        logger.error(f"❌ 数据库表初始化失败: {e}")
        logger.warning("⚠️  数据库表将在首次请求时创建")


# Root endpoint
@app.get("/")
def read_root():
    """Root endpoint - API health check"""
    logger.info("访问根路径")
    return {
        "message": "Avery Content Generation API",
        "version": "1.0.0",
        "status": "running",
        "environment": settings.environment,
        "docs": "/docs",
        "logs": "/logs"
    }


@app.get("/health")
def health_check():
    """Health check endpoint"""
    logger.debug("健康检查请求")
    return {
        "status": "healthy",
        "services": {
            "api": "ok",
            "database": "ok",
            "novita": "configured" if settings.novita_api_key else "not_configured",
            "tavily": "configured" if settings.tavily_api_key else "not_configured",
        }
    }


@app.get("/logs")
async def get_logs(lines: int = 100):
    """
    获取最近的日志行

    Args:
        lines: 返回的日志行数（默认100，最大1000）
    """
    import os

    log_file = "logs/avery.log"
    lines = min(lines, 1000)  # 限制最大行数

    if not os.path.exists(log_file):
        return {"error": "日志文件不存在", "log_file": log_file}

    try:
        with open(log_file, 'r', encoding='utf-8') as f:
            # 读取最后N行
            all_lines = f.readlines()
            last_lines = all_lines[-lines:] if len(all_lines) > lines else all_lines

        return {
            "log_file": log_file,
            "total_lines": len(all_lines),
            "returned_lines": len(last_lines),
            "logs": "".join(last_lines)
        }
    except Exception as e:
        logger.error(f"读取日志文件失败: {e}")
        return {"error": str(e), "log_file": log_file}


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
app.include_router(auth_router.router)
app.include_router(content_router.router, prefix="/api/v1/content", tags=["Content"])
app.include_router(infographic_router.router)

# Shutdown event
@app.on_event("shutdown")
async def shutdown_event():
    """应用关闭时的处理"""
    logger.info("="*60)
    logger.info("🛑 Avery Content Generation API 关闭")
    logger.info("="*60)


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000, reload=True)
