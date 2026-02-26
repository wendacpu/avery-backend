#!/bin/bash

# Groq API 配置脚本
# 使用方法：bash configure_groq.sh YOUR_GROQ_API_KEY

if [ -z "$1" ]; then
    echo "❌ 错误：请提供你的 Groq API Key"
    echo ""
    echo "使用方法："
    echo "  bash configure_groq.sh gsk_your-actual-api-key-here"
    echo ""
    echo "获取 API Key："
    echo "  1. 访问 https://console.groq.com/keys"
    echo "  2. 点击 'Create Key'"
    echo "  3. 复制 API Key（格式：gsk_...）"
    echo ""
    exit 1
fi

GROQ_KEY="$1"
ENV_FILE="/Users/wanting/program/CC/Avery/backend/.env"

# 验证 API Key 格式
if [[ ! $GROQ_KEY =~ ^gsk_ ]]; then
    echo "❌ 错误：Groq API Key 应该以 'gsk_' 开头"
    echo "你提供的是：$GROQ_KEY"
    exit 1
fi

echo "🔧 正在配置 Groq API..."

# 备份原 .env 文件
if [ -f "$ENV_FILE" ]; then
    cp "$ENV_FILE" "${ENV_FILE}.backup.$(date +%Y%m%d_%H%M%S)"
    echo "✅ 已备份原 .env 文件"
fi

# 检查是否已存在 GROQ_API_KEY
if grep -q "^GROQ_API_KEY=" "$ENV_FILE" 2>/dev/null; then
    # 替换现有的 API Key
    sed -i '' "s/^GROQ_API_KEY=.*/GROQ_API_KEY=$GROQ_KEY/" "$ENV_FILE"
    echo "✅ 已更新现有的 GROQ_API_KEY"
else
    # 添加新的 API Key
    echo "" >> "$ENV_FILE"
    echo "# Groq API (文本生成 - 免费)" >> "$ENV_FILE"
    echo "GROQ_API_KEY=$GROQ_KEY" >> "$ENV_FILE"
    echo "✅ 已添加新的 GROQ_API_KEY"
fi

echo ""
echo "✅ 配置完成！"
echo ""
echo "下一步："
echo "  1. 重启后端服务："
echo "     cd /Users/wanting/program/CC/Avery/backend"
echo "     source venv/bin/activate"
echo "     nohup uvicorn api.main:app --host 0.0.0.0 --port 8000 --reload > /tmp/avery-backend.log 2>&1 &"
echo ""
echo "  2. 查看日志验证："
echo "     tail -20 /tmp/avery-backend.log"
echo ""
echo "  3. 应该看到："
echo "     'Groq client initialized for content generation (free)'"
echo ""
