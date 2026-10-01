"""Streamlit UI for Multi-Document Privacy-Preserving Intelligent Document Processing."""

import json
import os
import tempfile
from pathlib import Path

import pandas as pd
import streamlit as st

from modules.document_processor import process_uploaded_file
from modules.excel_writer import document_to_excel
from modules.gemini_extractor import extract_with_gemini

OUTPUT_DIR = "output"
OUTPUT_FILE = os.path.join(OUTPUT_DIR, "batch_records.xlsx")
JSON_FILE = os.path.join(OUTPUT_DIR, "last_batch_record.json")
os.makedirs(OUTPUT_DIR, exist_ok=True)


def run_app():
    st.set_page_config(page_title="Multi-Document IDP with Local Qwen VLM", page_icon="📄", layout="wide")
    st.title("A Privacy-Preserving Multi-Document IDP System")
    st.caption("Classifies, extracts, and exports mixed documents (Mark Sheets, Invoices, Certificates, ID Cards, PDFs, Word, Excel) into a type-split Excel workbook.")

    with st.sidebar:
        st.header("Pipeline Configuration")
        engine = st.radio(
            "Extraction Engine",
            ["Local Qwen VLM (Ollama)", "Direct Digital Ingestion (DOCX/XLSX)", "Gemini Vision (Hosted Reference)"],
            index=0
        )
        
        selected_model = "qwen2.5-vl:7b"
        gemini_key = ""
        if "Qwen" in engine:
            selected_model = st.text_input("Ollama Model Tag", "qwen2.5-vl:7b", help="Local open-weight Vision-Language Model served via Ollama.")
            st.caption("🔒 100% Local Inference: No data leaves your machine.")
        elif "Gemini" in engine:
            gemini_key = st.text_input("Google AI Studio API Key", type="password")
            st.caption("🌐 Hosted Reference API")

        st.subheader("Classification & Review Parameters")
        tau_val = st.slider("Classification Tau Gate", 0.0, 1.0, 0.60, 0.05, help="Confidence threshold below which documents fall back to GENERIC schema.")
        theta_val = st.slider("Field Review Threshold (θ)", 0.50, 0.95, 0.70, 0.05, help="Fields with confidence below θ or null values are flagged for human review.")

    uploaded_files = st.file_uploader(
        "Upload photos, scans, PDFs, Word (.docx) or Excel (.xlsx) files",
        type=["png", "jpg", "jpeg", "webp", "tiff", "pdf", "docx", "xlsx"],
        accept_multiple_files=True
    )

    if not uploaded_files:
        st.info("Please upload one or more document files above to begin batch extraction.")
        st.markdown("""
        ### Features Supported:
        - **Automatic Document Classification**: Mark Sheets, Invoices, Certificates, ID Cards, Attendance Registers, or Generic Fallback.
        - **Multi-Format Support**: Camera photos, scanned images, multi-page PDFs, digital Word and Excel files.
        - **Type-Split Workbook**: Exports a clean Summary sheet, per-type sheets (`Summary_mark_sheet`, `Summary_invoice`), long-format `Fields`, and indexed `Table Data`.
        - **Human-in-the-Loop Review**: Automatically flags low-confidence or blank fields before export.
        """)
        return

    st.success(f"{len(uploaded_files)} file(s) selected for processing.")

    if st.button("Process Batch Documents", type="primary", use_container_width=True):
        batch_records = []
        progress_bar = st.progress(0)
        status_text = st.empty()

        for idx, file_item in enumerate(uploaded_files, start=1):
            status_text.text(f"Processing ({idx}/{len(uploaded_files)}): {file_item.name}...")
            suffix = Path(file_item.name).suffix.lower()

            with tempfile.NamedTemporaryFile(delete=False, suffix=suffix) as tmp:
                tmp.write(file_item.getvalue())
                tmp_path = tmp.name

            try:
                if "Gemini" in engine:
                    if not gemini_key:
                        st.error("Please enter your Gemini API key in the sidebar.")
                        return
                    res = extract_with_gemini(file_item.getvalue(), file_item.type or "image/jpeg", file_item.name, gemini_key)
                    res["document_type"] = "mark_sheet" if "co_row" in res and res["co_row"] else "other"
                    res["reliability"] = "hosted API"
                    batch_records.append(res)
                else:
                    engine_code = "qwen_ollama" if "Qwen" in engine else "direct"
                    records = process_uploaded_file(tmp_path, file_bytes=file_item.getvalue(), engine=engine_code)
                    batch_records.extend(records)
            except Exception as err:
                st.error(f"Error processing {file_item.name}: {err}")
            finally:
                if os.path.exists(tmp_path):
                    os.unlink(tmp_path)

            progress_bar.progress(idx / len(uploaded_files))

        status_text.text("Batch processing complete! Generating Excel workbook...")
        
        # Save Outputs
        with open(JSON_FILE, "w", encoding="utf-8") as f:
            json.dump(batch_records, f, indent=2, ensure_ascii=False)

        excel_path = document_to_excel(batch_records, OUTPUT_FILE)
        st.session_state["batch_records"] = batch_records
        st.session_state["excel_path"] = excel_path
        st.session_state["json_path"] = JSON_FILE

    batch_records = st.session_state.get("batch_records")
    if not batch_records:
        return

    st.subheader("Batch Classification & Extraction Results")
    summary_df = pd.DataFrame([
        {
            "S.No": idx + 1,
            "File Name": r.get("source", ""),
            "Document Type": r.get("document_type", "other"),
            "Reliability": r.get("reliability", "high"),
            "Engine": r.get("engine", ""),
            "Review Flagged": len(r.get("needs_review", [])),
            "Mean Confidence": r.get("confidence", 1.0)
        }
        for idx, r in enumerate(batch_records)
    ])
    st.dataframe(summary_df, use_container_width=True)

    # Detailed per-document inspection
    st.subheader("Human-in-the-Loop Field Review")
    doc_options = [f"Doc #{idx+1}: {r.get('source', '')} ({r.get('document_type', '')})" for idx, r in enumerate(batch_records)]
    selected_doc_idx = st.selectbox("Select document to inspect", range(len(doc_options)), format_func=lambda i: doc_options[i])
    selected_doc = batch_records[selected_doc_idx]

    col_left, col_right = st.columns(2)
    with col_left:
        st.markdown(f"**Extracted Fields for `{selected_doc.get('source')}`**")
        fields_df = pd.DataFrame([
            {
                "field": fk,
                "value": fv,
                "confidence": selected_doc.get("field_confidences", {}).get(fk, 0.85),
                "needs_review": "⚠️ YES" if fk in selected_doc.get("needs_review", []) else "✅ OK"
            }
            for fk, fv in selected_doc.get("fields", {}).items()
        ])
        st.data_editor(fields_df, hide_index=True, use_container_width=True)

    with col_right:
        st.markdown("**Flagged Review Items**")
        review_items = selected_doc.get("needs_review", [])
        if review_items:
            st.warning("Fields requiring verification: " + ", ".join(review_items))
        else:
            st.success("All fields passed confidence check and non-blank rule.")

        with st.expander("Raw Extraction Text / Response"):
            st.text_area("VLM Raw Output", selected_doc.get("text", ""), height=250)

    # Download Buttons
    st.divider()
    col1, col2 = st.columns(2)
    with open(st.session_state["excel_path"], "rb") as f:
        excel_bytes = f.read()
    with open(st.session_state["json_path"], "rb") as f:
        json_bytes = f.read()

    col1.download_button(
        "📥 Download Type-Split Excel Workbook (.xlsx)",
        data=excel_bytes,
        file_name="batch_extracted_records.xlsx",
        mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
        use_container_width=True
    )
    col2.download_button(
        "📥 Download Full JSON Metadata (.json)",
        data=json_bytes,
        file_name="batch_extracted_records.json",
        mime="application/json",
        use_container_width=True
    )


if __name__ == "__main__":
    run_app()
