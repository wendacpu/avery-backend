# 🎯 快速查看生图过程 - 参考卡片

## 🚀 立即开始（3种方法）

### 方法1: 前端界面（最简单）
```
1. 打开 http://localhost:3000/generate
2. 填写表单，点击"Start Generating"
3. 观察进度界面 → 自动显示步骤和进度
```

### 方法2: 实时监控（推荐）
```bash
./monitor-logs.sh
```
✅ 实时显示关键步骤
✅ emoji标记便于识别
✅ 自动过滤无关信息

### 方法3: 详细日志
```bash
tail -f logs/avery.log
```
✅ 最详细
✅ 完整信息
✅ 支持搜索过滤

---

## 📊 生成步骤对照表

| 前端显示 | 后端日志 | 对应文件 |
|---------|---------|----------|
| Validate Input | 开始内容生成流程 | `content.py:114` |
| Extract Data | 提取数据和推荐主题 | `content.py:70` |
| Recommend Topics | 生成主题推荐 | `topic_recommender.py:95` |
| Analyze Structure | 分析内容结构 | `advanced_content_generator.py` |
| Deep Search | 使用5个专业深度查询 | `deep_search.py:85` |
| Synthesize Research | 使用V2 Executive级别综合 | `advanced_content_generator.py:856` |
| Infographic Spec | 生成12个模块规格 | `advanced_content_generator.py:937` |
| Generate Content | 生成5-7个战略支柱 | `advanced_content_generator.py:81` |
| Visual Design | 视觉设计规划 | `image_generator.py:28` |
| Generate Image | 调用Gemini API | `image_generator.py:28` |
| Complete | 内容生成流程完成 | `content.py:319` |

---

## 🔍 快速诊断命令

### 查看特定步骤：
```bash
# Deep Search
grep "Deep Search\|获得.*结果" logs/avery.log

# 内容生成
grep "内容生成完成\|Executive级别" logs/avery.log

# 图片生成
grep "图片生成成功\|Novita\|Gemini" logs/avery.log

# 错误信息
grep "ERROR\|❌\|失败" logs/avery.log
```

### 查看最近生成：
```bash
# 最近20行
tail -20 logs/avery.log

# 搜索特定关键词
grep "AI tools" logs/avery.log | tail -10

# 查看完整生成流程
grep -E "开始|完成|成功|失败" logs/avery.log | tail -15
```

---

## 📱 前端进度界面说明

### 进度条：
```
[████████████░░░░░░░░] 60%
```
- 显示总体完成百分比
- 每2秒更新一次

### 当前步骤：
```
Current step: Deep Search
```
- 显示正在执行的具体步骤
- 实时更新

### 步骤列表：
```
✓ Validate Input      ← 已完成（绿色）
✓ Extract Data        ← 已完成（绿色）
⟳ Deep Search         ← 进行中（旋转图标）
  Synthesize Research ← 待执行（灰色）
```

---

## 💻 后端日志标记

### Emoji标记：
- 🎨 图片生成相关
- 📡 API调用
- 📊 数据处理
- ✅ 成功完成
- ❌ 错误失败

### 日志级别：
- `INFO` - 正常流程
- `WARNING` - 警告信息
- `ERROR` - 错误信息

---

## 🚨 常见问题快速定位

### 问题：生成卡在某一步

**查看：**
```bash
# 查看当前步骤
tail -5 logs/avery.log

# 查看是否有错误
grep ERROR logs/avery.log | tail -5
```

### 问题：Deep Search没有结果

**查看：**
```bash
grep "Deep Search\|Tavily" logs/avery.log | tail -10
```

### 问题：内容质量不好

**查看：**
```bash
grep "内容生成完成\|bullet\|要点" logs/avery.log | tail -10
```

### 问题：图片生成失败

**查看：**
```bash
grep "图片生成\|Novita\|Gemini\|ERROR" logs/avery.log | tail -10
```

---

## 🎁 一键查看脚本

### 创建快速查看命令：

```bash
# 添加到 ~/.bashrc 或 ~/.zshrc
alias avery-logs='cd /Users/wanting/program/CC/Avery/backend && ./monitor-logs.sh'
alias avery-status='cd /Users/wanting/program/CC/Avery/backend && tail -20 logs/avery.log'
alias avery-errors='cd /Users/wanting/program/CC/Avery/backend && grep ERROR logs/avery.log | tail -10'
alias avery-image='cd /Users/wanting/program/CC/Avery/backend && grep "图片生成\|Novita" logs/avery.log | tail -10'
```

**使用：**
```bash
avery-logs      # 实时监控
avery-status    # 查看状态
avery-errors    # 查看错误
avery-image     # 查看图片生成
```

---

## 📊 生成时间参考

### 正常生成时间：
- Deep Search: 5-10秒
- Research Synthesis: 3-5秒
- Content Generation: 5-10秒
- Image Generation: 5-15秒
- **总计**: 约30-60秒

### 如果超过2分钟：
```bash
# 检查是否卡住
tail -10 logs/avery.log

# 查看进程状态
ps aux | grep uvicorn

# 必要时重启
./stop.sh && ./start.sh
```

---

## ✅ 推荐工作流程

### 开发调试：
```bash
# 终端1：启动后端
./start.sh

# 终端2：监控日志
./monitor-logs.sh

# 浏览器：前端操作
# 打开 http://localhost:3000/generate
# 点击"Start Generating"
# 观察两个界面的进度
```

### 快速检查：
```bash
# 一条命令查看最新状态
tail -20 logs/avery.log | grep -E "✅|❌|📊|🎨"
```

---

## 🎯 你应该看到什么

### 成功生成的完整日志：
```
📡 开始内容生成流程
📊 使用V2定制查询进行Deep Search
✅ Deep Search获得15个结果
📊 使用V2升级版Research Synthesis
✅ Research Synthesis完成
🎨 生成infographic规格: 12个模块
📡 使用V2升级版生成文字内容
✅ 内容生成完成
🎨 开始调用图片生成API
✅ Gemini 图片生成成功
✅ 内容生成流程完成
```

**如果看到这些，说明一切正常！**

---

**快速参考完成！选择最适合你的方式查看生成过程。**
