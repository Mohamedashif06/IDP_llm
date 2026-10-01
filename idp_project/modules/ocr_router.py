import re

import cv2
import numpy as np
import pytesseract


def clean_text(text):
    if text is None:
        return ""
    text = re.sub(r"\s+", " ", str(text).replace("\n", " "))
    return text.strip()


def clean_digits(text):
    return "".join(character for character in clean_text(text) if character.isdigit())


def clean_alnum(text):
    return re.sub(r"[^A-Za-z0-9]", "", clean_text(text)).upper()


def prepare_image(image, max_side=240):
    if image is None:
        return None
    if not isinstance(image, np.ndarray):
        image = np.asarray(image)
    if image.size == 0:
        return None
    if image.ndim == 3:
        gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
    else:
        gray = image

    height, width = gray.shape[:2]
    longest = max(height, width)
    if longest < 8:
        return None
    if longest < max_side:
        scale = min(3.0, max_side / longest)
        gray = cv2.resize(gray, None, fx=scale, fy=scale, interpolation=cv2.INTER_CUBIC)
    elif longest > max_side:
        scale = max_side / longest
        gray = cv2.resize(gray, None, fx=scale, fy=scale, interpolation=cv2.INTER_AREA)

    gray = cv2.GaussianBlur(gray, (3, 3), 0)
    _, binary = cv2.threshold(gray, 0, 255, cv2.THRESH_BINARY + cv2.THRESH_OTSU)
    return binary


def _format_result(text, confidence, engine, mode, **extra):
    if mode == "digits":
        text = clean_digits(text)
    elif mode == "alnum":
        text = clean_alnum(text)
    result = {
        "text": text,
        "confidence": float(confidence or 0),
        "engine": engine,
    }
    result.update(extra)
    return result


def tesseract_read(image, mode="text"):
    prepared = prepare_image(image)
    if prepared is None:
        return _format_result("", 0, "tesseract", mode)

    config = {
        "digits": "--oem 1 --psm 8 -c tessedit_char_whitelist=0123456789",
        "alnum": (
            "--oem 1 --psm 7 "
            "-c tessedit_char_whitelist=ABCDEFGHIJKLMNOPQRSTUVWXYZ"
            "abcdefghijklmnopqrstuvwxyz0123456789-/"
        ),
    }.get(mode, "--oem 1 --psm 7")

    try:
        data = pytesseract.image_to_data(
            prepared, config=config, timeout=4, output_type=pytesseract.Output.DICT
        )
        tokens = [str(token) for token in data["text"] if str(token).strip()]
        scores = [float(score) for score in data["conf"] if float(score) >= 0]
        text = clean_text(" ".join(tokens))
        if mode == "digits":
            text = clean_digits(text)
        elif mode == "alnum":
            text = clean_alnum(text)
        confidence = sum(scores) / len(scores) if scores and text else 0.0
        return _format_result(text, confidence, "tesseract", mode)
    except Exception as error:
        return _format_result("", 0, "tesseract", mode, error=str(error))


def read_cell(image, mode="text", min_confidence=55.0):
    """Read one cell with Tesseract only.

    PaddleOCR/EasyOCR were previously chained as fallbacks for every cell.
    That loaded two neural OCR models and ran them up to 21 times per sheet,
    which made processing extremely slow. Accuracy review stays in the UI.
    """
    del min_confidence
    return tesseract_read(image, mode)
