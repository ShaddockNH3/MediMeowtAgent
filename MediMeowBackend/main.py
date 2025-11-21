from fastapi import FastAPI, Request, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from fastapi.responses import JSONResponse
from fastapi.exceptions import RequestValidationError
from pathlib import Path
from config import settings
from app.routers import (
    user_router,
    doctor_router,
    questionnaire_router,
    department_router
)
from app.database import engine, Base
from app.utils.response import error_response

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

# 全局异常处理器
@app.exception_handler(HTTPException)
async def http_exception_handler(request: Request, exc: HTTPException):
    """处理 HTTPException，返回标准 HTTP 状态码 + base 格式"""
    # 映射状态码到错误代码
    code_map = {
        401: "10002",  # 未授权/登录失效
        403: "10003",  # 权限不足
        404: "10004",  # 资源不存在
        500: "10005",  # 服务器错误
    }
    
    return JSONResponse(
        status_code=exc.status_code,  # 返回标准 HTTP 状态码
        content=error_response(
            code=code_map.get(exc.status_code, "10001"),
            msg=exc.detail
        )
    )

@app.exception_handler(RequestValidationError)
async def validation_exception_handler(request: Request, exc: RequestValidationError):
    """处理请求参数验证错误"""
    errors = []
    for error in exc.errors():
        field = ".".join(str(x) for x in error["loc"][1:])  # 跳过 'body'
        errors.append(f"{field}: {error['msg']}")
    
    return JSONResponse(
        status_code=400,  # 参数错误返回 400
        content=error_response(
            code="10007",
            msg=f"参数验证失败: {'; '.join(errors)}"
        )
    )

@app.exception_handler(Exception)
async def general_exception_handler(request: Request, exc: Exception):
    """处理所有未捕获的异常"""
    import traceback
    print(f"未捕获的异常: {str(exc)}")
    traceback.print_exc()
    
    return JSONResponse(
        status_code=500,  # 服务器错误返回 500
        content=error_response(
            code="10005",
            msg=f"服务器内部错误: {str(exc)}"
        )
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
    print("数据库表创建完成")
    print("应用已启动")


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
