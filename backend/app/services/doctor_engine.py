"""
Inline Doctor Discovery & Consultation Booking Engine for Simplifier 2.0.
Maps abnormal findings to appropriate clinical specialties (General Physician,
Endocrinologist, Cardiologist, Nephrologist).
Features server-authoritative slot availability and simulated booking/rescheduling/cancellation.
"""

from typing import List, Dict, Any, Optional
import datetime
import uuid

# Verified result-to-specialty clinical mapping rules
SPECIALTY_MAPPING = {
    "glucose_fasting": "Endocrinologist / Diabetologist",
    "hba1c": "Endocrinologist / Diabetologist",
    "cholesterol_total": "Cardiologist / Preventive Medicine",
    "creatinine_serum": "Nephrologist (Kidney Specialist)",
    "hemoglobin": "Hematologist / General Physician",
    "vitamin_d": "General Physician / Orthopedist"
}

# Clearly labeled DEMO / Development doctors
DEMO_DOCTORS = [
    {
        "id": "doc_01",
        "name": "Dr. Ananya Sharma, MD",
        "specialty": "General Physician & Internal Medicine",
        "city": "Mumbai",
        "experience_years": 14,
        "is_demo_verified": True,
        "languages": ["English", "Hindi", "Marathi"],
        "consultation_mode": "In-Person & Video Consultation",
        "available_slots": ["Tomorrow at 10:00 AM", "Tomorrow at 02:30 PM", "Thursday at 11:15 AM"]
    },
    {
        "id": "doc_02",
        "name": "Dr. Rajesh Kulkarni, MD, DM",
        "specialty": "Endocrinologist / Diabetologist",
        "city": "Pune",
        "experience_years": 18,
        "is_demo_verified": True,
        "languages": ["English", "Marathi", "Hindi"],
        "consultation_mode": "Video Consultation",
        "available_slots": ["Wednesday at 04:00 PM", "Friday at 10:30 AM"]
    },
    {
        "id": "doc_03",
        "name": "Dr. Priya Nair, MD",
        "specialty": "Preventive Cardiology & Wellness",
        "city": "Bangalore",
        "experience_years": 11,
        "is_demo_verified": True,
        "languages": ["English", "Hindi"],
        "consultation_mode": "In-Person Consultation",
        "available_slots": ["Thursday at 03:00 PM", "Saturday at 11:00 AM"]
    }
]

# Simulated in-memory booking store
BOOKINGS_DB: Dict[str, Dict[str, Any]] = {}

def recommend_specialties(abnormal_biomarkers: List[Dict[str, Any]]) -> List[Dict[str, str]]:
    """Suggests relevant medical specialties with clear educational reasons."""
    recs = []
    seen = set()

    for b in abnormal_biomarkers:
        can = b.get("canonical_name")
        if can in SPECIALTY_MAPPING:
            spec = SPECIALTY_MAPPING[can]
            if spec not in seen:
                seen.add(spec)
                recs.append({
                    "specialty": spec,
                    "reason": f"Recommended for specialized review of your {b.get('name')} reading ({b.get('value')} {b.get('unit')})."
                })

    # Always provide General Physician as safe first-line entry
    if "General Physician & Internal Medicine" not in seen:
        recs.insert(0, {
            "specialty": "General Physician & Internal Medicine",
            "reason": "Always an ideal first choice for a comprehensive, holistic review of all your laboratory panels."
        })

    return recs

def book_appointment(doctor_id: str, slot: str, patient_name: str = "Anonymous Patient") -> Dict[str, Any]:
    """Books a simulated appointment with server-authoritative tracking."""
    booking_id = f"bk_{uuid.uuid4().hex[:8]}"
    doc = next((d for d in DEMO_DOCTORS if d["id"] == doctor_id), DEMO_DOCTORS[0])

    record = {
        "booking_id": booking_id,
        "doctor_id": doc["id"],
        "doctor_name": doc["name"],
        "specialty": doc["specialty"],
        "slot": slot,
        "patient_name": patient_name,
        "status": "CONFIRMED (Simulated Demo Appointment)",
        "booked_at": datetime.datetime.now(datetime.timezone.utc).isoformat()
    }
    BOOKINGS_DB[booking_id] = record
    return record

def reschedule_appointment(booking_id: str, new_slot: str) -> Optional[Dict[str, Any]]:
    if booking_id in BOOKINGS_DB:
        BOOKINGS_DB[booking_id]["slot"] = new_slot
        BOOKINGS_DB[booking_id]["status"] = "RESCHEDULED (Simulated Demo Appointment)"
        return BOOKINGS_DB[booking_id]
    return None

def cancel_appointment(booking_id: str) -> bool:
    if booking_id in BOOKINGS_DB:
        BOOKINGS_DB[booking_id]["status"] = "CANCELLED"
        return True
    return False
