"""Local consultation preparation. No outbound report sharing or booking simulation."""
from fastapi import APIRouter, HTTPException
from fastapi.responses import Response
from pydantic import BaseModel, Field
from app.api.endpoints.reports import get_report_record, get_simplified_report
from app.services.pdf_generator import generate_pdf_report

router=APIRouter()

class PreparationRequest(BaseModel):
    report_id: str = Field(min_length=1,max_length=100)
    consent_to_include_report: bool = False
    language: str = Field(default='en', pattern='^(en|hi|mr)$')

@router.get('/preparation/{report_id}')
async def preparation(report_id: str, lang: str = 'en'):
    get_report_record(report_id)
    report=await get_simplified_report(report_id,lang)
    return {'report_id':report_id,'findings':[{'name':item['name'],'value':item['value'],'reference_range':item['reference_range'],'status':item['status']} for item in report.get('prioritized_attention',[])],'questions':report.get('suggested_doctor_questions',[]),'sharing_status':'not_shared','booking_status':'not_booked','is_demo':report.get('is_synthetic_fixture',False)}

@router.post('/pdf')
async def preparation_pdf(payload: PreparationRequest):
    get_report_record(payload.report_id)
    if not payload.consent_to_include_report:
        raise HTTPException(403,'Explicit patient consent to include medical report information is required.')
    report=await get_simplified_report(payload.report_id,payload.language)
    return Response(generate_pdf_report(report,payload.language),media_type='application/pdf',headers={'Content-Disposition':'attachment; filename="MediInsight_Consultation_Preparation.pdf"','X-Report-Sharing':'not-shared','Cache-Control':'no-store'})
