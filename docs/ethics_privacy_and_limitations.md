# Ethics, Privacy, and Limitations

## 倫理、隱私與限制 | Ethics, Privacy, and Limitations

This document defines the privacy boundary, ethical positioning, and modeling limitations for the **Risk-Aware Clinical AI Screening System for Cognitive Function** portfolio project.

Because this project is based on a clinical AI research context involving multimodal patient data, this file is intentionally explicit about what is **not released**, what the demo **does and does not claim**, and how the model output should be interpreted.

---

## 1. Repository Privacy Boundary | Repository 隱私邊界

This repository is a **portfolio reconstruction** and does not release real clinical data.

### 1.1 No Patient-Level Data Released

This repository does **not** include:

```text
patient-level records
hospital raw spreadsheets
medical record extracts
subject IDs
date-level visit records
medication records linked to individuals
laboratory results linked to individuals
MoCA scores linked to real participants
```

Any example tables in this repository should be synthetic or mock data.

### 1.2 No Raw Face / Tongue Images Released

This repository does **not** include raw clinical images, including:

```text
face images
tongue images
side-angle face images
lower-tongue images
MRI / MRS images
image metadata linked to real participants
```

For a public portfolio, image-related examples should be represented only as:

```text
mock image paths
synthetic metadata
placeholder tensors
generated non-patient images
conceptual diagrams
```

### 1.3 No Identifiable Clinical Information

This repository does not release any information that can identify individual participants, including:

```text
names
medical record numbers
exact dates of visits
raw image files
original clinical forms
unmasked subject identifiers
rare clinical combinations that could identify individuals
```

All public examples should be de-identified or synthetic.

---

## 2. Synthetic Demo Only | 僅使用 Synthetic Demo

The public version of this project should use **synthetic data only**.

Recommended public demo files:

```text
examples/
├── synthetic_patient_input_schema.json
├── synthetic_patient_examples.csv
├── sample_risk_outputs.json
└── sample_triage_cases.md
```

These files are intended to demonstrate the pipeline structure, not to reproduce the original clinical dataset.

A safe public example should show:

```text
how input features are structured
how model outputs are formatted
how uncertainty is represented
how triage rules are applied
how clinician review is triggered
```

It should not show:

```text
real clinical measurements
real patient images
real hospital records
real participant-level cognitive scores
```

---

## 3. Not a Diagnostic Tool | 非診斷工具

This repository is **not** a medical device, diagnostic system, or clinical decision automation tool.

The correct positioning is:

```text
clinical AI screening demo
risk-aware decision-support prototype
portfolio reconstruction
human-in-the-loop triage design
```

The incorrect positioning would be:

```text
AI diagnosis system
automatic cognitive impairment detector
replacement for MoCA
replacement for clinicians
production-ready medical device
```

The model output should be interpreted only as a **risk signal** that may help decide whether additional clinical review or formal assessment is needed.

Suggested repository statement:

> This project is for portfolio and research demonstration purposes only. It is not intended for clinical diagnosis, medical decision-making, or patient care.

中文版本：

> 本專案僅作為作品集與研究展示用途，不作為臨床診斷、醫療決策或病人照護使用。

---

## 4. Human Clinician Remains the Final Decision Maker | 臨床專業人員仍是最後決策者

A risk-aware clinical AI system should support clinicians, not replace them.

The system may help:

```text
summarize multimodal signals
flag potentially high-risk cases
highlight model uncertainty
suggest follow-up priority
support documentation and review
```

The system should not:

```text
confirm a disease diagnosis
make treatment decisions
override clinician judgment
interpret XAI explanations without domain expertise
make claims beyond validation evidence
```

Any high-risk or high-uncertainty output should require clinician review.

Recommended triage principle:

```text
High predicted risk + low uncertainty
→ recommend formal assessment

High predicted risk + high uncertainty
→ clinician review required

Low predicted risk + high uncertainty
→ collect more data or manual review

Low predicted risk + low uncertainty
→ routine monitoring
```

---

## 5. Study Design Limitation | 研究設計限制

The original project was designed as a pilot, cross-sectional, multimodal clinical AI study. Cross-sectional data can reveal associations and support exploratory prediction, but it cannot fully establish causal direction.

This matters because a model may identify that certain physiological markers are associated with cognitive scores, but that does not prove that those markers cause cognitive decline.

For example:

```text
physiological marker ↔ cognitive score
```

does not automatically mean:

```text
physiological marker → cognitive decline
```

A safe interpretation is:

> The model may identify predictive or associative risk markers, but causal mechanisms require stronger study designs.

---

## 6. Small-Sample and Pilot-Study Limitation | 小樣本與 Pilot Study 限制

The pilot study summarized in the project materials collected multimodal data from 110 participants. This is valuable for proof-of-concept development and early-stage modeling, but it also creates limitations.

Important limitations include:

```text
limited statistical power
unstable subgroup analysis
possible overfitting
limited external generalizability
sensitivity to missing data
sensitivity to image quality
difficulty validating rare disease patterns
```

A public portfolio should therefore avoid claiming that the model is clinically validated.

Appropriate claim:

> This project demonstrates a risk-aware clinical AI pipeline using multimodal data and synthetic examples.

Inappropriate claim:

> This model is ready to diagnose cognitive impairment in clinical practice.

---

## 7. Need for Prospective Validation | 需要前瞻性驗證

