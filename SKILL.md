---
name: exampass
description: 将课程资料（PPT/Word/PDF）按章节生成知识清单和交互式章节测试，帮助高效期末复习。
---

# ExamPass Assistant

## 执行流程（主线程直出，目标 2 分钟）

### 第一步：提取内容（~30s）
```bash
python scripts/run_exampass.py <目标目录>
```

### 第二步：Claude 分析并生成（~90s）
Claude 读取 `_extraction_bundle.json`，深度分析后直接调用：

```python
from scripts.template_engine import save_knowledge_html, save_test

save_knowledge_html(body_html, '知识清单.html', '章节标题')
save_test(questions, '章节测试.html', '章节标题', '满分 100 分', duration_minutes=30)
```

### 第三步：完成
浏览器打开 HTML 即可使用。Ctrl+P 打印为 PDF。

## 关键约定

- **主线程执行，不用子 Agent**：省去子 Agent 启动、环境建立、脚本编写的开销
- HTML body 用 H2/H3/p/table/blockquote，公式 $$...$$ / $...$
- 不用中文弯引号，不用 Unicode 箭头符号，用 --&gt;
- 题目不加编号，选项不加 A/B/C/D 前缀（模板自动添加）
- 题目 explanation 中公式需写成 \$...\$（转义反斜杠）
