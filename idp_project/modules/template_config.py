"""TEMPLATES Registry for Document Types and Schemas."""

from typing import Any, Dict

TEMPLATES: Dict[str, Dict[str, Any]] = {
    "mark_sheet": {
        "roll_number": "string",
        "register_number": "string",
        "student_name": "string",
        "course_code_name": "string",
        "year_semester": "string",
        "date_session": "string",
        "pages_used": "string",
        "examiner_signature": "string",
        "grand_total_words": "string",
        "marks_table": [
            {"question": "string", "marks": "number"}
        ]
    },
    "certificate": {
        "holder_name": "string",
        "certificate_number": "string",
        "issuing_body": "string",
        "course_exam_title": "string",
        "date_of_issue": "string",
        "grade_or_class": "string"
    },
    "invoice": {
        "invoice_number": "string",
        "invoice_date": "string",
        "vendor_name": "string",
        "buyer_name": "string",
        "tax_id": "string",
        "subtotal": "number",
        "tax_amount": "number",
        "total_amount": "number",
        "line_items": [
            {"description": "string", "quantity": "number", "unit_price": "number", "amount": "number"}
        ]
    },
    "id_card": {
        "holder_name": "string",
        "id_number": "string",
        "date_of_birth": "string",
        "department_role": "string",
        "valid_until": "string",
        "issuing_authority": "string"
    },
    "attendance_register": {
        "class_department": "string",
        "month_year": "string",
        "staff_name": "string",
        "total_students": "number",
        "staff_signature": "string",
        "attendance_grid": [
            {"student_name": "string", "roll_no": "string", "days_present": "number"}
        ]
    }
}

GENERIC_SCHEMA: Dict[str, Any] = {
    "notes": "string",
    "needs_review": True,
    "key_value_pairs": [
        {"key": "string", "value": "string", "confidence": 0.8}
    ],
    "tables": [
        {"table_name": "string", "headers": ["string"], "rows": [["string"]]}
    ]
}
