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
