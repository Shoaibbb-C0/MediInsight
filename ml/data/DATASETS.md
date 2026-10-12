# Dataset Acquisition & Lineage Record for Simplifier 2.0

## Permitted Usable Sources
1. **Clinical Lab Synthetic Benchmark (Built-in reproducible generator)**
   - Source: Simplifier Laboratory Simulation Engine (`ml/pipelines/synthetic_generator.py`)
   - License: MIT License (project native)
   - Scope: Multi-panel synthetic blood and metabolic laboratory reports with realistic clinical variability, multiple table styles, phone camera distortion, noise, perspective skew, and annotation labels.
   - Purpose: Generating clean, diverse ground truth annotations for CBC, Metabolic, Thyroid, Liver, Renal, and Lipid panels.

2. **Public Health Data Reference Specs**
   - Source: LOINC / CDC National Health and Nutrition Examination Survey (NHANES) Laboratory Specifications & reference intervals (Public Domain / US Government Works).
   - Intended Use: Standardizing canonical biomarker names, reference intervals, and measurement units across clinical assays.

## Strict Restrictions:
- No scraping of private patient documents or protected health records (PHI).
- Dataset splits are grouped strictly by template design (`template_id`), ensuring zero test-set leakage between training layouts and held-out test evaluations.
