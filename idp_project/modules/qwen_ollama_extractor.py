"""Local Qwen Vision-Language Model Extractor served via Ollama API.

Performs Classify-then-Extract pipeline:
1. Classification: Qwen VLM predicts type and confidence.
2. Routing: Tau threshold check selects TEMPLATES schema or GENERIC fallback.
3. Extraction: Qwen VLM extracts schema fields with JSON safety & retry.
4. Flagging: Blank-aware confidence review rule flags uncertain fields.
"""

from __future__ import annotations

import base64
import io
import json
import re
import urllib.request
import urllib.error
from typing import Any, Dict, Tuple
from PIL import Image

from modules.template_config import TEMPLATES, GENERIC_SCHEMA
from modules.field_normalizer import canonicalize_fields

OLLAMA_ENDPOINT = "http://localhost:11434/api/generate"
DEFAULT_MODEL = "qwen2.5-vl:7b"
TAU_THRESHOLD = 0.60
THETA_DEFAULT = 0.70
THETA_GENERIC = 0.85


CLASSIFICATION_PROMPT = """Classify this document page. Return ONLY JSON:
{"type": "mark_sheet" | "certificate" | "invoice" | "id_card" | "attendance_register" | "other", "confidence": 0.0 to 1.0}.
If unsure or unrecognized, choose "other"."""


EXTRACTION_PROMPT_TEMPLATE = """You are a structured document extraction system. Read the attached document image and return ONLY a JSON object matching this target schema:
{schema_json}

Instructions:
1. Return valid JSON only. Do NOT include markdown code block fences (like ```json).
2. If a field is blank, unreadable, or missing in the document, set its value to null.
3. Provide a 'confidence' float between 0.0 and 1.0 for each extracted field.
4. Do NOT fabricate or guess missing values.
"""


def _image_to_base64(image_input: Any) -> str:
    """Convert numpy array, PIL Image, or raw bytes to Base64 string."""
    if isinstance(image_input, bytes):
        return base64.b64encode(image_input).decode("utf-8")
    elif hasattr(image_input, "save"): # PIL Image
        buffer = io.BytesIO()
        image_input.save(buffer, format="JPEG")
        return base64.b64encode(buffer.getvalue()).decode("utf-8")
    else: # Numpy array (BGR or RGB)
        import cv2
        if image_input.ndim == 3 and image_input.shape[2] == 3:
            _, buffer = cv2.imencode(".jpg", image_input)
            return base64.b64encode(buffer.tobytes()).decode("utf-8")
        buffer = io.BytesIO()
        Image.fromarray(image_input).save(buffer, format="JPEG")
        return base64.b64encode(buffer.getvalue()).decode("utf-8")


def _call_ollama(prompt: str, image_b64: str, model: str = DEFAULT_MODEL, format_schema: dict = None) -> str:
    """Send request to local Ollama API."""
    payload: Dict[str, Any] = {
        "model": model,
        "prompt": prompt,
        "images": [image_b64],
        "stream": False,
        "options": {
            "temperature": 0.0
        }
    }
    if format_schema:
        payload["format"] = format_schema

    data = json.dumps(payload).encode("utf-8")
    req = urllib.request.Request(OLLAMA_ENDPOINT, data=data, headers={"Content-Type": "application/json"})

    try:
        with urllib.request.urlopen(req, timeout=45) as response:
            res_json = json.loads(response.read().decode("utf-8"))
            return res_json.get("response", "")
    except urllib.error.URLError as e:
        raise RuntimeError(f"Ollama server not reachable at {OLLAMA_ENDPOINT}. Error: {e}")


def _repair_and_parse_json(raw_text: str) -> Dict[str, Any]:
    """Strip fences and parse JSON with fallback strategies."""
    if not raw_text:
        return {}

    cleaned = re.sub(r"^```(?:json)?\s*", "", raw_text.strip(), flags=re.I)
    cleaned = re.sub(r"\s*```$", "", cleaned, flags=re.I).strip()

    start = cleaned.find("{")
    end = cleaned.rfind("}")
    candidate = cleaned[start : end + 1] if start >= 0 and end >= start else cleaned

    try:
        return json.loads(candidate)
    except json.JSONDecodeError:
        pass

    try:
        import json_repair
        repaired = json_repair.loads(candidate or raw_text)
        if isinstance(repaired, dict):
            return repaired
    except Exception:
        pass

    # Regex extraction fallback
    extracted = {}
    for m in re.finditer(r'"([^"\\]+)":\s*("([^"\\]*)"|null|\d+(?:\.\d+)?)', raw_text):
        key = m.group(1)
        val = m.group(3) if m.group(3) is not None else m.group(2)
        if val == "null":
            val = None
        extracted[key] = val
    return extracted


