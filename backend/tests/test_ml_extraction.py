import pytest
from app.services.extraction_service import ExtractionEngine
from app.services.image_processor import assess_image_quality, deskew_and_enhance
import numpy as np

def test_extraction_engine_model_loaded():
    engine = ExtractionEngine()
    assert engine.model is not None, "Trained ML model checkpoint should be loaded"
    assert len(engine.model.classes_) >= 10

def test_extraction_engine_inference_on_text():
    engine = ExtractionEngine()
    # Test line from casual report
    line = "Fasting Blood Glucose : 124.5 mg/dL (70 - 99 mg/dL)"
    probs = engine.model.predict_proba([line])[0]
    best_idx = np.argmax(probs)
    predicted_canonical = engine.model.classes_[best_idx]
    assert predicted_canonical == "glucose_fasting"
    assert probs[best_idx] > 0.80

def test_image_quality_assessment():
    # Synthetic flat image
    img = np.ones((400, 400, 3), dtype=np.uint8) * 255
    metrics = assess_image_quality(img)
    assert "blur_score" in metrics
    assert "is_blurry" in metrics
    assert "glare_ratio" in metrics

def test_numeric_measurement_parser():
    engine = ExtractionEngine()
    assert engine.parse_numeric_measurement("HbA1c 6.4 %") == "6.4"
    assert engine.parse_numeric_measurement("Total Cholesterol 215 mg/dL") == "215"
    assert engine.parse_numeric_measurement("No numbers here") is None

def test_printed_lab_interval_and_unit_are_preserved():
    import pymupdf
    doc = pymupdf.open()
    page = doc.new_page()
    page.insert_text((40, 60), "Fasting Blood Glucose : 6.2 mmol/L (3.9 - 5.5 mmol/L)")
    values = ExtractionEngine().process_document(doc.tobytes(), "source.pdf")
    item = next(item for item in values if item.canonical_name == "glucose_fasting")
    assert item.value == "6.2"
    assert item.unit == "mmol/L"
    assert item.reference_range == "3.9 - 5.5"


def test_multipage_column_values_and_distinct_reports():
    import pymupdf
    engine = ExtractionEngine()
    def document(values):
        doc = pymupdf.open()
        for value in values:
            page = doc.new_page()
            for x, text in [(40, "Fasting Blood Glucose"), (250, str(value)), (310, "mg/dL"), (400, "70 - 99")]:
                page.insert_text((x, 70), text)
        return doc.tobytes()
    first = engine.process_document(document([124.5, 140.2]), "columns.pdf")
    second = engine.process_document(document([88.4]), "different.pdf")
    assert [(item.value, item.source_page) for item in first] == [("124.5", 1), ("140.2", 2)]
    assert [item.value for item in second] == ["88.4"]
    assert all(item.reference_range == "70 - 99" for item in first)


def test_missing_printed_interval_is_review_required():
    import pymupdf
    doc = pymupdf.open()
    doc.new_page().insert_text((40, 60), "Fasting Blood Glucose 124.5 mg/dL")
    values = ExtractionEngine().process_document(doc.tobytes(), "missing-range.pdf")
    assert len(values) == 1
    assert values[0].reference_range == ""
    assert values[0].requires_verification
    assert values[0].status == "needs_review"


def test_page_limit_is_not_silent_truncation():
    import pymupdf
    doc = pymupdf.open()
    for _ in range(11): doc.new_page()
    with pytest.raises(ValueError, match="1–10"):
        ExtractionEngine().process_document(doc.tobytes(), "too-many.pdf")
