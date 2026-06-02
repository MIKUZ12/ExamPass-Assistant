"""
Single entry-point for /exampass skill.
Usage: python scripts/run_exampass.py <target_directory>

Handles the full pipeline:
  1. Scan & group files
  2. Extract content (text + images)
  3. Save extraction to JSON for Claude analysis
  4. Print instructions for the next step

No inline Python in shell commands needed. All output written to files.
"""

import sys, os, json, re

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from scanner import scan_and_group, get_group_name
from extractor import extract_file, merge_group_content
from utils import safe_filename


def _slide_context(result, image_path):
    """Return lightweight slide context for extracted PPT images."""
    if result.get('type') not in ('.pptx', '.ppt'):
        return {}

    match = re.search(r'slide(\d+)_img', os.path.basename(image_path))
    if not match:
        return {}

    slide_number = int(match.group(1))
    for slide in result.get('raw', {}).get('slides', []):
        if slide.get('number') == slide_number:
            text = slide.get('text') or ''
            return {
                'slide': slide_number,
                'slide_title': slide.get('title', ''),
                'text_preview': text[:180],
            }
    return {'slide': slide_number}


def main(target_dir):
    target = os.path.abspath(target_dir)
    if not os.path.isdir(target):
        print("ERROR: Directory not found:", target)
        sys.exit(1)

    groups = scan_and_group(target)
    if not groups:
        print("No supported files (PPTX/DOCX/PDF) found in", target)
        sys.exit(0)

    print("Found", len(groups), "group(s)\n")

    for folder, files in groups.items():
        group_name = get_group_name(folder, target)
        print("=" * 50)
        print("Processing:", group_name)
        print("Files:", len(files))
        print("=" * 50)

        results = []
        image_candidates = []
        image_root = os.path.join(folder, '_exampass_images')

        for fpath in files:
            fname = os.path.basename(fpath)
            ext = os.path.splitext(fpath)[1].lower()
            print("  Extracting:", fname, "(" + ext + ")")

            stem = safe_filename(os.path.splitext(fname)[0]) or 'source'
            image_output_dir = os.path.join(image_root, stem)
            result = extract_file(fpath, image_output_dir=image_output_dir)
            results.append(result)

            for image_path in result.get('images', []):
                candidate = {
                    'id': 'img_' + str(len(image_candidates) + 1).zfill(3),
                    'source_file': fname,
                    'path': os.path.relpath(image_path, folder),
                    'filename': os.path.basename(image_path),
                }
                candidate.update(_slide_context(result, image_path))
                image_candidates.append(candidate)

            # Save individual extraction text for debugging
            txt_path = os.path.join(folder, fname + '_extracted.txt')
            with open(txt_path, 'w', encoding='utf-8') as f:
                f.write(result['text_summary'])
            print("    Text:", len(result['text_summary']), "chars ->", txt_path)

        merged = merge_group_content(results)

        # Save extraction bundle for Claude analysis
        bundle = {
            'group_name': group_name,
            'folder': folder,
            'merged_text': merged,
            'file_count': len(files),
            'image_candidates': image_candidates,
            'individual_results': [
                {
                    'filename': os.path.basename(f),
                    'text_length': len(r['text_summary']),
                    'image_count': len(r.get('images', [])),
                }
                for f, r in zip(files, results)
            ],
        }
        bundle_path = os.path.join(folder, '_extraction_bundle.json')
        with open(bundle_path, 'w', encoding='utf-8') as f:
            json.dump(bundle, f, ensure_ascii=False)
        print("  Bundle saved:", bundle_path)
        print("  Total merged:", len(merged), "chars")
        print("  Image candidates:", len(image_candidates))
        print()

    print("Done. Extraction complete for", len(groups), "group(s).")
    print()
    print("Next step: Claude reads the _extraction_bundle.json files and runs:")
    print("  from template_engine import save_knowledge_html, save_test")
    print("  save_knowledge_html(body_html, 'path/to/output.html', title)")
    print("  save_test(questions_list, 'path/to/test.html', title, subtitle)")


if __name__ == '__main__':
    if len(sys.argv) < 2:
        print("Usage: python run_exampass.py <target_directory>")
        sys.exit(1)
    main(sys.argv[1])
