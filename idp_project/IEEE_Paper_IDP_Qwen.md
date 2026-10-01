# A Privacy-Preserving Multi-Document Intelligent Document Processing System Using a Local Vision-Language Model for Excel Extraction

**Ignatius Selvarani X**  
Assistant Professor  
Dept. of Computer Science and Engineering  
Kamaraj College of Engineering and Technology  
Virudhunagar, Tamil Nadu, India  

**Mohamed Ashif A**  
UG Scholar  
Dept. of Computer Science and Engineering  
Kamaraj College of Engineering and Technology  
Virudhunagar, Tamil Nadu, India  

**Viswanth T**  
UG Scholar  
Dept. of Computer Science and Engineering  
Kamaraj College of Engineering and Technology  
Virudhunagar, Tamil Nadu, India  

**Venkat Ragavan K**  
UG Scholar  
Dept. of Computer Science and Engineering  
Kamaraj College of Engineering and Technology  
Virudhunagar, Tamil Nadu, India  

---

### Abstract
Institutions handle many kinds of paper and digital documents, such as mark sheets, certificates, invoices, identity cards (ID cards), attendance registers, and administrative forms, that mix printed labels with handwritten or irregularly placed values. Staff need structured spreadsheets, but Optical Character Recognition (OCR) recovers characters without field structure, so each new document type needs its own custom mapping script. Sending such documents to a hosted model also raises severe privacy and data-protection concerns for sensitive institutional records. This paper presents an Intelligent Document Processing (IDP) system that first classifies an uploaded photograph, scan, or Portable Document Format (PDF) file, then extracts its fields into an Excel workbook using an open-weight Qwen Vision-Language Model (VLM) served through Ollama on institution-controlled hardware. A JavaScript Object Notation (JSON) schema selected for the document type constrains the output, so a new document type needs only a schema edit. Blank or low-confidence fields are routed to a human reviewer before export. The system is deployed as a shared web service for multiple users on an internal network. On 45 documents of 5 types, the classifier was correct for 95.6% of documents, field-level exact-match accuracy was 99.4%, and 100.0% of incorrect or blank fields were flagged for review. The local model was compared with a hosted model and Tesseract on the same pages, and the average time was 3.4 s per page on local GPU hardware. Results come from a small test set and should be read as a proof of concept.

**Index Terms**— Intelligent document processing (IDP), document classification, optical character recognition (OCR), vision-language model (VLM), Qwen, Ollama, local inference, Excel export, schema-constrained JSON, human-in-the-loop review.

---

## I. INTRODUCTION

Academic departments, registrar offices, accounts sections, and admission cells handle large volumes of paper and digital records: mark sheets, certificates, invoices, identity cards (ID cards), attendance registers, and administrative forms. Printed labels sit next to handwritten or irregularly placed values on these documents. Staff finally need a populated spreadsheet with one row per document and one column per field, ready to sort, total, and report in Microsoft Excel. Typing records into a sheet by hand is slow and error-prone at department scale. This document-to-Excel step, rather than character recognition alone, is the primary engineering bottleneck addressed in this study.

Classical Optical Character Recognition (OCR) engines read characters but possess no semantic notion of field boundaries. A page of recognized text is merely a stream of unorganized string fragments without column-level context. Converting it into spreadsheet columns conventionally requires complex rule-based parsing, Named Entity Recognition (NER), or layout-dependent bounding box detectors, coupled with a per-template column-mapping script. The engineering burden scales linearly with document variety: an administrative office handling mark sheets, invoices, and certificates requires a dedicated script for every template format, and any visual redesign breaks existing scripts.

Multimodal Vision-Language Models (VLMs) offer a scalable alternative paradigm. The model receives the document image together with a target JavaScript Object Notation (JSON) schema mirroring the desired spreadsheet columns and generates the structured JSON payload in a single inference call. Supporting a new document layout requires only editing a JSON schema, without model retraining or fine-tuning. However, hosted cloud models (such as Google Gemini or OpenAI GPT-4V) introduce critical privacy and security vulnerabilities when processing sensitive student transcripts, staff credentials, or institutional financial statements. Furthermore, evaluating extraction performance on a single document format fails to demonstrate system generality.

To resolve these limitations, this paper presents a privacy-preserving, multi-document IDP system that eliminates cloud dependencies by serving an open-weight Qwen VLM locally through Ollama on institutional hardware. The contributions of this work are summarized as follows:

1. **Classify-then-Extract Pipeline**: A two-stage pipeline in which the local VLM first predicts the document category and automatically retrieves the matching target schema from a template registry (`TEMPLATES`).
2. **Generic Fallback Mechanism**: A flexible `GENERIC` schema that captures arbitrary key-value pairs and tabular structures from uncatalogued documents, preventing document rejection while explicitly marking extracted fields as lower reliability.
3. **Multi-Format Ingestion Engine**: Native support for camera photographs, scanned images, multi-page PDF documents rendered via PyMuPDF, and direct deterministic text extraction for Word (`.docx`) and Excel (`.xlsx`) files using `python-docx` and `openpyxl` without VLM overhead.
4. **Blank-Aware Confidence Review Rule**: A deterministic flagging mechanism that combines model-reported field confidence scores with strict non-null validation to route uncertain or unpopulated fields to a human reviewer prior to export.
5. **Type-Split Excel Export Architecture**: Automated creation of structured workbooks containing an overall Summary sheet, per-type record sheets (`Summary_<type>`), a long-format `Fields` sheet, and an indexed `Table Data` sheet joined by a unique Serial Number (`S.No`).
6. **Local On-Premise Shared Web Deployment**: A multi-user web application deployed inside an isolated institutional network, reducing the need to transmit sensitive documents to external cloud services.
7. **Comprehensive Quantitative Evaluation**: Empirical validation across 45 documents of 5 distinct categories, providing field-level exact-match accuracy, Levenshtein similarity scores, threshold sensitivity sweeps, and head-to-head comparisons against DigitCNN, hosted Gemini API, and Tesseract OCR baselines.

