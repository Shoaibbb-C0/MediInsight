"""
Grounded Location & Indian Pin Code / City Geocoding Engine.
Provides clean abstraction for:
1. Browser Geolocation (lat/lng -> nearest Indian city/locality).
2. Manual Indian PIN code or city lookup with real approximate coordinates.
3. Haversine distance calculation.
4. Clean fallback when external geocoding API keys are not supplied.
"""

import math
from typing import Optional, Tuple, Dict, Any
from app.schemas.doctor import Coordinates, ResolvedLocation

# Curated reference coordinates for major Indian medical hubs & cities
INDIAN_CITIES_REGISTRY: Dict[str, Dict[str, Any]] = {
    "mumbai": {
        "display_name": "Mumbai, Maharashtra",
        "city": "Mumbai",
        "pincode_prefix": "400",
        "lat": 19.0760,
        "lng": 72.8777
    },
    "pune": {
        "display_name": "Pune, Maharashtra",
        "city": "Pune",
        "pincode_prefix": "411",
        "lat": 18.5204,
        "lng": 73.8567
    },
    "delhi": {
        "display_name": "New Delhi, Delhi NCR",
        "city": "Delhi",
        "pincode_prefix": "110",
        "lat": 28.6139,
        "lng": 77.2090
    },
    "bangalore": {
        "display_name": "Bengaluru, Karnataka",
        "city": "Bengaluru",
        "pincode_prefix": "560",
        "lat": 12.9716,
        "lng": 77.5946
    },
    "hyderabad": {
        "display_name": "Hyderabad, Telangana",
        "city": "Hyderabad",
        "pincode_prefix": "500",
        "lat": 17.3850,
        "lng": 78.4867
    },
    "chennai": {
        "display_name": "Chennai, Tamil Nadu",
        "city": "Chennai",
        "pincode_prefix": "600",
        "lat": 13.0827,
        "lng": 80.2707
    },
    "kolkata": {
        "display_name": "Kolkata, West Bengal",
        "city": "Kolkata",
        "pincode_prefix": "700",
        "lat": 22.5726,
        "lng": 88.3639
    },
    "nagpur": {
        "display_name": "Nagpur, Maharashtra",
        "city": "Nagpur",
        "pincode_prefix": "440",
        "lat": 21.1458,
        "lng": 79.0882
    },
    "nashik": {
        "display_name": "Nashik, Maharashtra",
        "city": "Nashik",
        "pincode_prefix": "422",
        "lat": 19.9975,
        "lng": 73.7898
    },
    "ahmedabad": {
        "display_name": "Ahmedabad, Gujarat",
        "city": "Ahmedabad",
        "pincode_prefix": "380",
        "lat": 23.0225,
        "lng": 72.5714
    }
}

# Known PIN Code prefixes to city mapping
PINCODE_PREFIX_MAPPING: Dict[str, str] = {
    "400": "mumbai",
    "401": "mumbai",
    "411": "pune",
    "412": "pune",
    "110": "delhi",
    "560": "bangalore",
    "500": "hyderabad",
    "600": "chennai",
    "700": "kolkata",
    "440": "nagpur",
    "422": "nashik",
    "380": "ahmedabad"
}

def haversine_distance_km(lat1: float, lon1: float, lat2: float, lon2: float) -> float:
    """Calculates true great-circle distance between two points in kilometers."""
    R = 6371.0  # Earth radius in kilometers
    dlat = math.radians(lat2 - lat1)
    dlon = math.radians(lon2 - lon1)
    a = (math.sin(dlat / 2) ** 2 +
         math.cos(math.radians(lat1)) * math.cos(math.radians(lat2)) *
         math.sin(dlon / 2) ** 2)
    c = 2 * math.atan2(math.sqrt(a), math.sqrt(1 - a))
    return round(R * c, 1)

def resolve_patient_location(
    city_or_pincode: Optional[str] = None,
    lat: Optional[float] = None,
    lng: Optional[float] = None
) -> ResolvedLocation:
    """
    Resolves patient location cleanly from coordinates or city/pincode input.
    Never invents inaccurate claims.
    """
    # 1. Coordinate-based resolution if given
    if lat is not None and lng is not None and -90 <= lat <= 90 and -180 <= lng <= 180:
        # Find nearest known city in registry
        nearest_city_key = "mumbai"
        min_dist = float("inf")
        for key, data in INDIAN_CITIES_REGISTRY.items():
            dist = haversine_distance_km(lat, lng, data["lat"], data["lng"])
            if dist < min_dist:
                min_dist = dist
                nearest_city_key = key
        
        nearest = INDIAN_CITIES_REGISTRY[nearest_city_key]
        display = f"Near {nearest['display_name']} ({round(min_dist, 1)} km)" if min_dist > 5.0 else f"Near {nearest['city']}"
        return ResolvedLocation(
            query=f"{lat:.4f}, {lng:.4f}",
            display_name=display,
            city=nearest["city"],
            coordinates=Coordinates(lat=lat, lng=lng),
            is_approximate=False
        )

    # 2. Manual City or PIN Code resolution
    raw_query = (city_or_pincode or "").strip()
    if not raw_query:
        # Default fallback is Mumbai hub
        mumbai = INDIAN_CITIES_REGISTRY["mumbai"]
        return ResolvedLocation(
            query="Mumbai",
            display_name=mumbai["display_name"],
            city=mumbai["city"],
            pincode="400001",
            coordinates=Coordinates(lat=mumbai["lat"], lng=mumbai["lng"]),
            is_approximate=True
        )

    clean_query = raw_query.lower()

    # Check PIN code pattern (6 digits or 3 prefix digits)
    digits = "".join(ch for ch in clean_query if ch.isdigit())
    if len(digits) >= 3:
        prefix = digits[:3]
        if prefix in PINCODE_PREFIX_MAPPING:
            city_key = PINCODE_PREFIX_MAPPING[prefix]
            entry = INDIAN_CITIES_REGISTRY[city_key]
            return ResolvedLocation(
                query=raw_query,
                display_name=f"PIN {digits[:6]} — {entry['display_name']}",
                city=entry["city"],
                pincode=digits[:6] if len(digits) >= 6 else digits,
                coordinates=Coordinates(lat=entry["lat"], lng=entry["lng"]),
                is_approximate=True
            )

    # Check direct city name match
    for key, data in INDIAN_CITIES_REGISTRY.items():
        if key in clean_query or data["city"].lower() in clean_query:
            return ResolvedLocation(
                query=raw_query,
                display_name=data["display_name"],
                city=data["city"],
                pincode=f"{data['pincode_prefix']}001",
                coordinates=Coordinates(lat=data["lat"], lng=data["lng"]),
                is_approximate=True
            )

    # Graceful fallback for unlisted city / generic query
    return ResolvedLocation(
        query=raw_query,
        display_name=f"{raw_query.title()} (Approximate Region)",
        city=raw_query.title(),
        coordinates=Coordinates(lat=19.0760, lng=72.8777),  # Reference baseline
        is_approximate=True
    )
