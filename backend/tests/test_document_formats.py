"""Known synthetic documents exercised through the real PDF/image/OCR pipeline."""
import io
import pymupdf
import pytest
from PIL import Image
from app.services.extraction_service import engine

@pytest.fixture(scope='module')
def source_document():
    document=pymupdf.open()
    page=document.new_page(width=1000,height=500)
    page.insert_text((40,50),'SYNTHETIC TEST FIXTURE - NOT A PATIENT',fontsize=18)
    page.insert_text((40,120),'Fasting Blood Glucose : 124.5 mg/dL (70 - 99 mg/dL)',fontsize=25)
    page.insert_text((40,190),'Serum Creatinine : 0.9 mg/dL (0.7 - 1.3 mg/dL)',fontsize=25)
    return document

@pytest.mark.parametrize('extension',['png','jpg','jpeg'])
def test_actual_image_ocr_preserves_source_measurements(source_document,extension):
    pix=source_document[0].get_pixmap(dpi=120,alpha=False)
    image=Image.open(io.BytesIO(pix.tobytes('png')))
    output=io.BytesIO();image.save(output,format='PNG' if extension=='png' else 'JPEG',quality=95)
    readings=engine.process_document(output.getvalue(),'synthetic.'+extension)
    assert any(item.value=='124.5' and item.unit=='mg/dL' and item.reference_range=='70 - 99' for item in readings)
    assert any(item.value=='0.9' and item.canonical_name=='creatinine_serum' for item in readings)


def test_actual_scanned_pdf_ocr(source_document):
    scan=pymupdf.open();page=scan.new_page(width=1000,height=500)
    page.insert_image(page.rect,stream=source_document[0].get_pixmap(dpi=120,alpha=False).tobytes('png'))
    values=engine.process_document(scan.tobytes(),'synthetic-scanned.pdf')
    assert any(item.value=='124.5' and item.source_page==1 for item in values)

@pytest.mark.parametrize('name,content',[('corrupt.pdf',b'%PDF bad'),('corrupt.jpg',b'not an image'),('empty.png',b'')])
def test_invalid_documents_do_not_generate_readings(name,content):
    with pytest.raises((ValueError,RuntimeError)):engine.process_document(content,name)
