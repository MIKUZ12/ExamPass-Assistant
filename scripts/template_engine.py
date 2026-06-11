"""Template engine for ExamPass HTML generation.

Architecture:
  templates/page_template.html  -- HTML shell (__TITLE__, __CSS__, __BODY__, __EXTRA_JS__)
  templates/base.css            -- shared styles
  templates/test.css            -- quiz-specific styles
  templates/test_js_template.js -- JS for interactive quiz (__QUESTIONS_PLACEHOLDER__, __LABELS_PLACEHOLDER__)
  templates/test_labels.json    -- Chinese UI labels
"""

import os
import json
import base64
import mimetypes
import html as _html

_TEMPLATES_DIR = os.path.join(os.path.dirname(os.path.dirname(__file__)), 'templates')


def _read(filename):
    path = os.path.join(_TEMPLATES_DIR, filename)
    if os.path.exists(path):
        with open(path, 'r', encoding='utf-8') as f:
            return f.read()
    return ''


_PAGE_TEMPLATE = _read('page_template.html')

_MATHJAX_CONFIG = '''<script>
MathJax = {
  tex: {
    inlineMath: [['$', '$']],
    displayMath: [['$$', '$$']]
  }
};
</script>'''

# MathJax: auto-download to local path if not present, fallback to CDN
_MATHJAX_LOCAL_DIR = os.path.join(os.path.dirname(os.path.dirname(__file__)), 'mathjax')
_MATHJAX_LOCAL_FILE = os.path.join(_MATHJAX_LOCAL_DIR, 'tex-svg.js')
_MATHJAX_CDN_URL = 'https://cdn.jsdelivr.net/npm/mathjax@3/es5/tex-svg.js'

def _ensure_mathjax():
    """Download MathJax locally if not present; return the src attribute value."""
    if os.path.exists(_MATHJAX_LOCAL_FILE):
        return 'src="mathjax/tex-svg.js"'
    try:
        os.makedirs(_MATHJAX_LOCAL_DIR, exist_ok=True)
        import urllib.request
        urllib.request.urlretrieve(_MATHJAX_CDN_URL, _MATHJAX_LOCAL_FILE)
        return 'src="mathjax/tex-svg.js"'
    except Exception:
        return f'src="{_MATHJAX_CDN_URL}"'


def _copy_mathjax_to_dir(target_dir):
    """Copy mathjax/tex-svg.js to target_dir/mathjax/ if not already there."""
    if not target_dir:
        return
    dest_dir = os.path.join(target_dir, 'mathjax')
    dest_file = os.path.join(dest_dir, 'tex-svg.js')
    if os.path.exists(dest_file):
        return
    if not os.path.exists(_MATHJAX_LOCAL_FILE):
        return
    os.makedirs(dest_dir, exist_ok=True)
    import shutil
    shutil.copy2(_MATHJAX_LOCAL_FILE, dest_file)

_MATHJAX_SCRIPT = '<script ' + _ensure_mathjax() + '></script>'


def _build_page(title, body_html, css_extra='', js_extra=''):
    """Fill the page template. JS goes AFTER body -- critical for DOM access."""
    css = _read('base.css') + '\n' + css_extra
    return (
        _PAGE_TEMPLATE
        .replace('__TITLE__', title)
        .replace('__MATHJAX_CONFIG__', _MATHJAX_CONFIG)
        .replace('__MATHJAX_SCRIPT__', _MATHJAX_SCRIPT)
        .replace('__CSS__', css)
        .replace('__BODY__', body_html)
        .replace('__EXTRA_JS__', js_extra)
    )


# ─── Knowledge page ─────────────────────────────────────────────────

import re as _re

_EMBEDDED_IMAGES_PLACEHOLDER = '{{EMBEDDED_IMAGES}}'
_INLINE_IMAGE_PATTERN = _re.compile(r'\{\{(?:IMAGE|EMBEDDED_IMAGE):\s*([^}]+?)\s*\}\}')


