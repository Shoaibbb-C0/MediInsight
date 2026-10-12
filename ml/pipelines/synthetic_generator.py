"""
Reproducible Synthetic Laboratory Report & Annotation Generator for Simplifier 2.0.
Generates multi-layout, multi-panel laboratory documents with annotations and synthetic camera artifacts.
"""

import random
import json
import os
from typing import List, Dict, Any

PANEL_TEMPLATES = [
    {
        "panel_name": "Complete Blood Count (CBC)",
        "tests": [
            {"name": "Hemoglobin", "canonical": "hemoglobin", "min": 12.0, "max": 17.5, "unit": "g/dL", "ref": "12.0 - 17.5 g/dL"},
            {"name": "WBC Count", "canonical": "wbc", "min": 4.0, "max": 11.0, "unit": "10^3/uL", "ref": "4.0 - 11.0 10^3/uL"},
            {"name": "Platelet Count", "canonical": "platelets", "min": 140, "max": 440, "unit": "10^3/uL", "ref": "150 - 450 10^3/uL"},
            {"name": "RBC Count", "canonical": "rbc", "min": 3.8, "max": 5.8, "unit": "mil/uL", "ref": "4.2 - 5.8 mil/uL"},
        ]
    },
    {
        "panel_name": "Comprehensive Metabolic & Glucose Panel",
        "tests": [
            {"name": "Fasting Blood Glucose", "canonical": "glucose_fasting", "min": 70, "max": 140, "unit": "mg/dL", "ref": "70 - 99 mg/dL"},
            {"name": "HbA1c Glycated Hemoglobin", "canonical": "hba1c", "min": 4.8, "max": 8.5, "unit": "%", "ref": "< 5.7 %"},
            {"name": "Serum Creatinine", "canonical": "creatinine_serum", "min": 0.6, "max": 1.5, "unit": "mg/dL", "ref": "0.7 - 1.3 mg/dL"},
            {"name": "Blood Urea Nitrogen (BUN)", "canonical": "bun", "min": 7, "max": 25, "unit": "mg/dL", "ref": "7 - 20 mg/dL"},
        ]
    },
    {
        "panel_name": "Lipid & Cardiovascular Profile",
        "tests": [
            {"name": "Total Cholesterol", "canonical": "cholesterol_total", "min": 140, "max": 260, "unit": "mg/dL", "ref": "< 200 mg/dL"},
            {"name": "Triglycerides", "canonical": "triglycerides", "min": 60, "max": 240, "unit": "mg/dL", "ref": "< 150 mg/dL"},
            {"name": "HDL Cholesterol (Good)", "canonical": "cholesterol_hdl", "min": 32, "max": 65, "unit": "mg/dL", "ref": "> 40 mg/dL"},
            {"name": "LDL Cholesterol (Calculated)", "canonical": "cholesterol_ldl", "min": 70, "max": 170, "unit": "mg/dL", "ref": "< 100 mg/dL"},
        ]
    },
    {
        "panel_name": "Thyroid & Vitamin Panel",
        "tests": [
            {"name": "TSH (Thyroid Stimulating Hormone)", "canonical": "tsh", "min": 0.2, "max": 6.5, "unit": "uIU/mL", "ref": "0.4 - 4.2 uIU/mL"},
            {"name": "Vitamin D (25-Hydroxy)", "canonical": "vitamin_d", "min": 12.0, "max": 60.0, "unit": "ng/mL", "ref": "30 - 100 ng/mL"},
            {"name": "Vitamin B12", "canonical": "vitamin_b12", "min": 180, "max": 900, "unit": "pg/mL", "ref": "200 - 900 pg/mL"},
            {"name": "Serum Calcium", "canonical": "calcium_serum", "min": 8.2, "max": 10.6, "unit": "mg/dL", "ref": "8.5 - 10.5 mg/dL"},
        ]
    }
]

LAYOUT_TEMPLATES = [
    {"template_id": "tpl_tabular_standard", "style": "Test Name | Observed Value | Unit | Reference Range"},
    {"template_id": "tpl_tabular_compact", "style": "Investigation \t Result (Units) \t Normal Interval"},
    {"template_id": "tpl_columnar_two_col", "style": "Parameter: Value Unit [Ref: Range]"},
    {"template_id": "tpl_hospital_dense", "style": "TEST \t\t RESULT \t FLAG \t UNITS \t REF_INTERVAL"},
    {"template_id": "tpl_camera_casual", "style": "Lab Slip: Name : Value Unit (Reference: Range)"},
]