Before any real-world clinical deployment, the system would need additional validation steps, such as:

```text
external validation on independent patient cohorts
prospective validation
longitudinal follow-up
subgroup performance analysis
calibration assessment
clinical workflow evaluation
clinician usability testing
regulatory review if applicable
```

For cognitive-risk screening, future validation should specifically evaluate:

```text
whether model risk scores predict future cognitive decline
whether uncertainty estimates identify unreliable cases
whether triage rules reduce missed high-risk cases
whether clinician review improves safety
whether false alarms create unnecessary workload
```

---

## 8. Image Data Limitation | 影像資料限制

Face and tongue images are sensitive biometric and clinical data. They should be treated as high-risk data types.

Important risks include:

```text
identifiability risk
lighting variation
camera device variation
cropping error
pose and angle differences
inconsistent tongue exposure
data quantity limitation
standardized photo specification limitation
```

For the tongue-image modeling direction, the project notes emphasize the need to compress images into low-dimensional features while checking reconstruction quality. The tongue-image slides also identify data quality, standardized photo specifications, and data quantity as limitations.

Portfolio-safe handling:

```text
do not publish raw images
do not publish participant images
use synthetic tensors or mock image features
describe preprocessing conceptually
release only code templates and documentation
```

---

## 9. XAI and Interpretability Limitation | 可解釋性限制

Explainable AI can support model interpretation, but it should not be treated as clinical proof.

XAI methods may show which image regions or variables influenced model output, but:

```text
different XAI methods may highlight different features
highlighted regions may not be clinically meaningful
spurious correlations may appear important
domain expertise is required for interpretation
XAI explanation is not the same as causal explanation
```

Therefore, XAI outputs should be framed as:

```text
model interpretation support
hypothesis generation
clinician discussion aid
```

not as:

```text
verified disease mechanism
standalone diagnostic evidence
causal proof
```

---

## 10. Bias, Fairness, and Generalizability | 偏誤、公平性與泛化性

Clinical AI systems may behave differently across patient subgroups.

Potential subgroup dimensions include:

```text
age
sex
education level
chronic disease burden
body composition
image quality
camera condition
clinic population
measurement completeness
```

A risk-aware version of this project should include subgroup evaluation when the data size allows.

Recommended checks:

```text
performance by age group
performance by sex
performance by disease burden
missingness by subgroup
image quality by subgroup
calibration by risk group
false-negative review
false-positive review
```

Because the original dataset is a pilot sample, subgroup claims should remain cautious.

---

## 11. Model Output Communication | 模型輸出溝通原則

Clinical AI outputs should be communicated in a way that avoids overconfidence.

Recommended output format:

```json
{
  "predicted_moca": 23.4,
  "risk_class": "medium",
  "uncertainty_level": "high",
  "key_predictors": ["lower total body water", "lower platelet count"],
  "triage_action": "clinician_review_recommended",
  "clinical_note": "This is a screening signal, not a diagnosis."
}
```

Avoid output format:

```json
{
  "diagnosis": "cognitive impairment",
  "confidence": "95%",
  "treatment": "..."
}
```

The system should communicate uncertainty and recommend clinician review when appropriate.

---

## 12. Public Portfolio Safety Checklist | 公開作品集安全檢查表

Before publishing this repository, confirm:

```text
[ ] No real patient-level records are included.
[ ] No raw face or tongue images are included.
[ ] No MRI / MRS raw files are included.
[ ] No hospital raw spreadsheets are included.
[ ] No subject IDs or identifiable metadata are included.
[ ] All examples are synthetic or mock data.
[ ] README states this is not a diagnostic tool.
[ ] README states this is not for medical decision-making.
[ ] The license applies only to reconstructed demo code.
[ ] Limitations are clearly documented.
[ ] Human clinician review remains part of the triage policy.
```

---

## 13. Recommended README Notice | README 建議聲明

The README should include the following statement:

> This repository does not release patient-level data, clinical images, hospital records, or identifiable information. All examples are synthetic or mock demonstrations. This project is not intended for clinical diagnosis, medical decision-making, or patient care. The code and documents are provided only for portfolio demonstration and research communication.

中文版本：

> 本 repository 不公開任何病人層級資料、臨床影像、醫院病歷或可識別資訊。所有範例皆為 synthetic 或 mock demonstration。本專案不作為臨床診斷、醫療決策或病人照護用途，僅作為作品集展示與研究溝通使用。

---

## 14. Key Takeaway | 核心重點

> A clinical AI portfolio project should demonstrate technical ability without exposing patient data or overstating clinical readiness. The safest and most professional framing is to present this work as a risk-aware, human-in-the-loop screening pipeline that uses synthetic examples to communicate data processing, modeling, uncertainty, and triage design.

中文版本：

> 醫療 AI 作品集的重點，是展示技術能力，同時不暴露病人資料、不誇大臨床成熟度。最安全也最專業的定位，是把此專案呈現為一個具風險意識、需要臨床人員審核的早期篩檢與分流流程，並使用 synthetic examples 展示資料處理、建模、不確定性與分流設計。

---

## 15. Source Materials Used | 參考素材

This document was drafted based on the following project materials:

- NTUH research proposal: *Incorporating artificial intelligence-assisted facial medical inspection into post-pandemic management of chronic diseases*
- NTUH pilot study progress report
- Tongue-image modeling slides
- Prior thesis framing and project notes on cognitive-risk screening
