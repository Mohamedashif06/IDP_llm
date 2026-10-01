"""Generate IEEE_Paper_IDP_Qwen.html and IEEE_Paper_IDP_Qwen.doc.

Uses standard Python library to build a full Word-compatible HTML manuscript.
Word opens this natively and saves it as IEEE_Paper_IDP_Qwen.docx with 1 click.
"""

import os
import re

PROJECT_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
MD_PATH = os.path.join(PROJECT_DIR, "IEEE_Paper_IDP_Qwen.md")
HTML_OUTPUT = os.path.join(PROJECT_DIR, "IEEE_Paper_IDP_Qwen.html")
DOC_OUTPUT = os.path.join(PROJECT_DIR, "IEEE_Paper_IDP_Qwen.doc")
GRAPHS_DIR = os.path.join(PROJECT_DIR, "output", "graphs")


def load_svg(name):
    path = os.path.join(GRAPHS_DIR, name)
    if os.path.exists(path):
        with open(path, "r", encoding="utf-8") as f:
            return f.read()
    return ""


def build_html_paper():
    with open(MD_PATH, "r", encoding="utf-8") as f:
        md_text = f.read()

    svg6 = load_svg("fig6_threshold_curl_curve.svg")
    svg7 = load_svg("fig7_type_accuracy_latency.svg")
    svg8 = load_svg("fig8_baseline_comparison.svg")

    html_content = f"""<!DOCTYPE html>
<html xmlns:o="urn:schemas-microsoft-com:office:office"
      xmlns:w="urn:schemas-microsoft-com:office:word"
      xmlns="http://www.w3.org/TR/REC-html40">
<head>
  <meta charset="utf-8">
  <title>A Privacy-Preserving Multi-Document Intelligent Document Processing System Using a Local Vision-Language Model for Excel Extraction</title>
  <style>
    @page {{
      size: 8.5in 11.0in;
      margin: 0.75in 0.75in 0.75in 0.75in;
      mso-header-margin: 0.5in;
      mso-footer-margin: 0.5in;
    }}
    body {{
      font-family: "Times New Roman", Times, serif;
      font-size: 10pt;
      line-height: 1.15;
      color: #000000;
      background-color: #ffffff;
      margin: 0;
      padding: 20px;
    }}
    h1.paper-title {{
      font-size: 18pt;
      font-weight: bold;
      text-align: center;
      margin-bottom: 12pt;
      color: #003366;
    }}
    .authors-table {{
      width: 100%;
      border-collapse: collapse;
      margin-bottom: 16pt;
    }}
    .authors-table td {{
      text-align: center;
      vertical-align: top;
      padding: 4px 8px;
      font-size: 9.5pt;
    }}
    .author-name {{
      font-weight: bold;
      font-size: 10.5pt;
    }}
    .abstract-box {{
      border: 1px solid #003366;
      background-color: #f8fafd;
      padding: 10pt 12pt;
      margin-bottom: 16pt;
      font-size: 9.5pt;
      line-height: 1.2;
    }}
    .abstract-title {{
      font-weight: bold;
      font-size: 10pt;
      color: #003366;
    }}
    .keywords {{
      font-style: italic;
      margin-top: 6pt;
    }}
    h2.section-heading {{
      font-size: 11pt;
      font-weight: bold;
      text-transform: uppercase;
      color: #003366;
      border-bottom: 1.5pt solid #003366;
      padding-bottom: 2pt;
      margin-top: 14pt;
      margin-bottom: 6pt;
    }}
    h3.subsection-heading {{
      font-size: 10pt;
      font-weight: bold;
      color: #003366;
      margin-top: 10pt;
      margin-bottom: 4pt;
    }}
    p {{
      text-align: justify;
      text-indent: 12pt;
      margin-top: 0;
      margin-bottom: 4pt;
    }}
    p.no-indent {{
      text-indent: 0;
    }}
    table.ieee-table {{
      width: 100%;
      border-collapse: collapse;
      margin-top: 8pt;
      margin-bottom: 8pt;
      font-size: 8.5pt;
    }}
    table.ieee-table th {{
      background-color: #003366;
      color: #ffffff;
      font-weight: bold;
      padding: 5px 6px;
      border: 1px solid #002244;
      text-align: center;
    }}
    table.ieee-table td {{
      padding: 4px 6px;
      border: 1px solid #cccccc;
      text-align: left;
    }}
    table.ieee-table tr:nth-child(even) {{
      background-color: #f9f9f9;
    }}
    .figure-box {{
      text-align: center;
      margin: 12pt 0;
      padding: 8pt;
      border: 1px solid #e0e0e0;
      background-color: #fafafa;
    }}
    .figure-caption {{
      font-size: 9pt;
      font-style: italic;
      color: #333333;
      margin-top: 6pt;
      text-align: center;
    }}
    .code-block {{
      font-family: "Courier New", Courier, monospace;
      font-size: 8.5pt;
      background-color: #f4f4f4;
      border: 1px solid #ddd;
      padding: 8px;
      margin: 8pt 0;
      white-space: pre-wrap;
      word-break: break-all;
    }}
  </style>
</head>
<body>

  <!-- Title -->
  <h1 class="paper-title">A Privacy-Preserving Multi-Document Intelligent Document Processing System Using a Local Vision-Language Model for Excel Extraction</h1>

  <!-- Authors Table -->
  <table class="authors-table">
    <tr>
      <td>
        <div class="author-name">Ignatius Selvarani X</div>
        <div>Assistant Professor</div>
        <div>Dept. of Computer Science &amp; Engineering</div>
        <div>Kamaraj College of Engineering &amp; Technology</div>
        <div>Virudhunagar, Tamil Nadu, India</div>
      </td>
      <td>
        <div class="author-name">Mohamed Ashif A</div>
        <div>UG Scholar</div>
        <div>Dept. of Computer Science &amp; Engineering</div>
        <div>Kamaraj College of Engineering &amp; Technology</div>
        <div>Virudhunagar, Tamil Nadu, India</div>
      </td>
      <td>
        <div class="author-name">Viswanth T</div>
        <div>UG Scholar</div>
        <div>Dept. of Computer Science &amp; Engineering</div>
        <div>Kamaraj College of Engineering &amp; Technology</div>
        <div>Virudhunagar, Tamil Nadu, India</div>
      </td>
      <td>
        <div class="author-name">Venkat Ragavan K</div>
        <div>UG Scholar</div>
        <div>Dept. of Computer Science &amp; Engineering</div>
        <div>Kamaraj College of Engineering &amp; Technology</div>
        <div>Virudhunagar, Tamil Nadu, India</div>
      </td>
    </tr>
  </table>

  <!-- Abstract Box -->
  <div class="abstract-box">
    <span class="abstract-title">Abstract—</span>Institutions handle many kinds of paper and digital documents, such as mark sheets, certificates, invoices, identity cards (ID cards), attendance registers, and administrative forms, that mix printed labels with handwritten or irregularly placed values. Staff need structured spreadsheets, but Optical Character Recognition (OCR) recovers characters without field structure, so each new document type needs its own custom mapping script. Sending such documents to a hosted model also raises severe privacy and data-protection concerns for sensitive institutional records. This paper presents an Intelligent Document Processing (IDP) system that first classifies an uploaded photograph, scan, or Portable Document Format (PDF) file, then extracts its fields into an Excel workbook using an open-weight Qwen Vision-Language Model (VLM) served through Ollama on institution-controlled hardware. A JavaScript Object Notation (JSON) schema selected for the document type constrains the output, so a new document type needs only a schema edit. Blank or low-confidence fields are routed to a human reviewer before export. The system is deployed as a shared web service for multiple users on an internal network. On 45 documents of 5 types, the classifier was correct for 95.6% of documents, field-level exact-match accuracy was 99.4%, and 100.0% of incorrect or blank fields were flagged for review. The local model was compared with a hosted model and Tesseract on the same pages, and the average time was 3.4 s per page on local GPU hardware. Results come from a small test set and should be read as a proof of concept.
    <div class="keywords">
      <strong>Index Terms—</strong> Intelligent document processing (IDP), document classification, optical character recognition (OCR), vision-language model (VLM), Qwen, Ollama, local inference, Excel export, schema-constrained JSON, human-in-the-loop review.
    </div>
  </div>

  <!-- GRAPH VISUAL FIGURES SECTION (EMBEDDED SVGs) -->
  <h2 class="section-heading">EMPIRICAL GRAPH FIGURES &amp; VISUAL EVIDENCE</h2>

  <!-- FIG 6 SVG -->
  <div class="figure-box">
    {svg6}
    <div class="figure-caption">Fig. 6. Human Review Threshold (θ) Operating Curve: Trade-off between Error Capture Rate (%) and Human Review Burden (% Flagged fields). Selected operating point θ = 0.70 captures 100.0% of errors while limiting review flags to 8.7%.</div>
  </div>

  <!-- FIG 7 SVG -->
  <div class="figure-box">
    {svg7}
    <div class="figure-caption">Fig. 7. Classification Accuracy and GPU Processing Latency per Document Type across 5 distinct categories.</div>
  </div>

  <!-- FIG 8 SVG -->
  <div class="figure-box">
    {svg8}
    <div class="figure-caption">Fig. 8. Head-to-Head Baseline Comparison: Field extraction accuracy, latency, and data privacy across Tesseract OCR (76.4%), DigitCNN (86.4%), hosted Gemini Flash (89.5%), and Proposed Local Qwen VLM (99.4%).</div>
  </div>

</body>
</html>
"""

    # Write HTML output
    with open(HTML_OUTPUT, "w", encoding="utf-8") as f:
        f.write(html_content)
    print(f"Generated HTML paper: {HTML_OUTPUT}")

    # Write DOC (MS Word native HTML alias)
    with open(DOC_OUTPUT, "w", encoding="utf-8") as f:
        f.write(html_content)
    print(f"Generated DOC paper (Word-compatible): {DOC_OUTPUT}")


if __name__ == "__main__":
    build_html_paper()
