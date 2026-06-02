"""Unified content extractor that dispatches to file-specific extractors."""

import os
from typing import Dict, Any, List, Optional

from extract_pptx import extract_pptx, build_text_summary as pptx_summary
from extract_docx import extract_docx, build_text_summary as docx_summary
from extract_pdf import extract_pdf, build_text_summary as pdf_summary
from image_extractor import extract_from_pptx, extract_from_docx, extract_from_pdf


def extract_file(filepath: str, image_output_dir: Optional[str] = None) -> Dict[str, Any]:
    """
    Extract content from a single file. Dispatches based on extension.
    Returns {'type': str, 'text_summary': str, 'images': [str], 'raw': dict}
    """
    ext = os.path.splitext(filepath)[1].lower()

    extractors = {
        '.pptx': (extract_pptx, pptx_summary, extract_from_pptx),
        '.ppt': (extract_pptx, pptx_summary, extract_from_pptx),
        '.docx': (extract_docx, docx_summary, extract_from_docx),
        '.doc': (extract_docx, docx_summary, extract_from_docx),
        '.pdf': (extract_pdf, pdf_summary, extract_from_pdf),
    }

    if ext not in extractors:
        raise ValueError(f"Unsupported file type: {ext}")

    raw_extractor, summarizer, img_extractor = extractors[ext]

    raw_data = raw_extractor(filepath)
    text_summary = summarizer(raw_data)

    images = []
    if image_output_dir:
        try:
            os.makedirs(image_output_dir, exist_ok=True)
            images = img_extractor(filepath, image_output_dir)
        except Exception:
            pass

    return {
        'type': ext,
        'text_summary': text_summary,
        'images': images,
        'raw': raw_data,
    }


def merge_group_content(extracted: List[Dict[str, Any]]) -> str:
    """
    Merge multiple extracted file contents into a single combined summary.
    Each item in list is from extract_file().
    """
    parts = []
    for item in extracted:
        parts.append(f"\n\n---\n\n{item['text_summary']}")

    return '\n'.join(parts)
