#!/bin/bash

echo "🛑 停止聊天机器人项目..."

# 检查docker-compose.yml是否存在
if [ ! -f "docker-compose.yml" ]; then
    echo "❌ docker-compose.yml文件不存在"
    exit 1
fi

# 停止所有服务
echo "📦 停止Docker服务..."
docker-compose down

echo ""
echo "✅ 项目已停止！"
echo ""
echo "📋 其他选项:"
echo "   - 完全清理(删除数据): docker-compose down -v"
echo "   - 查看状态: docker-compose ps"
echo "   - 重新启动: ./start.sh"
