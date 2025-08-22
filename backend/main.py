from fastapi import FastAPI, Depends, HTTPException, status
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from contextlib import asynccontextmanager
import uvicorn
import os

from app.api import auth, chat, upload
# from app.db.database import engine
# from app.models import Base

# 创建数据库表
# Base.metadata.create_all(bind=engine)

@asynccontextmanager
async def lifespan(app: FastAPI):
    # 启动时的操作
    print("🚀 聊天机器人后端服务启动中...")
    yield
    # 关闭时的操作
    print("👋 聊天机器人后端服务关闭中...")

# 创建FastAPI应用
app = FastAPI(
    title="AI图像识别聊天机器人",
    description="基于Qwen-VL的多模态AI聊天机器人后端API",
    version="1.0.0",
    lifespan=lifespan
)

# 配置CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:5173", "http://localhost:3000", "http://localhost", "http://frontend"],  # 前端地址
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# 挂载静态文件
app.mount("/uploads", StaticFiles(directory="uploads"), name="uploads")

# 包含路由
app.include_router(auth.router, prefix="/api/auth", tags=["认证"])
app.include_router(chat.router, prefix="/api/chat", tags=["聊天"])
app.include_router(upload.router, prefix="/api/upload", tags=["文件上传"])

@app.get("/")
async def root():
    return {
        "message": "AI图像识别聊天机器人后端API",
        "version": "1.0.0",
        "docs": "/docs"
    }

@app.get("/health")
async def health_check():
    return {"status": "healthy", "message": "服务运行正常"}

if __name__ == "__main__":
    # 从环境变量获取配置
    host = os.getenv("HOST", "0.0.0.0")
    port = int(os.getenv("PORT", "8000"))
    debug = os.getenv("DEBUG", "True").lower() == "true"
    
    uvicorn.run(
        "main:app",
        host=host,
        port=port,
        reload=debug
    )
