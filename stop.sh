#!/bin/bash
# Avery 后端停止脚本 - 手动停止所有后端进程

echo "=== Avery Content Generation - 后端停止 ==="
echo ""

# 查找所有占用端口8000的进程
PIDS=$(lsof -ti :8000 2>/dev/null)

if [ -z "$PIDS" ]; then
    echo "✅ 没有发现运行中的后端进程"
    echo "   端口8000空闲"
    exit 0
fi

echo "🔍 发现以下进程占用端口8000:"
echo "$PIDS" | while read pid; do
    echo "   PID: $pid"
    ps -p $pid -o command= | sed 's/^/     /'
done

echo ""
echo "🛑 正在停止进程..."

# 停止所有进程
echo "$PIDS" | xargs kill -9 2>/dev/null

# 等待一下
sleep 1

# 验证清理结果
REMAINING=$(lsof -ti :8000 2>/dev/null)
if [ -z "$REMAINING" ]; then
    echo "✅ 所有进程已停止"
    echo "   端口8000已释放"
else
    echo "⚠️  部分进程仍在运行:"
    echo "$REMAINING" | while read pid; do
        echo "   PID: $pid"
    done
    echo ""
    echo "💡 可以手动强制停止:"
    echo "$REMAINING" | while read pid; do
        echo "   kill -9 $pid"
    done
fi

echo ""
echo "=== 停止完成 ==="
