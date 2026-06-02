# ExamPass Assistant

**Turn lecture slides into study materials with deep explanations, inline figures, derivations, quizzes, and wrong-answer review.**

> [中文](./README.md)

---

### Repository Note

This is a customized repository maintained by **[@MIKUZ12](https://github.com/MIKUZ12)**:

- Current repository: `https://github.com/MIKUZ12/ExamPass-Assistant`
- Original project: `https://github.com/WUBING2023/ExamPass-Assistant`

This repository is adapted from the original project. It keeps the original extraction, HTML generation, and quiz workflow, while adding custom features focused on deeper chapter explanations, inline source figures, stronger quiz design, and wrong-answer analysis. Original contributors are credited below.

---

### What is this

An AI-powered exam prep assistant. Drop in lecture PPTs, Word handouts, or PDF readings — it generates:

- **Professor-style Chapter Guides** — narrative explanations that connect slides/modules, derive formulas step by step, and place figures next to the theory they explain
- **Interactive Quizzes** — 28 questions, 100 points. Click to answer, one-click grading, per-question correct/incorrect badges, detailed explanations, common mistake warnings, and wrong-answer review export

Open in any browser. Ctrl+P to print as PDF. MathJax renders formulas perfectly.

### Why

The universal pain of finals week: scattered lecture files, no clear sense of exam priorities, no reliable practice questions.

ExamPass reads your course materials with Claude, extracts key concepts with logical narratives, and generates self-grading quizzes. Students use it to study smarter. Instructors use it to create exercises and assignments in seconds.

### Supported Formats

PPTX · DOCX · PDF (with image recognition via multimodal analysis)

### Quick Start

```bash
git clone https://github.com/MIKUZ12/ExamPass-Assistant.git
cd ExamPass-Assistant
pip install -r requirements.txt
```

### Usage

**Generate chapter materials** — run `/exampass` in any course directory. The skill scans subfolders, groups files by chapter, extracts all content, performs deep analysis, and outputs professor-style guides + interactive quizzes into each folder.

**Use in your own code**:

```python
from scripts.template_engine import save_knowledge_html, save_test

# Chapter guide — pass HTML body directly (engine adds H1 + TOC)
# Use {{IMAGE:img_001}} to inline a key source figure next to the explanation.
body = '<h2>Deep Module Walkthrough</h2>\n<h3>Why the learning curve matters</h3>\n<p>...</p>{{IMAGE:img_001}}'
save_knowledge_html(
    body,
    'knowledge.html',
    'Chapter 15',
    embedded_images=[{
        'id': 'img_001',
        'path': '_exampass_images/slides/slide4_img2.png',
        'caption': 'Learning curve',
    }],
)

# Interactive quiz — pass question data, get a self-grading page
questions = [
    {"type": "choice", "points": 2,
     "question": "What is the core function of a language model?",
     "options": ["Translation", "Estimating sentence probability",
                 "Tokenization", "Object recognition"],
     "answer": 1,
     "explanation": "A language model computes P(w1,...,wT)...",
     "pitfall": "Don't confuse language models with translation systems."},
]
save_test(questions, 'quiz.html', 'Chapter 15', '100 points', duration_minutes=30)
```

### How It Works

1. **Scan & Group** — recursively finds all PPTX/DOCX/PDF files, groups by parent folder
2. **Extract** — pulls text, tables, and embedded images from each file
3. **Analyze** — the model reads the content, reconstructs the chapter logic, derives formulas, explains figures, and selects important source images
4. **Generate** — produces styled self-contained HTML with inline images, MathJax formulas, interactive quiz logic, and wrong-answer review export

### Project Structure

```
EPA/
├── SKILL.md                    # /exampass entry point
├── exampass-final.md           # /exampass-final entry point
├── scripts/                    # Core Python modules
│   ├── scanner.py              # Recursive scanning & grouping
│   ├── extractor.py            # Unified extraction dispatcher
│   ├── extract_pptx.py         # PPTX extraction
│   ├── extract_docx.py         # DOCX extraction
│   ├── extract_pdf.py          # PDF extraction
│   ├── image_extractor.py      # Image extraction for multimodal analysis
│   ├── template_engine.py      # HTML template engine
│   ├── html_generator.py       # Fast generator
│   ├── generate_cached.py      # Cache-based instant re-runs
│   ├── run_exampass.py         # Single-script extraction entry
│   ├── knowledge_analyzer.py   # Knowledge list prompt builder
│   ├── test_generator.py       # Quiz generation prompt builder
│   ├── exam_generator.py       # Final exam prompt builder
│   └── utils.py
├── templates/                  # CSS & HTML templates
│   ├── base.css                # Shared styles (warm paper, dual-color)
│   ├── test.css                # Interactive quiz styles
│   ├── page_template.html      # HTML page shell
│   ├── test_js_template.js     # Quiz JS template
│   └── test_labels.json        # Chinese UI labels
├── tests/                      # 110 test cases
└── requirements.txt
```

### Contributors

- Customized Version Maintenance: [@MIKUZ12](https://github.com/MIKUZ12)
- Original Project Development & Maintenance: [@WUBING2023](https://github.com/WUBING2023)
- Inspirational Contribution: yaxing@cvc.uab.es
- Testing: [@YeMoonlight](https://github.com/YeMoonlight)
- Testing: [@Yuzhihan-zyr](https://github.com/Yuzhihan-zyr)

### License

[CC BY-NC 4.0](./LICENSE) — free to use, modify, and share for non-commercial purposes. Commercial use requires a separate license.

Copyright (c) 2025 ExamPass Assistant Contributors
