# AI 图像识别聊天机器人

一个基于 Vue 3 + FastAPI 的全栈 AI 聊天机器人项目，支持图像识别和文本对话。

## 项目结构

```
chatbot/
├── backend/          # 后端服务 (FastAPI + Python)
├── frontend/         # 前端应用 (Vue 3 + TypeScript)
├── .git/            # Git版本控制
├── .vscode/         # VS Code配置
├── start.sh         # 启动脚本
├── stop.sh          # 停止脚本
└── README.md        # 项目说明
```

## 快速开始

### 1. 启动后端服务

```bash
cd backend
python main.py
```

后端服务将在 `http://localhost:8000` 启动

### 2. 启动前端应用

```bash
cd frontend
npm install
npm run dev
```

前端应用将在 `http://localhost:5173` 启动

### 3. 访问应用

打开浏览器访问 `http://localhost:5173` 即可使用聊天机器人

## 功能特性

- 🔐 用户认证系统
- 💬 实时 AI 对话
- 🖼️ 图像识别分析
- 📱 响应式设计
- 💾 聊天历史记录
- 🔄 流式 AI 响应
- 📋 可展开/收起侧边栏
- 🔍 聊天搜索功能
- 👤 用户中心管理

## 侧边栏功能

### 展开状态

- **切换按钮**: 收起/展开侧边栏
- **新建对话**: 创建新的聊天会话
- **搜索聊天**: 通过关键词搜索历史对话
- **历史记录**: 跳转到历史记录管理页面
- **最近对话**: 显示历史聊天会话列表
- **用户中心**: 用户信息和设置管理

### 收起状态

- 只显示功能图标和用户头像
- 保持所有功能的可访问性
- 节省屏幕空间

## 技术栈

### 后端

- FastAPI
- SQLAlchemy
- MySQL
- JWT 认证
- 阿里云 Qwen 大模型

### 前端

- Vue 3
- TypeScript
- Pinia 状态管理
- Vue Router
- Vite 构建工具

## 开发说明

- 前端代码位于 `frontend/` 目录
- 后端代码位于 `backend/` 目录
- 数据库配置在 `backend/app/core/config.py`
- 环境变量配置在 `backend/.env`

## 使用说明

### 启动整个项目

```bash
./start.sh
```

### 停止所有服务

```bash
./stop.sh
```

### 分别启动服务

```bash
# 启动后端
cd backend && python main.py

# 启动前端
cd frontend && npm run dev
```
