"""Generate styled HTML directly — no Markdown or Pandoc needed.

For knowledge pages: pass HTML body to generate_html().
For test pages: pass question data to save_test().
"""

import os
from template_engine import save_knowledge_html, save_test


def generate_html(body_html, output_path, title='知识清单', embedded_images=None):
    """Wrap raw HTML body into a styled knowledge page and save to file."""
    try:
        if output_path.endswith('.pdf'):
            output_path = output_path[:-4] + '.html'
        save_knowledge_html(body_html, output_path, title, embedded_images=embedded_images)
        return os.path.exists(output_path) and os.path.getsize(output_path) > 100
    except Exception as e:
        print(f"生成失败: {e}")
        return False