def _resolve_image_path(path, base_dir):
    if not path:
        return ''
    if os.path.isabs(path):
        return path
    return os.path.join(base_dir, path)


def _image_to_data_uri(path):
    mime, _ = mimetypes.guess_type(path)
    if not mime:
        mime = 'image/png'
    with open(path, 'rb') as f:
        encoded = base64.b64encode(f.read()).decode('ascii')
    return 'data:' + mime + ';base64,' + encoded


def _image_item_value(item, key, default=''):
    if isinstance(item, str):
        if key in ('path', 'file'):
            return item
        if key == 'caption':
            return os.path.basename(item)
        return default
    return item.get(key, default)


def _image_item_keys(item):
    image_path = _image_item_value(item, 'path') or _image_item_value(item, 'file')
    keys = []
    if not isinstance(item, str):
        for key in ('id', 'image_id', 'candidate_id'):
            value = item.get(key)
            if value:
                keys.append(str(value))
    if image_path:
        keys.extend([
            image_path,
            os.path.basename(image_path),
        ])
    return [key.strip() for key in keys if key and key.strip()]


def _build_image_index(embedded_images):
    index = {}
    for item in embedded_images or []:
        for key in _image_item_keys(item):
            index[key] = item
    return index


def _render_embedded_image(item, base_dir, figure_number=None):
    """Render one selected course image as a self-contained data URI figure."""
    if not item:
        return ''

    image_path = _image_item_value(item, 'path') or _image_item_value(item, 'file')
    caption = _image_item_value(item, 'caption') or os.path.basename(image_path)
    note = _image_item_value(item, 'note') or _image_item_value(item, 'reason')
    image_id = _image_item_value(item, 'id') or _image_item_value(item, 'image_id')

    if not isinstance(item, str) and item.get('data_uri'):
        src = item['data_uri']
    else:
        resolved = _resolve_image_path(image_path, base_dir)
        if not resolved or not os.path.exists(resolved):
            return ''
        src = _image_to_data_uri(resolved)

    caption_html = _html.escape(caption)
    alt_html = _html.escape(caption or '课程图片')
    note_html = ''
    if note:
        note_html = '<span class="embedded-image-note">' + _html.escape(note) + '</span>'
    number_html = ''
    if figure_number is not None:
        number_html = '<strong>图 ' + str(figure_number) + '.</strong> '
    attrs = ''
    if image_id:
        attrs = ' data-image-id="' + _html.escape(str(image_id)) + '"'

    return (
        '<figure class="embedded-image"' + attrs + '>\n'
        '  <img src="' + src + '" alt="' + alt_html + '"/>\n'
        '  <figcaption>' + number_html + caption_html + note_html + '</figcaption>\n'
        '</figure>'
    )


def _render_embedded_images(embedded_images, base_dir):
    """Render selected course images as a fallback self-contained figure group."""
    if not embedded_images:
        return ''

    figures = []
    for idx, item in enumerate(embedded_images, start=1):
        figure = _render_embedded_image(item, base_dir, figure_number=idx)
        if figure:
            figures.append(figure)

    if not figures:
        return ''

    return (
        '<section class="embedded-images">\n'
        '<h2>关键原图对照</h2>\n'
        '<p class="embedded-images-intro">以下图片已内嵌进本 HTML，可离线打开并对照学习。</p>\n'
        + '\n'.join(figures) +
        '\n</section>\n'
    )


def _inject_embedded_images(body_html, embedded_images, base_dir):
    image_index = _build_image_index(embedded_images)

    def replace_inline(match):
        key = match.group(1).strip()
        return _render_embedded_image(image_index.get(key), base_dir)

    body_html = _INLINE_IMAGE_PATTERN.sub(replace_inline, body_html)

    if _EMBEDDED_IMAGES_PLACEHOLDER in body_html:
        image_html = _render_embedded_images(embedded_images, base_dir)
        return body_html.replace(_EMBEDDED_IMAGES_PLACEHOLDER, image_html)
    return body_html

