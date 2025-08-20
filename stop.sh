#!/bin/bash

# AI图像识别聊天机器人停止脚本

echo "🛑 停止AI图像识别聊天机器人..."

# 停止后端服务
echo "📡 停止后端服务..."
pkill -f "python.*main.py" 2>/dev/null || echo "后端服务未运行"

# 停止前端服务
echo "🌐 停止前端服务..."
pkill -f "vite" 2>/dev/null || echo "前端服务未运行"

# 停止npm进程
echo "📦 停止npm进程..."
pkill -f "npm run dev" 2>/dev/null || echo "npm进程未运行"

echo "✅ 所有服务已停止"
