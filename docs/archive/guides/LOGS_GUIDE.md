# 📋 Avery 日志查看指南

## 🚀 快速开始

### 方法1：使用日志查看脚本（推荐）

```bash
cd /Users/wanting/program/CC/Avery/backend

# 查看最近100行日志
./view-logs.sh

# 实时跟踪日志
./view-logs.sh -f

# 只显示错误
./view-logs.sh -e

# 搜索关键词
./view-logs.sh -s "图片生成"

# 显示最近50行
./view-logs.sh -n 50
```

### 方法2：直接查看日志文件

```bash
# 查看最近100行
tail -n 100 logs/avery.log

# 实时跟踪
tail -f logs/avery.log

# 搜索关键词
grep "图片生成" logs/avery.log

# 只显示错误
grep ERROR logs/avery.log

# 查看最近50行错误
grep ERROR logs/avery.log | tail -50
```

### 方法3：通过 API 查看

```bash
# 浏览器访问
http://localhost:8000/logs?lines=100

# 或使用 curl
curl http://localhost:8000/logs?lines=50
```

---

## 📊 日志位置

**主日志文件：** `logs/avery.log`

**日志目录：** `logs/`

```
backend/
├── logs/
│   ├── avery.log           # 当前日志
│   ├── avery.log.1         # 轮转备份1
│   ├── avery.log.2         # 轮转备份2
│   └── ...
├── start.sh                # 启动脚本
└── view-logs.sh            # 日志查看脚本
```

---

## 🎯 日志查看场景

### 场景1：生图失败，想看详细错误

```bash
# 实时跟踪日志
./view-logs.sh -f

# 在另一个终端重新生成内容
# 观察日志输出
```

**你会看到：**
```
2026-03-15 10:30:15 | INFO     | api.services.image_generator:280 | 🎨 开始生成图片...
2026-03-15 10:30:15 | INFO     | api.services.image_generator:285 |    主题: How to Use AI Tools...
2026-03-15 10:30:15 | INFO     | api.services.image_generator:287 |    Prompt 长度: 1234 字符
2026-03-15 10:30:16 | INFO     | api.services.image_generator:345 | 📡 调用 Gemini API
2026-03-15 10:30:17 | ERROR    | api.services.image_generator:370 | ❌ HTTP 错误 401
2026-03-15 10:30:17 | ERROR    | api.services.image_generator:371 | ❌ 响应内容: {"error": "Invalid API key"}
2026-03-15 10:30:17 | WARNING  | api.services.image_generator:290 | 🔄 回退到模拟图片
```

### 场景2：Deep Search 失败

```bash
# 搜索 Deep Search 相关日志
./view-logs.sh -s "Deep Search"
```

### 场景3：只看错误和警告

```bash
# 过滤错误和警告
./view-logs.sh -e

# 或使用 grep
grep -E "ERROR|WARNING" logs/avery.log | tail -50
```

### 场景4：查看启动信息

```bash
# 查看应用启动日志
./view-logs.sh -s "启动"

# 或查看文件头部
head -50 logs/avery.log
```

---

## 🔍 日志格式

每条日志包含以下信息：

```
时间戳 | 日志级别 | 模块:行号 | 消息
```

**示例：**
```
2026-03-15 10:30:15 | INFO     | api.services.image_generator:280 | 🎨 开始生成图片...
```

**字段说明：**
- **时间戳**：`2026-03-15 10:30:15`
- **日志级别**：`INFO`, `WARNING`, `ERROR`, `DEBUG`
- **模块位置**：`api.services.image_generator:280`
- **消息**：实际的日志内容

---

## 🎨 日志级别

| 级别 | 颜色 | 说明 | 示例 |
|------|------|------|------|
| **DEBUG** | 青色 | 调试信息 | 请求参数、响应数据 |
| **INFO** | 绿色 | 一般信息 | 流程进度、成功消息 |
| **WARNING** | 黄色 | 警告信息 | API 未配置、回退方案 |
| **ERROR** | 红色 | 错误信息 | API 调用失败、异常 |
| **CRITICAL** | 紫色 | 严重错误 | 系统崩溃、数据丢失 |

---

## 📱 通过 API 查看日志

### 访问日志端点

```bash
# 浏览器访问
http://localhost:8000/logs?lines=100

# 指定行数
http://localhost:8000/logs?lines=50

# 使用 curl
curl http://localhost:8000/logs?lines=20

# 美化输出
curl http://localhost:8000/logs?lines=20 | jq
```

**响应格式：**
```json
{
  "log_file": "logs/avery.log",
  "total_lines": 1234,
  "returned_lines": 20,
  "logs": "2026-03-15 10:30:15 | INFO | ...\n2026-03-15 10:30:16 | INFO | ..."
}
```

---

## 🔧 日志轮转

日志文件会自动轮转，防止文件过大：

- **最大文件大小**：10MB
- **保留备份数**：5个

**轮转文件：**
```
logs/
├── avery.log       # 当前日志
├── avery.log.1     # 最新备份
├── avery.log.2     # 第2个备份
├── avery.log.3     # 第3个备份
├── avery.log.4     # 第4个备份
└── avery.log.5     # 最旧备份
```

---

## 🎯 常用命令速查

| 操作 | 命令 |
|------|------|
| 查看最近100行 | `./view-logs.sh` |
| 实时跟踪 | `./view-logs.sh -f` |
| 只显示错误 | `./view-logs.sh -e` |
| 搜索关键词 | `./view-logs.sh -s "关键词"` |
| 显示最近50行 | `./view-logs.sh -n 50` |
| 查看文件大小 | `ls -lh logs/avery.log` |
| 统计错误数量 | `grep ERROR logs/avery.log \| wc -l` |
| 查看最近1小时日志 | `find logs/ -name "*.log" -mmin -60 -exec cat {} \;` |

---

## 💡 提示

1. **实时调试时**：使用 `./view-logs.sh -f` 实时跟踪
2. **查找错误时**：使用 `./view-logs.sh -e` 只看错误
3. **搜索特定功能**：使用 `./view-logs.sh -s "关键词"`
4. **查看API调用**：搜索 `📡` 或 `API`
5. **查看图片生成**：搜索 `🎨` 或 `图片`
6. **查看Deep Search**：搜索 `Deep` 或 `Tavily`

---

## 🆘 日志文件过大怎么办？

### 方法1：清理旧日志

```bash
# 删除所有日志备份
rm logs/avery.log.*

# 清空当前日志
> logs/avery.log
```

### 方法2：压缩旧日志

```bash
# 压缩日志备份
gzip logs/avery.log.*

# 解压查看
gunzip -c logs/avery.log.1.gz
```

### 方法3：自动清理（推荐）

在 `start.sh` 中添加自动清理：

```bash
# 删除30天前的日志备份
find logs/ -name "*.log.*" -mtime +30 -delete
```

---

**最后更新**：2026-03-15
**维护者**：送送 🤖
