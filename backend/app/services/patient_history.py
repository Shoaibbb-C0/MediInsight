"""
Patient Medical Profile & Health History Management Service for Simplifier 2.0.
Supports progressive disclosure (Skip, Don't know, Prefer not to say),
owner-scoped local isolation, and secure history mutation/deletion.
"""

from typing import Dict, Any, List, Optional
import datetime
from pydantic import BaseModel, Field

class PatientProfile(BaseModel):
    user_id: str = "local_default_patient"
    age_bracket: Optional[str] = None  # e.g. '18-35', '36-50', '51-65', '65+'
    sex_assigned_at_birth: Optional[str] = None  # 'male', 'female', 'prefer_not_to_say'
    is_pregnant: Optional[bool] = None
    known_conditions: List[str] = Field(default_factory=list)
    current_medications: List[str] = Field(default_factory=list)
    allergies: List[str] = Field(default_factory=list)
    reported_symptoms: List[str] = Field(default_factory=list)
    testing_reason: Optional[str] = None
    last_updated: str = Field(default_factory=lambda: datetime.datetime.now(datetime.timezone.utc).isoformat())

class HistoricalReportRecord(BaseModel):
    report_id: str
    user_id: str = "local_default_patient"
    report_date: str
    title: str
    measurements: List[Dict[str, Any]]
    created_at: str = Field(default_factory=lambda: datetime.datetime.now(datetime.timezone.utc).isoformat())

class PatientHistoryService:
    def __init__(self):
        # In-memory storage keyed by user_id for development isolation
        self.profiles: Dict[str, PatientProfile] = {
            "local_default_patient": PatientProfile(user_id="local_default_patient")
        }
        self.history_records: Dict[str, List[HistoricalReportRecord]] = {
            "demo_patient": [
                HistoricalReportRecord(
                    report_id="rep_past_01",
                    user_id="demo_patient",
                    report_date="2026-06-15",
                    title="Routine Health Checkup",
                    measurements=[
                        {"canonical_name": "glucose_fasting", "name": "Fasting Blood Glucose", "value": "104", "unit": "mg/dL", "status": "high", "range": "70 - 99 mg/dL"},
                        {"canonical_name": "hba1c", "name": "HbA1c", "value": "5.9", "unit": "%", "status": "high", "range": "< 5.7 %"},
                        {"canonical_name": "creatinine_serum", "name": "Serum Creatinine", "value": "0.85", "unit": "mg/dL", "status": "normal", "range": "0.7 - 1.3 mg/dL"},
                        {"canonical_name": "cholesterol_total", "name": "Total Cholesterol", "value": "198", "unit": "mg/dL", "status": "normal", "range": "< 200 mg/dL"},
                        {"canonical_name": "vitamin_d", "name": "Vitamin D", "value": "14.2", "unit": "ng/mL", "status": "low", "range": "30 - 100 ng/mL"}
                    ]
                )
            ]
        }

    def get_profile(self, user_id: str = "local_default_patient") -> PatientProfile:
        if user_id not in self.profiles:
            self.profiles[user_id] = PatientProfile(user_id=user_id)
        return self.profiles[user_id]

    def update_profile(self, profile: PatientProfile) -> PatientProfile:
        profile.last_updated = datetime.datetime.now(datetime.timezone.utc).isoformat()
        self.profiles[profile.user_id] = profile
        return profile

    def get_user_history(self, user_id: str = "local_default_patient") -> List[HistoricalReportRecord]:
        return self.history_records.get(user_id, [])

    def add_history_record(self, record: HistoricalReportRecord) -> HistoricalReportRecord:
        if record.user_id not in self.history_records:
            self.history_records[record.user_id] = []
        self.history_records[record.user_id].insert(0, record)
        return record

    def delete_history_record(self, user_id: str, report_id: str) -> bool:
        if user_id in self.history_records:
            initial_len = len(self.history_records[user_id])
            self.history_records[user_id] = [r for r in self.history_records[user_id] if r.report_id != report_id]
            return len(self.history_records[user_id]) < initial_len
        return False

patient_history_service = PatientHistoryService()
