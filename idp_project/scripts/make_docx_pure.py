"""Generate native IEEE_Paper_IDP_Qwen.docx using ONLY Python standard library (zipfile + xml).

NO third-party dependencies required (no pip install python-docx needed!).
Generates valid OpenXML Word Document (.docx).
"""

import os
import zipfile
import xml.etree.ElementTree as ET

PROJECT_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
MD_PATH = os.path.join(PROJECT_DIR, "IEEE_Paper_IDP_Qwen.md")
DOCX_OUTPUT = os.path.join(PROJECT_DIR, "IEEE_Paper_IDP_Qwen.docx")


def create_content_types():
    return """<?xml version="1.0" encoding="UTF-8" standalone="yes"?>
<Types xmlns="http://schemas.openxmlformats.org/package/2006/content-types">
  <Default Extension="rels" ContentType="application/vnd.openxmlformats-package.relationships+xml"/>
  <Default Extension="xml" ContentType="application/xml"/>
  <Override PartName="/word/document.xml" ContentType="application/vnd.openxmlformats-officedocument.wordprocessingml.document.main+xml"/>
  <Override PartName="/word/styles.xml" ContentType="application/vnd.openxmlformats-officedocument.wordprocessingml.styles+xml"/>
</Types>"""


def create_rels():
    return """<?xml version="1.0" encoding="UTF-8" standalone="yes"?>
<Relationships xmlns="http://schemas.openxmlformats.org/package/2006/relationships">
  <Relationship Id="rId1" Type="http://schemas.openxmlformats.org/officeDocument/2006/relationships/officeDocument" Target="word/document.xml"/>
</Relationships>"""


def create_doc_rels():
    return """<?xml version="1.0" encoding="UTF-8" standalone="yes"?>
<Relationships xmlns="http://schemas.openxmlformats.org/package/2006/relationships">
  <Relationship Id="rId1" Type="http://schemas.openxmlformats.org/officeDocument/2006/relationships/styles" Target="styles.xml"/>
</Relationships>"""


def create_styles():
    return """<?xml version="1.0" encoding="UTF-8" standalone="yes"?>
<w:styles xmlns:w="http://schemas.openxmlformats.org/wordprocessingml/2006/main">
  <w:docDefaults>
    <w:rPrDefault>
      <w:rPr>
        <w:rFonts w:ascii="Times New Roman" w:hAnsi="Times New Roman" w:cs="Times New Roman"/>
        <w:sz w:val="20"/>
        <w:szCs w:val="20"/>
      </w:rPr>
    </w:rPrDefault>
  </w:docDefaults>
</w:styles>"""


def build_document_xml():
    with open(MD_PATH, "r", encoding="utf-8") as f:
        lines = f.readlines()

    body_elements = []

    for line in lines:
        line_str = line.strip()
        if not line_str:
            continue

        # Headings
        if line_str.startswith("# "):
            title_text = line_str[2:].replace("**", "").strip()
            body_elements.append(
                f'<w:p><w:pPr><w:jc w:val="center"/><w:spacing w:before="240" w:after="120"/></w:pPr>'
                f'<w:r><w:rPr><w:b/><w:sz w:val="36"/><w:color w:val="003366"/></w:rPr><w:t>{escape_xml(title_text)}</w:t></w:r></w:p>'
            )
        elif line_str.startswith("## "):
            h1_text = line_str[3:].replace("**", "").strip()
            body_elements.append(
                f'<w:p><w:pPr><w:spacing w:before="240" w:after="120"/><w:keepNext/></w:pPr>'
                f'<w:r><w:rPr><w:b/><w:sz w:val="24"/><w:color w:val="003366"/></w:rPr><w:t>{escape_xml(h1_text)}</w:t></w:r></w:p>'
            )
        elif line_str.startswith("### "):
            h2_text = line_str[4:].replace("**", "").strip()
            body_elements.append(
                f'<w:p><w:pPr><w:spacing w:before="180" w:after="80"/><w:keepNext/></w:pPr>'
                f'<w:r><w:rPr><w:b/><w:sz w:val="22"/><w:color w:val="003366"/></w:rPr><w:t>{escape_xml(h2_text)}</w:t></w:r></w:p>'
            )
        elif line_str.startswith("TABLE ") or line_str.startswith("FIG. "):
            body_elements.append(
                f'<w:p><w:pPr><w:jc w:val="center"/><w:spacing w:before="180" w:after="60"/><w:keepNext/></w:pPr>'
                f'<w:r><w:rPr><w:b/><w:sz w:val="19"/><w:color w:val="003366"/></w:rPr><w:t>{escape_xml(line_str)}</w:t></w:r></w:p>'
            )
        elif line_str.startswith("|"):
            # Table row parsing skipped for paragraph text simplicity or basic XML table
            pass
        else:
            # Paragraph
            text_clean = line_str.replace("**", "").replace("*", "").replace("`", "")
            body_elements.append(
                f'<w:p><w:pPr><w:jc w:val="both"/><w:spacing w:after="80"/><w:ind w:firstLine="240"/></w:pPr>'
                f'<w:r><w:t>{escape_xml(text_clean)}</w:t></w:r></w:p>'
            )

    body_xml = "".join(body_elements)

    return f"""<?xml version="1.0" encoding="UTF-8" standalone="yes"?>
<w:document xmlns:w="http://schemas.openxmlformats.org/wordprocessingml/2006/main">
  <w:body>
    {body_xml}
    <w:sectPr>
      <w:pgSz w:w="12240" w:h="15840"/>
      <w:pgMar w:top="1080" w:right="1080" w:bottom="1080" w:left="1080"/>
    </w:sectPr>
  </w:body>
</w:document>"""


def escape_xml(text):
    return (
        text.replace("&", "&amp;")
        .replace("<", "&lt;")
        .replace(">", "&gt;")
        .replace('"', "&quot;")
        .replace("'", "&apos;")
    )


def generate_docx():
    content_types = create_content_types()
    rels = create_rels()
    doc_rels = create_doc_rels()
    styles = create_styles()
    doc_xml = build_document_xml()

    with zipfile.ZipFile(DOCX_OUTPUT, "w", zipfile.ZIP_DEFLATED) as zf:
        zf.writestr("[Content_Types].xml", content_types)
        zf.writestr("_rels/.rels", rels)
        zf.writestr("word/_rels/document.xml.rels", doc_rels)
        zf.writestr("word/styles.xml", styles)
        zf.writestr("word/document.xml", doc_xml)

    print(f"Direct native DOCX generated successfully without dependencies: {DOCX_OUTPUT}")


if __name__ == "__main__":
    generate_docx()
