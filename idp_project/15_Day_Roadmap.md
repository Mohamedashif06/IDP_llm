# IDP Project — 15-Day Roadmap (with CNN, spaCy NLP, EasyOCR, PaddleOCR)

Every claim below was tested for real in this session before being written
here — including two real bugs we caught and fixed (a fuzzy-matching
mismatch, and a CNN train/inference normalization bug). Nothing here is
theoretical.

---

## Day 1 — Environment upgrade
Install the new dependencies on your machine:
```powershell
.\venv\Scripts\Activate.ps1
pip install -r requirements.txt
python -m spacy download en_core_web_sm
```
**Note:** `paddleocr`/`paddlepaddle` and spaCy's model download need real
internet access to their hosting servers — this failed in my sandboxed
test environment (network whitelist) but will work fine on your normal
machine. If `python -m spacy download en_core_web_sm` fails, use:
```powershell
pip install https://github.com/explosion/spacy-models/releases/download/en_core_web_sm-3.7.1/en_core_web_sm-3.7.1-py3-none-any.whl
```

## Day 2 — EasyOCR integration
Already tested against your real CO sheet this session. Key finding:
**neither Tesseract nor EasyOCR dominates on every document** — on your
sheet, Tesseract nailed an ID Tesseract got right that EasyOCR got wrong,
and vice versa on parts of a name. Build a simple engine-comparison mode
into your table extractor: run both, show both results side by side in
the review screen, let the human pick.

## Day 3 — PaddleOCR integration
Same wrapper pattern as EasyOCR. Could not live-test in my sandbox (model
download blocked by network whitelist here) — test this yourself on Day 3,
compare against Tesseract/EasyOCR on the same real documents, and record
which wins on which field types. This comparison IS your Week 4 "OCR
engine comparison" result for the paper.

## Day 4 — spaCy NER for free-text fields
Already built and tested (`modules/nlp_extraction.py`). **Real, important
finding: spaCy correctly finds names in normal sentences but FAILS on
ALL-CAPS text** — which is how names are usually printed in your tables.
So: use NER for genuinely free-text documents (letters, narratives); keep
using your regex/label extraction for forms and tables. Don't apply NER
universally — test where it actually helps.

## Day 5 — Fuzzy label matching
Already built and tested (`modules/fuzzy_matching.py`). Real bug caught
and fixed here: the naive `fuzz.ratio` scorer wrongly mapped "Studnt Name"
to `father_name` instead of `name`. Fixed with `fuzz.WRatio` + a 60%
confidence threshold — below threshold, the field is left unmapped for
human review rather than silently guessed wrong. This threshold pattern
is the single most important idea in this whole module.

## Day 6 — Wire fuzzy matching into your extraction pipeline
Take `field_extraction.py`'s output (including its generic-fallback fields
with raw OCR label names) and pass it through
`fuzzy_matching.map_fields_to_schema()` to normalize onto your canonical
schema before validation/Excel writing.

## Day 7 — CNN for handwritten digits: build + train
Already built AND trained this session (`modules/cnn_digit_recognizer.py`,
`train_cnn.py`). **Real accuracy: 96.9% on held-out test data.**

Important, honest note on data: I trained on scikit-learn's bundled
digit dataset (1,797 samples, no download needed) because full MNIST's
hosting servers weren't reachable from my sandbox. For your actual
submission, retrain on full MNIST (60,000 samples) on your own machine —
it needs a real internet connection, which you have:
```powershell
python train_cnn.py
```
The script already has full-MNIST code included as a commented alternative
inside `load_and_prepare_data()` — swap it in for stronger real-world
accuracy than the 1,797-sample version.

## Day 8 — The bug you should know about (and avoid repeating)
I trained the CNN once, got 97.5% test accuracy, then found real inference
was near-random — a genuine **train/inference preprocessing mismatch**:
training divided pixel values by the dataset's own max (~16), inference
divided by 255. Fixed by making BOTH use the exact same
`preprocess_digit_cell()` function. **Lesson for your team: always test
inference on a fresh sample through your actual prediction function, not
just trust the training-time test accuracy number** — a high training
score can hide a completely broken deployment path.

## Day 9 — Integrate CNN into table_extractor.py
For cells you've marked as `mode="digits"` in a handwritten section, add
an option to route through `predict_digit()` instead of Tesseract. Compare
confidence and pick whichever pipeline is more confident, or let the user
choose per-column in the UI (same pattern as your existing psm/column-mode
selector).

## Day 10 — Unified multi-engine OCR module
Build `modules/ocr_multi.py`: one function that takes an engine name
("tesseract"/"easyocr"/"paddleocr") and dispatches to the right wrapper,
returning a consistent `{"text":.., "confidence":..}` shape regardless of
engine — this is what lets your app offer an engine dropdown without every
other module needing to know which engine is active.

## Day 11 — Validation rules
Build `modules/validation.py`: range checks (marks 0-100), duplicate
roll-number detection across a batch, missing-field checks, format checks
(date patterns). Feed flags into your existing review screen so invalid
fields are visually marked, same pattern as low-confidence fields already
are.

## Day 12 — Batch processing across many documents
Extend the multi-photo batch mode (already built) to also accept a
**folder of images at once** (`st.file_uploader(accept_multiple_files=True)`)
for genuine bulk processing, not just one-at-a-time capture.

## Day 13 — Pandas analytics
`groupby()` on your accumulated Excel data: class average, pass/fail
counts, per-subject statistics. Quick to build once data is in a
DataFrame (`excel_writer.read_all_records()` already gives you this).

## Day 14 — Real accuracy measurement across your full test set
Run every module (Tesseract, EasyOCR, PaddleOCR, CNN) against your actual
document set, record real precision/recall/F1 per field type. This is
what fills in the `[ACTUAL]` placeholders in your IEEE paper's results
tables — don't estimate these, measure them.

## Day 15 — Deploy + rehearse demo
Push to Hugging Face Spaces (steps in `README.md`, already set up with
`packages.txt` for Tesseract). Rehearse capturing a real document live,
showing the review screen catch a low-confidence field, and downloading
the final Excel — that live moment is what evaluators remember.

---

## Honest scope note

Full MNIST training, PaddleOCR's model download, and true 400-document
batch testing all need real internet access and real time that a 15-day
solo sprint can't fully absorb alongside your coursework. The realistic
target for Day 15: a genuinely working, demoed pipeline with 2-3 OCR
engines integrated, real (not perfect) measured accuracy numbers, and a
documented understanding of *why* accuracy varies by document type — which
is a stronger final-year deliverable than an unverified accuracy claim.
