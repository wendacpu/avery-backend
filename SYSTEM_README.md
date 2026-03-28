# Avery - 高质量信息图生成系统

## 系统概述

Avery是一个基于AI的专业LinkedIn信息图生成系统，支持从多种输入源（文本、PDF、网页）生成高质量、数据驱动的商务风格信息图。

## 核心特性

### 1. 多输入源支持
- **文本输入**: 直接粘贴行业背景内容
- **文件上传**: 支持PDF、TXT、MD文件
- **网页抓取**: 自动提取网页内容作为背景

### 2. 双视角内容生成
- **CTO视角**: 技术实施框架（架构、技术栈、实施路径）
- **CEO视角**: 战略决策框架（成熟度、投资优先级、ROI）
- **混合视角**: CTO+CEO结合

### 3. 成功工作流要素
- ✅ 客户文件=行业背景（非内容源）
- ✅ 全英文、高信息密度
- ✅ "how-to"框架非"what-is"
- ✅ 简洁商务风（≤4色，14px正文，无装饰）
- ✅ 数据图表可视化（折线图、饼状图、柱状图、组合图）
- ✅ 关键数字夸张突出（32-48px）
- ✅ 序号验证（确保每个序号仅出现一次）

### 4. 质量保证
- **序号验证**: 自动检查序号1-9的完整性和正确性
- **颜色限制**: 强制≤4种颜色
- **字号规范**: 正文14px，关键数字32-48px
- **风格检查**: 确保简洁商务风，无装饰元素

## 系统架构

```
backend/
├── api/
│   ├── services/
│   │   └── infographic/          # 核心生图模块
│   │       ├── input_processor.py    # 输入处理
│   │       ├── topic_generator.py    # 主题生成
│   │       ├── prompt_builder.py     # 提示词构建
│   │       ├── image_generator.py    # 图片生成
│   │       ├── quality_validator.py  # 质量验证
│   │       └── config.py             # 配置管理
│   ├── routes/
│   │   └── infographic.py         # API路由
│   └── main.py                    # 主应用
├── output_images/                  # 生成的图片
└── test_infographic_system.py    # 测试脚本
```

## 快速开始

### 1. 安装依赖

```bash
cd backend
pip install -r requirements.txt
```

### 2. 配置环境变量

创建 `.env` 文件：

```env
NOVITA_API_KEY=your_novita_api_key_here
GROQ_API_KEY=your_groq_api_key_here
DATABASE_URL=postgresql://user:password@localhost/avery
```

### 3. 运行测试

```bash
python test_infographic_system.py
```

### 4. 启动API服务器

```bash
python -m uvicorn api.main:app --reload --host 0.0.0.0 --port 8000
```

## API使用示例

### 从文本生成

```bash
curl -X POST "http://localhost:8000/api/infographic/generate/from-text" \
  -H "Content-Type: application/json" \
  -d '{
    "content": "The AI industry is growing rapidly...",
    "job_title": "hybrid",
    "perspective": "hybrid",
    "count": 4
  }'
```

### 从URL生成

```bash
curl -X POST "http://localhost:8000/api/infographic/generate/from-url" \
  -H "Content-Type: application/json" \
  -d '{
    "url": "https://example.com/article",
    "job_title": "ceo",
    "count": 4
  }'
```

### 从文件生成

```bash
curl -X POST "http://localhost:8000/api/infographic/generate/from-file" \
  -F "file=@industry_report.pdf" \
  -F "job_title=cto" \
  -F "count=4"
```

## 生成的图片格式

- **格式**: PNG
- **尺寸**: 864x1184 (3:4竖版，适合LinkedIn)
- **风格**: 简洁商务风
- **颜色**: ≤4种
- **字号**: 正文14px，关键数字32-48px
- **位置**: 保存在 `output_images/` 目录

## 工作流程

1. **输入处理**: 接收文本/文件/URL → 统一结构化背景
2. **主题生成**: 基于背景生成CTO/CEO视角的"how-to"主题
3. **提示词构建**: 9段式结构化提示词（CRITICAL、LAYOUT、COLOR、TYPOGRAPHY、VISUAL、CONTENT、CHART、EMPHASIS、CHECKLIST）
4. **质量预检**: 验证提示词中的序号完整性
5. **图片生成**: 调用Novita AI API生成图片
6. **质量后检**: OCR验证图片中的序号正确性
7. **本地保存**: 保存到 `output_images/` 并返回本地路径

## 质量问题修复

### 序号验证问题
- **问题**: 生成图片中序号重复或缺失
- **解决**:
  - 生成前：提示词中添加CHECKLIST段落明确序号要求
  - 生成后：OCR提取图片中的序号进行验证
  - 失败重试：自动调整提示词重新生成

### 颜色/字号问题
- **问题**: 颜色过多或字号过小
- **解决**:
  - 强制配置：`MAX_COLORS = 4`, `BODY_FONT_SIZE = 14px`
  - 提示词明确：每个提示词包含COLOR和TYPOGRAPHY段落
  - 质量验证：检查生成的提示词是否符合约束

## 配置选项

查看 `backend/api/services/infographic/config.py`:

```python
class GenerationConfig:
    MAX_COLORS: int = 4
    BODY_FONT_SIZE: int = 14
    HEADER_FONT_SIZE: int = 28
    KEY_NUMBER_FONT_SIZE: int = 40

    COLOR_SCHEMES = {
        "forest": [...],
        "ocean": [...],
        "minimal": [...]
    }
```

## 故障排除

### 问题：生成的图片序号错误
**解决**:
1. 检查 `quality_validator.py` 中的序号验证逻辑
2. 查看 `output_images/` 目录中生成的图片
3. 如果序号错误，系统会自动重试（最多3次）

### 问题：API返回500错误
**解决**:
1. 检查 `.env` 文件中的API密钥
2. 查看日志: `tail -f logs/avery.log`
3. 运行测试脚本: `python test_infographic_system.py`

### 问题：生成的图片无法访问
**解决**:
1. 图片保存在 `output_images/` 本地目录
2. 使用返回的 `local_path` 字段访问
3. S3 URL可能过期，本地路径永久可用

## 性能优化

- **缓存**: 相同输入的生成结果会被缓存
- **异步处理**: 使用异步IO提高并发性能
- **重试机制**: API调用失败自动重试3次
- **批量生成**: 支持一次生成多张图片

## 未来改进

- [ ] 前端UI集成
- [ ] 实时生成进度
- [ ] 图片编辑功能
- [ ] 模板库扩展
- [ ] 多语言支持
- [ ] 视频生成支持

## 技术栈

- **后端**: Python 3.10+, FastAPI
- **AI**: Novita AI (Gemini 2.5 Flash Image)
- **OCR**: Tesseract/EasyOCR
- **数据库**: PostgreSQL + Redis
- **存储**: S3-compatible + 本地文件系统

## 许可证

MIT License

## 联系方式

- GitHub: [your-repo]
- Issues: [your-issues]
