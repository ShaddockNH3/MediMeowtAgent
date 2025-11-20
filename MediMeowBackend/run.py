#!/usr/bin/env python3
"""
MediMeow Backend - 一键启动脚本
自动检查环境、配置、数据库连接，并启动服务
"""
import sys
import os
import subprocess
from pathlib import Path

def check_python_version():
    """检查Python版本"""
    version = sys.version_info
    if version.major < 3 or (version.major == 3 and version.minor < 8):
        print(f"Python版本过低: {version.major}.{version.minor}.{version.micro} (需要 3.8+)")
        return False
    return True


def check_dependencies():
    """检查依赖包"""
    requirements_file = Path(__file__).parent / "requirements.txt"
    
    if not requirements_file.exists():
        print("requirements.txt 不存在")
        return False
    
    try:
        import fastapi
        import sqlalchemy
        import pymysql
        import jose
        import passlib
        return True
    except ImportError as e:
        print(f"缺少依赖: {e.name}")
        print(f"   pip install -r requirements.txt")
        return False


def check_env_file():
    """检查环境配置文件"""
    env_file = Path(__file__).parent / ".env"
    env_example = Path(__file__).parent / ".env.example"
    
    if not env_file.exists():
        print(".env 不存在")
        return False
    return True


def check_database_connection():
    """检查数据库连接"""
    try:
        sys.path.insert(0, str(Path(__file__).parent))
        from config import settings
        from sqlalchemy import create_engine, text
        
        engine = create_engine(settings.DATABASE_URL, pool_pre_ping=True)
        with engine.connect() as conn:
            result = conn.execute(text("SELECT 1"))
            result.fetchone()
        return True
    except Exception as e:
        print(f"数据库连接失败: {str(e)[:50]}")
        return False


def init_database():
    """初始化数据库表"""
    try:
        from app.database import Base, engine
        Base.metadata.create_all(bind=engine)
        return True
    except Exception as e:
        print(f"数据库表初始化失败: {str(e)[:50]}")
        return False


def create_upload_directory():
    """创建上传目录"""
    try:
        from config import settings
        upload_dir = Path(settings.UPLOAD_DIR)
        upload_dir.mkdir(parents=True, exist_ok=True)
        return True
    except Exception as e:
        print(f"创建上传目录失败: {str(e)[:50]}")
        return False


def start_server(dev_mode=True):
    try:
        if dev_mode:
            subprocess.run([
                sys.executable, "-m", "uvicorn",
                "main:app",
                "--host", "0.0.0.0",
                "--port", "8000",
                "--reload"
            ])
        else:
            subprocess.run([
                sys.executable, "-m", "uvicorn",
                "main:app",
                "--host", "0.0.0.0",
                "--port", "8000"
            ])
    except Exception as e:
        return False
    
    return True

def main():
    os.chdir(Path(__file__).parent)
    checks = [check_python_version, check_dependencies, check_env_file]
    
    for check_func in checks:
        if not check_func():
            sys.exit(1)
    
    # 数据库检查
    db_ok = check_database_connection()
    if db_ok:
        init_database()
        create_upload_directory()
    else:
        print("\n数据库未就绪")
        user_input = input("是否继续? (y/n): ")
        if user_input.lower() != 'y':
            sys.exit(0)
    
    # 启动服务
    dev_mode = "--prod" not in sys.argv
    start_server(dev_mode=dev_mode)


if __name__ == "__main__":
    main()
