"""Type-Split Excel Export Writer.

Generates an auditable workbook with:
1. Summary sheet (S.No, Document Type, Reliability, File Name, Review Count, Mean Confidence).
2. Summary_<type> sheets (one wide sheet per document type present in the batch).
3. Fields sheet (long-format per-field rows with S.No, field, value, confidence, review flag).
4. Table Data sheet (long-format table cells indexed by S.No).
"""

import os
from typing import Any, Dict, List, Sequence
from openpyxl import Workbook, load_workbook
from openpyxl.styles import Alignment, Font, PatternFill

HEADER_FILL = PatternFill("solid", fgColor="D9EAF7")
HEADER_FONT = Font(bold=True)


def document_to_excel(documents: List[Dict[str, Any]] | Dict[str, Any], excel_path: str) -> str:
    """Export a list of extracted document records into a type-split Excel workbook."""
    if isinstance(documents, dict):
        doc_list = [documents]
    else:
        doc_list = documents

    os.makedirs(os.path.dirname(excel_path) or ".", exist_ok=True)
    wb = Workbook()

    # 1. Summary Sheet
    ws_summary = wb.active
    ws_summary.title = "Summary"
    summary_headers = ["S.No", "Document Type", "Reliability", "File Name", "Review Count", "Fields Count", "Mean Confidence"]
    ws_summary.append(summary_headers)

    for col in range(1, len(summary_headers) + 1):
        cell = ws_summary.cell(1, col)
        cell.font = HEADER_FONT
        cell.fill = HEADER_FILL

    # Group documents by type
    docs_by_type: Dict[str, List[Tuple[int, Dict[str, Any]]]] = {}

    # 2. Prepare Fields and Table Data sheets
    ws_fields = wb.create_sheet("Fields")
    ws_fields.append(["S.No", "Document Type", "Field Name", "Value", "Confidence", "Review Flag"])
    for col in range(1, 7):
        cell = ws_fields.cell(1, col)
        cell.font = HEADER_FONT
        cell.fill = HEADER_FILL

    ws_tables = wb.create_sheet("Table Data")
    ws_tables.append(["S.No", "Document Type", "Table Name", "Row No", "Column Name", "Value"])
    for col in range(1, 7):
        cell = ws_tables.cell(1, col)
        cell.font = HEADER_FONT
        cell.fill = HEADER_FILL

    for s_no, doc in enumerate(doc_list, start=1):
        doc_type = str(doc.get("document_type", "other"))
        reliability = str(doc.get("reliability", "high"))
        file_name = str(doc.get("source", f"doc_{s_no}"))
        needs_review = doc.get("needs_review", [])
        review_count = len(needs_review) if isinstance(needs_review, list) else 0
        fields = doc.get("fields", {})
        confidences = doc.get("field_confidences", {})
        mean_conf = doc.get("confidence", 1.0)

        # Summary Row
        ws_summary.append([
            s_no, doc_type, reliability, file_name, review_count, len(fields), mean_conf
        ])

        # Track for type-split sheet
        if doc_type not in docs_by_type:
            docs_by_type[doc_type] = []
        docs_by_type[doc_type].append((s_no, doc))

        # Long format Fields
        for fname, val in fields.items():
            fconf = confidences.get(fname, 0.85) if isinstance(confidences, dict) else 0.85
            is_flagged = "YES" if fname in needs_review or val is None or str(val).strip() == "" else "NO"
            ws_fields.append([s_no, doc_type, fname, str(val) if val is not None else "", fconf, is_flagged])

        # Long format Table Data
        tables = doc.get("tables", [])
        if isinstance(tables, list):
            for t_idx, tbl in enumerate(tables, start=1):
                tname = tbl.get("table_name", f"Table_{t_idx}") if isinstance(tbl, dict) else f"Table_{t_idx}"
                rows = tbl.get("rows", []) if isinstance(tbl, dict) else []
                headers = tbl.get("headers", []) if isinstance(tbl, dict) else []

                for r_idx, row in enumerate(rows, start=1):
                    if isinstance(row, dict):
                        for col_k, col_v in row.items():
                            ws_tables.append([s_no, doc_type, tname, r_idx, col_k, str(col_v)])
                    elif isinstance(row, list):
                        for c_idx, cell_v in enumerate(row, start=0):
                            c_name = headers[c_idx] if c_idx < len(headers) else f"Col_{c_idx+1}"
                            ws_tables.append([s_no, doc_type, tname, r_idx, c_name, str(cell_v)])

    # 3. Build Summary_<type> per-type sheets
    for doc_type, type_docs in docs_by_type.items():
        sheet_title = f"Summary_{doc_type}"[:31]
        ws_type = wb.create_sheet(sheet_title)

        # Collect union of field keys for this document type
        type_field_keys = []
        for _, d in type_docs:
            for k in d.get("fields", {}).keys():
                if k not in type_field_keys:
                    type_field_keys.append(k)

        type_headers = ["S.No", "File Name", "Reliability"] + type_field_keys
        ws_type.append(type_headers)

        for col in range(1, len(type_headers) + 1):
            cell = ws_type.cell(1, col)
            cell.font = HEADER_FONT
            cell.fill = HEADER_FILL

        for s_no, d in type_docs:
            row_vals = [s_no, d.get("source", ""), d.get("reliability", "high")]
            fdict = d.get("fields", {})
            for fk in type_field_keys:
                row_vals.append(str(fdict.get(fk, "") or ""))
            ws_type.append(row_vals)

    # Styling and column width adjustments
    for ws in wb.worksheets:
        ws.freeze_panes = "A2"
        for col in ws.columns:
            col_letter = col[0].column_letter
            max_len = max(len(str(cell.value or "")) for cell in col)
            ws.column_dimensions[col_letter].width = min(max(max_len + 3, 12), 40)

    wb.save(excel_path)
    wb.close()
    return excel_path
