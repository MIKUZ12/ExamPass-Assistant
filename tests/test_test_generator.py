"""Tests for test_generator.py."""

import pytest
from test_generator import (
    build_test_prompt,
    split_test_and_answer,
    build_test_markdown,
    build_answer_markdown,
)


class TestBuildTestPrompt:
    def test_basic(self):
        text = "## 知识点\n监督学习的定义和分类。"
        prompt = build_test_prompt(text)
        assert "命题专家" in prompt or "测试题" in prompt
        assert text in prompt

    def test_with_count(self):
        prompt = build_test_prompt("content", question_count=10)
        assert "10 道" in prompt

    def test_with_knowledge(self):
        prompt = build_test_prompt("text", knowledge_markdown="# Knowledge\n要点")
        assert "知识清单" in prompt or "Knowledge" in prompt

    def test_empty_content(self):
        prompt = build_test_prompt("")
        assert len(prompt) > 0

    def test_prompt_requires_deep_distractors_and_derivations(self):
        prompt = build_test_prompt("公式推导和图表解释。")
        assert "同一概念簇" in prompt
        assert "一眼排除" in prompt
        assert "公式推导题" in prompt
        assert "错题复盘提示" in prompt


class TestSplitTestAndAnswer:
    def test_standard_split(self):
        full = "## 题目\n\n1. 选择题\n内容\n\n## 答案与解析\n\n1. A\n解析"
        q, a = split_test_and_answer(full)
        assert "## 题目" in q
        assert "## 答案与解析" in a
        assert "选择题" in q
        assert "A" in a

    def test_no_answer_section(self):
        full = "## 题目\n\nJust questions here"
        q, a = split_test_and_answer(full)
        assert q == full
        assert a == ""

    def test_alternate_answer_marker(self):
        full = "## 题目\nQ1\n\n## 答案\nA1"
        q, a = split_test_and_answer(full)
        assert "题目" in q
        assert "答案" in a
        assert "A1" in a

    def test_empty_input(self):
        q, a = split_test_and_answer("")
        assert q == ""
        assert a == ""


class TestBuildMarkdown:
    def test_test_markdown(self):
        md = build_test_markdown("## 题目\n测试内容", "第一章")
        assert "第一章" in md
        assert "章节测试" in md
        assert "测试内容" in md

    def test_answer_markdown(self):
        md = build_answer_markdown("## 答案与解析\n解析内容", "第一章")
        assert "第一章" in md
        assert "答案与解析" in md
        assert "解析内容" in md
