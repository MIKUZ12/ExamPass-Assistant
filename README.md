# ExamPass Assistant

**把课堂讲义变成可对照、可推导、可复盘的考试复习系统。** 一键将 PPT、Word、PDF 课件转化为教授式章节讲义和交互式测试题。

> [English](./README_EN.md)

---

### 仓库说明

这是 **[@MIKUZ12](https://github.com/MIKUZ12)** 维护的自用改造版仓库：

- 当前仓库：`https://github.com/MIKUZ12/ExamPass-Assistant`
- 原始项目：`https://github.com/WUBING2023/ExamPass-Assistant`

本仓库基于原始项目二次开发，保留原项目的课程资料提取、HTML 生成、章节测试等基础能力，并围绕“真正讲懂课程内容”做了定制增强。原项目作者和贡献者信息保留在下方贡献者与许可证部分。

---

### 适用场景

| 角色 | 用途 |
|------|------|
| 大学生 | 上传课程 PPT/讲义，自动生成教授式章节讲义 + 交互式章节测试，按逻辑链、公式推导和图表含义复习 |
| 授课教师 | 课件一键转化为结构化讲义，自动生成有区分度的配套习题、答案解析和错题复盘材料 |
| 考研/考证 | 参考书 PDF 转为可推导、可自测、可错题复盘的复习材料 |

### 核心功能

- 支持 PPTX / DOCX / PDF，递归扫描目录，按章节自动分组
- 提取文字、表格、图片，并在 `_extraction_bundle.json` 中记录关键图片候选
- 生成**教授式章节讲义 HTML**：先建立章节知识地图，再逐页 / 逐模块讲解前后逻辑、概念动机、公式推导、图表含义和考试考法
- 支持**图片内联嵌入**：通过 `{{IMAGE:img_001}}` 将 PPT 中的关键图嵌入到对应讲解段落旁边，最终 HTML 使用 data URI，不依赖本地图片文件
- 支持**公式与图文融合讲解**：公式必须在相关模块中逐步推导，图表必须解释坐标轴、曲线、箭头、模块和变量关系
- 生成**交互式章节测试 HTML**：28 题 100 分，点击选项→一键批改→逐题显示正确/错误+详细解析+易错提醒
- 生成**错题分析文档**：自动收录客观题错题，导出 Markdown，附带可复制的错题分析 Prompt
- 强化**题目质量约束**：选择题干扰项必须来自同一概念簇、真实错因或推导链，不允许一眼排除的奇怪选项
- 分析结果自动缓存，同目录再次运行秒级出结果
- 浏览器打开即用，Ctrl+P 打印为 PDF

### 快速开始

```bash
git clone https://github.com/MIKUZ12/ExamPass-Assistant.git
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
- `知识清单.html` — 教授式复习讲义（章节主线、逐页/逐模块讲解、公式推导、图文内联）
- `章节测试.html` — 交互式自测（可选可批改、逐题解析）

#### 在代码中调用

```python
from scripts.template_engine import save_knowledge_html, save_test

# 教授式讲义：HTML body 直接传入（引擎自动加 H1 + 目录）
# 可用 {{IMAGE:img_001}} 将关键图片嵌入到对应讲解段落旁边
body = '<h2>逐页 / 逐模块深度讲解</h2>\n<h3>学习曲线为什么重要</h3>\n<p>...</p>{{IMAGE:img_001}}'
save_knowledge_html(
    body,
    '知识清单.html',
    '第15章 序列生成模型',
    embedded_images=[{
        'id': 'img_001',
        'path': '_exampass_images/课件/slide4_img2.png',
        'caption': '学习曲线示意图',
    }],
)

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
├── tests/                      # 110 个测试用例
└── requirements.txt
```

### 贡献者

- 当前改造版维护：[@MIKUZ12](https://github.com/MIKUZ12)
- 原项目开发与维护：[@WUBING2023](https://github.com/WUBING2023)
- 启发性贡献：yaxing@cvc.uab.es
- 测试：[@YeMoonlight](https://github.com/YeMoonlight)
- 测试：[@Yuzhihan-zyr](https://github.com/Yuzhihan-zyr)

### 许可证

本软件采用 **Creative Commons BY-NC 4.0** 许可证。

- 允许自由使用、修改、再分发（需署名）
- **禁止商业用途**

完整条款见 [LICENSE](./LICENSE)。

Copyright (c) 2025 ExamPass Assistant Contributors
