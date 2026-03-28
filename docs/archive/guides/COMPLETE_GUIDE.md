# 🎉 系统管理完整指南

## ✅ 已完成的工作

### 1. **端口管理** ✅
- 关闭了占用8000端口的旧进程
- 创建了自动端口检查的启动脚本

### 2. **日志系统** ✅
- 配置了完整的日志系统
- 创建了日志查看脚本
- 支持日志轮转（10MB自动备份，保留5个）

### 3. **API端点** ✅
- `/` - 根路径，显示系统信息
- `/health` - 健康检查
- `/logs` - 通过API查看日志

---

## 🚀 快速启动

### 启动后端

```bash
cd /Users/wanting/program/CC/Avery/backend
./start.sh
```

**你会看到：**
```
✓ 已激活虚拟环境

=== Avery Content Generation - 后端启动 ===

📡 启动信息:
   虚拟环境: /Users/wanting/program/CC/Avery/backend/venv
   Python: .../venv/bin/python
   版本: Python 3.12.2
   工作目录: /Users/wanting/program/CC/Avery/backend
   日志级别: INFO

🌐 服务地址:
   API: http://localhost:8000
   文档: http://localhost:8000/docs
   调试: http://localhost:8000/debug

按 Ctrl+C 停止服务
```

---

## 📋 日志查看（三种方法）

### 方法1：使用查看脚本（最推荐）⭐

```bash
# 查看最近100行
./view-logs.sh

# 实时跟踪（像 tail -f）
./view-logs.sh -f

# 只显示错误
./view-logs.sh -e

# 搜索关键词
./view-logs.sh -s "图片生成"

# 显示最近50行
./view-logs.sh -n 50
```

**脚本选项：**
- `-f, --follow` - 实时跟踪日志
- `-n, --lines N` - 显示最后N行（默认100）
- `-e, --errors` - 只显示错误
- `-s, --search TEXT` - 搜索关键词
- `-h, --help` - 显示帮助

### 方法2：直接查看文件

```bash
# 查看最近100行
tail -n 100 logs/avery.log

# 实时跟踪
tail -f logs/avery.log

# 搜索错误
grep ERROR logs/avery.log

# 查看文件大小
ls -lh logs/avery.log
```

### 方法3：通过浏览器/API

```bash
# 浏览器访问
http://localhost:8000/logs?lines=100

# 或使用 curl
curl http://localhost:8000/logs?lines=50
```

---

## 📊 日志位置和格式

### 日志文件位置

```
/Users/wanting/program/CC/Avery/backend/logs/
├── avery.log       # 当前日志
├── avery.log.1     # 备份1
├── avery.log.2     # 备份2
└── ...
```

### 日志格式

```
时间戳 | 级别 | 模块:行号 | 消息
```

**示例：**
```
2026-03-15 10:39:14 | INFO | api.main:41 | 🚀 Avery Content Generation API 启动
2026-03-15 10:39:14 | INFO | api.main:44 | 🔑 Novita API: 已配置
2026-03-15 10:39:14 | INFO | api.main:50 | ✅ 数据库表初始化成功
```

### 日志级别

| 级别 | 颜色 | 说明 |
|------|------|------|
| **DEBUG** | 青色 | 调试信息 |
| **INFO** | 绿色 | 一般信息 |
| **WARNING** | 黄色 | 警告信息 |
| **ERROR** | 红色 | 错误信息 |

---

## 🔍 实用场景

### 场景1：生图失败，查看详细错误

```bash
# 终端1：启动服务并实时跟踪日志
./start.sh

# 终端2：实时跟踪日志（过滤图片生成相关）
./view-logs.sh -f | grep "图片"

# 或在终端2实时跟踪所有日志
./view-logs.sh -f
```

### 场景2：检查系统健康状态

```bash
# 检查服务是否运行
curl http://localhost:8000/health

# 查看最近的错误
./view-logs.sh -e

# 查看启动信息
./view-logs.sh -s "启动"
```

### 场景3：统计错误数量

```bash
# 统计今天的错误数量
grep "$(date +%Y-%m-%d)" logs/avery.log | grep ERROR | wc -l

# 查看最近1小时的日志
find logs/ -name "*.log" -mmin -60 -exec cat {} \;
```

