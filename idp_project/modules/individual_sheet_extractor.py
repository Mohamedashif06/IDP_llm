from concurrent.futures import ThreadPoolExecutor
from collections.abc import Mapping

from modules.cycle_test_schema import empty_record
from modules.ocr_router import read_cell
from modules.preprocessing import correct_document
from modules.template_config import DEFAULT_TEMPLATE
from modules.cnn_digit_recognizer import load_digit_model, predict_digit
from pathlib import Path


REGIONS = DEFAULT_TEMPLATE.regions

MARK_FIELDS = [
    "q1", "q2", "q3", "q4", "q5",
    "6_a_i", "6_a_ii", "6_b_i", "6_b_ii",
    "7_a_i", "7_a_ii", "7_b_i", "7_b_ii",
    "8_a_i", "8_a_ii", "8_b_i", "8_b_ii", "total_50",
]


def crop_region(image, region):
    height, width = image.shape[:2]
    x1, y1, x2, y2 = region
    return image[
        int(y1 * height):int(y2 * height),
        int(x1 * width):int(x2 * width),
    ]


def read_text_region(image, mode="text"):
    result = read_cell(image, mode)
    return result.get("text", ""), result.get("confidence", 0.0)


_CNN_MODEL = None
_CNN_READY = False


def _get_cnn_model():
    global _CNN_MODEL, _CNN_READY
    if not _CNN_READY:
        _CNN_READY = True
        try:
            _CNN_MODEL = load_digit_model(Path(__file__).with_name("digit_cnn_weights.pt"))
        except Exception:
            _CNN_MODEL = None
    return _CNN_MODEL


def _read_mark(image, field):
    crop = crop_region(image, REGIONS[field])
    text, confidence = read_text_region(crop, "digits")
    # A CNN specialises in one handwritten digit. It is a second opinion,
    # not a replacement for OCR on multi-digit marks or blank cells.
    cnn = predict_digit(_get_cnn_model(), crop)
    if cnn["confidence"] >= 92 and (not text or cnn["confidence"] > confidence):
        text, confidence = cnn["digit"], cnn["confidence"]
    return field, text, confidence


def extract_student_sheet(image, roster: Mapping[str, str] | None = None):
    record = empty_record()
    warnings = []
    confidence = {}

    if image is None:
        return {"record": record, "confidence": {}, "warnings": ["No image supplied"]}

    try:
        image = correct_document(image)
    except Exception:
        warnings.append("Document alignment fallback used")

    crop = crop_region(image, REGIONS["roll_no"])
    record["roll_no"], confidence["roll_no"] = read_text_region(crop, "alnum")

    crop = crop_region(image, REGIONS["registration_no"])
    record["registration_no"], confidence["registration_no"] = read_text_region(
        crop,
        "alnum",
    )

    if roster and record["roll_no"] in roster:
        record["name"] = roster[record["roll_no"]]
    elif record["roll_no"]:
        warnings.append(f"No roster entry for roll number {record['roll_no']}")

    with ThreadPoolExecutor(max_workers=8) as pool:
        results = list(pool.map(lambda field: _read_mark(image, field), MARK_FIELDS))

    for field, text, score in results:
        record[field] = text
        confidence[field] = score

    for field in MARK_FIELDS:
        value = record[field]
        if not value:
            warnings.append(f"{field}: missing")
            continue
        try:
            number = int(value)
        except ValueError:
            warnings.append(f"{field}: invalid value '{value}'")
            continue
        if number < 0 or number > 20:
            warnings.append(f"{field}: suspicious mark {number}")

    try:
        mark_sum = sum(int(record[field]) for field in MARK_FIELDS[:-1])
        reported_total = int(record["total_50"])
        if reported_total != mark_sum:
            warnings.append(
                f"Total mismatch: OCR total={reported_total}, calculated={mark_sum}"
            )
        record["total_100"] = str(reported_total * 2)
    except (TypeError, ValueError):
        warnings.append("Total 50 could not be read")

    return {"record": record, "confidence": confidence, "warnings": warnings}
