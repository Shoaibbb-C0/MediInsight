"""
Pydantic Schemas for Feature 3 — Production-Grade Doctor Discovery & Appointment System.
Distinguishes authorized onboarded providers, external discovery results, and clearly-labeled synthetic demo providers.
"""

from typing import List, Dict, Any, Optional
from pydantic import BaseModel, Field
from enum import Enum

class ProviderSource(str, Enum):
    AUTHORIZED_ONBOARDED = "authorized_onboarded"
    EXTERNAL_DISCOVERY = "external_discovery"
    DEMO_SYNTHETIC = "demo_synthetic"

class VerificationStatus(str, Enum):
    VERIFIED = "verified"
    UNVERIFIED = "unverified"
    SOURCE_LISTED = "source_listed"

class BookingCapability(str, Enum):
    DIRECT_BOOKING = "direct_booking"       # Server-authoritative atomic slot reservation
    EXTERNAL_REQUEST = "external_request"   # Call, WhatsApp enquiry, or external booking page
    DEMO_SIMULATED = "demo_simulated"       # Simulated dev-mode reservation

class SpecialtyRecommendation(BaseModel):
    specialty_id: str
    specialty_name: str
    why_suggesting: str
    observed_finding: Optional[str] = None
    is_fallback: bool = False
    urgent_warning: Optional[str] = None

class Coordinates(BaseModel):
    lat: float
    lng: float

class DoctorProvider(BaseModel):
    id: str
    name: str
    clinic_name: str
    specialty: str
    specialty_id: str
    city: str
    pincode: Optional[str] = None
    address: str
    coordinates: Optional[Coordinates] = None
    distance_km: Optional[float] = None
    
    phone: Optional[str] = None
    phone_available: bool = False
    
    whatsapp_number: Optional[str] = None
    whatsapp_verified: bool = False
    
    source: ProviderSource = ProviderSource.DEMO_SYNTHETIC
    verification_status: VerificationStatus = VerificationStatus.SOURCE_LISTED
    booking_capability: BookingCapability = BookingCapability.DEMO_SIMULATED
    
    external_booking_url: Optional[str] = None
    available_slots: List[str] = Field(default_factory=list)
    languages: List[str] = Field(default_factory=list)
    last_updated: str

class LocationResolutionRequest(BaseModel):
    city_or_pincode: Optional[str] = None
    lat: Optional[float] = None
    lng: Optional[float] = None

class ResolvedLocation(BaseModel):
    query: str
    display_name: str
    city: str
    pincode: Optional[str] = None
    coordinates: Optional[Coordinates] = None
    is_approximate: bool = True

class DoctorDiscoveryResponse(BaseModel):
    report_id: str
    recommended_specialties: List[SpecialtyRecommendation]
    selected_specialty_id: str
    resolved_location: ResolvedLocation
    providers: List[DoctorProvider]
    total_count: int
    is_demo_mode: bool
    live_provider_api_configured: bool
    disclaimer: str

class AppointmentStatus(str, Enum):
    CONFIRMED = "confirmed"
    PENDING_REQUEST = "pending_request"
    RESCHEDULED = "rescheduled"
    CANCELLED = "cancelled"
    DEMO_CONFIRMED = "demo_confirmed"

class DirectBookingRequest(BaseModel):
    doctor_id: str
    slot: str
    patient_name: str = "Anonymous Patient"
    patient_phone: Optional[str] = None
    patient_email: Optional[str] = None
    report_id: Optional[str] = None

class RescheduleBookingRequest(BaseModel):
    booking_id: str
    new_slot: str

class CancelBookingRequest(BaseModel):
    booking_id: str
    reason: Optional[str] = None

class AppointmentRecord(BaseModel):
    booking_id: str
    user_id: str
    doctor_id: str
    doctor_name: str
    clinic_name: str
    specialty: str
    slot: str
    patient_name: str
    status: AppointmentStatus
    booking_capability: BookingCapability
    phone: Optional[str] = None
    whatsapp_number: Optional[str] = None
    address: str
    coordinates: Optional[Coordinates] = None
    created_at: str
    updated_at: str
    is_demo: bool = True
