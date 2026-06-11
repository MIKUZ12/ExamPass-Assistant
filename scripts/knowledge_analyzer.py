"""Prepare prompts and assemble markdown for knowledge list generation."""


def build_knowledge_prompt(text_summary: str, images: list = None) -> str:
    """
    Build the analysis prompt for Claude to generate a knowledge list.
    The caller (skill) sends this prompt to Claude and receives markdown.
    """
    prompt = """你是一位资深的大学课程辅导专家。请根据以下课程资料，生成一份**期末考试复习知识清单**。

## 输出要求

### 1. 核心知识点
- 提取所有**定义、定理、公式、关键概念**
- 每个知识点给出**简洁解释**
- 公式使用 LaTeX 语法（$...$ 行内，$$...$$ 独立行）

### 2. 重点解题方法
- 整理资料中出现的**解题步骤、技巧、常见陷阱**
- 每个方法附一个**简短示例**
- 标注方法适用的**题型类型**

### 3. 考试高频考点
- 基于内容强调程度、重复频率、例题密度判断考点重要性
- 用 ⭐ 标注重要程度（⭐ 了解，⭐⭐ 掌握，⭐⭐⭐ 必考）
- 给出每个考点的**典型出题形式**

### 4. 数学公式规范
- 行内公式用 `$...$`，独立公式用 `$$...$$`。
- 不要在一句中文中使用 `$$...$$`。
- 所有数学变量和公式都必须放在公式环境中，例如 `$K_v$`、`$A^{T}$`、`$1/K_v$`、`$G(s)$`。
- 矩阵写 `\begin{bmatrix} ... \end{bmatrix}`，不能写 `\begin{\bmatrix}`。
- 分段函数写 `\begin{cases} ... \end{cases}`。
- 分数写 `\frac{a}{b}`，极限写 `\lim_{s \to 0}`，无穷写 `\infty`。
- 转置写 `$A^{T}$`，不要写裸露的 `A^T`。

### 5. 格式要求
- 使用 Markdown 层级标题（# ## ###）
- 表格用于对比类内容
- 使用 > 引用块标注特别重要的内容
- 每个一级标题下的内容要有清晰的逻辑顺序

---

## 课程资料内容

"""
    prompt += text_summary

    if images:
        prompt += f"\n\n注意：本课程资料包含 {len(images)} 张图片（图表/示意图），请一并分析。\n"

    return prompt


def build_knowledge_markdown(analysis_result: str, title: str) -> str:
    """Wrap Claude's analysis result into a complete knowledge list markdown document."""
    return f"""---
title: "{title} - 期末复习知识清单"
lang: zh-CN
toc: true
toc-depth: 3
---

# {title}

## 期末复习知识清单

> 生成时间：自动生成 | 建议搭配章节测试题使用

{analysis_result}
"""
