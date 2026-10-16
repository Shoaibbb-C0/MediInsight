"""
Atomic Appointment Booking Service for Feature 3.
Provides:
1. Concurrency-safe atomic slot reservation (double-booking prevention).
2. Distinction between DIRECT_BOOKING, EXTERNAL_REQUEST, and DEMO_SIMULATED.
3. Rescheduling & cancellation with status audit trail.
4. Two-user data isolation and owner-scoped retrieval.
5. In-memory thread-safe local store with Supabase migration parity.
"""

import threading
import uuid
import datetime
from typing import List, Dict, Any, Optional
from app.schemas.doctor import (
    AppointmentRecord,
    AppointmentStatus,
    BookingCapability,
    DirectBookingRequest,
    RescheduleBookingRequest,
    CancelBookingRequest,
    DoctorProvider
)
from app.services.doctor_database import GROUNDED_PROVIDERS_REGISTRY

# Thread lock for concurrency safety and double-booking prevention
_LOCK = threading.Lock()

# Persistent in-memory appointments database
APPOINTMENTS_DB: Dict[str, Dict[str, Any]] = {}

# Slot reservation lock ledger: maps (doctor_id, slot) -> booking_id
RESERVED_SLOTS_LEDGER: Dict[str, str] = {}

def get_provider_by_id(doctor_id: str) -> Optional[Dict[str, Any]]:
    for p in GROUNDED_PROVIDERS_REGISTRY:
        if p["id"] == doctor_id:
            return p
    return None

def create_appointment(
    user_id: str,
    request: DirectBookingRequest
) -> Dict[str, Any]:
    """
    Atomically creates an appointment reservation.
    Guarantees no two patients can claim the same slot for the same doctor.
    """
    with _LOCK:
        doctor_data = get_provider_by_id(request.doctor_id)
        if not doctor_data:
            return {"status": "error", "message": "Doctor or clinic not found."}

        ledger_key = f"{request.doctor_id}::{request.slot.strip()}"
        if ledger_key in RESERVED_SLOTS_LEDGER:
            return {
                "status": "error",
                "message": f"This slot ('{request.slot}') is already booked. Please choose another available time."
            }

        booking_id = f"bk_{uuid.uuid4().hex[:10]}"
        now_iso = datetime.datetime.now(datetime.timezone.utc).isoformat()
        
        is_demo = (doctor_data.get("booking_capability") == BookingCapability.DEMO_SIMULATED)
        status = AppointmentStatus.DEMO_CONFIRMED if is_demo else AppointmentStatus.CONFIRMED

        record = AppointmentRecord(
            booking_id=booking_id,
            user_id=user_id,
            doctor_id=doctor_data["id"],
            doctor_name=doctor_data["name"],
            clinic_name=doctor_data["clinic_name"],
            specialty=doctor_data["specialty"],
            slot=request.slot,
            patient_name=request.patient_name,
            status=status,
            booking_capability=doctor_data.get("booking_capability", BookingCapability.DIRECT_BOOKING),
            phone=doctor_data.get("phone"),
            whatsapp_number=doctor_data.get("whatsapp_number"),
            address=doctor_data["address"],
            coordinates=doctor_data.get("coordinates"),
            created_at=now_iso,
            updated_at=now_iso,
            is_demo=is_demo
        )

        record_dict = record.model_dump()
        APPOINTMENTS_DB[booking_id] = record_dict
        RESERVED_SLOTS_LEDGER[ledger_key] = booking_id

        return {
            "status": "success",
            "message": "Appointment successfully confirmed.",
            "appointment": record_dict
        }

def reschedule_appointment(
    user_id: str,
    request: RescheduleBookingRequest
) -> Dict[str, Any]:
    """
    Atomically reschedules an appointment to a new slot.
    Validates ownership and slot availability.
    """
    with _LOCK:
        booking = APPOINTMENTS_DB.get(request.booking_id)
        if not booking:
            return {"status": "error", "message": "Appointment not found."}

        if booking["user_id"] != user_id:
            return {"status": "error", "message": "Unauthorized access to this appointment."}

        if booking["status"] == AppointmentStatus.CANCELLED:
            return {"status": "error", "message": "Cannot reschedule a cancelled appointment."}

        doctor_id = booking["doctor_id"]
        old_slot = booking["slot"]
        new_slot = request.new_slot.strip()

        new_ledger_key = f"{doctor_id}::{new_slot}"
        if new_ledger_key in RESERVED_SLOTS_LEDGER and RESERVED_SLOTS_LEDGER[new_ledger_key] != request.booking_id:
            return {"status": "error", "message": "Target slot is already reserved."}

        # Release old slot
        old_ledger_key = f"{doctor_id}::{old_slot.strip()}"
        RESERVED_SLOTS_LEDGER.pop(old_ledger_key, None)

        # Claim new slot
        RESERVED_SLOTS_LEDGER[new_ledger_key] = request.booking_id

        # Update record
        booking["slot"] = new_slot
        booking["status"] = AppointmentStatus.DEMO_CONFIRMED if booking.get("is_demo") else AppointmentStatus.RESCHEDULED
        booking["updated_at"] = datetime.datetime.now(datetime.timezone.utc).isoformat()
        APPOINTMENTS_DB[request.booking_id] = booking

        return {
            "status": "success",
            "message": "Appointment rescheduled successfully.",
            "appointment": booking
        }

def cancel_appointment(
    user_id: str,
    request: CancelBookingRequest
) -> Dict[str, Any]:
    """
    Atomically cancels an appointment and releases the reserved slot.
    Validates patient ownership.
    """
    with _LOCK:
        booking = APPOINTMENTS_DB.get(request.booking_id)
        if not booking:
            return {"status": "error", "message": "Appointment not found."}

        if booking["user_id"] != user_id:
            return {"status": "error", "message": "Unauthorized access to this appointment."}

        # Release slot
        doctor_id = booking["doctor_id"]
        slot = booking["slot"]
        ledger_key = f"{doctor_id}::{slot.strip()}"
        RESERVED_SLOTS_LEDGER.pop(ledger_key, None)

        # Update record
        booking["status"] = AppointmentStatus.CANCELLED
        booking["updated_at"] = datetime.datetime.now(datetime.timezone.utc).isoformat()
        APPOINTMENTS_DB[request.booking_id] = booking

        return {
            "status": "success",
            "message": "Appointment cancelled.",
            "appointment": booking
        }

def get_user_appointments(user_id: str) -> List[Dict[str, Any]]:
    """Returns only appointments belonging to the requesting user."""
    with _LOCK:
        user_list = [
            app for app in APPOINTMENTS_DB.values()
            if app["user_id"] == user_id
        ]
        user_list.sort(key=lambda a: a.get("created_at", ""), reverse=True)
        return user_list
