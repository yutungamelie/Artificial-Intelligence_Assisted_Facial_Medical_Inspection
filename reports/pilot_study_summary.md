# Pilot Study Summary

## Pilot Study Summary | Pilot Study Portfolio Report

This report summarizes the pilot study behind the **Risk-Aware Clinical AI Screening System for Cognitive Function** portfolio project.

The goal of this file is to present the original clinical AI study in a professional portfolio format: why the study was needed, what data were collected, what was achieved, what my contribution was, and how the original research context is reconstructed safely for a public GitHub repository.

This report is written as a **portfolio reconstruction**. It does not release patient-level data, hospital raw files, clinical images, or any identifiable information.

---

## 1. Research Background | 研究背景

Chronic disease management is a long-term healthcare challenge. Chronic conditions require repeated monitoring, follow-up, and interpretation of physiological change over time. During and after the COVID-19 pandemic, this problem became more visible because many chronic disease patients reduced hospital visits, which made routine monitoring more difficult.

In telemedicine and mobile health settings, clinicians may lose access to parts of traditional in-person examination, including:

```text
visual inspection
palpation
percussion
auscultation
face-to-face interaction
```

The research project was motivated by the idea that AI-assisted visual inspection may help clinicians recover part of this missing information in remote or low-contact care settings.

The original project title was:

```text
Incorporating artificial intelligence-assisted facial medical inspection
into post-pandemic management of chronic diseases
```

The broader clinical motivation was:

> Use multimodal patient data, especially face and tongue images, to explore whether AI models can support chronic disease management, remote health monitoring, and clinical decision support.

---

## 2. Research Goals | 研究目標

The original research proposal defined the project as a cross-disciplinary study combining family medicine, artificial intelligence, and psychology.

The planned multimodal data sources included:

```text
a. interview-based medical history and physiological measurements
b. chronic disease clinical indicators
c. face and tongue images
d. MRI / MRS brain-structure imaging
e. cognitive function assessment results
```

The proposal organized the study around four major aims:

```text
Aim 1:
Collect five types of multimodal data from 500–1,000 patients.

Aim 2:
Train deep neural network models that use face or tongue images
to predict physiological measurements or chronic disease indicators.

Aim 3:
Use explainable AI methods to understand which face / tongue features
the model uses for prediction.

Aim 4:
Analyze the relationship between physiological / chronic disease indicators
and brain / cognitive outcomes.
```

For the portfolio version, the project is reframed more cautiously as:

```text
multimodal clinical data
→ exploratory AI modeling
→ cognitive-risk screening signals
→ uncertainty-aware triage
→ human-in-the-loop clinical review
```

---

## 3. Study Design | 研究設計

The study was conducted as a pilot study at the Family Medicine Department of National Taiwan University Hospital.

The pilot study was designed as a cross-sectional multimodal data collection and modeling project.

Conceptual study workflow:

```text
Patient recruitment
→ informed consent
→ physiological measurements
→ structured interview and medical record review
→ cognitive / psychological assessments
→ face and tongue image acquisition
→ MRI / MRS imaging when applicable
→ multimodal database construction
→ AI / statistical modeling
```

The portfolio interpretation is:

> The study created a pilot multimodal clinical dataset that can support research on chronic disease indicators, cognitive function, medical image representation, and AI-assisted risk screening.

---

## 4. Data Collected | 蒐集資料

The pilot study collected five major categories of multimodal data.

### 4.1 Interview-Based Medical History and Physiological Measurements

This category included:

```text
age
sex
disease history
medication history
allergy history
dietary habits
smoking and alcohol behavior
physical activity
psychological health
sleep condition
body measurements
blood pressure
body composition
```

### 4.2 Chronic Disease Clinical Indicators

The project focused on several chronic disease domains, including:

```text
type 2 diabetes / glycemic control
kidney disease indicators
cardiovascular indicators
liver disease indicators
cancer-related indicators
sleep and mental health indicators
```

Examples of measured or retrieved clinical indicators:

```text
GluAC
A1C
eGFR
UACR
total cholesterol
HDL-C
LDL-C
triglycerides
CBC
ALT
AST
blood pressure
medication records
diagnosis codes
```

