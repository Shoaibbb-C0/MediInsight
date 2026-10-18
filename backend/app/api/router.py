from fastapi import APIRouter
from app.api.endpoints import reports

api_router = APIRouter()
api_router.include_router(reports.router, prefix="/reports", tags=["reports"])

from app.api.endpoints import consultation
from app.core import auth
api_router.include_router(consultation.router, prefix="/consultation", tags=["consultation"])
api_router.include_router(auth.router, prefix="/auth", tags=["auth"])
