#!/bin/bash
# Avery 后端启动脚本 - 带自动清理功能

# 获取脚本所在目录
SCRIPT_DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" && pwd )"

# PID跟踪变量
BACKEND_PID=""

# 清理函数 - 在脚本退出时自动调用
cleanup() {
    local exit_code=$?

    echo ""
    echo "=== 正在清理进程 ==="

    # 杀死跟踪的后端进程
    if [ -n "$BACKEND_PID" ]; then
        echo "🛑 停止后端进程 (PID: $BACKEND_PID)..."
        kill $BACKEND_PID 2>/dev/null
        wait $BACKEND_PID 2>/dev/null
        echo "✅ 后端进程已停止"
    fi

    # 清理端口8000上可能残留的进程
    local pids=$(lsof -ti :8000 2>/dev/null)
    if [ -n "$pids" ]; then
        echo "🧹 清理端口8000上的残留进程..."
        echo "$pids" | xargs kill -9 2>/dev/null
        echo "✅ 端口8000已清理"
    fi

    echo "=== 清理完成 ==="
    echo ""

    exit $exit_code
}

# 设置trap - 捕获各种退出信号
trap cleanup EXIT INT TERM HUP

# 激活虚拟环境
if [ -f "$SCRIPT_DIR/venv/bin/activate" ]; then
    source "$SCRIPT_DIR/venv/bin/activate"
    echo "✓ 已激活虚拟环境"
else
    echo "✗ 虚拟环境未找到"
    echo "  请先运行: python3 -m venv venv"
    echo "  然后运行: pip install -r requirements.txt"
    exit 1
fi

# 检查并自动清理端口占用
echo "🔍 检查端口8000..."
if lsof -Pi :8000 -sTCP:LISTEN -t >/dev/null 2>&1; then
    echo "⚠️  端口 8000 已被占用"
    echo "🧹 自动清理中..."

    # 获取占用端口的进程
    old_pids=$(lsof -ti :8000 2>/dev/null)
    if [ -n "$old_pids" ]; then
        echo "   发现进程: $old_pids"
        echo "$old_pids" | xargs kill -9 2>/dev/null
        sleep 1
        echo "✅ 旧进程已清理"
    fi
else
    echo "✅ 端口8000空闲"
fi

# 设置环境变量
export PYTHONPATH="$SCRIPT_DIR:$PYTHONPATH"
export LOG_LEVEL=INFO

# 探测正确的 Python 可执行文件
PYTHON_EXEC="python"
if [ -f "$SCRIPT_DIR/venv/bin/python" ]; then
    PYTHON_EXEC="$SCRIPT_DIR/venv/bin/python"
elif [ -f "$SCRIPT_DIR/venv/bin/python3" ]; then
    PYTHON_EXEC="$SCRIPT_DIR/venv/bin/python3"
fi

echo ""
echo "=== Avery Content Generation - 后端启动 ==="
echo ""
echo "📡 启动信息:"
echo "   虚拟环境: $SCRIPT_DIR/venv"
echo "   Python: $PYTHON_EXEC"
echo "   版本: $($PYTHON_EXEC --version 2>&1)"
echo "   工作目录: $SCRIPT_DIR"
echo "   日志级别: $LOG_LEVEL"
echo ""
echo "🌐 服务地址:"
echo "   API: http://localhost:8000"
echo "   文档: http://localhost:8000/docs"
echo "   调试: http://localhost:8000/debug"
echo ""
echo "✨ 新功能: 脚本退出时自动清理进程"
echo "   - 按 Ctrl+C 停止服务并自动清理"
echo "   - 关闭终端窗口也会自动清理"
echo ""
echo "================================"
echo ""

# 启动后端并跟踪PID
cd "$SCRIPT_DIR"
$PYTHON_EXEC -m uvicorn api.main:app \
    --reload \
    --host 0.0.0.0 \
    --port 8000 \
    --log-level info &

# 保存后端进程PID
BACKEND_PID=$!

echo "🚀 后端启动中... (PID: $BACKEND_PID)"
echo ""
echo "📊 进程信息:"
echo "   后端PID: $BACKEND_PID"
echo "   检查进程: ps -p $BACKEND_PID"
echo "   查看日志: tail -f logs/avery.log"
echo ""
echo "⏳ 等待服务启动..."
sleep 3

# 检查进程是否还在运行
if ps -p $BACKEND_PID > /dev/null 2>&1; then
    echo "✅ 后端启动成功！"
    echo ""
    echo "🌐 服务已就绪:"
    echo "   - API: http://localhost:8000"
    echo "   - 文档: http://localhost:8000/docs"
    echo ""
    echo "💡 提示:"
    echo "   - 按 Ctrl+C 停止服务并自动清理"
    echo "   - 或直接关闭窗口，也会自动清理"
    echo ""
else
    echo "❌ 后端启动失败，请检查日志"
    echo "   查看日志: tail -f logs/avery.log"
    exit 1
fi

# 保持脚本运行，等待用户按Ctrl+C
# 这样trap处理器可以在退出时自动清理
echo "⏸️  服务运行中... (按 Ctrl+C 停止)"
echo ""

# 等待后端进程
wait $BACKEND_PID