def _auto_toc_and_title(body_html, title):
    """Auto-inject H1 title + TOC block, and add anchor IDs to H2/H3 headings."""
    h1_html = '<h1>' + title + '</h1>\n'

    # Parse H2 and H3 headings, assign IDs
    toc_items = []

    def replace_heading(match):
        level = int(match.group(1))
        text = match.group(2).strip()
        # Remove HTML tags from text for clean TOC entry
        clean = _re.sub(r'<[^>]+>', '', text)
        # Generate anchor from a hash of the text (stable and safe)
        anchor = 's' + str(abs(hash(clean)))[:8]
        toc_items.append({'level': level, 'text': clean, 'anchor': anchor})
        return '<h' + str(level) + ' id="' + anchor + '">' + text + '</h' + str(level) + '>'

    body_html = _re.sub(r'<h([23])[^>]*?>(.+?)</h\1>', replace_heading, body_html, flags=_re.DOTALL)

    # Build TOC
    if toc_items:
        toc_html = '<div class="toc">\n<h2>目录</h2>\n<ul>\n'
        for item in toc_items:
            indent = '  ' if item['level'] == 3 else ''
            toc_html += indent + '<li><a href="#' + item['anchor'] + '">' + item['text'] + '</a></li>\n'
        toc_html += '</ul>\n</div>\n'
    else:
        toc_html = ''

    return h1_html + toc_html + body_html


def save_knowledge_html(body_html, output_path, title, embedded_images=None):
    _copy_mathjax_to_dir(os.path.dirname(os.path.abspath(output_path)))
    body_html = _inject_embedded_images(
        body_html,
        embedded_images,
        os.path.dirname(os.path.abspath(output_path)),
    )
    body_html = _auto_toc_and_title(body_html, title)
    html = _build_page(title, body_html)
    out_dir = os.path.dirname(output_path)
    if out_dir:
        os.makedirs(out_dir, exist_ok=True)
    with open(output_path, 'w', encoding='utf-8') as f:
        f.write(html)


# ─── Question validation ───────────────────────────────────────────

def _iter_question_strings(questions):
    """Yield (label, text) for every string field in every question."""
    for i, q in enumerate(questions, start=1):
        for key in ("question", "explanation", "pitfall", "knowledge_point", "diagnosis_hint"):
            value = q.get(key)
            if isinstance(value, str):
                yield f"Q{i}.{key}", value
        for j, opt in enumerate(q.get("options") or []):
            if isinstance(opt, str):
                yield f"Q{i}.options[{j}]", opt


def _validate_math_text(label, text):
    """Check a single text field for broken LaTeX that would render incorrectly."""
    import re as _vre

    # Control characters that indicate Python ate a LaTeX backslash
    _bad_controls = {
        "\x07": "疑似 \\arctan 或 \\approx 被 Python 解释成 BEL 控制字符",
        "\x0c": "疑似 \\frac 被 Python 解释成 form feed 控制字符",
    }
    for ch, reason in _bad_controls.items():
        if ch in text:
            raise ValueError(f"{label} 含损坏控制字符：{reason}；片段={text[:160]!r}")

    # Tab inside a formula usually means \to was eaten
    for m in _vre.finditer(r"\$[^$]*\$", text):
        if "\t" in m.group(0):
            raise ValueError(
                f"{label} 的公式中含 Tab，通常是 \\to 写坏了；公式={m.group(0)!r}"
            )

    # Unmatched $
    if text.count("$") % 2 != 0:
        raise ValueError(
            f"{label} 的 $ 数量为奇数，公式分隔符未闭合；片段={text[:160]!r}"
        )

    # Wrong bmatrix / cases environment syntax
    if r"\begin{\bmatrix}" in text or r"\end{\bmatrix}" in text:
        raise ValueError(
            f"{label} 写错了 bmatrix 环境，应为 \\begin{{bmatrix}} / \\end{{bmatrix}}"
        )
    if r"\begin{\cases}" in text or r"\end{\cases}" in text:
        raise ValueError(
            f"{label} 写错了 cases 环境，应为 \\begin{{cases}} / \\end{{cases}}"
        )

    # Obvious corrupted LaTeX fragments
    _bad_frags = ["fracK", "fracs", "lim_{sto", "stoinfty", "rctan", "pprox"]
    for pat in _bad_frags:
        if pat in text:
            raise ValueError(f"{label} 含疑似损坏公式片段 `{pat}`")


