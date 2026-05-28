# Multimodal Data Pipeline

## 多模態資料管線 | Multimodal Data Pipeline

This document describes how multimodal clinical data in the **Risk-Aware Clinical AI Screening System for Cognitive Function** can be organized into a reproducible, privacy-preserving, and model-ready data pipeline.

The purpose of this document is not to release real hospital data. Instead, it explains the structure of the original research data and defines how a public portfolio version should reconstruct the pipeline using **synthetic / mock data only**.

---

## 1. Pipeline Overview | 資料管線總覽

The original clinical research project was designed around multimodal data collected from patients with chronic diseases at the Family Medicine Department of National Taiwan University Hospital. The project materials describe five major data modalities:

```text
Patient Data
├── Clinical / Physiological Data
│   ├── interview-based medical history
│   ├── physiological measurements
│   ├── chronic disease indicators
│   ├── blood and urine biomarkers
│   └── medication-related variables
│
├── Psychological / Behavioral Questionnaires
│   ├── BFI personality traits
│   ├── WHO-5 well-being
│   ├── CES-D depressive symptoms
│   └── CPSQI sleep quality
│
├── Cognitive Assessment
│   └── MoCA total score and related cognitive measures
│
├── Face / Tongue Images
│   ├── frontal face image
│   ├── side-angle face images
│   ├── upper tongue image
│   └── lower tongue image
│
├── MRI / MRS Brain Imaging
│   ├── brain structure
│   └── spectroscopy-related information
│
└── Derived Modeling Tables
    ├── cleaned tabular dataset
    ├── variable coding table
    ├── pairwise correlation matrix
    ├── selected feature groups
    └── model-ready synthetic demo tables
```

In this repository, the public version of the pipeline should be reconstructed as:

```text
Raw Clinical Sources
→ Data Cleaning and Coding
→ Feature Grouping
→ Data Quality Checks
→ Derived Modeling Tables
→ Risk-Aware Modeling
→ Synthetic Demo Outputs
```

---

## 2. Raw Data Sources | 原始資料來源

The original project involved multiple raw sources collected or organized during the pilot study. Based on the project notes, the tabular side of the data pipeline began with hospital-organized raw data and questionnaire / physiological indicator forms.

### 2.1 Hospital-Organized Raw Data

Original internal source:

```text
Raw Data (醫院整理).xlsx
```

Purpose:

- store clinical and physiological information organized by the hospital;
- serve as the first structured data source before cleaning and coding;
- preserve subject-level information for internal research use only.

Public portfolio policy:

- do not include this file;
- do not include patient-level records;
- reproduce only the schema using synthetic rows.

### 2.2 Merged and Coded Raw Data

Intermediate internal source:

```text
Raw Data with Coding (已將兩個表格合併).xlsx
```

Purpose:

- merge questionnaire responses and physiological indicator data;
- standardize variable names;
- add coding logic and variable annotations;
- create one model-ready working table.

Public portfolio policy:

- do not include the original merged file;
- publish only a synthetic version such as `examples/synthetic_patient_examples.csv`.

### 2.3 Questionnaire Data

The questionnaire side includes:

- structured interview form;
- MoCA cognitive assessment;
- psychological and behavioral questionnaires;
- total scores for selected scales.

The preprocessing note indicates that only total-score variables were retained for modeling, while item-level questionnaire fields were removed to avoid unnecessary dimensionality and noise.

### 2.4 Physiological Indicator Data

The physiological side includes:

- disease history;
- medication-related variables;
- blood test indicators;
- urine test indicators;
- body composition metrics;
- vital signs and related physiological measurements.

The preprocessing notes also mention that disease-history variables and medication columns require careful interpretation. For example, disease diagnosis and medication use may appear in adjacent variables, and some coding inconsistencies require manual review.

### 2.5 Image Data

The original project also included standardized face and tongue images. These images are not part of the public portfolio repository.

Public portfolio policy:

- do not release face images;
- do not release tongue images;
- use mock image paths or synthetic image metadata only;
- if demo images are needed, use generated / non-patient / placeholder images.