### 4.3 Face and Tongue Images

The imaging data included standardized visual inspection materials:

```text
frontal face image
side-angle face images
upper tongue image
lower tongue image
```

These images were intended for future CNN-based modeling and explainable AI analysis.

Portfolio note:

```text
No raw face or tongue images should be released in the public repository.
```

### 4.4 MRI / MRS Brain Imaging

The project also planned to collect brain-structure and spectroscopy-related data because chronic diseases may be associated with neuroinflammation, brain damage, and cognitive decline.

Portfolio note:

```text
MRI / MRS data should be described conceptually only.
No raw neuroimaging data should be released.
```

### 4.5 Cognitive Function Assessment

The study collected mental and cognitive assessment results, including cognitive function measures relevant to MoCA-based cognitive-risk modeling.

In the portfolio version, this later became a key modeling direction:

```text
physiological and psychological indicators
→ MoCA prediction
→ cognitive-risk screening
```

---

## 5. Study Scale | 研究規模

The original proposal planned to collect multimodal data from:

```text
500–1,000 patients
```

The one-year pilot study successfully collected data from:

```text
110 patients
```

The progress report states that since January 1, 2023, the study collected five categories of multimodal data from 110 patients:

```text
1. interview-based medical history and physiological measurements
2. chronic disease clinical indicators
3. face and tongue photos
4. MRI / MRS brain-structure images
5. cognitive function assessment results
```

Portfolio interpretation:

> The pilot dataset was sufficient for proof-of-concept development and early modeling experiments, but it should not be treated as enough evidence for production-level clinical deployment.

---

## 6. Sanity Check | 建全性測試

A sanity check was conducted to confirm that the image modeling pipeline could learn meaningful information from standardized face images.

The completed sanity-check task was:

```text
Input:
frontal face image

Output:
biological sex classification

Model:
CNN-based binary classification

Reported accuracy:
0.93
```

Why this sanity check matters:

```text
it verifies that the face-image pipeline can load and process images
it checks whether image quality is sufficient for a basic visual classification task
it confirms that the modeling setup can learn a strong signal from the dataset
it provides an early validation before attempting more clinically complex targets
```

Risk-aware interpretation:

> A sex-classification sanity check does not prove clinical diagnostic ability. It only confirms that the image pipeline can learn a relatively clear visual signal.

This distinction is important for responsible portfolio communication.

---

## 7. Original Modeling Vision | 原始建模願景

The original research project aimed to train CNN models with:

```text
face images
tongue images
brain images
```

as model inputs, and with:

```text
chronic disease classification
physiological measurements
clinical indicators
```

as model outputs.

The project expected two types of models:

### 7.1 Classification Models

Example outputs:

```text
chronic disease category
ICD-related diagnosis information
binary disease status
```

Evaluation metrics:

```text
accuracy
AUC
```

### 7.2 Regression Models

Example outputs:

```text
eGFR
UACR
biochemical markers
continuous physiological measurements
```

Evaluation metrics:

```text
correlation between predicted and true values
relative prediction error
```

### 7.3 Explainable AI

The proposal emphasized using XAI to understand which face / tongue features the CNN model used to make predictions.

Important caution from the project materials:

> Different XAI methods may highlight different decision features, so domain expertise is still required to correctly interpret XAI results.

Portfolio interpretation:

> Explainability should support clinical review and hypothesis generation, not replace clinical reasoning.

---

## 8. My Role | 我負責的內容

In this portfolio reconstruction, my contribution is framed as supporting the transformation of a clinical pilot study into a risk-aware AI modeling workflow.

My responsibilities can be summarized as:

```text
1. supported multimodal clinical AI pilot study execution;
2. organized and interpreted project materials, progress reports, and modeling directions;
3. contributed to tabular data preprocessing and feature organization;
4. worked with physiological, psychological, and cognitive variables for downstream modeling;
5. explored MoCA cognitive-function prediction using tabular clinical indicators;
6. supported image preprocessing logic for face / tongue modeling directions;
7. summarized modeling routes into interpretable portfolio modules;
8. reframed the project into a risk-aware clinical AI screening pipeline.
```

