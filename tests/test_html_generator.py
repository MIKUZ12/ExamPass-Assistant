"""Tests for html_generator.py (now outputs .html)."""

import os
import pytest
from html_generator import generate_html
from template_engine import save_test


SAMPLE_MARKDOWN = """---
title: "测试文档"
lang: zh-CN
---

# 第一章 测试

## 1.1 基本概念

这是一个测试段落。包含一些**加粗**和*斜体*文字。

测试公式：$E = mc^2$

$$\\sum_{i=1}^{n} x_i = \\bar{x}$$

### 1.1.1 子节

| 名称 | 数值 | 描述 |
|------|------|------|
| Alpha | 1.0 | 学习率 |
| Beta | 0.9 | 动量 |

> **重点**：这是一个重要的知识点。

- 项目1
- 项目2
- 项目3
"""


class TestMarkdownToPDF:
    def test_basic_conversion(self, temp_dir):
        output = os.path.join(temp_dir, "test_output.html")
        result = generate_html(SAMPLE_MARKDOWN, output)
        assert result is True
        assert os.path.exists(output)
        assert os.path.getsize(output) > 0

    def test_chinese_content(self, temp_dir):
        md = """---
title: "中文测试"
lang: zh-CN
---

# 机器学习基础

机器学习是人工智能的一个重要分支。

## 监督学习

监督学习使用带标签的数据进行训练。
"""
        output = os.path.join(temp_dir, "chinese_test.html")
        result = generate_html(md, output)
        assert result is True
        assert os.path.exists(output)
        assert os.path.getsize(output) > 0

    def test_math_formulas(self, temp_dir):
        md = """# 公式测试

行内公式：$f(x) = wx + b$

独立公式：

$$\\frac{\\partial L}{\\partial w} = \\frac{1}{n}\\sum_{i=1}^{n} 2(y_i - \\hat{y}_i)(-x_i)$$

矩阵：

$$\\begin{bmatrix} a & b \\\\ c & d \\end{bmatrix}$$
"""
        output = os.path.join(temp_dir, "math_test.html")
        result = generate_html(md, output)
        assert result is True

    def test_table_rendering(self, temp_dir):
        md = """# 表格测试

| 算法 | 准确率 | 训练时间 |
|------|--------|----------|
| SVM | 95.2% | 120s |
| Random Forest | 94.8% | 85s |
| XGBoost | 96.1% | 200s |
| Neural Network | 95.5% | 600s |
"""
        output = os.path.join(temp_dir, "table_test.html")
        result = generate_html(md, output)
        assert result is True

    def test_empty_content(self, temp_dir):
        output = os.path.join(temp_dir, "empty.html")
        result = generate_html("# Empty\n", output)
        assert result is True

    def test_invalid_output_path(self, temp_dir):
        output = os.path.join(temp_dir, "nonexistent", "out.html")
        result = generate_html("# test", output)
        # Should handle gracefully — handle gracefully on invalid paths
        assert isinstance(result, bool)

    def test_output_overwrites(self, temp_dir):
        output = os.path.join(temp_dir, "overwrite.html")
        generate_html("# First\n", output)
        generate_html("# Second\n", output)
        assert os.path.exists(output)

    def test_interactive_test_includes_wrong_review_tools(self, temp_dir):
        output = os.path.join(temp_dir, "test.html")
        questions = [
            {
                "type": "choice",
                "points": 2,
                "question": "下列哪项最符合条件？",
                "options": ["正确边界", "漏掉条件", "混淆概念", "中间结论"],
                "answer": 0,
                "knowledge_point": "条件适用",
                "diagnosis_hint": "混淆适用条件",
                "explanation": "<strong>正确答案</strong>：A。",
                "pitfall": "不要漏掉条件。",
            }
        ]
        save_test(
            questions,
            output,
            "章节测试",
            wrong_answer_analysis_prompt="按错因归类并补全推导。",
        )

        html = open(output, encoding="utf-8").read()
        assert "wrong-review-box" in html
        assert "renderWrongReviewMarkdown" in html
        assert "按错因归类并补全推导。" in html
        assert "下载错题文档" in html