### 2.6 MRI / MRS Data

The original project design included MRI / MRS brain imaging to connect chronic disease, neuroinflammation-related mechanisms, brain structure, and cognitive function.

Public portfolio policy:

- do not release raw neuroimaging data;
- describe the modality at a conceptual level only;
- use placeholder feature names if needed, such as `brain_feature_001`.

---

## 3. Data Modalities | 資料模態

The pipeline should treat each data type as a separate modality before merging into modeling tables.

| Modality | Example Variables / Data | Role in Modeling |
|---|---|---|
| Demographics | age, sex, education group | baseline covariates |
| Chronic disease indicators | diabetes, hypertension, kidney disease, cardiovascular disease, liver disease, sleep disorder | disease burden and risk context |
| Physiological measurements | height, weight, waist circumference, blood pressure, body composition | low-burden clinical signals |
| Blood / urine biomarkers | A1C, fasting glucose, LDL, HDL, creatinine, GFR, UACR, platelet count, hsCRP, ferritin | physiological predictors |
| Psychological / behavioral questionnaires | WHO-5, CES-D, CPSQI, BFI traits | mental health, sleep, and behavioral covariates |
| Cognitive assessment | MoCA | main cognitive outcome |
| Face / tongue images | standardized facial and tongue photos | image-based predictive signals |
| MRI / MRS | brain structure / spectroscopy features | future mechanistic or validation features |

---

## 4. Data Linkage by Subject ID | 以受試者編號串接資料

All modalities should be linked through a subject-level identifier.

```text
subject_id
├── questionnaire table
├── physiological indicator table
├── cognitive assessment table
├── image metadata table
├── MRI / MRS metadata table
└── derived modeling table
```

The public repository should preserve the logic of linkage without exposing real identifiers.

Recommended public schema:

```text
synthetic_patient_id
├── demographic features
├── physiological features
├── questionnaire scores
├── cognitive target
├── image metadata placeholder
└── derived risk output
```

Example:

```csv
synthetic_patient_id,age,sex,TBW,Plt,WHO5,CESD,CPSQI,MoCA
synthetic_001,68,F,32.5,230,16,8,6,24
synthetic_002,55,M,38.2,280,19,5,4,28
```

---

## 5. Feature Groups | 特徵群組

The preprocessing notes organize retained tabular variables into several feature groups. These groups can be used to design the synthetic demo schema and modeling pipeline.

### 5.1 Grouping Variables

```text
Group
Sex
Age
```

Purpose:

- represent cohort membership or clinical grouping;
- provide baseline demographic adjustment;
- help evaluate subgroup behavior and model robustness.

### 5.2 Body and Vital-Sign Indicators

```text
BH
WC
SBP
DBP
BW
FFM
BFM
BFP
```

Interpretation:

- `BH`: body height
- `WC`: waist circumference
- `SBP`: systolic blood pressure
- `DBP`: diastolic blood pressure
- `BW`: body weight
- `FFM`: fat-free mass
- `BFM`: body fat mass
- `BFP`: body fat percentage

Potential modeling role:

- general physiological status;
- metabolic and vascular risk context;
- baseline adjustment variables.

### 5.3 Sleep-Related Indicators

```text
Chrono
Interrupt
Nap
```

Interpretation:

- sleep chronotype;
- sleep interruption frequency;
- daytime nap duration.

Risk-aware note:

Some sleep-related variables may be subjective or behaviorally ambiguous. These variables should be reviewed carefully before modeling and may require sensitivity analysis.

### 5.4 Questionnaire Total Scores

```text
CES-D
CPSQI
WHO-5
MoCA
Extraversion
Agreeableness
Conscientiousness
Neuroticism
Openness
```

Interpretation:

- `CES-D`: depressive symptom score;
- `CPSQI`: sleep quality score;
- `WHO-5`: well-being score;
- `MoCA`: cognitive assessment score;
- BFI traits: personality-related covariates.

Modeling role:

- MoCA is the main cognitive target in the cognitive-risk pipeline;
- other questionnaire scores may be used as covariates or secondary signals.

