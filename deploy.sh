#!/bin/bash

# Docker 部署脚本
set -e

echo "🚀 开始 Docker 部署..."

# 检查 Docker 和 docker-compose
if ! command -v docker &> /dev/null; then
    echo "❌ Docker 未安装，请先安装 Docker"
    exit 1
fi

if ! command -v docker-compose &> /dev/null; then
    echo "❌ docker-compose 未安装，请先安装 docker-compose"
    exit 1
fi

# 创建必要的目录
echo "📁 创建部署目录..."

# 创建前端目录
if [ ! -d "/opt/webapp-frontend" ]; then
    echo "创建前端目录: /opt/webapp-frontend"
    sudo mkdir -p /opt/webapp-frontend/dist
    sudo chown $USER:$USER /opt/webapp-frontend -R
fi

# 创建数据目录
if [ ! -d "/data" ]; then
    echo "创建数据目录: /data"
    mkdir -p /data/{postgres,redis}
fi

# 检查前端文件
if [ ! -f "/opt/webapp-frontend/dist/index.html" ]; then
    echo "⚠️  警告: 前端文件不存在于 /opt/webapp-frontend/dist/"
    echo "请将前端打包文件复制到该目录"

    # 创建一个简单的 index.html 用于测试
    cat > /opt/webapp-frontend/dist/index.html << EOF
<!DOCTYPE html>
<html>
<head>
    <title>Frontend Placeholder</title>
    <meta charset="utf-8">
</head>
<body>
    <h1>前端服务运行中</h1>
    <p>API 地址: <a href="http://localhost:15000" target="_blank">http://localhost:15000</a></p>
    <p>请将您的前端打包文件复制到 /opt/webapp-frontend/dist/ 目录</p>
</body>
</html>
EOF
    echo "✅ 已创建测试页面"
fi

# 检查环境变量文件
if [ ! -f ".env" ]; then
    if [ -f ".env.example" ]; then
        echo "📋 复制环境变量文件..."
        cp .env.example .env
        echo "⚠️  请编辑 .env 文件配置您的环境变量"
    else
        echo "❌ 找不到 .env.example 文件"
        exit 1
    fi
fi

# 构建和启动服务
echo "🔨 构建 Docker 镜像..."
docker-compose build

echo "🚀 启动服务..."
docker-compose up -d

# 等待服务启动
echo "⏳ 等待服务启动..."
sleep 10

# 检查服务状态
echo "📊 检查服务状态..."
docker-compose ps

# 健康检查
echo "🏥 健康检查..."
sleep 5

API_STATUS=$(curl -s -o /dev/null -w "%{http_code}" http://localhost:15000/health || echo "000")
FRONTEND_STATUS=$(curl -s -o /dev/null -w "%{http_code}" http://localhost:18080/ || echo "000")

echo ""
echo "==============================================="
echo "🎉 部署完成！"
echo "==============================================="
echo ""
echo "服务访问地址:"
echo "  🌐 前端: http://localhost:18080"
echo "  🔌 API:  http://localhost:15000"
echo "  🗄️  数据库: localhost:15432"
echo "  📦 Redis: localhost:16379"
echo ""
echo "服务状态:"
if [ "$API_STATUS" == "200" ]; then
    echo "  ✅ API 服务: 运行正常"
else
    echo "  ❌ API 服务: 状态异常 (HTTP $API_STATUS)"
fi

if [ "$FRONTEND_STATUS" == "200" ]; then
    echo "  ✅ 前端服务: 运行正常"
else
    echo "  ❌ 前端服务: 状态异常 (HTTP $FRONTEND_STATUS)"
fi
echo ""
echo "常用命令:"
echo "  查看日志: make logs"
echo "  停止服务: make down"
echo "  重启服务: make restart"
echo "  服务状态: make status"
echo ""
echo "数据目录:"
echo "  前端文件: /opt/webapp-frontend/dist/"
echo "  数据库数据: /data/postgres/"
echo "  Redis 数据: /data/redis/"
echo "==============================================="