#!/bin/bash

# AI图像识别聊天机器人启动脚本

echo "🚀 启动AI图像识别聊天机器人..."

# 检查后端是否已运行
if ! pgrep -f "python.*main.py" > /dev/null; then
    echo "📡 启动后端服务..."
    cd backend
    python main.py &
    BACKEND_PID=$!
    cd ..
    echo "✅ 后端服务已启动 (PID: $BACKEND_PID)"
else
    echo "✅ 后端服务已在运行"
fi

# 等待后端启动
echo "⏳ 等待后端服务启动..."
sleep 3

# 检查前端是否已运行
if ! pgrep -f "vite" > /dev/null; then
    echo "🌐 启动前端服务..."
    cd frontend
    npm run dev &
    FRONTEND_PID=$!
    cd ..
    echo "✅ 前端服务已启动 (PID: $FRONTEND_PID)"
else
    echo "✅ 前端服务已在运行"
fi

echo ""
echo "🎉 服务启动完成！"
echo "📱 前端地址: http://localhost:5173"
echo "🔧 后端地址: http://localhost:8000"
echo ""
echo "按 Ctrl+C 停止所有服务"

# 等待用户中断
wait