### 5.5 Blood and Urine Indicators

```text
TBW
FIB4
A1C
GluAC
Insulin
TCHO
LDL
TG
HDL
Cr
GFR
UACR
UA
ALT
AST
T-Bil
D-Bil
Hb
Plt
hsCRP
Ferritin
```

Potential modeling role:

- metabolic function;
- kidney function;
- liver function;
- inflammation;
- vascular and hematological signals;
- physiological predictors of cognitive risk.

In the cognitive-function modeling route, variables such as total body water (`TBW`) and platelet count (`Plt`) are particularly important because they emerged as stable physiological predictors in the thesis modeling results.

---

## 6. Target Variables | 建模目標變數

The repository should distinguish between original research targets and portfolio demo targets.

### 6.1 Cognitive Function Target

Primary target for this portfolio project:

```text
MoCA total score
```

Use case:

```text
Physiological / questionnaire / image-derived features
→ predict MoCA or cognitive-risk class
→ estimate uncertainty
→ assign triage action
```

Derived target examples:

```text
predicted_moca
cognitive_risk_label
risk_class: low / medium / high
triage_action
```

### 6.2 Physiological Targets for Image Modeling

For image-based modeling, possible targets include:

```text
blood markers
urine markers
body composition variables
chronic disease indicators
```

Use case:

```text
face / tongue image
→ image features
→ physiological target prediction
```

### 6.3 Chronic Disease Classification Targets

For chronic disease modeling, possible classification outputs include:

```text
diabetes status
kidney disease status
cardiovascular disease status
liver disease status
sleep disorder status
cancer-related indicators
```

Risk-aware note:

Disease classification outputs should be framed as screening / decision-support signals rather than diagnostic conclusions.

---

## 7. Derived Modeling Tables | 衍生建模資料表

The internal workflow used derived tables to support modeling and feature selection.

### 7.1 Cleaned Tabular Dataset

Internal purpose:

```text
Raw Data
→ merged table
→ coding table
→ selected variables
→ cleaned modeling dataset
```

Portfolio equivalent:

```text
examples/synthetic_patient_examples.csv
```

Recommended columns:

```text
synthetic_patient_id
age
sex
TBW
Plt
A1C
GluAC
LDL
GFR
hsCRP
WHO5
CESD
CPSQI
MoCA
predicted_moca
cognitive_risk_label
```

### 7.2 Pairwise Correlation Matrix

Internal purpose:

- inspect relationships among retained variables;
- identify variables with moderate or high correlation;
- support feature grouping;
- reduce redundant modeling targets.

Portfolio equivalent:

```text
reports/feature_grouping_summary.md
examples/synthetic_correlation_summary.csv
```

Recommended processing logic:

```text
cleaned tabular dataset
→ compute pairwise correlation matrix
→ flag |correlation| >= 0.3
→ group highly related variables
→ document feature groups and modeling implications
```

### 7.3 Model-Ready Tables

Recommended public tables:

```text
examples/synthetic_patient_examples.csv
examples/synthetic_patient_input_schema.json
examples/sample_risk_outputs.json
```

These should be enough for a public demo without exposing original clinical data.

---

## 8. Data Quality Issues | 資料品質與風險議題

A risk-aware AI pipeline should document data quality issues before modeling.

### 8.1 Coding Consistency

Potential issue:

- disease status and medication variables may not always align;
- cohort group coding may differ across files;
- some records require manual verification.

Recommended handling:

```text
1. document coding rules;
2. add data validation checks;
3. flag inconsistent records;
4. avoid silently overwriting uncertain values.
```

### 8.2 Variable Naming and Encoding

Potential issue:

- Chinese variable names may cause package compatibility or encoding issues;
- inconsistent naming makes reproducibility harder.

Recommended handling:

```text
1. maintain a variable dictionary;
2. translate variables into consistent English names;
3. keep original meaning in documentation;
4. version the coding table.
```

### 8.3 Missingness and Low-Quality Variables

Potential issue:

