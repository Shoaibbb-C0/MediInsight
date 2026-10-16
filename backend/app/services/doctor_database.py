"""
Curated Provider Database and Multi-Source Adapter for Feature 3.
Distinguishes:
1. Authorized onboarded clinics with server-authoritative slot booking.
2. Verified external directory listings (contact/call/WhatsApp enquiry only).
3. Clearly labeled simulated development demo doctors.
Strictly eliminates fake avatars, fake ratings, and ungrounded claims.
"""

from typing import List, Dict, Any, Optional
import datetime
from app.schemas.doctor import (
    DoctorProvider,
    ProviderSource,
    VerificationStatus,
    BookingCapability,
    Coordinates
)
from app.services.location_service import haversine_distance_km

# Curated provider directory
GROUNDED_PROVIDERS_REGISTRY: List[Dict[str, Any]] = [
    # --- MUMBAI ---
    {
        "id": "prov_mum_01",
        "name": "Dr. Ananya Sharma, MD",
        "clinic_name": "Apex Internal Medicine & Diagnostic Centre",
        "specialty": "General Physician & Internal Medicine",
        "specialty_id": "general_physician",
        "city": "Mumbai",
        "pincode": "400012",
        "address": "Dr. E Borges Road, Parel, Mumbai, Maharashtra 400012",
        "coordinates": {"lat": 19.0025, "lng": 72.8423},
        "phone": "+91 22 2417 7000",
        "phone_available": True,
        "whatsapp_number": "+919820011223",
        "whatsapp_verified": True,
        "source": ProviderSource.AUTHORIZED_ONBOARDED,
        "verification_status": VerificationStatus.VERIFIED,
        "booking_capability": BookingCapability.DIRECT_BOOKING,
        "available_slots": ["Tomorrow at 10:00 AM", "Tomorrow at 02:30 PM", "Thursday at 11:15 AM"],
        "languages": ["English", "Hindi", "Marathi"],
        "last_updated": "2026-10-10"
    },
    {
        "id": "prov_mum_02",
        "name": "Dr. Sanjeev Mehta, MD, DM",
        "clinic_name": "Metabolic Care & Endocrine Clinic",
        "specialty": "Endocrinologist / Diabetologist",
        "specialty_id": "endocrinology",
        "city": "Mumbai",
        "pincode": "400050",
        "address": "Linking Road, Bandra West, Mumbai, Maharashtra 400050",
        "coordinates": {"lat": 19.0596, "lng": 72.8295},
        "phone": "+91 22 2640 1200",
        "phone_available": True,
        "whatsapp_number": "+919820033445",
        "whatsapp_verified": True,
        "source": ProviderSource.AUTHORIZED_ONBOARDED,
        "verification_status": VerificationStatus.VERIFIED,
        "booking_capability": BookingCapability.DIRECT_BOOKING,
        "available_slots": ["Wednesday at 11:00 AM", "Friday at 04:30 PM"],
        "languages": ["English", "Hindi", "Gujarati"],
        "last_updated": "2026-10-10"
    },
    {
        "id": "prov_mum_03",
        "name": "Dr. Rohini Deshmukh, MD, DM",
        "clinic_name": "Mumbai Nephrology Care & Dialysis Centre",
        "specialty": "Nephrologist (Kidney Specialist)",
        "specialty_id": "nephrology",
        "city": "Mumbai",
        "pincode": "400016",
        "address": "Mahim West, Mumbai, Maharashtra 400016",
        "coordinates": {"lat": 19.0350, "lng": 72.8400},
        "phone": "+91 22 2445 8900",
        "phone_available": True,
        "whatsapp_number": "+919820055667",
        "whatsapp_verified": False,
        "source": ProviderSource.EXTERNAL_DISCOVERY,
        "verification_status": VerificationStatus.SOURCE_LISTED,
        "booking_capability": BookingCapability.EXTERNAL_REQUEST,
        "available_slots": [],
        "languages": ["English", "Marathi", "Hindi"],
        "last_updated": "2026-10-08"
    },
    {
        "id": "prov_mum_04",
        "name": "Dr. Vikram Joshi, MD",
        "clinic_name": "Central Hematology Care",
        "specialty": "Hematologist / Blood Specialist",
        "specialty_id": "hematology",
        "city": "Mumbai",
        "pincode": "400004",
        "address": "Girgaon, Charni Road, Mumbai, Maharashtra 400004",
        "coordinates": {"lat": 18.9550, "lng": 72.8180},
        "phone": "+91 22 2382 4500",
        "phone_available": True,
        "whatsapp_number": None,
        "whatsapp_verified": False,
        "source": ProviderSource.EXTERNAL_DISCOVERY,
        "verification_status": VerificationStatus.SOURCE_LISTED,
        "booking_capability": BookingCapability.EXTERNAL_REQUEST,
        "available_slots": [],
        "languages": ["English", "Hindi", "Marathi"],
        "last_updated": "2026-10-09"
    },
    {
        "id": "prov_mum_05",
        "name": "Dr. Vivek Merchant, MD, DM",
        "clinic_name": "Cardiovascular Wellness & Preventive Clinic",
        "specialty": "Cardiologist / Heart Specialist",
        "specialty_id": "cardiology",
        "city": "Mumbai",
        "pincode": "400020",
        "address": "Marine Lines, Mumbai, Maharashtra 400020",
        "coordinates": {"lat": 18.9430, "lng": 72.8250},
        "phone": "+91 22 2200 3344",
        "phone_available": True,
        "whatsapp_number": "+919820077889",
        "whatsapp_verified": True,
        "source": ProviderSource.AUTHORIZED_ONBOARDED,
        "verification_status": VerificationStatus.VERIFIED,
        "booking_capability": BookingCapability.DIRECT_BOOKING,
        "available_slots": ["Thursday at 03:00 PM", "Saturday at 10:00 AM"],
        "languages": ["English", "Hindi"],
        "last_updated": "2026-10-10"
    },

    # --- PUNE ---
    {
        "id": "prov_pune_01",
        "name": "Dr. Rajesh Kulkarni, MD, DM",
        "clinic_name": "Pune Endocrinology & Diabetes Institute",
        "specialty": "Endocrinologist / Diabetologist",
        "specialty_id": "endocrinology",
        "city": "Pune",
        "pincode": "411004",
        "address": "Deccan Gymkhana, FC Road, Pune, Maharashtra 411004",
        "coordinates": {"lat": 18.5170, "lng": 73.8410},
        "phone": "+91 20 2565 8900",
        "phone_available": True,
        "whatsapp_number": "+919822011223",
        "whatsapp_verified": True,
        "source": ProviderSource.AUTHORIZED_ONBOARDED,
        "verification_status": VerificationStatus.VERIFIED,
        "booking_capability": BookingCapability.DIRECT_BOOKING,
        "available_slots": ["Wednesday at 04:00 PM", "Friday at 10:30 AM"],
        "languages": ["English", "Marathi", "Hindi"],
        "last_updated": "2026-10-11"
    },
    {
        "id": "prov_pune_02",
        "name": "Dr. Sunita Pathak, MD",
        "clinic_name": "Sahyadri Family Practice Clinic",
        "specialty": "General Physician & Internal Medicine",
        "specialty_id": "general_physician",
        "city": "Pune",
        "pincode": "411038",
        "address": "Kothrud, Paud Road, Pune, Maharashtra 411038",
        "coordinates": {"lat": 18.5074, "lng": 73.8077},
        "phone": "+91 20 2538 4100",
        "phone_available": True,
        "whatsapp_number": "+919822033445",
        "whatsapp_verified": True,
        "source": ProviderSource.AUTHORIZED_ONBOARDED,
        "verification_status": VerificationStatus.VERIFIED,
        "booking_capability": BookingCapability.DIRECT_BOOKING,
        "available_slots": ["Tomorrow at 09:30 AM", "Thursday at 05:00 PM"],
        "languages": ["English", "Marathi", "Hindi"],
        "last_updated": "2026-10-10"
    },
    {
        "id": "prov_pune_03",
        "name": "Dr. Amit Chordia, MD, DM",
        "clinic_name": "Pune Kidney & Hypertension Clinic",
        "specialty": "Nephrologist (Kidney Specialist)",
        "specialty_id": "nephrology",
        "city": "Pune",
        "pincode": "411001",
        "address": "Camp, Bund Garden Road, Pune, Maharashtra 411001",
        "coordinates": {"lat": 18.5320, "lng": 73.8780},
        "phone": "+91 20 2612 7700",
        "phone_available": True,
        "whatsapp_number": None,
        "whatsapp_verified": False,
        "source": ProviderSource.EXTERNAL_DISCOVERY,
        "verification_status": VerificationStatus.SOURCE_LISTED,
        "booking_capability": BookingCapability.EXTERNAL_REQUEST,
        "available_slots": [],
        "languages": ["English", "Marathi", "Hindi"],
        "last_updated": "2026-10-09"
    },

    # --- BANGALORE ---
    {
        "id": "prov_blr_01",
        "name": "Dr. Priya Nair, MD",
        "clinic_name": "Narayana Integrated Family Care",
        "specialty": "General Physician & Internal Medicine",
        "specialty_id": "general_physician",
        "city": "Bengaluru",
        "pincode": "560034",
        "address": "Koramangala 4th Block, Bengaluru, Karnataka 560034",
        "coordinates": {"lat": 12.9340, "lng": 77.6280},
        "phone": "+91 80 2552 1100",
        "phone_available": True,
        "whatsapp_number": "+919845011223",
        "whatsapp_verified": True,
        "source": ProviderSource.AUTHORIZED_ONBOARDED,
        "verification_status": VerificationStatus.VERIFIED,
        "booking_capability": BookingCapability.DIRECT_BOOKING,
        "available_slots": ["Tomorrow at 11:30 AM", "Thursday at 03:00 PM"],
        "languages": ["English", "Hindi", "Kannada"],
        "last_updated": "2026-10-10"
    },

    # --- DELHI NCR ---
    {
        "id": "prov_del_01",
        "name": "Dr. Arvind Saxena, MD",
        "clinic_name": "Delhi Internal Medicine & Endocrine Clinic",
        "specialty": "General Physician & Internal Medicine",
        "specialty_id": "general_physician",
        "city": "Delhi",
        "pincode": "110016",
        "address": "Green Park Main, New Delhi 110016",
        "coordinates": {"lat": 28.5580, "lng": 77.2060},
        "phone": "+91 11 2656 3400",
        "phone_available": True,
        "whatsapp_number": "+919810011223",
        "whatsapp_verified": True,
        "source": ProviderSource.AUTHORIZED_ONBOARDED,
        "verification_status": VerificationStatus.VERIFIED,
        "booking_capability": BookingCapability.DIRECT_BOOKING,
        "available_slots": ["Tomorrow at 10:00 AM", "Thursday at 02:00 PM"],
        "languages": ["English", "Hindi"],
        "last_updated": "2026-10-11"
    }
]

