"""Prepare prompts and assemble markdown for chapter test generation."""


def build_test_prompt(text_summary: str, knowledge_markdown: str = "", question_count: int = None) -> str:
    """
    Build the analysis prompt for Claude to generate chapter test questions.
    Returns a structured test with questions and answers.
    """
    count_guide = ""
    if question_count:
        count_guide = f"\n请生成大约 {question_count} 道题目。"

    prompt = f"""你是一位严格的大学课程命题专家和阅卷教师。请根据以下课程资料，生成一套**有区分度的章节测试题**。{count_guide}

## 命题要求

### 题型配比
- **选择题**（约 45%）：4 个选项，考察概念边界、公式条件、推导步骤、图表理解和常见错法。选项必须有迷惑性但保证唯一正确答案。
- **判断题**（约 20%）：聚焦高频陷阱，不能是定义原句的简单改写。
- **简答 / 推导题**（约 25%）：考察解题方法应用、公式推导、图表解释和知识串联，要求写出关键步骤。
- **综合题**（约 10%）：接近期末真题难度，要求跨概念分析或计算。

### 质量要求
- 题目之间**相互独立**，不暗示其他题目的答案
- 覆盖资料中的**核心知识点**，重点内容可多出
- 难度梯度：35% 基础辨析 + 40% 推导/应用 + 25% 综合迁移
- 每套题必须包含：概念边界题、公式推导题、图表/框图解释题、条件适用题、易错辨析题、综合应用题
- 选择题的 4 个选项必须属于同一概念簇或同一推导链，长度和表达风格相近
- 干扰项必须来自真实错因，例如：混淆相近概念、漏掉适用条件、把中间结论当最终结论、符号含义错置、图表轴/箭头读反、只记公式不懂前提
- 禁止出现一眼排除的选项，例如无关名词、明显相反的废话、过度绝对化但资料中没有争议的表述、和题干领域完全无关的选项
- 题目不能只问「是什么」，必须经常追问「为什么」「怎么推出」「条件变了会怎样」「图中变化说明什么」
- 每道题标注**分值**

### 数学公式硬性要求

- 所有数学符号必须用 `$...$` 包裹，包括选项中的 `$K_v$`、`$A^{T}$`、`$1/K_v$`。
- 行内公式只能用 `$...$`，禁止在句子中使用 `$$...$$`。
- 块级公式才能使用 `$$...$$`，且必须独立成段。
- 分数写 `\frac{a}{b}`。
- 极限写 `\lim_{s \to 0}`。
- 无穷写 `\infty`。
- 反正切写 `\arctan(at)`。
- 近似写 `\approx`。
- 矩阵写 `\begin{bmatrix} ... \end{bmatrix}`，不能写 `\begin{\bmatrix}`。
- 分段函数写 `\begin{cases} ... \end{cases}`。
- 转置写 `$A^{T}$`，不要写裸露的 `A^T`。
- 比较关系写 `$0 < \zeta < 1$`。

### 章节测试 questions JSON 要求

- 选择题 `answer` 必须是正确选项下标：0、1、2、3。
- 判断题 `answer` 必须是 0 或 1，其中 0 表示"正确"，1 表示"错误"。
- 不要把 `answer` 写成 `"A"`、`"B"`、`"PBH判据"` 或公式文本。
- `question`、`options`、`explanation`、`pitfall` 中出现数学表达式时必须符合 MathJax 写法。
- 不要生成裸露的 `A^T`、`K_v`、`1/K_v`、`G(s)`。

正确 JSON 示例：
```json
{
  "type": "choice",
  "points": 2,
  "question": "静态误差系数 $K_v$ 的定义是：",
  "options": [
    "$K_v = \\lim_{s \\to 0} G(s)$",
    "$K_v = \\lim_{s \\to 0} sG(s)$",
    "$K_v = \\lim_{s \\to 0} s^2G(s)$",
    "$K_v = \\lim_{s \\to \\infty} sG(s)$"
  ],
  "answer": 1,
  "knowledge_point": "静态误差系数定义",
  "explanation": "正确答案：$K_v = \\lim_{s \\to 0} sG(s)$。",
  "pitfall": "不要把 $K_v$ 与 $K_p$、$K_a$ 混淆。"
}
```

### 输出格式

先输出**纯题目部分**，用 `## 题目` 标记开始。
然后输出**答案与解析部分**，用 `## 答案与解析` 标记开始。

答案部分要求：
- 选择题：给正确答案 + **每个选项为什么对/错** + 该错误选项对应的典型错因
- 判断题：说明判断边界，指出题干中哪个词或条件决定正误
- 推导/计算题：给**完整推导过程**，不能跳步，必须解释每一步使用的定义、公式或图表信息
- 简答/综合题：给**完整解题过程** + **评分要点** + **满分标准** + 常见扣分点
- 每道题都要给出「错题复盘提示」，说明答错后应该回看哪一类概念、公式、图表或例题

---

## 课程资料内容

{text_summary}
"""

    if knowledge_markdown:
        prompt += f"\n\n---\n\n## 本章知识清单（供参考）\n\n{knowledge_markdown}\n"

    prompt += """

---

请严格按照以上要求输出，先输出"## 题目"，再输出"## 答案与解析"。
"""
    return prompt


def split_test_and_answer(full_output: str) -> tuple:
    """Split combined output into (questions_only, answers_only)."""
    if "## 答案与解析" in full_output:
        parts = full_output.split("## 答案与解析", 1)
        questions = parts[0].strip()
        answers = "## 答案与解析\n" + parts[1].strip()
        return questions, answers
    elif "## 答案" in full_output:
        parts = full_output.split("## 答案", 1)
        questions = parts[0].strip()
        answers = "## 答案\n" + parts[1].strip()
        return questions, answers
    else:
        return full_output, ""


def build_test_markdown(questions: str, title: str) -> str:
    """Wrap questions into a standalone test markdown."""
    return f"""---
title: "{title} - 章节测试"
lang: zh-CN
---

# {title}

## 章节测试

> 说明：请独立完成，闭卷作答。

{questions}
"""


def build_answer_markdown(answers: str, title: str) -> str:
    """Wrap answers into a standalone answer markdown."""
    return f"""---
title: "{title} - 章节测试答案与解析"
lang: zh-CN
---

# {title}

## 章节测试 · 答案与解析

{answers}
"""