- some variables may have excessive missing values;
- some variables may have low variance or unclear reliability;
- subjective behavioral variables may not align with objective physiological states.

Recommended handling:

```text
1. compute missingness rate;
2. flag low-variance variables;
3. separate subjective and objective measurements;
4. perform sensitivity analysis before using uncertain variables.
```

### 8.4 Redundant and Correlated Variables

Potential issue:

- many physiological variables are correlated;
- redundant variables may make interpretation unstable;
- highly correlated targets may be grouped before model training.

Recommended handling:

```text
1. compute pairwise correlations;
2. group related variables;
3. avoid over-interpreting unstable coefficients;
4. validate selected predictors using alternative models.
```

### 8.5 Image Quality and Metadata

Potential issue:

- lighting variation;
- face/tongue cropping quality;
- image angle and distance;
- camera device differences.

Recommended handling:

```text
1. save image metadata;
2. include lighting and capture-quality checks;
3. avoid using low-quality images without flags;
4. treat image preprocessing errors as clinical AI risk factors.
```

### 8.6 Small-Sample Pilot Data

Potential issue:

- pilot data may be useful for exploratory modeling but insufficient for broad clinical deployment;
- performance estimates may be unstable;
- subgroup evaluation may be limited.

Recommended handling:

```text
1. frame results as exploratory;
2. report uncertainty;
3. use human-in-the-loop triage;
4. require external validation before clinical use.
```

---

## 9. Public Demo Strategy | 公開展示策略：Synthetic Data Only

Because this is a clinical AI project, the public GitHub repository should not release real clinical records or patient images.

### 9.1 Do Not Release

```text
real patient-level data
raw hospital spreadsheets
face images
tongue images
MRI / MRS data
medical record details
identifiable information
internal hospital documents
```

### 9.2 Release Instead

```text
synthetic schema
synthetic patient rows
mock risk outputs
data pipeline documentation
feature group descriptions
example preprocessing code
risk triage logic
modeling strategy notes
```

### 9.3 Recommended Public Files

```text
examples/
├── synthetic_patient_input_schema.json
├── synthetic_patient_examples.csv
├── sample_risk_outputs.json
└── sample_triage_cases.md
```

### 9.4 Privacy Boundary Statement

Suggested repository statement:

> This repository does not release patient-level data, clinical images, hospital records, or identifiable information. All examples are synthetic or mock demonstrations designed to show the data pipeline and risk-aware modeling logic.

中文版本：

> 本 repository 不公開任何病人層級資料、臉舌照片、醫院原始資料或可識別資訊；所有範例皆為 synthetic / mock data，僅用於展示資料管線與風險意識建模邏輯。

---

## 10. Suggested Implementation Mapping | 對應程式模組

This document maps to the following repository modules:

```text
src/data_preprocessing/
├── tabular_cleaning.py
├── variable_filtering.py
└── correlation_grouping.py

src/image_preprocessing/
├── face_crop_quality_check.py
├── tongue_image_preprocessing.py
└── lighting_metadata_parser.py

src/risk_triage/
├── cognitive_risk_score.py
├── uncertainty_score.py
└── clinical_triage_rule.py
```

Recommended workflow:

```text
1. Use synthetic_patient_examples.csv as the public input.
2. Run tabular_cleaning.py to validate schema and standardize names.
3. Run variable_filtering.py to flag missingness and low-quality variables.
4. Run correlation_grouping.py to generate a correlation summary.
5. Feed selected features into modeling modules.
6. Convert model outputs into risk classes and triage actions.
```

---

## 11. Key Takeaway | 核心重點

> The multimodal data pipeline is the foundation of this risk-aware clinical AI project. The goal is not only to combine many data types, but to preserve traceability from raw clinical signals to cleaned features, model-ready tables, uncertainty-aware outputs, and clinician-reviewed triage decisions.

中文版本：

> 多模態資料管線是這個臨床 AI 專案的核心：重點不只是把很多資料合併在一起，而是要讓每個臨床訊號從原始資料、清理、特徵分群、建模表格，到不確定性輸出與臨床分流決策，都能被追蹤與審核。

---