# Explicitly classify bundled examples. No live source or verification is configured.
for provider in GROUNDED_PROVIDERS_REGISTRY:
    provider.update(source=ProviderSource.DEMO_SYNTHETIC,
                    verification_status=VerificationStatus.UNVERIFIED,
                    booking_capability=BookingCapability.DEMO_SIMULATED,
                    phone_available=False, whatsapp_verified=False,
                    phone=None, whatsapp_number=None)


def search_providers(
    specialty_id: Optional[str] = None,
    city: Optional[str] = None,
    patient_lat: Optional[float] = None,
    patient_lng: Optional[float] = None
) -> List[DoctorProvider]:
    """
    Retrieves grounded providers matched by specialty and locality.
    Computes precise Haversine distance when patient coordinates are available.
    """
    results: List[DoctorProvider] = []
    clean_city = (city or "").strip().lower()

    for item in GROUNDED_PROVIDERS_REGISTRY:
        # Specialty filter (if given, check match or general physician fallback)
        if specialty_id and specialty_id != "all":
            if item["specialty_id"] != specialty_id and item["specialty_id"] != "general_physician":
                continue

        # City filter (loose containment)
        if clean_city and clean_city != "all":
            if clean_city not in item["city"].lower() and item["city"].lower() not in clean_city:
                continue

        # Calculate distance if coordinates provided
        dist_km = None
        if patient_lat is not None and patient_lng is not None and item.get("coordinates"):
            dist_km = haversine_distance_km(
                patient_lat,
                patient_lng,
                item["coordinates"]["lat"],
                item["coordinates"]["lng"]
            )

        provider_obj = DoctorProvider(
            id=item["id"],
            name=item["name"],
            clinic_name=item["clinic_name"],
            specialty=item["specialty"],
            specialty_id=item["specialty_id"],
            city=item["city"],
            pincode=item.get("pincode"),
            address=item["address"],
            coordinates=Coordinates(**item["coordinates"]) if item.get("coordinates") else None,
            distance_km=dist_km,
            phone=item.get("phone"),
            phone_available=bool(item.get("phone_available") and item.get("phone")),
            whatsapp_number=item.get("whatsapp_number"),
            whatsapp_verified=bool(item.get("whatsapp_verified")),
            source=item["source"],
            verification_status=item["verification_status"],
            booking_capability=item["booking_capability"],
            available_slots=item.get("available_slots", []),
            languages=item.get("languages", []),
            last_updated=item["last_updated"]
        )
        results.append(provider_obj)

    # Sort by distance if available, otherwise by onboarded status
    if patient_lat is not None and patient_lng is not None:
        results.sort(key=lambda p: (p.distance_km if p.distance_km is not None else 9999.0))
    else:
        results.sort(key=lambda p: (0 if p.source == ProviderSource.AUTHORIZED_ONBOARDED else 1))

    return results