---

## 🛠️ 系统管理命令

### 端口管理

```bash
# 查看占用8000端口的进程
lsof -i :8000

# 杀死占用端口的进程
kill -9 <PID>

# 或使用诊断脚本
./diagnose.sh
```

### 进程管理

```bash
# 查看Python进程
ps aux | grep python

# 杀死后端进程
pkill -f "uvicorn api.main:app"

# 或使用
kill -9 $(lsof -t -i:8000)
```

### 日志管理

```bash
# 查看日志文件大小
du -sh logs/

# 清空当前日志
> logs/avery.log

# 删除旧日志备份
rm logs/avery.log.*

# 压缩日志
gzip logs/avery.log.*
```

---

## 📁 相关文件

| 文件 | 用途 |
|------|------|
| `start.sh` | 启动后端服务 |
| `view-logs.sh` | 查看日志 |
| `diagnose.sh` | 系统诊断 |
| `logs/avery.log` | 主日志文件 |
| `LOGS_GUIDE.md` | 详细日志指南 |
| `DEBUG_GUIDE.md` | 调试指南 |
| `README_DEV.md` | 开发者指南 |
| `QUICKSTART.md` | 快速开始 |

---

## 🎯 日常使用流程

### 典型的工作流程

1. **启动服务**
   ```bash
   ./start.sh
   ```

2. **在另一个终端跟踪日志**
   ```bash
   ./view-logs.sh -f
   ```

3. **在前端生成内容**

4. **观察日志输出**
   - 查看每个步骤的进度
   - 检查是否有错误
   - 验证图片生成成功

5. **停止服务**
   - 在启动终端按 `Ctrl+C`

---

## 💡 提示和技巧

### 1. 快速检查系统状态

```bash
# 一键诊断
./diagnose.sh
```

### 2. 查找特定功能的日志

```bash
# 图片生成
./view-logs.sh -s "🎨"

# Deep Search
./view-logs.sh -s "Deep"

# API调用
./view-logs.sh -s "📡"
```

### 3. 监控错误

```bash
# 实时监控错误
./view-logs.sh -f -e

# 统计错误类型
grep ERROR logs/avery.log | awk '{print $NF}' | sort | uniq -c
```

### 4. 清理系统

```bash
# 删除失败的数据库记录
psql -U avery -d avery -c "DELETE FROM content_generations WHERE status = 'failed';"

# 清理旧日志（保留最近7天）
find logs/ -name "*.log.*" -mtime +7 -delete
```

---

## 🆘 常见问题

### Q1: 端口8000被占用怎么办？

```bash
# 方案1：使用诊断脚本
./diagnose.sh

# 方案2：手动查找并关闭
lsof -i :8000
kill -9 <PID>

# 方案3：使用启动脚本（会自动检查）
./start.sh
```

### Q2: 日志文件太大怎么办？

```bash
# 查看日志大小
ls -lh logs/

# 清空当前日志
> logs/avery.log

# 删除备份
rm logs/avery.log.*

# 压缩备份
gzip logs/avery.log.*
```

### Q3: 如何实时查看生图过程？

```bash
# 终端1：启动服务
./start.sh

# 终端2：实时跟踪日志
./view-logs.sh -f

# 终端3：只看图片生成相关
./view-logs.sh -f | grep "图片"
```

### Q4: 日志在哪里？

**主日志文件：** `logs/avery.log`

**完整路径：** `/Users/wanting/program/CC/Avery/backend/logs/avery.log`

---

## 🎊 总结

现在你有了一个完整的系统：

✅ **自动启动脚本** - `./start.sh`
✅ **日志查看工具** - `./view-logs.sh`
✅ **系统诊断工具** - `./diagnose.sh`
✅ **详细的日志记录** - 所有操作都有日志
✅ **多种查看方式** - 脚本、文件、API
✅ **自动日志轮转** - 防止文件过大

---

**开始使用吧！** 🚀

```bash
cd /Users/wanting/program/CC/Avery/backend
./start.sh
```

然后在另一个终端：

```bash
./view-logs.sh -f
```

有问题随时问我，tiffany！🎉
