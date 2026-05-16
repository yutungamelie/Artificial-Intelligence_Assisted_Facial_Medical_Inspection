# Risk-Aware Clinical AI Screening System for Cognitive Function
# 具風險意識的臨床 AI 認知功能早期篩檢系統

## A multimodal AI pipeline for cognitive-risk prediction, uncertainty estimation, and human-in-the-loop triage
## 一套用於認知風險預測、不確定性估計與人工審核分流的多模態 AI 管線

## Project Overview & My Contributions | 專案簡介與我負責的內容

### English

This project was developed from a pilot study at the Department of Family Medicine, National Taiwan University Hospital. The goal was to explore whether multimodal clinical data—including physiological measurements, blood and urine markers, psychological and behavioral questionnaires, cognitive assessment scores, and face/tongue images—could support early screening of cognitive-risk signals in chronic disease management and telehealth settings.

Instead of framing the system as an automated diagnostic tool, I positioned it as a **clinical decision-support pipeline**. The system is designed to predict cognitive-risk signals, estimate model uncertainty, provide interpretable risk factors, and route high-risk or low-confidence cases to clinician review.

My contributions focused on translating the clinical research question into an executable data science and AI workflow. I supported multimodal data collection, image preprocessing, tabular data cleaning, correlation-based feature exploration, model experimentation, prediction target reframing, and the design of a risk-aware decision layer. I also explored future deployment directions, including the possibility of applying the pipeline to edge-device settings such as Jetson Nano.

### 中文

本專案整理自臺大醫院家庭醫學部慢性病管理前瞻性研究 pilot study。專案目標是在遠距醫療與行動健康照護情境下，探索多模態臨床資料是否能協助慢性病患者進行認知風險的早期篩檢。資料型態包含生理檢測、血液與尿液指標、心理與行為問卷、認知測驗分數，以及臉部與舌頭影像等。

本作品的重點不是宣稱 AI 可以取代醫師診斷，而是將模型設計成一套 **臨床決策支援管線**：系統輸出認知風險訊號、估計模型不確定性、提供可解釋的關鍵因子，並將高風險或低信心個案導向醫師或專業人員進一步審核。

我在此 pilot study 中負責將臨床研究問題轉換成可執行的資料科學與 AI workflow。具體工作包含多模態資料蒐集支援、影像前處理、tabular data 清理、相關性結構探索、模型實驗、預測目標重新定義，以及風險分層與不確定性決策規則的設計。我也曾初步探索未來將模型部署至 edge device，例如 Jetson Nano，作為 camera-based screening system 的可能方向。

## Repository Structure | Repository 架構

```text
risk-aware-clinical-ai-screening/
├── README.md
│
├── docs/
│   ├── clinical_problem_framing.md
│   ├── multimodal_data_pipeline.md
│   ├── image_preprocessing_notes.md
│   ├── tabular_data_preprocessing.md
│   ├── modeling_strategy.md
│   ├── uncertainty_triage_policy.md
│   ├── explainability_and_model_interpretation.md
│   ├── causal_inference_future_direction.md
│   ├── edge_deployment_notes.md
│   └── ethics_privacy_and_limitations.md
│
├── examples/
│   ├── synthetic_patient_input_schema.json
│   ├── synthetic_patient_examples.csv
│   ├── sample_risk_outputs.json
│   └── sample_triage_cases.md
│
├── src/
│   ├── data_preprocessing/
│   │   ├── tabular_cleaning.py
│   │   ├── variable_filtering.py
│   │   └── correlation_grouping.py
│   │
│   ├── image_preprocessing/
│   │   ├── face_crop_quality_check.py
│   │   ├── tongue_image_preprocessing.py
│   │   └── lighting_metadata_parser.py
│   │
│   ├── modeling/
│   │   ├── tabular_moca_prediction.py
│   │   ├── image_feature_extraction.py
│   │   └── physiological_target_prediction.py
│   │
│   ├── risk_triage/
│   │   ├── cognitive_risk_score.py
│   │   ├── uncertainty_score.py
│   │   └── clinical_triage_rule.py
│   │
│   └── evaluation/
│       ├── bootstrap_ci.py
│       ├── model_agreement_check.py
│       └── error_analysis.py
│
├── reports/
│   ├── pilot_study_summary.md
│   ├── tabular_model_findings.md
│   ├── image_to_physiology_findings.md
│   ├── uncertainty_extension_proposal.md
│   └── portfolio_reflection.md
│
├── demo/
│   ├── screenshots/
│   └── demo_video_link.md
│
├── requirements.txt
└── LICENSE
```
