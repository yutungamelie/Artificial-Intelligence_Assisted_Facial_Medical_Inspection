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
│   └── Project overview, contribution summary, and repository guide
│
├── docs/
│   ├── clinical_problem_framing.md
│   ├── data_dictionary.md
│   ├── model_card.md
│   ├── risk_policy.md
│   └── ethics_and_privacy_note.md
│
├── data/
│   ├── README.md
│   └── synthetic_examples/
│       └── demo_patient_records.csv
│
├── notebooks/
│   ├── 01_tabular_data_cleaning.ipynb
│   ├── 02_correlation_exploration.ipynb
│   ├── 03_tabular_modeling_moca_prediction.ipynb
│   └── 04_uncertainty_and_risk_layer.ipynb
│
├── src/
│   ├── preprocessing/
│   │   ├── image_preprocessing.py
│   │   └── tabular_preprocessing.py
│   │
│   ├── modeling/
│   │   ├── train_tabular_model.py
│   │   ├── evaluate_model.py
│   │   └── explainability.py
│   │
│   └── risk_layer/
│       ├── uncertainty_estimation.py
│       ├── risk_stratification.py
│       └── human_review_policy.py
│
├── reports/
│   ├── error_analysis.md
│   ├── model_comparison.md
│   └── limitations.md
│
├── demo/
│   ├── screenshots/
│   └── synthetic_patient_risk_dashboard.md
│
├── requirements.txt
└── LICENSE
```
