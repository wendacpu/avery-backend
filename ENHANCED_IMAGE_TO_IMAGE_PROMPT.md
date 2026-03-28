# 图生图提示词增强版本

**更新时间:** 2026-03-17
**问题:** 75%概率出现错字漏字，黄色背景仍然存在

---

## ✅ 修正后的图生图提示词

### 提示词1: 质量提升提示词 (enhancement_prompt)

**位置:** `infographic_service.py` 第310-350行
**使用场景:** 每次生成图片后，立即执行的质量提升

```python
enhancement_prompt = f"""Enhance this infographic to improve quality and fix text issues:

CRITICAL TEXT FIXES (MANDATORY):
1. FIX TYPOS AND MISSPELLINGS:
   - Check EVERY word carefully - correct any misspelled words
   - Fix missing letters (e.g., "te t" → "test", "infor ation" → "information")
   - Fix extra letters (e.g., "ggo" → "go", "testt" → "test")
   - Fix common OCR errors: "rn" → "m", "vv" → "w", "cl" → "d"

2. FIX CHARACTER DISTORTION:
   - Sharpen ALL text for perfect readability
   - Fix any stretched, compressed, or tilted characters
   - Ensure consistent font size and weight throughout
   - Make all letters crisp and well-formed

3. FIX CHART TEXT:
   - Pay EXTRA attention to chart labels and axis titles
   - Fix ANY garbled text in data labels
   - Ensure ALL chart text is perfectly clear and accurate
   - Verify numbers in charts are correct (no digit confusion)

4. BACKGROUND COLOR (CRITICAL):
   - Change ALL module backgrounds to PURE WHITE (#FFFFFF)
   - Remove any yellow, beige, or colored backgrounds
   - Ensure entire canvas background is pure white
   - NO yellow or colored backgrounds allowed

VISUAL QUALITY:
- Enhance overall image sharpness and clarity
- Improve color vibrancy while maintaining professional appearance
- Clean up any visual artifacts or noise
- Ensure clean edges and boundaries

LAYOUT INTEGRITY:
- Maintain exact same layout and structure
- Do NOT change content organization
- Only fix text and background color issues

MANDATORY FIXES:
- Correct ALL typos and spelling errors
- Fix ALL character distortions
- Change ALL backgrounds to pure white
- Verify every single word is perfect"""
```

---

### 提示词2: 序号修正提示词 (correction_prompt)

**位置:** `infographic_service.py` 第390-450行
**使用场景:** OCR验证失败后，针对性修正

```python
correction_prompt = f"""Fix all text issues in this infographic while preserving design and layout:

CRITICAL TEXT FIXES (MANDATORY):
1. FIX TYPOS AND MISSPELLINGS:
   - Check EVERY single word - correct ALL misspellings
   - Fix missing letters: "te t" → "test", "infor ation" → "information"
   - Fix extra letters: "ggo" → "go", "testt" → "test"
   - Fix common errors: "rn" → "m", "vv" → "w", "cl" → "d", "li" → "h"
   - Verify each word is a valid English word

2. FIX CHARACTER DISTORTION:
   - Sharpen ALL text for perfect clarity
   - Fix stretched, compressed, or tilted characters
   - Ensure consistent font size throughout (EXACTLY 14px body text)
   - Make every letter perfectly formed and readable

3. FIX CHART TEXT (CRITICAL):
   - Pay EXTREME attention to chart labels
   - Fix ANY garbled text in axis titles and data labels
   - Verify all numbers in charts are correct (no digit confusion)
   - Ensure chart text is perfectly clear

4. BACKGROUND COLOR (CRITICAL):
   - Change ALL backgrounds to PURE WHITE (#FFFFFF)
   - Remove ANY yellow, beige, or colored module backgrounds
   - Entire canvas must be pure white
   - NO colored backgrounds permitted

5. SEQUENCE NUMBERS:
   - Ensure each sequence number (1, 2, 3, ...) appears EXACTLY ONCE
   - Numbers must be clearly visible and correctly ordered
   - Fix any missing or duplicate sequence numbers

DO NOT CHANGE:
- Overall design layout
- Content organization and structure
- Visual elements position (except backgrounds)
- Any non-text, non-color design aspects

FIX ONLY:
- ALL typos and spelling errors
- ALL character distortions
- ALL colored backgrounds (change to white)
- Sequence number errors
- Chart text accuracy"""
```

