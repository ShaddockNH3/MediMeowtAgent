#!/usr/bin/env python3
"""
MediMeow Backend - 一键启动脚本
自动检查环境、配置、数据库连接，并启动服务
"""
import sys
import os
import subprocess
from pathlib import Path


def print_banner():
    """打印启动横幅"""
    banner = """
╔════════════════════════════════════════╗
║   MediMeow Backend - 启动程序          ║
║   智能医疗预诊系统后端服务             ║
╚════════════════════════════════════════╝
"""
    print(banner)


def check_python_version():
    """检查Python版本"""
    print("🔍 检查Python版本...")
    version = sys.version_info
    if version.major < 3 or (version.major == 3 and version.minor < 8):
        print("❌ Python版本过低，需要 Python 3.8 或更高版本")
        print(f"   当前版本: Python {version.major}.{version.minor}.{version.micro}")
        return False
    print(f"✅ Python版本: {version.major}.{version.minor}.{version.micro}")
    return True


def check_dependencies():
    """检查依赖包"""
    print("\n🔍 检查依赖包...")
    requirements_file = Path(__file__).parent / "requirements.txt"
    
    if not requirements_file.exists():
        print("❌ requirements.txt 文件不存在")
        return False
    
    try:
        import fastapi
        import sqlalchemy
        import pymysql
        import jose
        import passlib
        print("✅ 核心依赖包已安装")
        return True
    except ImportError as e:
        print(f"❌ 缺少依赖包: {e.name}")
        print("\n请运行以下命令安装依赖:")
        print(f"  pip install -r {requirements_file}")
        return False


def check_env_file():
    """检查环境配置文件"""
    print("\n🔍 检查环境配置...")
    env_file = Path(__file__).parent / ".env"
    env_example = Path(__file__).parent / ".env.example"
    
    if not env_file.exists():
        print("⚠️  .env 文件不存在")
        if env_example.exists():
            print("💡 提示: 请复制 .env.example 为 .env 并修改配置")
            print("   使用默认配置启动（数据库连接可能失败）")
        else:
            print("⚠️  警告: .env.example 也不存在")
        return False
    
    print("✅ 环境配置文件存在")
    return True


def check_database_connection():
    """检查数据库连接"""
    print("\n🔍 检查数据库连接...")
    
    try:
        # 动态导入以避免环境问题
        sys.path.insert(0, str(Path(__file__).parent))
        from config import settings
        from sqlalchemy import create_engine, text
        
        print(f"   数据库: {settings.DATABASE_URL.split('@')[-1] if '@' in settings.DATABASE_URL else 'localhost'}")
        
        engine = create_engine(settings.DATABASE_URL, pool_pre_ping=True)
        with engine.connect() as conn:
            result = conn.execute(text("SELECT 1"))
            result.fetchone()
        
        print("✅ 数据库连接成功")
        return True
    except Exception as e:
        print(f"❌ 数据库连接失败: {str(e)}")
        print("\n请检查:")
        print("  1. MariaDB/MySQL 服务是否已启动")
        print("  2. .env 文件中的数据库配置是否正确")
        print("  3. 数据库和用户是否已创建")
        print("\n参考文档: MARIADB_SETUP.md")
        return False


def init_database():
    """初始化数据库表"""
    print("\n🔍 初始化数据库表...")
    
    try:
        from app.database import Base, engine
        Base.metadata.create_all(bind=engine)
        print("✅ 数据库表初始化完成")
        return True
    except Exception as e:
        print(f"❌ 数据库表初始化失败: {str(e)}")
        return False


def create_upload_directory():
    """创建上传目录"""
    print("\n🔍 创建上传目录...")
    
    try:
        from config import settings
        upload_dir = Path(settings.UPLOAD_DIR)
        upload_dir.mkdir(parents=True, exist_ok=True)
        print(f"✅ 上传目录: {upload_dir.absolute()}")
        return True
    except Exception as e:
        print(f"❌ 创建上传目录失败: {str(e)}")
        return False


def start_server(dev_mode=True):
    """启动服务器"""
    print("\n" + "="*50)
    print("🚀 启动 MediMeow Backend 服务...")
    print("="*50 + "\n")
    
    try:
        if dev_mode:
            print("📍 开发模式 - 自动重载已启用")
            print("📡 服务地址: http://localhost:8000")
            print("📚 API文档: http://localhost:8000/docs")
            print("📖 ReDoc: http://localhost:8000/redoc")
            print("\n按 Ctrl+C 停止服务\n")
            
            # 使用uvicorn命令行启动
            subprocess.run([
                sys.executable, "-m", "uvicorn",
                "main:app",
                "--host", "0.0.0.0",
                "--port", "8000",
                "--reload"
            ])
        else:
            print("📍 生产模式")
            subprocess.run([
                sys.executable, "-m", "uvicorn",
                "main:app",
                "--host", "0.0.0.0",
                "--port", "8000"
            ])
    except KeyboardInterrupt:
        print("\n\n👋 服务已停止")
    except Exception as e:
        print(f"\n❌ 启动失败: {str(e)}")
        return False
    
    return True


def main():
    """主函数"""
    print_banner()
    
    # 切换到脚本所在目录
    os.chdir(Path(__file__).parent)
    
    # 环境检查
    checks = [
        ("Python版本", check_python_version),
        ("依赖包", check_dependencies),
        ("环境配置", check_env_file),
    ]
    
    for check_name, check_func in checks:
        if not check_func():
            print(f"\n❌ {check_name}检查失败，请修复后重试")
            sys.exit(1)
    
    # 数据库检查（允许失败，继续启动）
    db_ok = check_database_connection()
    if db_ok:
        init_database()
        create_upload_directory()
    else:
        print("\n⚠️  数据库未就绪，但服务可以启动（部分功能不可用）")
        user_input = input("\n是否继续启动? (y/n): ")
        if user_input.lower() != 'y':
            print("👋 已取消启动")
            sys.exit(0)
    
    # 启动服务
    dev_mode = "--prod" not in sys.argv
    start_server(dev_mode=dev_mode)


if __name__ == "__main__":
    main()
