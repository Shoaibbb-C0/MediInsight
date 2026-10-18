import pytest
from fastapi.testclient import TestClient
from app.main import app
from app.core.config import Settings

client = TestClient(app)

def test_health_check():
    response = client.get("/health")
    assert response.status_code == 200
    data = response.json()
    assert data["status"] == "healthy"
    assert data["environment"] == "development"

def make_lab_pdf():
    import pymupdf
    doc = pymupdf.open()
    page = doc.new_page()
    page.insert_text((40, 60), "Fasting Blood Glucose : 124.5 mg/dL (70 - 99 mg/dL)")
    return doc.tobytes()


def test_upload_valid_file():
    response = client.post("/api/v1/reports/upload", files={"file": ("blood_test.pdf", make_lab_pdf(), "application/pdf")})
    assert response.status_code == 200
    data = response.json()
    assert data["filename"] == "blood_test.pdf"
    assert data["is_synthetic_fixture"] is False
    extracted = client.get(f"/api/v1/reports/{data['report_id']}/extractions").json()
    assert any(item["value"] == "124.5" for item in extracted)


def test_empty_extraction_never_substitutes_demo(monkeypatch):
    from app.api.endpoints.reports import engine
    monkeypatch.setattr(engine, "process_document", lambda *_: [])
    response = client.post("/api/v1/reports/upload", files={"file": ("unreadable.pdf", b"empty", "application/pdf")})
    assert response.status_code == 422
    assert "No demonstration values" in response.json()["detail"]


def test_unknown_report_does_not_return_synthetic_values():
    for endpoint in ["extractions", "summary", "questions", "nutrition/plan", "doctors", "pdf"]:
        assert client.get(f"/api/v1/reports/not-a-real-report/{endpoint}").status_code == 404


def test_upload_unsupported_file_fails_safely():
    file_content = b"malicious executable or unsupported format"
    files = {"file": ("report.exe", file_content, "application/octet-stream")}
    response = client.post("/api/v1/reports/upload", files=files)
    assert response.status_code == 400
    assert "Unsupported file format" in response.json()["detail"]

def test_get_extractions_and_verify():
    # 1. Fetch extractions
    response = client.get("/api/v1/reports/rep_demo_fixture/extractions")
    assert response.status_code == 200
    extractions = response.json()
    assert len(extractions) > 0
    
    # 2. Verify low confidence biomarker
    target = next((item for item in extractions if item["requires_verification"]), extractions[0])
    verify_payload = {
        "biomarker_id": target["id"],
        "corrected_value": "6.2",
        "patient_note": "Looked closely at paper printout"
    }
    v_res = client.post(f"/api/v1/reports/rep_demo_fixture/verify", json=verify_payload)
    assert v_res.status_code == 200
    assert v_res.json()["status"] == "success"
    assert v_res.json()["updated_biomarker"]["corrected_value"] == "6.2"

def test_questionnaire_precedes_report_flow():
    report_id = "rep_flow_test"
    
    # 1. Upload
    files = {"file": ("panel.pdf", make_lab_pdf(), "application/pdf")}
    up_res = client.post("/api/v1/reports/upload", files=files)
    report_id = up_res.json()["report_id"]
    
    # 2. Get questions
    q_res = client.get(f"/api/v1/reports/{report_id}/questions")
    assert q_res.status_code == 200
    questions = q_res.json()["questions"]
    assert len(questions) >= 1
    
    # 3. Submit answers
    answers_payload = {
        "report_id": report_id,
        "answers": [
            {"question_id": questions[0]["id"], "selected_option_id": questions[0]["options"][0]["id"]}
        ]
    }
    sub_res = client.post(f"/api/v1/reports/{report_id}/questions/submit", json=answers_payload)
    assert sub_res.status_code == 200
    
    # 4. Final summary in EN
    summary_res = client.get(f"/api/v1/reports/{report_id}/summary?lang=en")
    assert summary_res.status_code == 200
    summary = summary_res.json()
    assert "patient_summary" in summary
    assert len(summary["prioritized_attention"]) > 0
    assert "disclaimer" in summary
    assert summary["language"] == "en"

    # 5. Final summary in Hindi
    hi_res = client.get(f"/api/v1/reports/{report_id}/summary?lang=hi")
    assert hi_res.status_code == 200
    hi_summary = hi_res.json()
    assert hi_summary["language"] == "hi"
    assert "जाँच में" in hi_summary["patient_summary"] or "परिणाम" in hi_summary["patient_summary"]

    # 6. Final summary in Marathi
    mr_res = client.get(f"/api/v1/reports/{report_id}/summary?lang=mr")
    assert mr_res.status_code == 200
    mr_summary = mr_res.json()
    assert mr_summary["language"] == "mr"
    assert "तपासणीत" in mr_summary["patient_summary"] or "निकाल" in mr_summary["patient_summary"]

    # 7. PDF download endpoints in all three languages
    for lang in ["en", "hi", "mr"]:
        pdf_res = client.get(f"/api/v1/reports/{report_id}/pdf?lang={lang}")
        assert pdf_res.status_code == 200
        assert pdf_res.headers["content-type"] == "application/pdf"
        assert len(pdf_res.content) > 1000
        import pymupdf
        doc = pymupdf.open(stream=pdf_res.content, filetype="pdf")
        assert "mg/dL" in "".join(page.get_text() for page in doc), "Source units must survive Devanagari PDF rendering"

def test_production_fails_closed_when_credentials_absent():
    prod_settings = Settings()
    prod_settings.ENVIRONMENT = "production"
    prod_settings.SUPABASE_URL = None
    prod_settings.SUPABASE_KEY = None
    
    with pytest.raises(RuntimeError) as exc_info:
        prod_settings.validate_production()
    assert "PRODUCTION CONFIG ERROR" in str(exc_info.value)


def test_declared_request_limit_rejects_before_processing():
    response = client.post("/api/v1/reports/upload", headers={"Content-Length": str(100*1024*1024)}, content=b"small")
    assert response.status_code == 413


def test_nutrition_rejects_unknown_safety_preferences():
    response = client.post("/api/v1/reports/rep_demo_fixture/nutrition/generate", json={"report_id":"rep_demo_fixture", "dietary_preference":"unknown", "age_group":"unknown"})
    assert response.status_code == 422


def test_chunked_request_limit_is_bounded(monkeypatch):
    from app.core.config import settings
    monkeypatch.setattr(settings, "MAX_FILE_SIZE_MB", 0)
    def chunks():
        for _ in range(20): yield b"a" * 65536
    response = client.post("/api/v1/auth/login", content=chunks(), headers={"Content-Type":"application/json"})
    assert response.status_code == 413
