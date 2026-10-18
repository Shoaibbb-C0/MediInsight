import io
import json
import pymupdf
import pytest
from PIL import Image
from fastapi.testclient import TestClient
from app.main import app
from app.services.abnormality_engine import classify_measurement
from app.services.pattern_engine import detect_conservative_medical_patterns, compute_historical_trends
from app.services.pdf_generator import generate_pdf_report
from app.api.endpoints.reports import REPORTS_DB,engine


@pytest.mark.parametrize('interval',['Male 70 - 99 Female 60 - 90','99 - 70','70 - 99 or 60 - 90'])
def test_ambiguous_interval_never_substitutes_a_standard(interval):
    assert classify_measurement('120',interval,canonical_name='glucose_fasting',unit='mg/dL')[0]=='NEEDS_REVIEW'


@pytest.mark.parametrize('value',['NaN','Infinity','-Infinity'])
def test_nonfinite_numbers_are_not_medical_readings(value):
    assert classify_measurement(value,'70 - 99')[0]=='NEEDS_REVIEW'


def test_pattern_uses_actual_value_and_excludes_uncertainty():
    actual={'canonical_name':'vitamin_d','value':'7.3','unit':'ng/mL','reference_range':'20 - 50','status':'low'}
    patterns=detect_conservative_medical_patterns([actual])
    assert '7.3' in patterns[0]['summary'] and '18.4' not in json.dumps(patterns)
    assert detect_conservative_medical_patterns([{**actual,'requires_verification':True}])==[]
    assert detect_conservative_medical_patterns([{'canonical_name':'glucose_fasting','value':'not readable','status':'needs_review'},{'canonical_name':'hba1c','value':'bad','status':'needs_review'}])==[]


def test_report_text_cannot_fetch_an_image_during_pdf_generation(monkeypatch):
    import reportlab.lib.utils
    original=reportlab.lib.utils.open_for_read
    def guarded(name,*args,**kwargs):
        assert not str(name).startswith(('http:','https:'))
        return original(name,*args,**kwargs)
    monkeypatch.setattr(reportlab.lib.utils,'open_for_read',guarded)
    payload={'patient_summary':'<img src="http://127.0.0.1/private"/>','disclaimer':'Test fixture'}
    result=generate_pdf_report(payload)
    doc=pymupdf.open(stream=result,filetype='pdf')
    assert '<img' in ''.join(page.get_text() for page in doc)


def test_camera_upload_processes_all_pages(monkeypatch):
    observed=[]
    from app.schemas.report import ExtractedBiomarker
    def extraction(content,filename):
        with pymupdf.open(stream=content,filetype='pdf') as document:
            observed.append(len(document))
        return [ExtractedBiomarker(id='b',name='Glucose',canonical_name='glucose_fasting',value='124.5',unit='mg/dL',reference_range='70 - 99',status='high',confidence=.9)]
    monkeypatch.setattr(engine,'process_document',extraction)
    image=Image.new('RGB',(400,600),'white');output=io.BytesIO();image.save(output,format='PNG')
    response=TestClient(app).post('/api/v1/reports/capture',files=[('files',('page1.png',output.getvalue(),'image/png')),('files',('page2.png',output.getvalue(),'image/png'))])
    assert response.status_code==200
    assert response.json()['page_count']==2
    assert observed==[2]


def test_real_report_requires_nutrition_safety_answers():
    REPORTS_DB['r']={'extractions':[],'answers':[]}
    assert TestClient(app).post('/api/v1/reports/r/nutrition/generate',json={'report_id':'r'}).status_code==422


@pytest.mark.parametrize('language',['hi','mr'])
def test_localized_api_validation_has_no_english_message(language):
    response=TestClient(app).post('/api/v1/reports/missing/nutrition/generate?lang='+language,json={})
    assert response.status_code==422
    assert any('\u0900'<=char<='\u097f' for char in response.json()['detail'])


def test_no_duplicate_nutrition_questions():
    from app.services.nutrition_questionnaire import get_localized_nutrition_questions
    ids=[item['id'] for item in get_localized_nutrition_questions()]
    assert len(ids)==len(set(ids))


def test_saved_plan_localizes_without_losing_the_selected_swap():
    client=TestClient(app)
    plan=client.post('/api/v1/reports/rep_demo_fixture/nutrition/generate',json={'report_id':'rep_demo_fixture','allergies':['none'],'dietary_preference':'vegetarian'}).json()
    alternate=plan['days'][0]['breakfast']['alternatives'][0]['id']
    swapped=client.post('/api/v1/reports/nutrition/swap',json={'plan_id':plan['plan_id'],'day_number':1,'meal_type':'breakfast','new_meal_id':alternate}).json()
    for language in ['hi','mr']:
        translated=client.get('/api/v1/reports/rep_demo_fixture/nutrition/plan?lang='+language).json()
        assert translated['plan_id']==plan['plan_id']
        assert translated['days'][0]['breakfast']['id']==alternate
        assert any('\u0900'<=char<='\u097f' for char in translated['disclaimer'])
        pdf=client.get('/api/v1/reports/rep_demo_fixture/nutrition/pdf?lang='+language)
        assert pdf.status_code==200 and pdf.content.startswith(b'%PDF')
