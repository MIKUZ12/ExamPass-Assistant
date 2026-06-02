"""Fast ExamPass generator with content caching.

First run (Claude analyzes): python generate_cached.py <dir> --build
    Reads _extraction_bundle.json, Claude creates _exam_cache.json, generates HTML.

Subsequent runs (instant): python generate_cached.py <dir>
    Reads _exam_cache.json, generates HTML in <1 second.

Force rebuild: python generate_cached.py <dir> --force
"""

import sys, os, json

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from template_engine import save_knowledge_html, save_test


def load_cache(directory):
    path = os.path.join(directory, '_exam_cache.json')
    if os.path.exists(path):
        with open(path, 'r', encoding='utf-8') as f:
            return json.load(f)
    return None


def save_cache(directory, knowledge_body, questions, embedded_images=None,
               wrong_answer_analysis_prompt='', **extra_cache):
    path = os.path.join(directory, '_exam_cache.json')
    cache = {
        'knowledge_body': knowledge_body,
        'questions': questions,
    }
    if embedded_images:
        cache['embedded_images'] = embedded_images
    if wrong_answer_analysis_prompt:
        cache['wrong_answer_analysis_prompt'] = wrong_answer_analysis_prompt
    cache.update(extra_cache)
    with open(path, 'w', encoding='utf-8') as f:
        json.dump(cache, f, ensure_ascii=False)


def generate(directory, knowledge_body, questions, title, subtitle='', duration=30,
             embedded_images=None, wrong_answer_analysis_prompt=''):
    """Generate both HTML files from content."""
    save_knowledge_html(
        knowledge_body,
        os.path.join(directory, '知识清单.html'),
        title,
        embedded_images=embedded_images,
    )
    save_test(
        questions,
        os.path.join(directory, '章节测试.html'),
        title, subtitle, duration_minutes=duration,
        wrong_answer_analysis_prompt=wrong_answer_analysis_prompt,
    )


def print_status(directory):
    for f in ['知识清单.html', '章节测试.html']:
        path = os.path.join(directory, f)
        if os.path.exists(path):
            print(f'  {f}: {os.path.getsize(path)/1024:.1f} KB')
        else:
            print(f'  {f}: MISSING')


if __name__ == '__main__':
    import argparse
    p = argparse.ArgumentParser()
    p.add_argument('directory')
    p.add_argument('--build', action='store_true', help='Build cache from extraction bundle')
    p.add_argument('--force', action='store_true', help='Force rebuild even if cache exists')
    args = p.parse_args()

    directory = os.path.abspath(args.directory)

    if args.force or args.build:
        # Load extraction bundle for Claude analysis
        bundle_path = os.path.join(directory, '_extraction_bundle.json')
        if not os.path.exists(bundle_path):
            # Try running extraction first
            print('Extraction bundle not found. Run:')
            print(f'  python run_exampass.py "{directory}"')
            sys.exit(1)

        with open(bundle_path, 'r', encoding='utf-8') as f:
            bundle = json.load(f)

        print(f'Loaded {len(bundle.get("merged_text",""))} chars of content.')
        print()
        print('=== STEP: Claude Analysis Required ===')
        print('Read _extraction_bundle.json, then build:')
        print('  knowledge_body = "<h2>...</h2>..."  (HTML with H2/H3/p/table/blockquote)')
        print('  questions = [{type:"choice",...}, ...]  (28 questions)')
        print('  embedded_images = [{path:"_exampass_images/...", caption:"...", reason:"..."}]  (optional important images)')
        print('  wrong_answer_analysis_prompt = "..."  (optional custom prompt for wrong-question review)')
        print()
        print('Then call:')
        print(f'  from generate_cached import save_cache, generate')
        print(f'  save_cache(directory, knowledge_body, questions, embedded_images=embedded_images, wrong_answer_analysis_prompt=wrong_answer_analysis_prompt)')
        print(f'  generate(directory, knowledge_body, questions, title, subtitle, duration=30, embedded_images=embedded_images, wrong_answer_analysis_prompt=wrong_answer_analysis_prompt)')
        sys.exit(0)

    # Fast path: use cached content
    cache = load_cache(directory)
    if cache:
        print('Cache found. Generating HTML...')
        title = cache.get('title') or os.path.basename(directory)
        generate(directory, cache['knowledge_body'], cache['questions'], title,
                 subtitle='满分 100 分', duration=30,
                 embedded_images=cache.get('embedded_images'),
                 wrong_answer_analysis_prompt=cache.get('wrong_answer_analysis_prompt', ''))
        print('Done.')
        print_status(directory)
    else:
        print('No cache found. Run with --build first to create cache.')
        print(f'  python generate_cached.py "{directory}" --build')