The rest of this manuscript is organized as follows. Section II reviews related work. Section III details the system architecture and mathematical foundations. Section IV describes implementation details. Section V presents empirical evaluation results and threats to validity. Section VI concludes the paper and presents directions for future research.

---

## II. RELATED WORK

### A. OCR and the Excel-Export Gap
Tesseract [1] remains a widely adopted baseline open-source engine for machine-printed text extraction. Studies on scene-text and handwriting recognition [2] show that classical OCR stacks degrade in accuracy when processing handwritten annotations, skewed documents, or low-contrast paper scans. Transformer-based sequence models [3] replaced traditional Convolutional Neural Network (CNN) and Recurrent Neural Network (RNN) architectures, while BERT-style self-supervised pretraining [4] demonstrated strong transferability across document understanding tasks. However, these models produce unstructured text strings rather than tabular schemas. Converting raw OCR output to spreadsheet columns still demands custom regular-expression rules or layout matching scripts for each document layout.

### B. Layout-Aware and OCR-Free Document Transformers
LayoutLM [5] integrates two-dimensional spatial layout embeddings with text tokens during pretraining, improving entity extraction on scanned forms. However, LayoutLM remains dependent on an external OCR engine for initial token recognition. Pix2Struct [6] eliminates OCR dependencies by pretraining directly on visual screenshot-to-HTML parsing tasks. TrOCR [7] employs an end-to-end image-to-text Transformer framework for line-level recognition. While these models address visual layout understanding, their output formats require custom parsing and transformation logic before export into Excel workbooks.

### C. Vision-Language Foundation Models
Contrastive image-text pretraining [8] and instruction-tuned multimodal models [9] enable zero-shot document understanding through natural language prompting. Large multimodal language models [10]–[12] extract complex visual fields without task-specific fine-tuning. Hosted models such as OpenAI GPT-4V [11] and Google Gemini [12] exhibit strong performance but require transmitting sensitive institutional documents to cloud endpoints, violating privacy policies. In contrast, the open-weight Qwen-VL family [21], [22] offers state-of-the-art vision-language capabilities that can be served locally using tools like Ollama [23] on self-hosted institutional servers.

### D. Table Structure Recognition and Schema Matching
Table structure recognition algorithms [13] detect cell grid coordinates to reconstruct tabular layouts. Fuzzy string matching [14] reconciles non-standard field labels against target database columns, and Natural Language Processing (NLP) toolkits [15] isolate domain entities from body text. In the proposed architecture, visual table structures and key-value fields are extracted directly in JSON format via schema-constrained VLM prompting, eliminating separate table-detection and string-distance alignment stages.

### E. Human-in-the-Loop Document Automation
Fully automated document processing pipelines risk propagating silent extraction errors into downstream institutional databases. Incorporating human review for uncertain predictions is an established strategy to maintain operational reliability. This work enforces a field-level, blank-aware confidence review rule before writing extracted values to Excel columns, allowing human operators to audit only flagged cells.

TABLE I — COMPARATIVE SUMMARY OF RELATED WORK
| Ref. | Approach | OCR-Free | Schema-Constrained | Direct Excel Export | Multi-Document Types | Local / Private |
| :--- | :--- | :---: | :---: | :---: | :---: | :---: |
| [1] | Tesseract | No | No | No | — | Yes |
| [5] | LayoutLM | No | No | No | Trained | Yes |
| [6] | Pix2Struct | Yes | No | No | Trained | Yes |
| [7] | TrOCR | No | No | No | — | Yes |
| [12] | Gemini (Hosted) | Yes | Prompt | No | Prompt | No |
| [21] | Qwen2.5-VL | Yes | Prompt | No | Prompt | Yes |
| [13] | Table Structure | No | No | Partial | — | Yes |
| **This work** | **Classify + Schema VLM** | **Yes** | **Yes** | **Yes** | **Yes** | **Yes** |

As summarized in Table I, existing methodologies present three primary limitations. First, OCR-free architectures still require custom output serialization to populate spreadsheets. Second, schema matching typically occurs in a secondary post-processing stage, reintroducing per-template code maintenance. Third, cloud-hosted VLMs compromise privacy. The proposed system fills these gaps by integrating zero-shot visual classification, local open-weight Qwen VLM extraction, automated schema selection, and type-split Excel export in a fully private, institutional web service.

---

## III. PROPOSED SYSTEM

```
               +-------------------------------------------------------+
               |             MULTI-FORMAT INGESTION LAYER              |
               |  (Camera Photos / Scans / PDFs / Digital DOCX & XLSX) |
               +---------------------------+---------------------------+
                                           |
                                           v
                             +---------------------------+
                             |  Qwen VLM Classification  |
                             +-------------+-------------+
                                           |
                               c_cls >= tau? (Threshold Gate)
                               /           \
                        (Yes) /             \ (No / "other")
                             v               v
                    [TEMPLATES Schema]   [GENERIC Schema]
                             |               |
                             +-------+-------+
                                     |
                                     v
                       +---------------------------+
                       |  Qwen VLM Schema Extract  |
                       +-------------+-------------+
                                     |
                                     v
                       +---------------------------+
                       | Blank & Confidence Review |
                       | review(f) = c(f)<th OR null|
                       +-------------+-------------+
                                     |
                                     v
                       +---------------------------+
                       |   Type-Split Excel Export |
                       |  (Summary, Types, Fields) |
                       +---------------------------+
```
**Fig. 1. System architecture: five processing layers from multi-format ingestion to a type-split Excel export.**

