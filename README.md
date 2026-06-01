# ExamPass Assistant

**把课堂讲义变成考试利器。** 一键将 PPT、Word、PDF 课件转化为结构化知识清单和交互式测试题。

> [English](./README_EN.md)

---

### 适用场景

| 角色 | 用途 |
|------|------|
| 大学生 | 上传课程 PPT/讲义，自动生成知识清单 + 交互式章节测试（选择+一键批改+逐题解析），高效通过期末考试 |
| 授课教师 | 课件一键转化为结构化知识总结，自动生成配套习题+答案解析，直接用于课堂教学或课后作业 |
| 考研/考证 | 参考书 PDF 转为精简知识清单，配合自测题检验掌握程度 |

### 核心功能

- 支持 PPTX / DOCX / PDF，递归扫描目录，按章节自动分组
- 提取文字、表格、图片（Claude 多模态分析）
- 生成**知识清单 HTML**：MathJax 公式完美渲染，双色标注（知识点黑色加粗 + 解释浅灰细体），重点分级标签（必考/重点/高频/了解），自动目录导航
- 生成**交互式章节测试 HTML**：28 题 100 分，点击选项→一键批改→逐题显示正确/错误+详细解析+易错提醒
- 分析结果自动缓存，同目录再次运行秒级出结果
- 浏览器打开即用，Ctrl+P 打印为 PDF

### 快速开始

```bash
git clone https://github.com/WUBING2023/ExamPass-Assistant.git
cd ExamPass-Assistant
pip install -r requirements.txt
```

### 使用方法

#### 生成章节知识清单 + 测试题

在课程目录下调用 `/exampass`，自动扫描子文件夹、提取内容、深度分析、生成 HTML。

```
课程/
├── 第一章-绪论/
│   ├── 课件.pptx
│   └── 讲义.pdf
├── 第二章-基础/
│   └── lecture.pdf
```

每个章节生成：
- `知识清单.html` — 结构化复习资料（逻辑链完整、双色扫读、公式完美）
- `章节测试.html` — 交互式自测（可选可批改、逐题解析）

#### 在代码中调用

```python
from scripts.template_engine import save_knowledge_html, save_test

# 知识清单：HTML body 直接传入（引擎自动加 H1 + 目录）
body = '<h2>一、序列建模基础</h2>\n<h3>1.1 什么是序列数据</h3>\n<p>...</p>'
save_knowledge_html(body, '知识清单.html', '第15章 序列生成模型')

# 交互式测试：题目列表直接传入
questions = [
    {"type": "choice", "points": 2,
     "question": "语言模型的核心功能是什么？",
     "options": ["翻译", "评估句子概率", "分词", "识别物体"],
     "answer": 1, "explanation": "语言模型计算词序列概率...",
     "pitfall": "注意区分语言模型和机器翻译"},
]
save_test(questions, '章节测试.html', '第15章', '满分 100 分', duration_minutes=30)
```

### 项目结构

```
EPA/
├── SKILL.md                    # /exampass 入口
├── exampass-final.md           # /exampass-final 入口
├── scripts/
│   ├── scanner.py              # 递归扫描与分组
│   ├── extractor.py            # 统一提取调度（PPTX/DOCX/PDF）
│   ├── extract_pptx.py         # PPTX 提取（文字+表格+图片）
│   ├── extract_docx.py         # DOCX 提取
│   ├── extract_pdf.py          # PDF 提取
│   ├── image_extractor.py      # 图片提取（供 Claude 多模态分析）
│   ├── template_engine.py      # HTML 模板引擎
│   ├── html_generator.py       # 快速生成器
│   ├── generate_cached.py      # 缓存加速（二次运行秒出）
│   ├── run_exampass.py         # 单脚本提取入口
│   ├── knowledge_analyzer.py   # 知识清单分析 prompt
│   ├── test_generator.py       # 测试题生成 prompt
│   ├── exam_generator.py       # 期末试卷 prompt
│   ├── web_research.py         # 网络调研
│   └── utils.py                # 通用工具
├── templates/
│   ├── base.css                # 共享样式（暖色纸张、双色标注）
│   ├── test.css                # 交互测试样式
│   ├── page_template.html      # HTML 页面模板
│   ├── test_js_template.js     # 测试页 JS 模板
│   └── test_labels.json        # 中文标签配置
├── tests/                      # 102 个测试用例
└── requirements.txt
```

### 贡献者

- 开发与维护：[@WUBING2023](https://github.com/WUBING2023)
- 启发性贡献：yaxing@cvc.uab.es
- 测试：[@YeMoonlight](https://github.com/YeMoonlight)
- 测试：[@Yuzhihan-zyr](https://github.com/Yuzhihan-zyr)

### 许可证

本软件采用 **Creative Commons BY-NC 4.0** 许可证。

- 允许自由使用、修改、再分发（需署名）
- **禁止商业用途**

完整条款见 [LICENSE](./LICENSE)。

Copyright (c) 2025 ExamPass Assistant Contributors