def classify_document(image_input: Any, model: str = DEFAULT_MODEL) -> Tuple[str, float]:
    """Classify document type using Qwen VLM."""
    image_b64 = _image_to_base64(image_input)
    try:
        response_text = _call_ollama(CLASSIFICATION_PROMPT, image_b64, model=model)
        parsed = _repair_and_parse_json(response_text)
        doc_type = str(parsed.get("type", "other")).lower().strip()
        confidence = float(parsed.get("confidence", 0.70))
        if doc_type not in TEMPLATES:
            doc_type = "other"
        return doc_type, confidence
    except Exception:
        return "other", 0.50


def extract_with_qwen(
    image_input: Any,
    source_name: str = "document.jpg",
    model: str = DEFAULT_MODEL,
    forced_type: str = None
) -> Dict[str, Any]:
    """Full Classify-then-Extract pipeline using local Qwen VLM."""
    image_b64 = _image_to_base64(image_input)

    # Step 1: Classification
    if forced_type and forced_type in TEMPLATES:
        predicted_type, cls_conf = forced_type, 1.0
    else:
        predicted_type, cls_conf = classify_document(image_input, model=model)

    # Step 2: Routing with Tau threshold
    if cls_conf >= TAU_THRESHOLD and predicted_type in TEMPLATES and predicted_type != "other":
        effective_type = predicted_type
        target_schema = TEMPLATES[effective_type]
        reliability = "high"
        theta_t = THETA_DEFAULT
    else:
        effective_type = "other"
        target_schema = GENERIC_SCHEMA
        reliability = "low (GENERIC fallback)"
        theta_t = THETA_GENERIC

    # Step 3: Schema-constrained extraction
    prompt = EXTRACTION_PROMPT_TEMPLATE.format(schema_json=json.dumps(target_schema, indent=2))
    raw_response = ""
    try:
        raw_response = _call_ollama(prompt, image_b64, model=model)
        parsed_data = _repair_and_parse_json(raw_response)
    except Exception as err:
        parsed_data = {
            "notes": f"Extraction error: {err}",
            "needs_review": True
        }

    # Step 4: Extract fields & apply blank-aware confidence review rule
    fields: Dict[str, Any] = {}
    field_confidences: Dict[str, float] = {}
    needs_review_fields: List[str] = []
    tables_data: List[Dict[str, Any]] = []

    # Flatten extracted keys
    for k, v in parsed_data.items():
        if k in ("notes", "needs_review", "key_value_pairs", "tables", "marks_table", "line_items", "attendance_grid"):
            continue
        val = None
        conf = 0.85
        if isinstance(v, dict):
            val = v.get("value")
            conf = float(v.get("confidence", 0.85))
        else:
            val = v
            conf = 0.85 if val is not None else 0.0

        fields[k] = val
        field_confidences[k] = conf

        # Confidence & blank-aware review rule: Eq. (2)
        # review(f) = 1 if c(f) < theta_t or value(f) is null
        if val is None or str(val).strip() == "" or conf < theta_t:
            needs_review_fields.append(k)

    # Extract tables if present
    for tk in ("marks_table", "line_items", "attendance_grid", "tables"):
        if tk in parsed_data and isinstance(parsed_data[tk], list):
            tables_data.append({
                "table_name": tk,
                "rows": parsed_data[tk]
            })

    if effective_type == "other" and "key_value_pairs" in parsed_data:
        kv_list = parsed_data.get("key_value_pairs", [])
        for item in kv_list:
            if isinstance(item, dict):
                k = item.get("key", "")
                v = item.get("value")
                c = float(item.get("confidence", 0.70))
                if k:
                    norm_k = re.sub(r"\s+", "_", k.lower())
                    fields[norm_k] = v
                    field_confidences[norm_k] = c
                    if v is None or str(v).strip() == "" or c < theta_t:
                        needs_review_fields.append(norm_k)

    fields = canonicalize_fields(fields)

    return {
        "source": source_name,
        "page_count": 1,
        "engine": f"Qwen VLM ({model} via Ollama)",
        "document_type": effective_type,
        "classification_confidence": cls_conf,
        "reliability": reliability,
        "confidence": round(sum(field_confidences.values()) / max(len(field_confidences), 1), 2),
        "fields": fields,
        "field_confidences": field_confidences,
        "tables": tables_data,
        "text": raw_response,
        "needs_review": needs_review_fields,
        "pages": []
    }