For GitHub portfolio purposes, my contribution is presented through the following modules:

```text
docs/clinical_problem_framing.md
docs/multimodal_data_pipeline.md
docs/tabular_data_preprocessing.md
docs/image_preprocessing_notes.md
docs/modeling_strategy.md
docs/uncertainty_triage_policy.md
reports/pilot_study_summary.md
reports/tabular_model_findings.md
reports/image_to_physiology_findings.md
```

---

## 9. Portfolio Reconstruction Scope | 作品集重建範圍

This repository is not a direct release of the hospital research project.

Instead, it is a portfolio-safe reconstruction that demonstrates:

```text
problem framing
multimodal data pipeline design
tabular preprocessing
image preprocessing logic
modeling strategy
risk-aware clinical AI positioning
uncertainty-aware prioritization recommendation design
ethical and privacy boundaries
```

### 9.1 Included in the Public Repository

The public GitHub repository may include:

```text
documentation
synthetic patient input schema
mock patient examples
sample risk outputs
modeling strategy notes
risk triage logic
portfolio-safe code templates
```

### 9.2 Excluded from the Public Repository

The public GitHub repository should not include:

```text
patient-level clinical records
hospital raw spreadsheets
real MoCA scores linked to participants
face images
tongue images
MRI / MRS raw data
identifiable metadata
internal hospital documents
production clinical software
```

### 9.3 Public Demo Strategy

Public examples should use only:

```text
synthetic data
mock image paths
placeholder model outputs
fictional triage cases
```

This allows the repository to show engineering ability without violating patient privacy or overstating clinical readiness.

---

## 10. Clinical Safety Framing | 臨床安全定位

This project should not be described as:

```text
AI diagnosis system
automatic cognitive impairment detector
production-ready medical device
clinician replacement
```

The safer and more accurate framing is:

```text
risk-aware clinical AI screening pipeline
early cognitive-risk signal exploration
decision-support prototype
human-in-the-loop triage design
portfolio reconstruction using synthetic examples
```

Suggested safety statement:

> This project is not intended for clinical diagnosis, medical decision-making, or patient care. It is a portfolio reconstruction that demonstrates how multimodal clinical data can be organized into a risk-aware AI screening workflow.

---

## 11. Key Technical Observations and Design Implications | 關鍵技術觀察與設計意涵

### 11.1 Problem Framing Matters More Than Model Complexity

In clinical AI, choosing a sophisticated model is not enough. The problem must be framed carefully:

```text
What is the target?
What is the clinical use case?
What is the risk of error?
Who reviews the output?
What data quality issues may affect the result?
```

### 11.2 Sanity Checks Are Necessary

Before using models for clinical targets, the pipeline should first pass simpler checks, such as whether a CNN can learn an obvious image signal.

### 11.3 Multimodal Data Requires Traceability

Because the study collected clinical, physiological, image, brain, and cognitive data, every modeling result should remain traceable to its data source and preprocessing decision.

### 11.4 Explainability Is Not Causality

XAI can help interpret model behavior, but it does not prove clinical mechanisms.

### 11.5 Pilot Studies Require Cautious Claims

The pilot study is valuable for proof-of-concept work, but broader clinical claims require external validation, prospective testing, and stronger causal evidence.

---

## 12. Portfolio Takeaway | 作品集總結

> This pilot study provided the foundation for a risk-aware clinical AI screening portfolio project. It collected multimodal data from 110 chronic disease patients, validated the feasibility of image-based CNN modeling through a face-image sanity check, and motivated a broader workflow that connects tabular clinical modeling, image preprocessing, explainability, uncertainty estimation, and human-in-the-loop triage.

中文版本：

> 這個 pilot study 是 risk-aware clinical AI screening 作品集的基礎：它從 110 位慢性病患者蒐集五大類多模態資料，透過正臉照片預測性別的 CNN sanity check 驗證影像建模管線可行，並進一步支持我將專案整理成結合表格臨床建模、影像前處理、可解釋性、不確定性估計與臨床人員審核分流的 AI 風險篩檢流程。

---