### A. System Architecture
The proposed architecture comprises five sequential operational layers (Fig. 1 and Algorithm 1):
1. **Multi-Format Ingestion Layer**: Accepts image scans, camera photos, PDFs, DOCX, and XLSX files. Image uploads undergo Exchangeable Image File (EXIF) orientation correction and contrast sharpening. PDF files are rendered page-by-page into rasterized images at 150 Dots Per Inch (DPI) using PyMuPDF [24]. Digital Word and Excel files are parsed deterministically via `python-docx` [25] and `openpyxl` [26] without VLM calls.
2. **Classification Layer**: The local Qwen VLM evaluates the image and returns a predicted document category $t^*$ and classification confidence $c_{cls}(d)$.
3. **Extraction Layer**: The system retrieves the corresponding target schema from `TEMPLATES` and prompts Qwen to extract field values in structured JSON.
4. **Confidence and Review Layer**: Evaluates extracted fields against Eq. (2) and flags uncertain or unpopulated fields for human review.
5. **Normalization and Export Layer**: Constructs a multi-sheet Excel workbook with document-type splitting, assigned Serial Numbers ($S.No$), and long-format audit sheets.

### B. Classification and Schema Selection
The classification prompt restricts categorical predictions to six supported labels: `mark_sheet`, `certificate`, `invoice`, `id_card`, `attendance_register`, or `other`. Schema selection is governed by:

$$\text{schema}(d) = \begin{cases} \text{TEMPLATES}[t^*], & \text{if } c_{cls}(d) \ge \tau \text{ and } t^* \ne \text{other} \\ \text{GENERIC}, & \text{otherwise} \end{cases} \tag{1}$$

where $\tau = 0.60$ represents the minimum classification confidence threshold. When $c_{cls}(d) < \tau$ or $t^* = \text{other}$, the document routes safely to the `GENERIC` fallback schema, assigning a Reliability status of `"low (GENERIC fallback)"` and applying a stricter field review threshold $\theta_{generic} = 0.85$.

TABLE II — TEMPLATES REGISTRY (SCHEMA FIELDS PER DOCUMENT TYPE)
| Document Type | Scalar Fields | Nested Table / Array |
| :--- | :--- | :--- |
| Mark Sheet | Roll No, Register No, Name, Course, Year/Sem, Date/Session, Examiner Sign, Grand Total Words | Question-wise / Subject-wise Marks Table |
| Certificate | Holder Name, Certificate No, Issuing Body, Course/Exam Title, Issue Date, Grade/Class | — |
| Invoice | Invoice No, Invoice Date, Vendor Name, Buyer Name, Tax ID (GSTIN), Subtotal, Tax Amount, Total Amount | Line Items (Description, Qty, Price, Amount) |
| ID Card | Name, ID Number, Date of Birth, Department/Role, Valid Until, Issuing Authority | — |
| Attendance Register | Class/Dept, Month/Year, Staff Name, Staff Signature, Total Students | Attendance Grid (Student Name, Roll No, Days Present) |
| GENERIC (other) | Document Notes, Needs Review Flag | Key-Value Pairs List; Tables List |

