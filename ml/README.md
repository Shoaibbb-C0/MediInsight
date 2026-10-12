# Machine Learning Architecture Boundary for Simplifier 2.0

This directory holds the OCR, medical entity extraction, and classification pipeline artifacts.

## Module Boundaries:
- `models/`: Weights and ONNX/PyTorch model checkpoints (e.g., table extraction, NER, layout parser).
- `data/`: Sample datasets and annotation schemas (raw, processed).
- `pipelines/`: OCR extractors (RapidOCR / PaddleOCR / PyMuPDF) and normalizers.

## Phase 1 Status:
Local development uses explicitly labeled synthetic fixtures (`backend/app/fixtures/synthetic_data.py`).
In Phase 2, the pipeline connecting OCR detection boxes to normalized medical entity schemas will be implemented here.
