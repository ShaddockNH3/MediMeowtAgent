from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from pathlib import Path
from config import settings
from app.routers import (
    user_router,
    doctor_router,
    questionnaire_router,
    department_router
)
from app.database import engine, Base

# 创建FastAPI应用
app = FastAPI(
    title="MediMeow Backend API",
    description="智能医疗预诊系统后端API",
    version="1.0.0",
    docs_url="/docs",
    redoc_url="/redoc"
)

# 配置CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.get_origins_list(),
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# 创建上传目录
upload_dir = Path(settings.UPLOAD_DIR)
upload_dir.mkdir(parents=True, exist_ok=True)

# 挂载静态文件目录
app.mount("/uploads", StaticFiles(directory=str(upload_dir)), name="uploads")

# 注册路由
app.include_router(user_router)
app.include_router(doctor_router)
app.include_router(questionnaire_router)
app.include_router(department_router)


@app.on_event("startup")
async def startup_event():
    """应用启动事件"""
    # 创建数据库表
    Base.metadata.create_all(bind=engine)
    print("✅ 数据库表创建完成")
    print(f"✅ 应用已启动")


@app.on_event("shutdown")
async def shutdown_event():
    """应用关闭事件"""
    print("👋 应用已关闭")


@app.get("/", tags=["Root"])
async def root():
    """根路径"""
    return {
        "message": "Welcome to MediMeow Backend API",
        "docs": "/docs",
        "redoc": "/redoc"
    }


@app.get("/health", tags=["Health"])
async def health_check():
    """健康检查"""
    return {
        "status": "healthy",
        "version": "1.0.0"
    }


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(
        "main:app",
        host="0.0.0.0",
        port=8000,
        reload=True
    )