def _validate_question_answer_schema(questions):
    """Validate answer field types and ranges."""
    for i, q in enumerate(questions, start=1):
        qtype = q.get("type")
        ans = q.get("answer")

        if qtype == "choice":
            if not isinstance(ans, int):
                raise ValueError(
                    f"Q{i}.answer 必须是选项下标 int（0/1/2/3），当前为 {ans!r}"
                )
            opts = q.get("options") or []
            if ans < 0 or ans >= len(opts):
                raise ValueError(
                    f"Q{i}.answer={ans} 超出 options 范围（共 {len(opts)} 个选项）"
                )

        if qtype == "tf":
            if ans not in (0, 1):
                raise ValueError(
                    f"Q{i}.answer 判断题必须是 0（正确）或 1（错误），当前为 {ans!r}"
                )


def _validate_questions_math(questions):
    """Run all validations on a questions list. Raises on first error."""
    _validate_question_answer_schema(questions)
    for label, text in _iter_question_strings(questions):
        _validate_math_text(label, text)


# ─── Interactive test page ──────────────────────────────────────────

def save_test(questions, output_path, title, subtitle='', duration_minutes=30, wrong_answer_analysis_prompt=''):
    """Generate an interactive test page.

    questions: list of {type, points, question, options, answer, explanation, pitfall}
    subtitle: optional custom subtitle (overrides auto-generated duration subtitle)
    duration_minutes: used in auto-generated subtitle if subtitle is empty
    """
    _copy_mathjax_to_dir(os.path.dirname(os.path.abspath(output_path)))
    _validate_questions_math(questions)
    questions_json = json.dumps(questions, ensure_ascii=False)
    labels = json.loads(_read('test_labels.json'))
    labels_json = json.dumps(labels, ensure_ascii=False)

    js_template = _read('test_js_template.js')
    js = js_template.replace('__QUESTIONS_PLACEHOLDER__', questions_json)
    js = js.replace('__LABELS_PLACEHOLDER__', labels_json)
    js = js.replace(
        '__WRONG_REVIEW_PROMPT_PLACEHOLDER__',
        json.dumps(wrong_answer_analysis_prompt or '', ensure_ascii=False),
    )
    js = '<script>\n' + js + '\n</script>'

    # Subtitle
    if subtitle:
        sub_html = '<p style="text-align:center;color:var(--ink-light);font-size:0.95em">' + subtitle + '</p>'
    else:
        sub_html = '<p style="text-align:center;color:var(--ink-light);font-size:0.95em">' + labels['duration_prefix'] + str(duration_minutes) + labels['duration_suffix'] + '</p>'

    body = '\n'.join([
        '<h1>' + title + '</h1>',
        '<h2 style="text-align:center">' + labels['page_title'] + '</h2>',
        sub_html,
        '',
        '<div id="score-box"><div class="score-num" id="score-num">0</div><div class="score-label">' + labels['score_label'] + '</div></div>',
        '<div id="questions-container"></div>',
        '<div class="grading-bar no-print"><button onclick="gradeAll()" id="grade-btn">' + labels['grade_button'] + '</button></div>',
        '<div id="wrong-review-box" class="wrong-review-box no-print"></div>',
    ])

    html = _build_page(title, body, css_extra=_read('test.css'), js_extra=js)
    out_dir = os.path.dirname(output_path)
    if out_dir:
        os.makedirs(out_dir, exist_ok=True)
    with open(output_path, 'w', encoding='utf-8') as f:
        f.write(html)
