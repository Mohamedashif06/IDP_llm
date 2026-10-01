"""Gemini Vision extraction for arbitrary documents with dynamic fields."""

from __future__ import annotations

import json
import re
import time
from modules.field_normalizer import canonicalize_fields

# Standard Google AI Studio free-tier model (1,500 free requests/day)
GEMINI_MODEL = "gemini-3.6-flash"

EXTRACTION_PROMPT = """Read this document carefully. Extract every visible
field and table value. Do not assume it is a marksheet or use fixed field
names. Use the exact printed label as the key, normalized to snake_case.
For tables, use a list of row objects under `tables`; preserve headers and
values. Return JSON only with this shape:
{
  "fields": {"any_detected_label": "value"},
  "tables": [{"title": "table title or table_1", "rows": [{"column": "value"}]}],
  "text": "complete readable document text",
  "needs_review": ["only values that are unclear or unreadable"]
}
If this is an internal assessment sheet, also return a `co_row` object. Put
the student identifiers and marks in one flat record using these standard
keys when present: registration_no, roll_no, name, q1 through q5, 6_a_i,
6_a_ii, 6_b_i, 6_b_ii, 7_a_i, 7_a_ii, 7_b_i, 7_b_ii, 8_a_i, 8_a_ii,
8_b_i, 8_b_ii, total_50, total_100. Question 1 and Q1 mean the same thing.
Never invent a value. Use an empty string and add it to needs_review if unclear."""


def _repair_and_parse_json(text: str) -> dict:
    """Bulletproof JSON parser with fallback repair strategies for VLM responses."""
    if not text:
        return {}

    # Strip code block fences
    cleaned = re.sub(r"^```(?:json)?\s*", "", text.strip(), flags=re.I)
    cleaned = re.sub(r"\s*```$", "", cleaned, flags=re.I).strip()

    # Find boundaries of JSON object
    start = cleaned.find("{")
    end = cleaned.rfind("}")
    candidate = cleaned[start : end + 1] if start >= 0 and end >= start else cleaned

    # Strategy 1: Standard json.loads
    try:
        return json.loads(candidate)
    except (TypeError, json.JSONDecodeError):
        pass

    # Strategy 2: json_repair library (if installed)
    try:
        import json_repair
        repaired = json_repair.loads(candidate or text)
        if isinstance(repaired, dict):
            return repaired
    except Exception:
        pass

    # Strategy 3: Attempt simple truncation repair (balancing unclosed braces/quotes)
    trancated_candidate = candidate
    if start >= 0:
        trancated_candidate = cleaned[start:]
        if trancated_candidate.count('"') % 2 != 0:
            trancated_candidate += '"'
        open_braces = trancated_candidate.count("{") - trancated_candidate.count("}")
        trancated_candidate += "}" * max(0, open_braces)
        try:
            return json.loads(trancated_candidate)
        except json.JSONDecodeError:
            pass

    # Strategy 4: Fallback field extraction using Regex
    extracted_fields = {}
    for match in re.finditer(r'"([^"\\]+)":\s*"([^"\\]*)"', text):
        k, v = match.group(1), match.group(2)
        if k not in ("fields", "tables", "text", "needs_review", "co_row", "title"):
            extracted_fields[k] = v

    return {
        "fields": extracted_fields,
        "tables": [],
        "text": text,
        "needs_review": ["Extracted text with fallback JSON parser"],
    }


def extract_with_gemini(
    file_bytes: bytes,
    mime_type: str,
    source_name: str,
    api_key: str,
    model: str = GEMINI_MODEL,
) -> dict:
    """Call Gemini Flash and normalise its structured result for the app."""
    try:
        from google import genai
        from google.genai import types
    except ImportError as error:
        raise RuntimeError("Install google-genai first: pip install google-genai") from error

    client = genai.Client(api_key=api_key)

    # Sequence of models to try if the requested model experiences 503 UNAVAILABLE or 404 NOT_FOUND
    models_to_try = [model]
    if model != "gemini-3.1-flash-lite":
        models_to_try.append("gemini-3.1-flash-lite")
    if model != "gemini-3.6-flash" and "gemini-3.6-flash" not in models_to_try:
        models_to_try.append("gemini-3.6-flash")

    last_error = None
    response = None
    used_model = model

    for current_model in models_to_try:
        # Allow retry attempt on 503 high demand spikes
        for attempt in range(2):
            try:
                response = client.models.generate_content(
                    model=current_model,
                    contents=[
                        types.Part.from_bytes(data=file_bytes, mime_type=mime_type or "image/jpeg"),
                        EXTRACTION_PROMPT,
                    ],
                    config=types.GenerateContentConfig(
                        response_mime_type="application/json",
                        temperature=0.1,
                        max_output_tokens=8192,
                    ),
                )
                used_model = current_model
                break
            except Exception as error:
                last_error = error
                err_msg = str(error)
                # If 503 UNAVAILABLE or 404 NOT_FOUND or high demand spike, retry or fallback
                is_temporary = any(
                    token in err_msg
                    for token in (
                        "503",
                        "UNAVAILABLE",
                        "high demand",
                        "404",
                        "NOT_FOUND",
                        "no longer available",
                        "ServerOverloaded",
                    )
                )
                if is_temporary:
                    time.sleep(1.0)
                    continue
                if "429" in err_msg or "RESOURCE_EXHAUSTED" in err_msg or "Quota exceeded" in err_msg:
                    raise RuntimeError(
                        "Gemini API rate limit reached (15 requests/minute). Please wait 30 seconds and try again."
                    ) from error
                if "API_KEY_INVALID" in err_msg or "API key not valid" in err_msg:
                    raise RuntimeError("Invalid Google AI Studio API key. Please check your key in sidebar.") from error
                raise RuntimeError(f"Gemini API error ({type(error).__name__}): {error}") from error
        if response is not None:
            break

    if response is None:
        raise RuntimeError(
            f"Google AI Studio server is temporarily busy (503 High Demand). Please click Extract document again in a few seconds. Details: {last_error}"
        )

    payload = getattr(response, "parsed", None)
    if not isinstance(payload, dict):
        raw_text = str(getattr(response, "text", "") or "").strip()
        payload = _repair_and_parse_json(raw_text)

    fields = payload.get("fields", {})
    if not isinstance(fields, dict):
        fields = {}
    fields = canonicalize_fields(fields)

    return {
        "source": source_name,
        "page_count": 1,
        "engine": used_model,
        "confidence": "review needs_review",
        "fields": fields,
        "tables": payload.get("tables", []) if isinstance(payload.get("tables"), list) else [],
        "co_row": payload.get("co_row", {}) if isinstance(payload.get("co_row"), dict) else {},
        "text": payload.get("text", "") or "",
        "needs_review": payload.get("needs_review", []) if isinstance(payload.get("needs_review"), list) else [],
        "pages": [],
    }
