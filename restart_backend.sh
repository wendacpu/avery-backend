#!/bin/bash

echo "🔄 重启后端服务..."

# 停止现有服务
echo "1️⃣ 停止现有后端服务..."
pkill -f "uvicorn api.main:app"
sleep 2

# 进入后端目录
cd /Users/wanting/program/CC/Avery/backend

# 激活虚拟环境
echo "2️⃣ 激活虚拟环境..."
source venv/bin/activate

# 启动服务
echo "3️⃣ 启动后端服务..."
nohup uvicorn api.main:app --host 0.0.0.0 --port 8000 --reload > /tmp/avery-backend.log 2>&1 &

# 等待启动
sleep 3

# 检查状态
echo ""
echo "4️⃣ 检查服务状态..."
if ps aux | grep -v grep | grep "uvicorn api.main:app" > /dev/null; then
    echo "✅ 后端服务启动成功！"
    echo ""
    echo "📋 最近日志："
    echo "---"
    tail -20 /tmp/avery-backend.log
    echo "---"
    echo ""
    echo "✅ 配置完成！现在可以测试生成了"
    echo "   访问：http://localhost:3000/generate"
else
    echo "❌ 后端服务启动失败"
    echo ""
    echo "查看完整日志："
    tail -50 /tmp/avery-backend.log
fi
