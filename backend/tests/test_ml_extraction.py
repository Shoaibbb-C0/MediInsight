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
