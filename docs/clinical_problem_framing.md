# Clinical Problem Framing

## 臨床問題定義 | Clinical Problem Framing

This document defines the clinical problem behind the **Risk-Aware Clinical AI Screening System for Cognitive Function**.  
The goal is to clarify why this project matters, what problem it is trying to solve, and why the system should be positioned as **early screening / clinical decision support / triage**, rather than an automated diagnostic tool.

---

## 1. Clinical Pain Point | 臨床痛點

Chronic disease management requires long-term monitoring, repeated follow-up, and continuous interpretation of physiological changes. However, this is difficult in real-world care settings because patients may not always return to the hospital regularly, and clinicians often need to make decisions based on fragmented clinical signals.

In the post-pandemic context, this challenge became more visible. Chronic disease patients may avoid hospital visits, while telemedicine and mobile health workflows reduce opportunities for traditional face-to-face inspection, palpation, percussion, and auscultation. As a result, clinicians may lose part of the contextual, visual, and interaction-based information that usually supports medical judgment.

From an AI application perspective, this creates a practical problem:

> How can we use multimodal clinical data to support earlier and lower-burden risk screening, while still keeping clinicians in the decision loop?

This project approaches that problem by exploring whether physiological measurements, blood and urine markers, psychological and behavioral questionnaires, cognitive assessment scores, and face/tongue images can be organized into a clinical AI pipeline for cognitive-risk screening.

---

## 2. Why Telemedicine and Mobile Health Matter | 為什麼慢性病管理需要遠距與行動健康輔助

Chronic diseases are long-term conditions that require repeated observation rather than one-time diagnosis. When patients reduce hospital visits, clinicians have fewer opportunities to detect gradual changes in health status.

Telemedicine and mobile health can help reduce this burden by enabling more scalable, low-contact, and potentially home- or community-based monitoring. However, remote care also introduces a limitation: clinicians may not directly observe the patient in the same way they would during an in-person visit.

This is where AI-assisted medical inspection becomes relevant. Computer vision and machine learning may help extract structured signals from images and clinical measurements, such as:

- face and tongue images,
- physiological measurements,
- blood and urine biomarkers,
- cognitive and psychological assessments,
- longitudinal or repeated health records in future extensions.

In this project, AI is not framed as a replacement for clinical judgment. Instead, it is framed as an additional layer that may help clinicians identify cases that deserve closer follow-up.

---

## 3. Why Cognitive-Risk Screening Matters | 為什麼認知風險篩檢有意義

Cognitive decline is especially important in chronic disease populations because chronic conditions may affect cognition through multiple physiological mechanisms, including:

- multimorbidity burden,
- hydration imbalance,
- systemic inflammation,
- vascular and microvascular dysfunction,
- age-related physiological vulnerability.

The Montreal Cognitive Assessment (MoCA) is a clinically validated cognitive assessment tool, but it requires trained personnel and administration time. This makes it harder to apply in large-scale, community-based, or routine screening settings.

Therefore, the clinical motivation of this project is not to replace MoCA. Instead, the goal is to explore whether lower-burden signals, such as physiological markers and multimodal clinical features, can help identify people who may benefit from formal cognitive assessment or clinician review.

In other words:

> The project uses AI to support early cognitive-risk screening, not to make a final cognitive diagnosis.

---

## 4. Why This Should Not Be Called “AI Diagnosis” | 為什麼不能說 AI 診斷

This project should not be described as an automated diagnostic system for several reasons.

### 4.1 The current data are from a pilot study

The available dataset comes from a pilot clinical research setting. The sample size is useful for exploratory modeling and hypothesis generation, but it is not sufficient for claiming production-level clinical diagnostic performance.

### 4.2 The study design is cross-sectional

The modeling results can identify associations and predictive signals, but they do not prove that a physiological marker causes cognitive decline. Causal claims would require stronger evidence, such as longitudinal follow-up, randomized intervention, or carefully designed causal inference studies.

### 4.3 Clinical decisions require professional interpretation

Even when a model identifies risk signals, the interpretation must consider clinical context, patient history, measurement quality, missing data, and possible confounders. AI outputs should be reviewed by clinicians, especially when the model is uncertain or when the predicted risk is high.

### 4.4 Model errors have asymmetric consequences

In clinical settings, false reassurance and false alarm have different risks. A model that misses a high-risk patient may delay evaluation, while a model that over-flags low-risk patients may create unnecessary anxiety or clinical workload. This is why the system should include uncertainty estimation and triage rules.

For these reasons, this repository frames the project as:

> **clinical decision support for cognitive-risk screening**, not autonomous diagnosis.

---

## 5. Correct System Positioning | 正確系統定位

The appropriate positioning of this project is:

```text
Multimodal Clinical Data
→ Risk Signal Prediction
→ Uncertainty Estimation
→ Interpretable Risk Factors
→ Human-in-the-Loop Triage
→ Formal Clinical Assessment if Needed
```

The system is designed to support three practical use cases:

### 5.1 Early Screening

The model may help identify patients who show physiological or multimodal signals associated with lower cognitive function.

### 5.2 Decision Support

The model may provide structured information to help clinicians prioritize follow-up, especially when multiple physiological, behavioral, and image-based signals are available.

### 5.3 Triage

The system can route cases into different action levels:

| Model Output | Uncertainty | Suggested Action |
|---|---:|---|
| Low risk | Low uncertainty | Routine monitoring |
| Medium risk | Any uncertainty | Follow-up monitoring |
| High risk | Low uncertainty | Recommend formal cognitive assessment |
| High risk | High uncertainty | Clinician review required |
| Missing or low-quality data | High uncertainty | Collect additional data or manual review |

This positioning keeps the model useful while avoiding overclaiming clinical authority.

---

## 6. Clinical AI Risk Framing | 臨床 AI 風險意識

A risk-aware clinical AI system should not only ask:

> “Can the model predict the outcome?”

It should also ask:

> “When should we trust the prediction, when should we ask for more information, and when should a clinician review the case?”

For this project, important risk dimensions include:

- data quality risk: missing values, noisy measurements, image quality issues;
- sample size risk: limited pilot data may not generalize;
- model uncertainty: predictions near clinical thresholds should be treated cautiously;
- subgroup risk: performance may differ across age, sex, disease burden, or measurement conditions;
- interpretability risk: statistical predictors should not be overinterpreted as causal mechanisms;
- clinical workflow risk: the model should support, not interrupt, clinician decision-making.

---

## 7. Portfolio Scope | Portfolio 展示範圍

This repository is a **portfolio reconstruction** of the clinical AI screening project. It is intended to demonstrate problem framing, data pipeline design, modeling strategy, uncertainty-aware triage, and responsible AI positioning.

The repository does **not** include:

- patient-level data,
- identifiable clinical records,
- face or tongue images from participants,
- hospital internal documents,
- production clinical software,
- any tool intended for real-world diagnosis.

All examples should use synthetic or mock data only.

---

## 8. Key Takeaway | 核心定位句

> This project is not designed to replace clinicians or automatically diagnose cognitive impairment. It is a risk-aware clinical AI screening pipeline that explores whether multimodal clinical data can support earlier cognitive-risk detection, uncertainty-aware triage, and human-in-the-loop decision support for chronic disease management.

中文版本：

> 本專案不是要讓 AI 取代醫師診斷，而是探索 AI 是否能在慢性病管理中，利用多模態臨床資料提供認知風險早期篩檢、模型不確定性分流，以及由臨床專業人員審核的決策支援流程。

---

