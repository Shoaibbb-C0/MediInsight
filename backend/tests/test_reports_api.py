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

def test_upload_valid_file():
    file_content = b"%PDF-1.4 demo test content"
    files = {"file": ("blood_test.pdf", file_content, "application/pdf")}
    response = client.post("/api/v1/reports/upload", files=files)
    assert response.status_code == 200
    data = response.json()
    assert "report_id" in data
    assert data["filename"] == "blood_test.pdf"
    assert data["file_type"] == "pdf"
    assert data["is_synthetic_fixture"] is True

def test_upload_unsupported_file_fails_safely():
    file_content = b"malicious executable or unsupported format"
    files = {"file": ("report.exe", file_content, "application/octet-stream")}
    response = client.post("/api/v1/reports/upload", files=files)
    assert response.status_code == 400
    assert "Unsupported file format" in response.json()["detail"]

def test_get_extractions_and_verify():
    # 1. Fetch extractions
    response = client.get("/api/v1/reports/rep_test123/extractions")
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
    v_res = client.post(f"/api/v1/reports/rep_test123/verify", json=verify_payload)
    assert v_res.status_code == 200
    assert v_res.json()["status"] == "success"
    assert v_res.json()["updated_biomarker"]["corrected_value"] == "6.2"

def test_questionnaire_precedes_report_flow():
    report_id = "rep_flow_test"
    
    # 1. Upload
    files = {"file": ("panel.png", b"fakeimagebytes", "image/png")}
    up_res = client.post("/api/v1/reports/upload", files=files)
    report_id = up_res.json()["report_id"]
    
    # 2. Get questions
    q_res = client.get(f"/api/v1/reports/{report_id}/questions")
    assert q_res.status_code == 200
    questions = q_res.json()["questions"]
    assert len(questions) >= 2
    
    # 3. Submit answers
    answers_payload = {
        "report_id": report_id,
        "answers": [
            {"question_id": questions[0]["id"], "selected_option_id": questions[0]["options"][0]["id"]}
        ]
    }
    sub_res = client.post(f"/api/v1/reports/{report_id}/questions/submit", json=answers_payload)
    assert sub_res.status_code == 200
    
    # 4. Final summary
    summary_res = client.get(f"/api/v1/reports/{report_id}/summary")
    assert summary_res.status_code == 200
    summary = summary_res.json()
    assert "patient_summary" in summary
    assert len(summary["key_findings"]) > 0
    assert "disclaimer" in summary

def test_production_fails_closed_when_credentials_absent():
    prod_settings = Settings()
    prod_settings.ENVIRONMENT = "production"
    prod_settings.SUPABASE_URL = None
    prod_settings.SUPABASE_KEY = None
    
    with pytest.raises(RuntimeError) as exc_info:
        prod_settings.validate_production()
    assert "PRODUCTION CONFIG ERROR" in str(exc_info.value)
