"""
Comprehensive Tests for Feature 3 — Production-Grade Doctor Discovery, Maps, and Atomic Appointments.
Covers:
1. Grounded specialty recommendation engine with medical rationale.
2. Urgent warning symptom alerting.
3. Indian city and PIN code location geocoding & Haversine distance calculation.
4. Provider discovery with verified vs external listings.
5. Atomic appointment booking & strict double-booking prevention.
6. Rescheduling and cancellation slot lifecycle.
7. Two-user isolation for appointments.
8. Multilingual endpoint verification (en, hi, mr).
"""

import pytest
from fastapi.testclient import TestClient
from app.main import app
from app.services.location_service import resolve_patient_location, haversine_distance_km
from app.services.doctor_database import search_providers
from app.services.specialty_recommender import generate_specialty_recommendations
from app.services.appointment_service import (
    create_appointment,
    reschedule_appointment,
    cancel_appointment,
    get_user_appointments,
    APPOINTMENTS_DB,
    RESERVED_SLOTS_LEDGER
)
from app.schemas.doctor import DirectBookingRequest, RescheduleBookingRequest, CancelBookingRequest

client = TestClient(app)

@pytest.fixture(autouse=True)
def clean_appointments_state():
    APPOINTMENTS_DB.clear()
    RESERVED_SLOTS_LEDGER.clear()
    yield
    APPOINTMENTS_DB.clear()
    RESERVED_SLOTS_LEDGER.clear()

def test_specialty_recommender_glucose_and_kidney():
    findings = [
        {"canonical_name": "glucose_fasting", "name": "Fasting Blood Glucose", "value": "118", "unit": "mg/dL", "status": "high"},
        {"canonical_name": "creatinine_serum", "name": "Serum Creatinine", "value": "1.8", "unit": "mg/dL", "status": "high"}
    ]
    recs_en = generate_specialty_recommendations(findings, lang="en")
    recs_hi = generate_specialty_recommendations(findings, lang="hi")
    recs_mr = generate_specialty_recommendations(findings, lang="mr")

    spec_ids = [r.specialty_id for r in recs_en]
    assert "endocrinology" in spec_ids
    assert "nephrology" in spec_ids
    assert "general_physician" in spec_ids  # Safe holistic fallback always present

    # Test Hindi and Marathi localization
    endo_hi = next(r for r in recs_hi if r.specialty_id == "endocrinology")
    assert "एंडोक्रिनोलॉजिस्ट" in endo_hi.specialty_name
    endo_mr = next(r for r in recs_mr if r.specialty_id == "endocrinology")
    assert "मधुमेह" in endo_mr.specialty_name

def test_specialty_recommender_urgent_bleeding_warning():
    findings = [
        {"canonical_name": "hemoglobin", "name": "Hemoglobin", "value": "8.1", "unit": "g/dL", "status": "low"}
    ]
    answers = [{"question_id": "q_hemo_bleeding_signs", "selected_option_id": "bleed_concerning"}]
    recs = generate_specialty_recommendations(findings, answers=answers, lang="en")
    assert any(r.urgent_warning is not None and "URGENT" in r.urgent_warning for r in recs)

def test_location_geocoding_city_and_pincode():
    # 1. City query
    loc_mumbai = resolve_patient_location(city_or_pincode="Mumbai")
    assert loc_mumbai.city == "Mumbai"
    assert loc_mumbai.coordinates is not None
    assert abs(loc_mumbai.coordinates.lat - 19.0760) < 0.01

    # 2. PIN code query (Pune prefix 411)
    loc_pune_pin = resolve_patient_location(city_or_pincode="411004")
    assert loc_pune_pin.city == "Pune"
    assert "PIN 411004" in loc_pune_pin.display_name

    # 3. Coordinate query (Bandra coordinates)
    loc_coords = resolve_patient_location(lat=19.0596, lng=72.8295)
    assert loc_coords.city == "Mumbai"
    assert loc_coords.is_approximate is False

def test_haversine_distance_calculation():
    # Mumbai (19.0760, 72.8777) to Pune (18.5204, 73.8567) is approx 115-125 km
    dist = haversine_distance_km(19.0760, 72.8777, 18.5204, 73.8567)
    assert 110.0 <= dist <= 130.0

def test_provider_discovery_api():
    res = client.get("/api/v1/reports/rep_demo_fixture/doctors?lang=en")
    assert res.status_code == 200
    data = res.json()
    assert "recommended_specialties" in data
    assert "providers" in data
    assert len(data["providers"]) > 0

    # Ensure provider cards have groundings
    first_prov = data["providers"][0]
    assert first_prov["phone_available"] is False
    assert first_prov["phone"] is None
    assert first_prov["address"] is not None
    assert first_prov["verification_status"] == "unverified"
    assert data["is_demo_mode"] is True
    assert data["live_provider_api_configured"] is False

def test_atomic_appointment_booking_and_double_booking_prevention():
    req1 = DirectBookingRequest(
        doctor_id="prov_mum_01",
        slot="Tomorrow at 10:00 AM",
        patient_name="Patient Alpha"
    )
    # First booking succeeds
    res1 = create_appointment("user_alpha", req1)
    assert res1["status"] == "success"
    booking_id = res1["appointment"]["booking_id"]

    # Immediate second attempt by another patient for the SAME slot must fail
    req2 = DirectBookingRequest(
        doctor_id="prov_mum_01",
        slot="Tomorrow at 10:00 AM",
        patient_name="Patient Beta"
    )
    res2 = create_appointment("user_beta", req2)
    assert res2["status"] == "error"
    assert "already booked" in res2["message"]

def test_reschedule_and_cancel_lifecycle():
    req = DirectBookingRequest(
        doctor_id="prov_mum_01",
        slot="Tomorrow at 10:00 AM",
        patient_name="Patient Gamma"
    )
    b_res = create_appointment("user_gamma", req)
    booking_id = b_res["appointment"]["booking_id"]

    # Reschedule
    resched = reschedule_appointment("user_gamma", RescheduleBookingRequest(
        booking_id=booking_id,
        new_slot="Thursday at 11:15 AM"
    ))
    assert resched["status"] == "success"
    assert resched["appointment"]["slot"] == "Thursday at 11:15 AM"
    assert resched["appointment"]["is_demo"] is True

    # Now the old slot (Tomorrow at 10:00 AM) must be free again for another user
    rebook = create_appointment("user_delta", DirectBookingRequest(
        doctor_id="prov_mum_01",
        slot="Tomorrow at 10:00 AM",
        patient_name="Patient Delta"
    ))
    assert rebook["status"] == "success"

    # Cancel booking
    canc = cancel_appointment("user_gamma", CancelBookingRequest(booking_id=booking_id))
    assert canc["status"] == "success"
    assert canc["appointment"]["status"] == "cancelled"

def test_two_user_appointment_isolation():
    req_u1 = DirectBookingRequest(
        doctor_id="prov_mum_01",
        slot="Tomorrow at 02:30 PM",
        patient_name="User One"
    )
    create_appointment("user_101", req_u1)

    req_u2 = DirectBookingRequest(
        doctor_id="prov_pune_01",
        slot="Wednesday at 04:00 PM",
        patient_name="User Two"
    )
    create_appointment("user_202", req_u2)

    apps_u1 = get_user_appointments("user_101")
    assert len(apps_u1) == 1
    assert apps_u1[0]["patient_name"] == "User One"

    apps_u2 = get_user_appointments("user_202")
    assert len(apps_u2) == 1
    assert apps_u2[0]["patient_name"] == "User Two"
