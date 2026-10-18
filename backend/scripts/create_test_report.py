"""Emit a synthetic source document for browser tests; no patient information."""
import sys
import argparse
from pathlib import Path
import pymupdf
parser=argparse.ArgumentParser()
parser.add_argument("--png",action="store_true")
parser.add_argument("--output")
args=parser.parse_args()
report=pymupdf.open();page=report.new_page()
page.insert_text((40,40),'SYNTHETIC TEST FIXTURE - NOT A PATIENT')
page.insert_text((40,80),'Fasting Blood Glucose : 124.5 mg/dL (70 - 99 mg/dL)')
page.insert_text((40,120),'Serum Creatinine : 0.9 mg/dL')
content=report[0].get_pixmap(dpi=150,alpha=False).tobytes('png') if args.png else report.tobytes()
if args.output:
    output=Path(args.output);output.parent.mkdir(parents=True,exist_ok=True);output.write_bytes(content)
else: sys.stdout.buffer.write(content)
