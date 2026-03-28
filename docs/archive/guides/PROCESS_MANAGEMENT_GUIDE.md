# 🎛️ 后端进程管理 - 完整指南

## 🚀 新功能：自动进程清理

**问题解决**: 每次启动前都需要手动找PID并kill进程

**新功能**:
- ✅ 启动时自动清理占用端口的进程
- ✅ 脚本退出时自动清理启动的进程
- ✅ Ctrl+C时自动清理
- ✅ 关闭终端窗口时自动清理

---

## 📋 可用的启动脚本

### 1. `start.sh` - 前台运行（推荐用于开发）

**特点**:
- ✅ 自动清理端口占用
- ✅ 自动跟踪进程PID
- ✅ 退出时自动清理
- ✅ 实时显示日志输出
- ✅ Ctrl+C立即停止并清理

**使用方法**:
```bash
./start.sh
```

**退出方法**:
- 按 `Ctrl+C` - 自动停止并清理
- 或直接关闭终端窗口 - 自动清理

**适用场景**:
- 开发调试
- 查看实时日志
- 测试新功能

---

### 2. `start-background.sh` - 后台运行（推荐用于生产）

**特点**:
- ✅ 自动清理端口占用
- ✅ 后台运行，不占用终端
- ✅ 日志输出到文件
- ✅ 可以关闭终端窗口

**使用方法**:
```bash
./start-background.sh
```

**管理方法**:
- 查看日志: `tail -f logs/avery.log`
- 停止服务: `./stop.sh`

**适用场景**:
- 长时间运行
- 不需要实时查看日志
- 服务器环境

---

### 3. `stop.sh` - 手动停止服务

**功能**:
- ✅ 查找所有占用端口8000的进程
- ✅ 显示进程信息
- ✅ 停止所有相关进程
- ✅ 验证清理结果

**使用方法**:
```bash
./stop.sh
```

**适用场景**:
- 手动停止后台运行的服务
- 清理僵尸进程
- 强制释放端口

---

## 🎯 使用场景推荐

### 开发环境
```bash
# 前台运行，方便调试
./start.sh

# 查看实时日志
tail -f logs/avery.log

# 停止服务
# 按 Ctrl+C（自动清理）
```

### 生产环境
```bash
# 后台运行
./start-background.sh

# 验证运行
ps aux | grep uvicorn

# 查看日志
tail -f logs/avery.log

# 停止服务
./stop.sh
```

### 快速重启
```bash
# 一键重启
./stop.sh && ./start-background.sh

# 或开发环境重启
./stop.sh && ./start.sh
```

---

## 🔍 进程管理详解

### 自动清理机制

**1. 启动时清理**:
```bash
# 检查端口8000占用
if lsof -Pi :8000 -sTCP:LISTEN -t >/dev/null 2>&1; then
    # 自动kill旧进程
    lsof -ti :8000 | xargs kill -9
fi
```

**2. 退出时清理**:
```bash
# 设置trap捕获退出信号
trap cleanup EXIT INT TERM HUP

cleanup() {
    # 杀死跟踪的进程
    if [ -n "$BACKEND_PID" ]; then
        kill $BACKEND_PID
    fi

    # 清理端口残留
    lsof -ti :8000 | xargs kill -9
}
```

### 进程状态检查

**查看后端进程**:
```bash
# 方法1: 查看端口占用
lsof -i :8000

# 方法2: 查看uvicorn进程
ps aux | grep uvicorn

# 方法3: 查看特定PID
ps -p <PID>
```

**查看后端日志**:
```bash
# 实时跟踪
tail -f logs/avery.log

# 查看最近100行
tail -100 logs/avery.log

# 搜索错误
grep ERROR logs/avery.log
```

---

## ⚠️ 常见问题解决

### 问题1: 端口仍然被占用

**症状**:
```bash
./start.sh
⚠️  端口 8000 已被占用
```

**解决方案**:
```bash
# 方法1: 使用自动清理脚本
./stop.sh

# 方法2: 手动清理
lsof -ti :8000 | xargs kill -9

# 方法3: 查找并手动kill
lsof -i :8000
kill -9 <PID>
```

### 问题2: 进程成为僵尸进程

**症状**:
```bash
ps aux | grep uvicorn
# 显示 <defunct> 或僵尸进程
```

**解决方案**:
```bash
# 强制清理所有相关进程
./stop.sh

# 或更彻底的清理
pkill -9 -f uvicorn
pkill -9 -f api.main
```

### 问题3: 脚本退出但进程仍在运行

**症状**:
```bash
./start.sh
# 按Ctrl+C后，进程仍在运行
```

**解决方案**:
```bash
# 这可能是新脚本的bug，请确认:
# 1. 使用最新的start.sh
# 2. 检查trap是否正确设置
# 3. 手动清理: ./stop.sh
```

---

## 📊 脚本对比

| 特性 | start.sh | start-background.sh | stop.sh |
|------|----------|---------------------|---------|
| 自动清理端口 | ✅ | ✅ | ✅ |
| 自动跟踪PID | ✅ | ❌ | N/A |
| 退出时清理 | ✅ | ❌ | N/A |
| 实时日志 | ✅ | ❌ | ❌ |
| 后台运行 | ❌ | ✅ | N/A |
| 生产环境 | ⚠️ | ✅ | N/A |
| 开发调试 | ✅ | ⚠️ | N/A |

---

## 🎓 最佳实践

### 开发工作流
```bash
# 1. 修改代码
vim api/main.py

# 2. 重启服务（自动清理）
./start.sh

# 3. 测试功能
curl http://localhost:8000/docs

# 4. 查看日志
tail -f logs/avery.log

# 5. 停止服务（Ctrl+C，自动清理）
```

### 生产工作流
```bash
# 1. 启动服务
./start-background.sh

# 2. 验证运行
curl http://localhost:8000/health

# 3. 定期检查日志
tail -100 logs/avery.log

# 4. 需要时重启
./stop.sh && ./start-background.sh
```

### 调试工作流
```bash
# 终端1: 启动服务
./start.sh

# 终端2: 监控日志
./monitor-logs.sh

# 终端3: 测试API
curl http://localhost:8000/api/test

# 完成后在终端1按Ctrl+C（自动清理）
```

---

## 🔧 技术细节

### Trap机制
```bash
# 捕获多种信号
trap cleanup EXIT    # 脚本正常退出
trap cleanup INT     # Ctrl+C
trap cleanup TERM    # kill命令
trap cleanup HUP     # 终端关闭
```

### PID跟踪
```bash
# 启动进程并获取PID
command &
BACKEND_PID=$!

# 在cleanup中使用
cleanup() {
    kill $BACKEND_PID  # 只杀死跟踪的进程
}
```

### 端口清理
```bash
# 查找占用端口的PID
PIDS=$(lsof -ti :8000)

# 杀死所有相关进程
echo "$PIDS" | xargs kill -9
```

---

## ✅ 总结

**新的进程管理特性**:
- ✅ 完全自动化，无需手动查找PID
- ✅ 多种运行模式适应不同场景
- ✅ 智能清理机制防止端口占用
- ✅ 退出时自动清理保持环境整洁

**推荐使用**:
- 开发: `./start.sh`
- 生产: `./start-background.sh`
- 停止: `./stop.sh`

**再也不用手动找PID和kill进程了！**