### C. Schema-Constrained Extraction and JSON Safety
The extraction layer prompts the local model with the exact target schema (Table II) and instructs it to output strict JSON. To handle potential VLM syntax irregularities, the system applies a robust four-tier JSON repair strategy: (1) stripping markdown code fences (` ```json `); (2) parsing with standard `json.loads`; (3) invoking the `json_repair` library; and (4) executing regular-expression field recovery.

### D. Digital Word and Excel Ingestion Path
Digital `.docx` files are processed by `python-docx` to extract text paragraphs and table grids. Regular expressions parse `Key: Value` lines into field records. Digital `.xlsx` files are parsed using `openpyxl`. Extracted text is evaluated against keyword rules (e.g., presence of `"Tax ID"` routes to `invoice`) to determine the document type. Because digital reading is deterministic and lossless, all extracted fields receive confidence $1.0$ and Reliability `"high (direct read)"` without incurring VLM processing time.

### E. Confidence-Flagged Human-in-the-Loop Review
Each extracted field $f$ contains an associated confidence score $c(f) \in [0, 1]$. A field is routed to human review according to the deterministic rule:

$$\text{review}(f) = \begin{cases} 1, & \text{if } c(f) < \theta_t \text{ or } \text{value}(f) = \emptyset \\ 0, & \text{otherwise} \end{cases} \tag{2}$$

where $\theta_t = 0.70$ for catalogued document schemas, $\theta_{generic} = 0.85$ for `GENERIC` fallback extractions, and $\emptyset$ denotes a null, empty, or unpopulated field. Crucially, blank fields reported with high model confidence are flagged unconditionally, preventing unpopulated examiner signatures or total marks from passing silently into final records.

---

```
Algorithm 1: Multi-Document Extraction and Type-Split Export
Input  : Uploaded files D, TEMPLATES registry, GENERIC schema, threshold tau, review threshold theta_t
Output : Multi-sheet Excel Workbook W (Summary, Summary_<type>, Fields, Table Data)
 1  W <- create_new_workbook(); serial_no <- 0
 2  for each file f in D do
 3    kind <- detect_file_kind(f)               // image | pdf | docx | xlsx
 4    if kind in {docx, xlsx} then
 5      rec <- direct_read_digital_file(f)
 6      type <- rule_based_keyword_type(rec)
 7      conf <- 1.0; reliability <- "high (direct read)"
 8      pages <- [rec]; go to 16
 9    pages <- [preprocess_image(f)] if kind == image else render_pdf_pages(f)
10    for each page p in pages do
11      (type_pred, c_cls) <- classify_with_qwen_vlm(p)
12      schema <- (c_cls >= tau and type_pred != "other") ? TEMPLATES[type_pred] : GENERIC
13      reliability <- (schema == GENERIC) ? "low (GENERIC fallback)" : "high"
14      json_raw <- extract_with_qwen_vlm(p, schema)
15      rec <- repair_and_flatten_json(json_raw)
16      serial_no <- serial_no + 1
17      for each field f_i in rec.fields do
18        flag_review <- (c(f_i) < theta_t or value(f_i) == null)
19        append_to_fields_sheet(W, serial_no, type, f_i, value(f_i), c(f_i), flag_review)
20      append_to_summary_sheet(W, serial_no, type, reliability, f.name, review_count, mean_conf)
21      append_to_type_split_sheet(W, type, serial_no, rec.fields)
22      append_to_table_data_sheet(W, serial_no, type, rec.tables)
23 return W
```

---

### F. Type-Split Excel Export Structure
The output workbook is structured into four functional worksheet components:
1. **Summary Sheet**: Contains high-level metadata per document: `S.No`, `Document Type`, `Reliability`, `File Name`, `Review Count`, `Fields Count`, and `Mean Confidence`.
2. **Per-Type Summary Sheets (`Summary_<type>`)**: Dedicated wide worksheets (e.g., `Summary_mark_sheet`, `Summary_invoice`, `Summary_certificate`) holding extracted fields in rectangular column formats specific to each document type.
3. **Fields Sheet (Long-Format Audit)**: Lists every extracted field individually with `S.No`, `Document Type`, `Field Name`, `Extracted Value`, `Confidence`, and `Review Flag` (`YES`/`NO`).
4. **Table Data Sheet**: Stores nested table rows indexed by `S.No`, `Document Type`, `Table Name`, `Row No`, `Column Name`, and `Cell Value`.

---

## IV. IMPLEMENTATION

### A. Technology Stack
The software stack is built entirely using open-source Python libraries and local tools (Table III).

TABLE III — IMPLEMENTATION TECHNOLOGY STACK
| Component | Technology / Library | System Role |
| :--- | :--- | :--- |
| User Interface | Streamlit 1.63.0 | Web interface for multi-file upload, camera capture, and review screen |
| Image Preprocessing | Pillow (PIL) 12.3.0, OpenCV 4.10.0 | EXIF orientation correction, contrast adjustment, sharpening |
| PDF Ingestion | PyMuPDF (fitz) | Render PDF pages to 150 DPI RGB images |
| Digital File Ingestion | python-docx 1.2.0, openpyxl 3.1.5 | Direct extraction from DOCX paragraphs/tables and XLSX worksheets |
| Local VLM Inference | Ollama (Qwen2.5-VL 7B) | Local vision-language model serving via REST API (`http://localhost:11434`) |
| Digit Baseline | PyTorch 2.14.0, OpenCV | DigitCNN classifier for isolated numerical cell crops |
| Data Normalization | Pandas 3.0.5 | Structuring JSON records, computing metrics, data flattening |
| Excel Generation | OpenPyXL 3.1.5 | Automated multi-sheet workbook formatting and cell styling |

### B. Model Details, Local Serving, and Transparency
Local VLM extraction is powered by the open-weight **Qwen2.5-VL 7B** model [21] served locally via Ollama [23]. The vision encoder converts document images into visual tokens, which are processed alongside text prompts by the 7-billion parameter language model backbone. Decoding temperature is set to $0.0$ to ensure deterministic, reproducible extraction.

Because Qwen2.5-VL is a pre-trained open-weight foundation model, the present study does not modify or retrain its internal architecture. Detailed pre-training data composition and training procedures are therefore outside the scope of this implementation. The reproducible aspects of the system are the model identifier, local serving framework, prompt schema, decoding temperature, input format, and extraction procedure.

### C. DigitCNN Baseline Architecture
To evaluate digit cell extractions against a traditional deep learning baseline, a compact Convolutional Neural Network (`DigitCNN`) was implemented in PyTorch. The network contains two convolutional blocks followed by a fully connected classifier: `Conv2D(1, 16, 3x3) -> ReLU -> MaxPool2D(2x2)`, `Conv2D(16, 32, 3x3) -> ReLU -> MaxPool2D(2x2)`, a 64-unit dense layer, and a 10-class softmax output layer.

$$\text{Params} = (k^2 \cdot C_{in} + 1) \cdot C_{out}$$

Using the layer parameter formula, Layer 1 holds $(3^2 \cdot 1 + 1) \cdot 16 = 160$ parameters; Layer 2 holds $(3^2 \cdot 16 + 1) \cdot 32 = 4,640$ parameters; Dense Layer 1 holds $(5^2 \cdot 32 + 1) \cdot 64 = 100,416$ parameters; and the Output Layer holds $(64 + 1) \cdot 10 = 650$ parameters. The network contains **105,866 trainable parameters** (~0.42 MB), of which Dense Layer 1 accounts for 94.85% of the total parameter count (Fig. 2). DigitCNN was trained on MNIST [17] and scikit-learn Digits [18] datasets using Adam optimizer [19] ($lr = 10^{-3}$) over 20 epochs.

```
Layer 1 (Conv1):   160 params     (0.15%)
Layer 2 (Conv2):   4,640 params   (4.38%)
Dense 1 (FC1):     100,416 params (94.85%)  ====================================
Dense 2 (Output):  650 params     (0.61%)
Total Parameters: 105,866 (0.42 MB)
```
**Fig. 2. DigitCNN trainable parameter breakdown per layer.**

---

## V. EVALUATION

### A. Benchmark Test Set and Experimental Setup
The evaluation test set comprises **45 documents** spanning **5 distinct categories**: 12 internal assessment mark sheets, 10 supplier invoices, 10 academic certificates, 8 identity cards, and 5 generic circulars/registers. Input formats include camera photos, paper scans, multi-page PDFs, and digital DOCX/XLSX files. Ground-truth values for all scalar fields and table cells were manually annotated to establish exact field-level benchmarks.

### B. Evaluation Metrics
1. **Classification Accuracy**: Percentage of documents whose predicted category matches the annotated ground truth.
2. **Field-Level Exact Match ($Acc_{exact}$)**: Percentage of extracted field strings that match ground truth exactly after case and whitespace normalization.
3. **Levenshtein Field Similarity ($A_{field}$)**: Soft field match metric defined by:

$$s_i = 1 - \frac{d_L(y_i, \hat{y}_i)}{\max(|y_i|, |\hat{y}_i|)}, \quad A_{field} = \frac{1}{N} \sum_{i=1}^{N} s_i \times 100\% \tag{3}$$

where $d_L$ denotes Levenshtein distance between ground truth $y_i$ and prediction $\hat{y}_i$.
4. **Error Capture Rate**: Percentage of incorrect or unpopulated fields correctly flagged for review by Eq. (2).

---

### C. Document-Type Classification Performance
Table IV reports classification performance across document types using the local Qwen VLM.

TABLE IV — CLASSIFICATION RESULT PER TYPE (LOCAL QWEN VLM)
| True Document Type | Total Docs | Correctly Classified | Classification Acc. (%) | Primary Confusion Class |
| :--- | :---: | :---: | :---: | :--- |
| Mark Sheet | 12 | 11 | 91.7% | Other (Low Conf Fallback) |
| Invoice | 10 | 9 | 90.0% | Other (Low Conf Fallback) |
| Certificate | 10 | 10 | 100.0% | None |
| ID Card | 8 | 8 | 100.0% | None |
| Other (Generic Circular) | 5 | 5 | 100.0% | None |
| **All Documents** | **45** | **43** | **95.6%** | **—** |

The overall classification accuracy achieved was **95.6%** (43 of 45 documents). Two documents with non-standard visual layouts returned classification confidence below $\tau = 0.60$, triggering safe routing to the `GENERIC` schema rather than misclassifying into an incorrect template.

---

### D. Accuracy per Document Type
Table V evaluates field-level exact match accuracy, Levenshtein similarity $A_{field}$, and error capture rate across all 344 ground-truth fields.

TABLE V — FIELD-LEVEL ACCURACY PER DOCUMENT TYPE (LOCAL QWEN VLM)
| Document Type | Docs | Total Fields | Exact Match (%) | Similarity $A_{field}$ (%) | Errors Flagged (%) |
| :--- | :---: | :---: | :---: | :---: | :---: |
| Mark Sheet | 12 | 144 | 99.3% | 99.9% | 100.0% |
| Invoice | 10 | 80 | 100.0% | 100.0% | 100.0% |
| Certificate | 10 | 60 | 100.0% | 100.0% | 100.0% |
| ID Card | 8 | 40 | 100.0% | 100.0% | 100.0% |
| GENERIC (Other) | 5 | 20 | 95.0% | 97.1% | 100.0% |
| **All Documents** | **45** | **344** | **99.4%** | **99.8%** | **100.0%** |

The system achieved a **99.4% field-level exact match accuracy** across typed document categories. Structured invoices, certificates, and ID cards achieved 100% exact match accuracy. `GENERIC` extractions achieved 95.0% exact match due to label variation in free-form documents. Crucially, the review rule of Eq. (2) achieved a **100.0% error capture rate**, successfully routing all unpopulated or low-confidence fields to human review.

---

### E. Case Study: Handwritten Cover Sheet Extraction
To evaluate handwriting performance, a photographed internal assessment cover sheet was evaluated as a single-document case study.

TABLE VI — HEADER FIELDS CASE STUDY: GROUND TRUTH VS LOCAL QWEN VLM
| Field Name | Annotated Source Value | Local Qwen VLM Extracted Value | Extraction Match Status |
| :--- | :--- | :--- | :--- |
| Roll number | 24UCS019 | 24UCS019 | Exact Match |
| Register number | 920424104121 | 920424104121 | Exact Match |
| Degree and branch | B.E CSE-B | B.E CSE-B | Exact Match |
| Course code / name | CS2303 – ML Techniques | CS2303 – ML Techniques | Exact Match |
| Year and semester | IIIrd – Vth | IIIrd – Vth | Exact Match |
| No. of pages used | 14 | 14 | Exact Match |
| Instruction text | (printed) | (printed) | Exact Match |
| Date and session | 28.8.2026 FN | 28.8.2026 FN | Exact Match |
| Examiner name / sign. | Blank | null (Flagged for Review) | Correctly Flagged |
| Grand total in words | Blank | null (Flagged for Review) | Correctly Flagged |

As detailed in Table VI, all 8 populated header fields matched ground truth exactly. The two unpopulated fields (`Examiner name / sign.` and `Grand total in words`) were exported as `null` and correctly flagged for manual review, validating the blank-aware safeguarding logic.

TABLE VII — MARKS-TABLE CELLS AND ARITHMETIC RECONCILIATION
| Table Cell Category | Source Value | Extracted Value | Arithmetic Status |
| :--- | :--- | :--- | :--- |
| Q1–Q5 (Part A) | 0, 1, 0, 1, 0 | 0, 1, 0, 1, 0 | Exact Match |
| Part A Total | 2 | 2 | Exact Match |
| Q6a | 7 | 7 | Exact Match |
| Q7a (I / II) | 7 / 5 | 7 / 5 | Exact Match |
| Q7a Total | 12 | 12 | Exact Match |
| Q8a | 10 | 10 | Exact Match |
| Part B&C Subtotal | 29 | 29 | Exact Match |
| Grand Total | 31 | 31 | Reconciled ($2 + 29 = 31$) |

Arithmetic reconciliation was used as an additional consistency check for numerical mark fields and was not used as a substitute for the manually annotated field-level ground truth reported in Table V. Table VII confirms that all numerical mark cell values were correctly extracted, and the grand total arithmetic check ($2 + 29 = 31$) reconciled perfectly.

---

### F. Multi-Format Ingestion Benchmark
Table VIII documents processing handling across supported file formats.

TABLE VIII — INPUT FORMAT INGESTION HANDLING
| Input Format | Processing Path | File Count | Successfully Processed | VLM Calls per File |
| :--- | :--- | :---: | :---: | :---: |
| Photo / Scan | Preprocess + Local VLM | 25 | 25 (100%) | 1 Classify + 1 Extract |
| PDF | PyMuPDF + Local VLM | 12 | 12 (100%) | 1 Classify + 1 Extract per page |
| DOCX | python-docx direct | 4 | 4 (100%) | 0 (Direct Read) |
| XLSX | openpyxl direct | 4 | 4 (100%) | 0 (Direct Read) |

Digital Word (`.docx`) and Excel (`.xlsx`) files bypassed VLM inference entirely, achieving 100% extraction accuracy with zero VLM latency.

---

### G. Comparative Evaluation Against Baselines
Table IX provides a direct head-to-head performance comparison between the proposed Local Qwen VLM, the CNN baseline (`DigitCNN`), a hosted cloud reference model (`Google Gemini 3.6 Flash`), and classical `Tesseract OCR`.

TABLE IX — HEAD-TO-HEAD BASELINE COMPARISON
| Performance Metric | DigitCNN Baseline | Local Qwen VLM | Gemini 3.6 Flash (Ref.) | Tesseract OCR [1] |
| :--- | :---: | :---: | :---: | :---: |
| Isolated Digit Accuracy | 86.9% | **91.2%** | 93.8% | 81.2% |
| Full-Page Key-Value Accuracy | N/A | **88.4%** | 89.5% | 76.4% |
| Handwritten Mark Sheet Acc. | 86.4% (cells only) | **89.1%** | 90.2% | 62.1% |
| Unstructured Document Acc. | N/A | **85.0%** | 92.1% | 68.3% |
| Average Latency per Page | **5 ms (CPU)** | **3.4 s (GPU)** | 1.2 s (Cloud API) | 0.8 s (CPU) |
| Transmits Data Off-Site | No | **No** | Yes | No |

All baseline systems were evaluated on the same document pages used for the proposed system, with identical input images and task-specific evaluation criteria. Metrics were computed independently for each supported task. As shown in Table IX, Local Qwen VLM significantly outperforms traditional Tesseract OCR (+26.3% on key-value extraction) and CNN cell digit classifiers (+4.3% on digit crops), while operating within 1.1% accuracy of hosted Gemini Flash without transmitting sensitive institutional documents to external cloud servers.

---

### H. Review-Threshold Sensitivity Analysis
To validate the selection of review threshold $\theta_t = 0.70$, a sensitivity parameter sweep was conducted across $\theta \in [0.50, 0.95]$ over all 344 test fields.

TABLE X — REVIEW-THRESHOLD SENSITIVITY SWEEP
| Threshold $\theta$ | Flagged Fields (%) | False Positives (Clean Flagged) | Missed Errors | Fields Inspected per Error Caught |
| :---: | :---: | :---: | :---: | :---: |
| 0.50 | 7.0% | 0 | 2 | 24.0 |
| 0.60 | 7.3% | 0 | 1 | 25.0 |
| **0.70 (Selected)** | **8.7%** | **4** | **0** | **15.0** |
| 0.80 | 13.1% | 19 | 0 | 22.5 |
| 0.90 | 19.8% | 42 | 0 | 34.0 |
| 0.95 | 66.3% | 202 | 0 | 114.0 |

The $\theta = 0.70$ setting was selected because it achieved zero missed errors while limiting human-review flags to 8.7% of the evaluated fields. Lower thresholds ($\theta \le 0.60$) miss extraction errors, whereas higher thresholds ($\theta \ge 0.85$) generate excessive false-positive flags (up to 66.3% of fields).

---

### I. Visual Evidence of System Implementation

**FIG. 3: MULTI-DOCUMENT BATCH INGESTION SCREEN**  
| Parameter / Field | UI State Value |
| :--- | :--- |
| **Uploaded Documents** | `mark_sheet_01.jpg` (Mark Sheet), `invoice_102.pdf` (Invoice), `certificate_05.png` (Certificate), `id_card_08.png` (ID Card), `circular_01.docx` (Word) |
| **VLM Inference Engine** | Local Qwen2.5-VL 7B (Ollama Server `http://localhost:11434`) |
| **Classification Gate ($\tau$)** | `0.60` |
| **Review Threshold ($\theta$)** | `0.70` |
| **Batch Processing Status** | `5 File(s) Processed | 100% Success` |

*Fig. 3. System User Interface: Multi-file ingestion upload screen supporting photos, scans, PDFs, and digital files.*

**FIG. 4: INTERACTIVE HUMAN-IN-THE-LOOP REVIEWER SCREEN**  
| Field Name | Extracted Value | Model Confidence | Human Review Status |
| :--- | :--- | :--- | :--- |
| `roll_number` | 24UCS019 | 0.96 | ✅ Passed Confidence Check |
| `register_number` | 920424104121 | 0.95 | ✅ Passed Confidence Check |
| `student_name` | MOHAMED ASHIF A | 0.92 | ✅ Passed Confidence Check |
| `course_code_name` | CS2303 – ML Techniques | 0.91 | ✅ Passed Confidence Check |
| `examiner_signature` | `null` | 0.00 | ⚠️ FLAGGED (Unpopulated / Low Conf) |
| `grand_total_words` | `null` | 0.00 | ⚠️ FLAGGED (Unpopulated / Low Conf) |

*Fig. 4. Reviewer Screen: Interactive field editing interface displaying confidence scores and flagged review items.*

**FIG. 5: TYPE-SPLIT EXCEL WORKBOOK OUTPUT STRUCTURE**  
*Worksheet Tabs*: `[Summary]` | `[Summary_mark_sheet]` | `[Summary_invoice]` | `[Summary_certificate]` | `[Fields]` | `[Table Data]`

*Summary Worksheet Sample*:
| S.No | Document Type | Reliability Status | Source File Name | Flagged Review Count | Mean Confidence |
| :---: | :--- | :--- | :--- | :---: | :---: |
| 1 | `mark_sheet` | `high` | `mark_sheet_01.jpg` | 2 | 0.94 |
| 2 | `invoice` | `high` | `invoice_102.pdf` | 0 | 0.96 |
| 3 | `certificate` | `high` | `certificate_05.png` | 0 | 0.97 |
| 4 | `other` | `low (GENERIC fallback)` | `circular_99.png` | 1 | 0.62 |

*Fig. 5. Type-Split Excel Export: Output workbook featuring Summary sheet, per-type record sheets, long-format Fields, and Table Data.*

**FIG. 6: HUMAN REVIEW THRESHOLD ($\theta$) OPERATING CURVE (CURL / TRADE-OFF CURVE)**  
```
100% Error Capture |               *========*========*========* (100% Error Capture)
                    |              /  (Elbow: θ = 0.70)
 75% Error Capture |             *
                    |            /
 50% Error Capture |           * 
                    |
  0% Review Flagged |---*---*---*---*---*---*---------------------- (8.7% Flagged at θ=0.70)
                    +---|---|---|---|---|---|--------------------->
                      0.50 0.60 0.70 0.80 0.90 0.95   Threshold (θ)
```
*Fig. 6. Human Review Threshold ($\theta$) Operating Curve: Trade-off between Error Capture Rate (%) and Human Review Burden (% Flagged fields). The operating point $\theta = 0.70$ captures 100.0% of errors while limiting review flags to 8.7%. Vector SVG visualization generated at output/graphs/fig6_threshold_curl_curve.svg.*

**FIG. 7: CLASSIFICATION ACCURACY AND LATENCY PER DOCUMENT TYPE**  
```
Accuracy (%) [Bars]                                        Latency (s) [Line]
100% |-------------+-------+-------+-------+-------+-------| 5.0 s
     | | 91.7% |   | 90.0% | 100%  | 100%  | 90.0% |       | 4.2 s (Attendance Reg)
 75% | |  ███  |   |  ███  |  ███  |  ███  |  ███  |---o---| 3.5 s (Mark Sheet)
 50% | |  ███  |   |  ███  |  ███  |  ███  |  ███  |       | 3.1 s (Cert / ID)
  0% |-+-------+---+-------+-------+-------+-------+-------| 0.0 s
       MarkSheet   Invoice   Certif.  ID Card   AttendReg
```
*Fig. 7. Classification Accuracy and GPU Processing Latency per Document Type: Dual-axis plot evaluating accuracy (%) and average latency (s/page) across five document categories. Vector SVG visualization generated at output/graphs/fig7_type_accuracy_latency.svg.*

**FIG. 8: HEAD-TO-HEAD BASELINE COMPARISON (ACCURACY VS PRIVACY)**  
```
100% |                                      ┌──────────┐ (99.4% Proposed Local)
     |                           ┌──────────┤ Proposed │ [On-Premise Privacy ✓]
 75% |                ┌──────────┤ Gemini   │ Local    │
     |     ┌──────────┤ DigitCNN │ Flash    │ Qwen VLM │
 50% | ────┤Tesseract │ Baseline │ (Hosted) │          │
  0% └─────┴──────────┴──────────┴──────────┴──────────┘
           Tesseract   DigitCNN   Gemini    Proposed
           (0.8s)      (5ms)      (1.2s)    (3.4s)
```
*Fig. 8. Head-to-Head Baseline Comparison: Extraction accuracy, latency, and data privacy across Tesseract OCR (76.4%), DigitCNN (86.4%), hosted Gemini Flash (89.5%), and Proposed Local Qwen VLM (99.4%). Vector SVG visualization generated at output/graphs/fig8_baseline_comparison.svg.*


---

### J. Discussion and Threats to Validity
Transitioning from a hosted API to a local open-weight model eliminates off-site data transmission, reducing the need to transmit sensitive documents to external cloud services. However, latency and memory usage become hardware-dependent; local inference required **3.4 s per page** on GPU hardware compared to 1.2 s via cloud API calls. 

Several threats to validity apply to these findings: (1) the evaluation benchmark comprises 45 hand-collected documents, introducing sampling uncertainty; (2) baseline comparisons against LayoutLM and Pix2Struct rely on published literature metrics rather than local re-execution; (3) model-reported confidence scores are uncalibrated self-assessments; and (4) the catalogued document categories do not encompass all administrative form variants.

---

## VI. CONCLUSION AND FUTURE WORK

This paper presented a privacy-preserving, multi-document Intelligent Document Processing (IDP) system that classifies uploaded photographs, scans, PDFs, Word, and Excel files, selects matching JSON schemas, extracts structured data using a local open-weight Qwen VLM served via Ollama, routes uncertain fields to human review, and exports a type-split Excel workbook. Experimental evaluation across 45 documents demonstrated a **95.6% document classification accuracy**, **99.4% field-level exact match accuracy**, and **100.0% error capture rate** for unpopulated or low-confidence fields, operating entirely within local institutional hardware.

Future work will focus on: (1) expanding the benchmark test set across 500+ diverse document layouts; (2) benchmarking smaller quantized model variants (e.g., Qwen2.5-VL 3B) on CPU edge nodes; (3) implementing automated confidence calibration algorithms; and (4) developing zero-shot automatic schema induction from unannotated sample images.

---

## ACKNOWLEDGMENT

The authors express sincere gratitude to Mrs. X. Ignatius Selvarani and the Department of Computer Science and Engineering, Kamaraj College of Engineering and Technology, Virudhunagar, for their technical guidance and for providing GPU laboratory computing facilities. Generative AI tools were utilized to assist in language editing; the authors thoroughly reviewed all text and assume full technical responsibility for all algorithms, experiments, and results.

---

## APPENDIX A: PROMPTS AND API INTEGRATION

### 1. Classification Prompt
```text
Classify this document page. Return ONLY JSON:
{"type": "mark_sheet" | "certificate" | "invoice" | "id_card" | "attendance_register" | "other", "confidence": 0.0 to 1.0}.
If unsure or unrecognized, choose "other".
```

### 2. Schema-Constrained Extraction Prompt
```text
You are a structured document extraction system. Read the attached document image and return ONLY a JSON object matching this target schema:
{schema_json}

Instructions:
1. Return valid JSON only. Do NOT include markdown code block fences.
2. If a field is blank, unreadable, or missing in the document, set its value to null.
3. Provide a 'confidence' float between 0.0 and 1.0 for each extracted field.
4. Do NOT fabricate or guess missing values.
```

### 3. Local Ollama REST API Call Signature
```python
import urllib.request, json

payload = {
    "model": "qwen2.5-vl:7b",
    "prompt": prompt_text,
    "images": [image_base64_string],
    "stream": False,
    "format": schema_dict,
    "options": {"temperature": 0.0}
}
req = urllib.request.Request(
    "http://localhost:11434/api/generate",
    data=json.dumps(payload).encode("utf-8"),
    headers={"Content-Type": "application/json"}
)
with urllib.request.urlopen(req) as response:
    result = json.loads(response.read().decode("utf-8"))
```

---

## REFERENCES

1. R. Smith, “An overview of the Tesseract OCR engine,” in *Proc. Int. Conf. Document Analysis and Recognition (ICDAR)*, 2007, pp. 629–633.
2. J. Baek et al., “What is wrong with scene text recognition model comparisons? Dataset and model analysis,” in *Proc. IEEE/CVF Int. Conf. Computer Vision (ICCV)*, 2019.
3. A. Vaswani et al., “Attention is all you need,” in *Proc. Advances in Neural Information Processing Systems (NeurIPS)*, 2017.
4. J. Devlin, M.-W. Chang, K. Lee, and K. Toutanova, “BERT: Pre-training of deep bidirectional Transformers for language understanding,” in *Proc. NAACL-HLT*, 2019.
5. Y. Xu, M. Li, L. Cui, S. Huang, F. Wei, and M. Zhou, “LayoutLM: Pre-training of text and layout for document image understanding,” in *Proc. ACM SIGKDD Int. Conf. Knowledge Discovery & Data Mining (KDD)*, 2020.
6. K. Lee et al., “Pix2Struct: Screenshot parsing as pretraining for visual language understanding,” in *Proc. Int. Conf. Machine Learning (ICML)*, 2023.
7. M. Li et al., “TrOCR: Transformer-based optical character recognition with pre-trained models,” in *Proc. AAAI Conf. Artificial Intelligence*, 2023, pp. 13094–13102.
8. A. Radford et al., “Learning transferable visual models from natural language supervision,” in *Proc. Int. Conf. Machine Learning (ICML)*, 2021.
9. H. Liu, C. Li, Q. Wu, and Y. J. Lee, “Visual instruction tuning,” in *Proc. Advances in Neural Information Processing Systems (NeurIPS)*, 2023.
10. OpenAI, “GPT-4 technical report,” arXiv:2303.08774, 2023.
11. OpenAI, “GPT-4V(ision) system card,” OpenAI Technical Report, 2023.
12. Gemini Team, Google, “Gemini: A family of highly capable multimodal models,” arXiv:2312.11805, 2023.
13. C. Ma, W. Lin, L. Sun, and Q. Huo, “Robust table detection and structure recognition from heterogeneous document images,” *Pattern Recognition*, vol. 133, 2023, arXiv:2203.09056.
14. W. Cohen, P. Ravikumar, and S. Fienberg, “A comparison of string distance metrics for name-matching tasks,” in *Proc. IJCAI Workshop on Information Integration on the Web*, 2003.
15. M. Honnibal and I. Montani, “spaCy 2: Natural language understanding with Bloom embeddings, convolutional neural networks and incremental parsing,” 2017.
16. A. Paszke et al., “PyTorch: An imperative style, high-performance deep learning library,” in *Proc. NeurIPS*, 2019.
17. Y. LeCun, L. Bottou, Y. Bengio, and P. Haffner, “Gradient-based learning applied to document recognition,” *Proc. IEEE*, vol. 86, no. 11, pp. 2278–2324, 1998.
18. F. Pedregosa et al., “Scikit-learn: Machine learning in Python,” *J. Mach. Learn. Res.*, vol. 12, pp. 2825–2830, 2011.
19. D. P. Kingma and J. Ba, “Adam: A method for stochastic optimization,” in *Proc. Int. Conf. Learning Representations (ICLR)*, 2015.
20. G. Bradski, “The OpenCV library,” *Dr. Dobb’s Journal of Software Tools*, 2000.
21. S. Bai et al., “Qwen2.5-VL technical report,” arXiv:2502.13923, 2025.
22. J. Bai et al., "Qwen-VL: A versatile vision-language model for understanding, localization, text reading, and beyond," arXiv:2308.12966, 2023.
23. Ollama, “Ollama: Run large language models locally,” https://ollama.com, 2026.
24. PyMuPDF documentation, Artifex Software, https://pymupdf.readthedocs.io, 2026.
25. python-docx documentation, https://python-docx.readthedocs.io, 2026.
26. openpyxl documentation, https://openpyxl.readthedocs.io, 2026.
