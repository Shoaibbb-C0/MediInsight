# Extraction and ML boundary

The application uses PyMuPDF digital table-row extraction, per-page RapidOCR/ONNX for scans/photos, and the bundled scikit-learn canonical-test classifier. Printed source values, units, reference intervals and page/line provenance are preserved. Uncertain/ambiguous measurements are excluded until reviewed; there is no synthetic fallback for real uploads.

`ml/models/biomarker_extractor_v1.joblib` is a trusted repository asset, not an uploaded patient model. The metadata file records metrics on the **synthetic** train/validation/test corpus. Those scores do not establish clinical accuracy, hospital-layout coverage, multilingual source OCR accuracy or performance on photographed real patient reports.

Local automated tests exercise generated digital/multi-page/column PDFs, PNG/JPG/JPEG images, scanned PDF OCR, invalid input and source-preservation behavior. The vocabulary/unit patterns remain limited. A representative de-identified corpus and qualified clinical/native-language review are required before patient launch.

`backend/scripts/check_runtime.py` verifies the checkpoint, PDF fonts and OCR initialization during backend builds. Public OCR model assets must be available at build time; no medical document is sent to a hosted OCR API by this pipeline.
