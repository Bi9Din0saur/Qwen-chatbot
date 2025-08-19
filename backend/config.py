import os
from typing import Optional
from pydantic_settings import BaseSettings

class Settings(BaseSettings):
    # 数据库配置
    database_url: str = "mysql+pymysql://username:password@localhost:3306/chatbot_db"
    
    # JWT配置
    secret_key: str = "your-secret-key-here-change-in-production"
    algorithm: str = "HS256"
    access_token_expire_minutes: int = 30
    
    # Qwen-VL API配置
    qwen_api_key: str = "your-qwen-api-key-here"
    qwen_base_url: str = "https://dashscope.aliyuncs.com/compatible-mode/v1"
    
    # 文件上传配置
    upload_dir: str = "./uploads"
    max_file_size: int = 10485760  # 10MB
    
    # Redis配置（可选）
    redis_url: Optional[str] = "redis://localhost:6379"
    
    # 应用配置
    debug: bool = True
    host: str = "0.0.0.0"
    port: int = 8000
    
    class Config:
        env_file = ".env"

settings = Settings()
