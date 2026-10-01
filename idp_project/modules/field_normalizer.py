"""Canonical field names while preserving arbitrary document fields."""

import re


_ALIASES = {
    "grandtotal": "total", "totalamount": "total", "nettotal": "total",
    "rollno": "roll_no", "rollnumber": "roll_no",
    "registrationno": "registration_no", "registerno": "registration_no",
    "studentname": "name", "fullname": "name", "customername": "name",
    "billno": "bill_number", "billnumber": "bill_number",
    "invoiceno": "invoice_number", "invoicenumber": "invoice_number",
    "phoneno": "phone", "mobileno": "mobile",
}


def canonical_field_name(label) -> str:
    """Map recognised synonyms, otherwise retain a clean dynamic label."""
    raw = str(label).strip().lower()
    compact = "".join(character for character in raw if character.isalnum())
    if compact in _ALIASES:
        return _ALIASES[compact]
    question = re.fullmatch(r"(?:question|q)(\d+)", compact)
    if question:
        return f"q{question.group(1)}"
    clean = re.sub(r"[^a-z0-9]+", "_", raw).strip("_")
    return clean or "unlabelled_field"


def canonicalize_fields(fields: dict) -> dict:
    """Keep first value for a canonical field; retain conflicting values."""
    result = {}
    for label, value in fields.items():
        key = canonical_field_name(label)
        if key not in result or not result[key]:
            result[key] = value
        elif value and str(value) != str(result[key]):
            suffix = 2
            while f"{key}_{suffix}" in result:
                suffix += 1
            result[f"{key}_{suffix}"] = value
    return result
