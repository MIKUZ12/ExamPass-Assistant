"""Tests for self-contained embedded images in generated HTML."""

import json
import os

from PIL import Image, ImageDraw

from conftest import create_sample_pptx
from generate_cached import generate, save_cache, load_cache
from run_exampass import main as run_exampass
from template_engine import save_knowledge_html


def _create_image(path):
    img = Image.new('RGB', (160, 90), color=(240, 248, 255))
    draw = ImageDraw.Draw(img)
    draw.rectangle((10, 10, 150, 80), outline=(40, 90, 160), width=3)
    draw.text((35, 38), "Curve", fill=(20, 20, 20))
    img.save(path)


def test_save_knowledge_html_embeds_selected_image_as_data_uri(temp_dir):
    image_path = os.path.join(temp_dir, "curve.png")
    _create_image(image_path)

    output = os.path.join(temp_dir, "知识清单.html")
    save_knowledge_html(
        '<h2>图表讲解</h2>{{EMBEDDED_IMAGES}}<p>正文说明。</p>',
        output,
        '测试章节',
        embedded_images=[
            {
                'path': 'curve.png',
                'caption': '训练曲线',
                'reason': '用于对照曲线变化',
            }
        ],
    )

    html = open(output, encoding='utf-8').read()
    assert 'data:image/png;base64,' in html
    assert 'src="curve.png"' not in html
    assert '训练曲线' in html
    assert '用于对照曲线变化' in html


def test_generate_cached_persists_and_embeds_images(temp_dir):
    image_path = os.path.join(temp_dir, "curve.png")
    _create_image(image_path)

    embedded_images = [{'id': 'img_001', 'path': 'curve.png', 'caption': '训练曲线'}]
    save_cache(
        temp_dir,
        '<h2>核心知识</h2><p>先解释曲线含义。</p>{{IMAGE:img_001}}<p>再推导公式。</p>',
        [],
        embedded_images=embedded_images,
    )
    cache = load_cache(temp_dir)

    assert cache['embedded_images'] == embedded_images

    generate(
        temp_dir,
        cache['knowledge_body'],
        cache['questions'],
        '测试章节',
        embedded_images=cache['embedded_images'],
    )

    html = open(os.path.join(temp_dir, '知识清单.html'), encoding='utf-8').read()
    assert 'data:image/png;base64,' in html
    assert '训练曲线' in html
    assert 'data-image-id="img_001"' in html


def test_save_knowledge_html_does_not_auto_create_image_section(temp_dir):
    image_path = os.path.join(temp_dir, "curve.png")
    _create_image(image_path)

    output = os.path.join(temp_dir, "知识清单.html")
    save_knowledge_html(
        '<h2>核心知识</h2><p>正文没有图片占位符。</p>',
        output,
        '测试章节',
        embedded_images=[{'id': 'img_001', 'path': 'curve.png', 'caption': '训练曲线'}],
    )

    html = open(output, encoding='utf-8').read()
    assert 'data:image/png;base64,' not in html
    assert '关键原图对照' not in html


def test_save_knowledge_html_embeds_image_inline_by_id(temp_dir):
    image_path = os.path.join(temp_dir, "curve.png")
    _create_image(image_path)

    output = os.path.join(temp_dir, "知识清单.html")
    save_knowledge_html(
        '<h2>学习曲线</h2><p>先讲训练误差。</p>{{IMAGE:img_001}}<p>再讲泛化误差。</p>',
        output,
        '测试章节',
        embedded_images=[
            {
                'id': 'img_001',
                'path': 'curve.png',
                'caption': '训练曲线',
                'reason': '这一张图必须和误差公式放在一起理解',
            }
        ],
    )

    html = open(output, encoding='utf-8').read()
    assert 'data:image/png;base64,' in html
    assert 'data-image-id="img_001"' in html
    assert html.index('先讲训练误差') < html.index('data:image/png;base64,') < html.index('再讲泛化误差')


def test_generate_cached_persists_wrong_answer_prompt(temp_dir):
    prompt = "请按错因分类，并补全每道错题涉及的推导链条。"
    save_cache(
        temp_dir,
        '<h2>核心知识</h2><p>内容。</p>',
        [],
        wrong_answer_analysis_prompt=prompt,
        title='测试章节',
    )
    cache = load_cache(temp_dir)

    assert cache['wrong_answer_analysis_prompt'] == prompt

    generate(
        temp_dir,
        cache['knowledge_body'],
        cache['questions'],
        cache['title'],
        wrong_answer_analysis_prompt=cache['wrong_answer_analysis_prompt'],
    )

    html = open(os.path.join(temp_dir, '章节测试.html'), encoding='utf-8').read()
    assert prompt in html
    assert 'wrong-review-box' in html


def test_run_exampass_writes_image_candidates(temp_dir):
    pptx_path = os.path.join(temp_dir, "lecture.pptx")
    create_sample_pptx(pptx_path, include_image=True, include_table=False)

    run_exampass(temp_dir)

    bundle_path = os.path.join(temp_dir, '_extraction_bundle.json')
    bundle = json.load(open(bundle_path, encoding='utf-8'))
    candidates = bundle['image_candidates']

    assert candidates
    assert candidates[0]['id'] == 'img_001'
    assert candidates[0]['source_file'] == 'lecture.pptx'
    assert candidates[0]['path'].startswith('_exampass_images/')
    assert os.path.exists(os.path.join(temp_dir, candidates[0]['path']))
