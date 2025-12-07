from pydantic_settings import BaseSettings
from pydantic import Field
from typing import List


class Settings(BaseSettings):
    """应用配置"""
    
    # 数据库配置 (MariaDB)
    DATABASE_URL: str = Field(
        default="mysql+pymysql://root:12345@localhost:3306/medimeow_db",
        description="MariaDB 数据库连接URL"
    )
    
    # JWT配置
    SECRET_KEY: str = Field(
        default="your-secret-key-change-in-production",
        description="JWT密钥"
    )
    ALGORITHM: str = Field(default="HS256", description="JWT加密算法")
    ACCESS_TOKEN_EXPIRE_MINUTES: int = Field(
        default=30,
        description="访问令牌过期时间(分钟)"
    )
    
    # 文件上传配置
    UPLOAD_DIR: str = Field(default="./uploads", description="上传文件目录")
    MAX_FILE_SIZE: int = Field(default=10485760, description="最大文件大小(字节)")
    
    # CORS配置
    ALLOWED_ORIGINS: str = Field(
        default="http://localhost:3000,http://localhost:5173",
        description="允许的跨域源"
    )

    # AI服务配置
    GLM_API_KEY: str = Field(
        default="8eb3feaa749d4797afee7a3eeca9ecc8.sStyqRnz3SLVVxyk",
        description="GLM API密钥"
    )
    AI_SERVICE_HOST: str = Field(
        default="127.0.0.1:50051",
        description="AI服务主机地址"
    )

    class Config:
        env_file = ".env"
        case_sensitive = True
    
    def get_origins_list(self) -> List[str]:
        """获取CORS允许的源列表"""
        return [origin.strip() for origin in self.ALLOWED_ORIGINS.split(",")]


settings = Settings()
