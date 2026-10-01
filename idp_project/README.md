---
title: Generic Document Extractor
emoji: 📄
colorFrom: blue
colorTo: green
sdk: streamlit
app_file: app.py
pinned: false
---

# Intelligent Document Processing — Streamlit Scanner

Upload or camera-capture any sheet: forms, bills, tables, certificates, or
letters. The app reads the full page, discovers visible field labels (for
example Name, Age, Place, Address, Bill No), and creates JSON plus Excel with
dynamic column headings. No student or marksheet fields are assumed.

## Local setup

```bash
python -m venv venv
venv\Scripts\activate        # Windows
source venv/bin/activate     # Mac/Linux
pip install -r requirements.txt
```

Also install the Tesseract OCR binary (see main course guide) — this is
separate from the pip packages above.

## Run locally

```bash
streamlit run app.py
```

The Streamlit workflow is:

1. Upload an image or PDF.
2. Select **Extract document**.
3. Review full text and detected `Label: Value` fields.
4. Download the complete JSON or Excel file.

Excel includes a dynamic `Extracted_Data` sheet whose headings come from the
uploaded document, plus `Pages` and `Words` sheets containing all raw OCR text
and word coordinates for auditing.

## Deploy to Hugging Face Spaces

1. Create a free account at https://huggingface.co
2. Create a New Space → SDK: **Streamlit** → visibility your choice
3. Either:
   - push this whole folder to the Space's git repo (`git remote add space <space-git-url>`, `git push space main`), OR
   - use the Space's web "Files" tab to upload `app.py`, `requirements.txt`,
     `packages.txt`, and the `modules/` folder directly
4. The Space builds automatically (installs `requirements.txt` AND
   `packages.txt` — the latter is what gets Tesseract installed on Hugging
   Face's servers, since it's not a pip package)
5. Once built, your Space gets a public **https://** URL — live mobile
   camera capture (`st.camera_input`) will work correctly here, unlike a
   plain `http://` local network address, because Space URLs are HTTPS
   by default

## Project structure

```
idp_project/
├── app.py                    # Streamlit UI — upload/camera extraction and Excel export
├── requirements.txt
├── packages.txt               # apt packages for Hugging Face Spaces (Tesseract)
├── modules/
│   ├── preprocessing.py       # image cleanup: deskew, denoise, threshold, quality check
│   ├── ocr_engine.py          # Tesseract wrapper with confidence scoring
│   ├── field_extraction.py    # regex + generic fallback for "Label: Value" form documents
│   ├── nlp_extraction.py      # spaCy name fallback for free-text form OCR
│   ├── cnn_digit_recognizer.py # trained CNN inference for digit table cells
│   ├── table_extractor.py     # grid-line detection + cell-by-cell OCR for dense table documents
│   └── excel_writer.py        # dynamic-column Excel writer, batch-append across multiple photos
├── tests/                     # pytest suite (19 tests)
└── sample_images/
```