---

## 🎯 关键改进点

### 1. **错字漏字修正** - 具体化

**修改前:**
```
- Check EVERY English word - fix typos, missing letters, distorted text
```

**修改后:**
```
1. FIX TYPOS AND MISSPELLINGS:
   - Check EVERY word carefully - correct any misspelled words
   - Fix missing letters (e.g., "te t" → "test", "infor ation" → "information")
   - Fix extra letters (e.g., "ggo" → "go", "testt" → "test")
   - Fix common OCR errors: "rn" → "m", "vv" → "w", "cl" → "d"
```

**改进:** 提供具体示例，明确常见错误类型

---

### 2. **纯白背景强制要求** - 新增

**修改前:** 没有提到背景颜色

**修改后:**
```
4. BACKGROUND COLOR (CRITICAL):
   - Change ALL module backgrounds to PURE WHITE (#FFFFFF)
   - Remove any yellow, beige, or colored backgrounds
   - Ensure entire canvas background is pure white
   - NO yellow or colored backgrounds allowed
```

**改进:** 明确要求纯白背景，禁止黄色/彩色背景

---

### 3. **图表文字特别关注** - 强化

**修改前:**
```
- Pay special attention to chart labels, axis titles, and data labels
```

**修改后:**
```
3. FIX CHART TEXT (CRITICAL):
   - Pay EXTRA attention to chart labels
   - Fix ANY garbled text in data labels
   - Ensure ALL chart text is perfectly clear and accurate
   - Verify numbers in charts are correct (no digit confusion)
```

**改进:** 使用更强的词汇（"EXTRA", "ANY", "ALL"），强调重要性

---

### 4. **指令级别提升**

| 修改项 | 修改前 | 修改后 |
|--------|--------|--------|
| 错字检查 | "Check EVERY English word" | "Check EVERY single word - correct ALL misspellings" |
| 字符扭曲 | "Fix any minor character distortions" | "Sharpen ALL text for perfect readability" |
| 背景颜色 | 未提及 | "CRITICAL" + "MANDATORY FIXES" |
| 优先级 | "QUALITY IMPROVEMENTS" | "CRITICAL TEXT FIXES (MANDATORY)" |

---

## 📊 预期效果

### 修改前:
- ❌ 75%概率出现错字漏字
- ❌ 黄色背景仍然常见
- ❌ 图表文字经常扭曲

### 修改后:
- ✅ 明确错字类型和示例
- ✅ 强制纯白背景
- ✅ 特别关注图表文字
- ✅ 使用CRITICAL和MANDATORY提升指令优先级

---

## 🔍 常见错字类型映射

提示词中包含的具体错误类型：

| 错误类型 | 示例 | 修正 |
|---------|------|------|
| **缺少字母** | "te t" | "test" |
| **多余字母** | "ggo" | "go" |
| **OCR混淆** | "rn" → "m" | "m" |
| **OCR混淆** | "vv" → "w" | "w" |
| **OCR混淆** | "cl" → "d" | "d" |
| **OCR混淆** | "li" → "h" | "h" |
| **拼写错误** | "infor ation" | "information" |

---

## 🔄 使用流程

```
图片生成
  ↓
[强制执行] 图生图质量提升 (flux-pro)
  使用 enhancement_prompt
  ↓
OCR验证
  ↓
如果失败 → 继续图生图修正 (flux-pro)
  使用 correction_prompt
  ↓
验证通过 → 输出最终图片
```

**关键点:**
1. 每次生成都执行图生图优化（不只是失败时）
2. 使用flux-pro独立模型（不是gemini-2.5-flash）
3. 提示词明确要求纯白背景
4. 提示词详细列出错字类型和修正方法

---

**文件位置:** `/backend/api/services/infographic_service.py`
**方法:** `generate_from_text()` - Step 6 (第310-450行)
