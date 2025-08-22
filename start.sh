#!/bin/bash

echo "🚀 启动聊天机器人项目..."

# 检查Docker是否运行
if ! docker info > /dev/null 2>&1; then
    echo "❌ Docker未运行，请先启动Docker"
    exit 1
fi

# 检查docker-compose.yml是否存在
if [ ! -f "docker-compose.yml" ]; then
    echo "❌ docker-compose.yml文件不存在"
    exit 1
fi

# 启动服务
echo "📦 启动Docker服务..."
docker-compose up -d

# 等待服务启动
echo "⏳ 等待服务启动..."
sleep 10

# 检查服务状态
echo "🔍 检查服务状态..."
docker-compose ps

# 检查后端健康状态
echo "🏥 检查后端健康状态..."
for i in {1..12}; do
    if curl -s http://localhost:8000/health > /dev/null; then
        echo "✅ 后端服务启动成功！"
        break
    else
        echo "⏳ 等待后端启动... ($i/12)"
        sleep 10
    fi
done

# 检查前端
echo "🌐 检查前端服务..."
if curl -s http://localhost > /dev/null; then
    echo "✅ 前端服务启动成功！"
else
    echo "⚠️  前端服务可能还在启动中..."
fi

echo ""
echo "🎉 项目启动完成！"
echo "📱 访问地址:"
echo "   - 前端界面: http://localhost"
echo "   - 后端API: http://localhost:8000"
echo "   - API文档: http://localhost:8000/docs"
echo ""
echo "📋 常用命令:"
echo "   - 查看状态: docker-compose ps"
echo "   - 查看日志: docker-compose logs"
echo "   - 停止服务: docker-compose down"
echo "   - 重启服务: docker-compose restart"
