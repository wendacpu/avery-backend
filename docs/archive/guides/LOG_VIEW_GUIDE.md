# 📡 实时日志查看指南 - 生图流程调试

## 🚀 推荐方法1: 使用专用监控脚本（最佳）

```bash
./monitor-logs.sh
```

**特点：**
- ✅ 专门为生图流程优化
- ✅ 自动高亮关键信息
- ✅ emoji标记便于快速识别
- ✅ 自动过滤无关日志

**显示示例：**
```
📡 调用 Gemini API: https://api.novita.ai/v1/images/generations
🎨 开始生成图片...
✅ Gemini 图片生成成功: https://...
🎨 保存图片URL到数据库
```

---

## 🔧 方法2: 使用view-logs.sh（已有脚本）

```bash
./view-logs.sh -f
```

**特点：**
- ✅ 支持follow模式（实时）
- ✅ 可以过滤错误信息: `./view-logs.sh -e`
- ✅ 可以搜索关键词: `./view-logs.sh -s "image"`

**示例命令：**
```bash
# 实时监控所有日志
./view-logs.sh -f

# 只看错误
./view-logs.sh -e -f

# 搜索图片相关
./view-logs.sh -s "image" -f
```

---

## 💻 方法3: 直接使用tail命令

```bash
# 实时查看完整日志
tail -f logs/avery.log

# 只看图片相关（高亮显示）
tail -f logs/avery.log | grep --line-buffered "image\|Image\|🎨\|novita"

# 只看错误
tail -f logs/avery.log | grep --line-buffered "ERROR\|WARNING\|❌"
```

---

## 🌐 方法4: 浏览器API方式

访问：http://localhost:8000/logs

**特点：**
- ✅ 可以在浏览器中查看
- ✅ 支持搜索和过滤
- ✅ 可以下载日志文件

---

## 🎯 调试生图流程的最佳实践

### 步骤1: 启动日志监控
```bash
# 在一个终端窗口中运行
./monitor-logs.sh
```

### 步骤2: 在前端触发生成
```
1. 打开 http://localhost:3000/generate
2. 填写表单
3. 点击"Start Generating"
```

### 步骤3: 观察日志输出
在monitor-logs.sh窗口中会看到：

```
📡 开始内容生成流程
📡 使用Deep Search V2定制查询
📡 Deep Search获得15个结果
🎨 开始生成infographic规格
🎨 开始调用图片生成API...
📡 调用 Gemini API: https://api.novita.ai/v1/images/generations
🎨 生成参数: model="gemini-2.0-flash-exp", prompt="..."
✅ Gemini 图片生成成功: https://novita-img...
🎨 保存图片URL到数据库
✅ 内容生成完成
```

### 步骤4: 识别错误
如果失败，会看到：

```
❌ Gemini API调用失败: 401 Unauthorized
   错误详情: Invalid API key
```

或

```
❌ 图片生成失败: timeout
   错误详情: Request timed out after 30s
```

---

## 📊 常见日志标记

| Emoji | 含义 | 示例 |
|-------|------|------|
| 🎨 | 图片生成相关 | "🎨 开始生成图片..." |
| 📡 | API调用 | "📡 调用 Gemini API" |
| ✅ | 成功 | "✅ 图片生成成功" |
| ❌ | 错误 | "❌ API调用失败" |
| 🔑 | API密钥 | "🔑 Novita API: 已配置" |
| 📊 | 数据处理 | "📊 处理infographic规格" |

---

## 🐛 快速诊断命令

### 检查最近的生图错误
```bash
grep -A 5 "❌\|ERROR" logs/avery.log | tail -50
```

### 查看所有图片生成记录
```bash
grep "🎨\|image\|Image" logs/avery.log | tail -20
```

### 查看最近的API调用
```bash
grep "📡\|novita\|Novita" logs/avery.log | tail -20
```

### 查看完整生成流程
```bash
grep "开始\|完成\|成功\|失败" logs/avery.log | tail -30
```

---

## 💡 实时调试技巧

### 1. 分屏查看
```bash
# 终端1: 监控日志
./monitor-logs.sh

# 终端2: 监控API请求
tail -f logs/avery.log | grep "POST\|GET\|200\|400\|500"

# 终端3: 监控错误
tail -f logs/avery.log | grep "ERROR\|❌"
```

### 2. 保存日志到文件
```bash
# 保存最近100行生图相关日志
grep "🎨\|image" logs/avery.log | tail -100 > image-debug.log
```

### 3. 实时搜索特定内容
```bash
# 搜索特定generation ID
tail -f logs/avery.log | grep "generation_id_12345"
```

---

## ⚠️ 常见问题诊断

### 问题1: "Generation failed. Please try again"

**查看日志：**
```bash
./monitor-logs.sh
```

**可能原因：**
1. API密钥无效 → `❌ Invalid API key`
2. 网络超时 → `❌ Request timeout`
3. 参数错误 → `❌ Invalid parameters`
4. 服务不可用 → `❌ Service unavailable`

### 问题2: 图片没有显示

**检查日志：**
```bash
grep "保存图片URL" logs/avery.log | tail -5
```

**验证URL：**
```bash
grep "https://novita-img" logs/avery.log | tail -1
```

### 问题3: Deep Search没有结果

**检查日志：**
```bash
grep "Deep Search\|Tavily" logs/avery.log | tail -10
```

---

## 📱 实时监控演示

### 完整的生成流程日志示例：

```
2026-03-15 11:30:00 | INFO | 📡 收到内容生成请求
2026-03-15 11:30:01 | INFO | 👤 用户职位: ceo_founder
2026-03-15 11:30:01 | INFO | 📊 使用V2定制查询进行Deep Search
2026-03-15 11:30:02 | INFO | 📡 调用Tavily API (5个查询)
2026-03-15 11:30:05 | INFO | ✅ Deep Search成功: 获得15个结果
2026-03-15 11:30:06 | INFO | 📊 开始研究综合 (V2 Executive级别)
2026-03-15 11:30:08 | INFO | ✅ 研究综合完成
2026-03-15 11:30:09 | INFO | 🎨 开始生成infographic规格
2026-03-15 11:30:10 | INFO | ✅ Infographic规格生成: 12个模块
2026-03-15 11:30:11 | INFO | 📡 开始内容生成 (V2)
2026-03-15 11:30:15 | INFO | ✅ 内容生成完成
2026-03-15 11:30:16 | INFO | 🎨 开始调用图片生成API
2026-03-15 11:30:16 | INFO | 📡 调用 Gemini API
2026-03-15 11:30:17 | INFO | 🎨 生成参数: model=gemini-2.0-flash-exp
2026-03-15 11:30:20 | INFO | ✅ Gemini 图片生成成功
2026-03-15 11:30:21 | INFO | 🎨 保存图片URL到数据库
2026-03-15 11:30:22 | INFO | ✅ 内容生成流程完成
```

---

## 🚀 立即开始

**最快的方式：**
```bash
# 1. 启动监控（新终端窗口）
./monitor-logs.sh

# 2. 触发生成（前端）
# 打开 http://localhost:3000/generate
# 点击"Start Generating"

# 3. 观察日志输出
# 在monitor-logs.sh窗口中实时查看
```

---

**准备好调试了吗？运行 `./monitor-logs.sh` 然后触发生成，就能看到完整的流程了！**
