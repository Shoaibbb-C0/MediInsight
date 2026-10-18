"""Build-time model preparation; no cloud project or medical document required."""
import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
from app.services.extraction_service import engine
from app.services import pdf_generator
from rapidocr import RapidOCR
if engine.model is None: raise RuntimeError("Required trained extraction checkpoint is missing.")
pdf_generator.init_pdf_fonts()
if not pdf_generator.DEVANAGARI_FONT_REGISTERED: raise RuntimeError("Bundled Devanagari PDF fonts are unavailable.")
RapidOCR()  # Downloads/checks OCR model assets during build rather than a patient's request.
print("Extraction model, PDF fonts and OCR runtime initialized.")
