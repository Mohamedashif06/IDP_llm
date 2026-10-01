"""Unified Document Processor.

Handles multi-format ingestion (Photos/scans, PDFs, DOCX, XLSX),
routes images to local Qwen VLM, and routes digital files to direct readers.
"""

from __future__ import annotations

import os
from pathlib import Path
from typing import Any, Dict, List

from modules.direct_file_reader import read_docx, read_xlsx
from modules.document_extractor import image_file_to_array, pdf_to_images
from modules.qwen_ollama_extractor import extract_with_qwen


def process_uploaded_file(
    file_path: str | Path,
    file_bytes: bytes = None,
    engine: str = "qwen_ollama",
    forced_type: str = None
) -> List[Dict[str, Any]]:
    """Process any uploaded file and return a list of page/record dicts."""
    file_path_str = str(file_path)
    suffix = Path(file_path_str).suffix.lower()

    # 1. Digital Word Documents (.docx)
    if suffix == ".docx":
        record = read_docx(file_bytes or file_path_str)
        record["source"] = Path(file_path_str).name
        return [record]

    # 2. Digital Excel Spreadsheets (.xlsx)
    if suffix == ".xlsx":
        record = read_xlsx(file_bytes or file_path_str)
        record["source"] = Path(file_path_str).name
        return [record]

    # 3. PDF Documents (.pdf)
    if suffix == ".pdf":
        images = pdf_to_images(file_path_str)
        records = []
        for idx, img in enumerate(images, start=1):
            src_name = f"{Path(file_path_str).name}_page_{idx}"
            if engine == "qwen_ollama":
                rec = extract_with_qwen(img, source_name=src_name, forced_type=forced_type)
            else:
                from modules.document_extractor import extract_page
                rec = extract_page(img, page_number=idx)
                rec["document_type"] = "other"
                rec["reliability"] = "standard"
            records.append(rec)
        return records

    # 4. Images (JPG, PNG, WEBP, TIFF)
    image_arr = image_file_to_array(file_path_str)
    if engine == "qwen_ollama":
        rec = extract_with_qwen(image_arr, source_name=Path(file_path_str).name, forced_type=forced_type)
    else:
        from modules.document_extractor import extract_page
        rec = extract_page(image_arr, page_number=1)
        rec["document_type"] = "other"
        rec["reliability"] = "standard"
    return [rec]
