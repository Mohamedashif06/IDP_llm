"""Template-free OCR extraction for images and PDF pages.

The result deliberately keeps the raw OCR evidence.  This makes it useful for
marksheets, invoices, forms and arbitrary documents without inventing missing
``q1``/``q2`` fields from a marksheet template.
"""

from __future__ import annotations

import re
from pathlib import Path

import cv2
import numpy as np
import pytesseract
from PIL import Image

from modules.preprocessing import correct_document, resize_for_speed
from modules.field_normalizer import canonicalize_fields


def pdf_to_images(pdf_path: str | Path) -> list[np.ndarray]:
    """Render a PDF locally. PyMuPDF is optional so image uploads still work."""
    try:
        import fitz  # PyMuPDF
    except ImportError as error:
        raise RuntimeError("PDF support needs PyMuPDF. Run: pip install PyMuPDF") from error

    document = fitz.open(str(pdf_path))
    try:
        pages = []
        for page in document:
            pixmap = page.get_pixmap(matrix=fitz.Matrix(2, 2), alpha=False)
            image = np.frombuffer(pixmap.samples, dtype=np.uint8).reshape(
                pixmap.height, pixmap.width, 3
            )
            pages.append(cv2.cvtColor(image, cv2.COLOR_RGB2BGR))
        return pages
    finally:
        document.close()


def image_file_to_array(image_path: str | Path) -> np.ndarray:
    with Image.open(image_path) as source:
        return cv2.cvtColor(np.asarray(source.convert("RGB")), cv2.COLOR_RGB2BGR)


def _prepare(image: np.ndarray) -> np.ndarray:
    image = resize_for_speed(image)
    try:
        image = correct_document(image)
    except Exception:
        pass
    gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY) if image.ndim == 3 else image
    return cv2.threshold(gray, 0, 255, cv2.THRESH_BINARY + cv2.THRESH_OTSU)[1]


def _as_float(value) -> float:
    try:
        return float(value)
    except (TypeError, ValueError):
        return 0.0


def _label_value_fields(lines: list[str]) -> dict[str, str]:
    """Find fields without requiring a pre-defined document schema.

    Explicit separators work for any label. A small set of universal labels
    also handles forms printed as `Name John` or `Address` on one line and
    the value on the next. Raw lines and words are retained even when a field
    cannot be inferred safely.
    """
    fields = {}
    label_words = (
        "name|age|gender|sex|place|city|state|country|address|email|phone|mobile|"
        "date|dob|department|designation|company|amount|total|bill|invoice|"
        "number|no|id|code|pin|pincode|quantity|price|description"
    )
    for index, line in enumerate(lines):
        match = re.match(r"^\s*([^:=]{2,60}?)\s*[:=\-]\s*(.+?)\s*$", line)
        if not match:
            match = re.match(rf"^\s*(({label_words})(?:\s+[A-Za-z]+){{0,3}})\s+(.+?)\s*$", line, re.I)
            if match:
                match = (match.group(1), match.group(3))
        if match:
            label_text, value = (match.group(1), match.group(2)) if not isinstance(match, tuple) else match
            label = re.sub(r"\s+", "_", label_text.strip().lower())
            fields[label] = value.strip()
            continue
        # Label and value in vertically adjacent form cells.
        if re.fullmatch(rf"\s*({label_words})(?:\s+[A-Za-z]+){{0,3}}\s*", line, re.I) and index + 1 < len(lines):
            value = lines[index + 1].strip()
            if value and not re.fullmatch(rf"({label_words}).*", value, re.I):
                fields[re.sub(r"\s+", "_", line.strip().lower())] = value
    return canonicalize_fields(fields)


def extract_page(image: np.ndarray, page_number: int = 1, language: str = "eng") -> dict:
    """Extract every recognised word and reconstruct reading-order text."""
    prepared = _prepare(image)
    # Documents vary: psm 6 is stronger on clean forms while psm 11 is often
    # better for receipts, invoices and camera photographs with sparse text.
    candidates = []
    for psm in (6, 11):
        data = pytesseract.image_to_data(
            prepared, lang=language, config=f"--oem 1 --psm {psm}",
            output_type=pytesseract.Output.DICT, timeout=25,
        )
        good_scores = [_as_float(score) for score in data["conf"] if _as_float(score) >= 0]
        token_count = sum(bool(str(value).strip()) for value in data["text"])
        # Prefer a result with both useful coverage and strong OCR confidence.
        quality = (sum(good_scores) / len(good_scores) if good_scores else 0) * min(token_count, 30)
        candidates.append((quality, data))
    data = max(candidates, key=lambda candidate: candidate[0])[1]
    words, grouped = [], {}
    for index, raw_text in enumerate(data["text"]):
        text = str(raw_text).strip()
        confidence = _as_float(data["conf"][index])
        if not text:
            continue
        block = (data["block_num"][index], data["par_num"][index], data["line_num"][index])
        word = {
            "text": text,
            "confidence": round(confidence, 1),
            "bbox": {
                "x": int(data["left"][index]), "y": int(data["top"][index]),
                "width": int(data["width"][index]), "height": int(data["height"][index]),
            },
        }
        words.append(word)
        grouped.setdefault(block, []).append(text)
    lines = [" ".join(parts) for parts in grouped.values()]
    readable = [word["confidence"] for word in words if word["confidence"] >= 0]
    return {
        "page": page_number,
        "text": "\n".join(lines),
        "lines": lines,
        "fields": _label_value_fields(lines),
        "words": words,
        "confidence": round(sum(readable) / len(readable), 1) if readable else 0.0,
    }


def extract_document(images: list[np.ndarray], source_name: str = "document", language: str = "eng") -> dict:
    pages = [extract_page(image, index + 1, language) for index, image in enumerate(images)]
    all_text = "\n\n".join(page["text"] for page in pages)
    fields = {}
    for page in pages:
        for name, value in page["fields"].items():
            fields[name if name not in fields else f"page_{page['page']}_{name}"] = value
    return {
        "source": source_name,
        "page_count": len(pages),
        "text": all_text,
        "fields": fields,
        "pages": pages,
        "engine": "tesseract",
        "confidence": round(sum(page["confidence"] for page in pages) / len(pages), 1) if pages else 0.0,
    }
