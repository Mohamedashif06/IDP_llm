import json
import sys
import types

import numpy as np

import app


def test_extract_with_gemini_uses_supported_model(monkeypatch):
    captured = {}

    class FakeResponse:
        text = json.dumps({
            "fields": {"name": "Alice"},
            "tables": [],
            "text": "Alice",
            "needs_review": [],
        })

    class FakeClient:
        def __init__(self, api_key):
            self.api_key = api_key
            self.models = self

        def generate_content(self, **kwargs):
            captured.update(kwargs)
            return FakeResponse()

    fake_google = types.ModuleType("google")
    fake_genai = types.ModuleType("google.genai")
    fake_genai.Client = FakeClient
    fake_genai.types = types.SimpleNamespace(
        Part=types.SimpleNamespace(from_bytes=lambda **kwargs: {"bytes": kwargs.get("data")}),
        GenerateContentConfig=lambda **kwargs: kwargs,
    )
    fake_google.genai = fake_genai

    monkeypatch.setitem(sys.modules, "google", fake_google)
    monkeypatch.setitem(sys.modules, "google.genai", fake_genai)

    from modules.gemini_extractor import extract_with_gemini

    result = extract_with_gemini(b"fake-image", "image/png", "example.png", "test-key")

    assert captured["model"] == "gemini-3.6-flash"
    assert result["engine"] == "gemini-3.6-flash"


def test_repair_and_parse_json_handles_fenced_and_truncated_output():
    from modules.gemini_extractor import _repair_and_parse_json

    fenced_json = "```json\n{\"fields\": {\"bill_no\": \"101\"}}\n```"
    parsed = _repair_and_parse_json(fenced_json)
    assert parsed.get("fields", {}).get("bill_no") == "101"


def test_process_sheet_auto_saves_to_excel_when_master_workbook_is_missing(monkeypatch, tmp_path):
    excel_path = tmp_path / "records.xlsx"
    json_path = tmp_path / "last_record.json"

    monkeypatch.setattr(app, "OUTPUT_FILE", str(excel_path))
    monkeypatch.setattr(app, "JSON_FILE", str(json_path))

    monkeypatch.setattr(
        app,
        "extract_student_sheet",
        lambda image: {
            "record": {"registration_no": "123", "name": "Alice"},
            "confidence": {"registration_no": 95, "name": 90},
            "warnings": [],
        },
    )

    calls = []

    def fake_append_record(record, workbook_path, sheet_name):
        calls.append(("append", workbook_path, record, sheet_name))
        excel_path.parent.mkdir(parents=True, exist_ok=True)
        with open(workbook_path, "wb") as handle:
            handle.write(b"fake")
        return 2

    monkeypatch.setattr(app, "append_record", fake_append_record)

    status, record, dataframe, confidence = app.process_sheet(np.zeros((10, 10, 3), dtype=np.uint8))

    assert "Auto-saved" in status
    assert record["registration_no"] == "123"
    assert any(call[0] == "append" for call in calls)
    assert json_path.exists()