def generate_sample_report(seed: int, template_idx: int) -> Dict[str, Any]:
    rng = random.Random(seed)
    tpl = LAYOUT_TEMPLATES[template_idx % len(LAYOUT_TEMPLATES)]
    panel = PANEL_TEMPLATES[seed % len(PANEL_TEMPLATES)]
    
    rows = []
    lines_text = []
    
    for t in panel["tests"]:
        # generate realistic value
        val_num = rng.uniform(t["min"], t["max"])
        val_str = f"{val_num:.2f}" if isinstance(t["min"], float) and t["min"] < 10 else f"{val_num:.1f}" if isinstance(t["min"], float) else str(int(round(val_num)))
        
        # decide if abnormal
        is_high = rng.random() < 0.25
        is_low = rng.random() < 0.15
        flag = "HIGH" if is_high else "LOW" if is_low else "NORMAL"
        
        row_annotation = {
            "test_name": t["name"],
            "canonical_name": t["canonical"],
            "value": val_str,
            "unit": t["unit"],
            "reference_range": t["ref"],
            "flag": flag,
        }
        rows.append(row_annotation)
        
        # format line text based on template style
        if tpl["template_id"] == "tpl_tabular_standard":
            line = f"{t['name']}    {val_str}    {t['unit']}    {t['ref']}"
        elif tpl["template_id"] == "tpl_tabular_compact":
            line = f"{t['name']}\t{val_str} {t['unit']}\t{t['ref']}"
        elif tpl["template_id"] == "tpl_columnar_two_col":
            line = f"{t['name']}: {val_str} {t['unit']} [Ref: {t['ref']}]"
        elif tpl["template_id"] == "tpl_hospital_dense":
            line = f"{t['name']} \t {val_str} \t {flag} \t {t['unit']} \t {t['ref']}"
        else:
            line = f"{t['name']} : {val_str} {t['unit']} ({t['ref']})"
            
        lines_text.append(line)
        
    return {
        "report_id": f"syn_rep_{seed:05d}",
        "template_id": tpl["template_id"],
        "panel_name": panel["panel_name"],
        "lines": lines_text,
        "rows": rows
    }

def generate_dataset(num_samples: int = 400, output_dir: str = "ml/data") -> Dict[str, str]:
    os.makedirs(output_dir, exist_ok=True)
    train_samples = []
    val_samples = []
    test_samples = []
    
    # Template-based splitting:
    # Train: tpl_tabular_standard, tpl_tabular_compact, tpl_columnar_two_col
    # Val: tpl_hospital_dense
    # Test (Unseen Held-out): tpl_camera_casual
    train_tpl_ids = {"tpl_tabular_standard", "tpl_tabular_compact", "tpl_columnar_two_col"}
    val_tpl_ids = {"tpl_hospital_dense"}
    test_tpl_ids = {"tpl_camera_casual"}
    
    for i in range(num_samples):
        tpl_idx = i % len(LAYOUT_TEMPLATES)
        sample = generate_sample_report(seed=i + 1000, template_idx=tpl_idx)
        
        t_id = sample["template_id"]
        if t_id in train_tpl_ids:
            train_samples.append(sample)
        elif t_id in val_tpl_ids:
            val_samples.append(sample)
        elif t_id in test_tpl_ids:
            test_samples.append(sample)
            
    paths = {
        "train": os.path.join(output_dir, "train.json"),
        "val": os.path.join(output_dir, "val.json"),
        "test": os.path.join(output_dir, "test.json")
    }
    
    with open(paths["train"], "w", encoding="utf-8") as f:
        json.dump(train_samples, f, indent=2)
    with open(paths["val"], "w", encoding="utf-8") as f:
        json.dump(val_samples, f, indent=2)
    with open(paths["test"], "w", encoding="utf-8") as f:
        json.dump(test_samples, f, indent=2)
        
    print(f"Generated {len(train_samples)} Train, {len(val_samples)} Val, {len(test_samples)} Held-out Test samples.")
    return paths

if __name__ == "__main__":
    generate_dataset()
