# Risk-Aware Clinical AI Screening System for Cognitive Function
# 具風險意識的臨床 AI 認知功能早期篩檢系統
## A multimodal AI pipeline for cognitive-risk prediction, uncertainty estimation, and human-in-the-loop triage.
標題(中英文標題)、副標題、專案簡介+我負責的內容(中英文)、repository架構

本專案來自臺大醫院家庭醫學部慢性病管理前瞻性研究(pilot study)，目標是在遠距醫療與行動健康照護的情境下，利用臉部／舌頭影像、生理檢測、心理行為問卷與認知測驗資料，探索 AI 是否能協助醫師進行慢性病與認知風險的早期篩檢。原始研究計畫明確設定要收集門診病人的多模態資料，包括病歷與生理測量、慢性病臨床指標、臉與舌部照片、MRI/MRS 腦影像、心智功能評估等五大類資料，並訓練深度神經網路輔助遠端判斷慢性病狀態。
我的角色是在這個 pilot study 中，將臨床研究問題轉換成可執行的資料科學與 AI pipeline：包含：多模態資料蒐集、影像前處理、tabular data 清理、相關性結構探索、模型實驗、預測目標重定義、後續把模型輸出轉換成風險分層與不確定性決策規則、(草擬應用到硬體系統Jetson Nano)。


This project presents a risk-aware clinical AI screening pipeline developed from a pilot study at the Department of Family Medicine, National Taiwan University Hospital. The goal was to explore whether multimodal clinical data—including physiological measurements, blood and urine markers, psychological questionnaires, cognitive scores, and face/tongue images—could support early cognitive-risk screening in chronic disease management.

Instead of framing the system as an automated diagnostic tool, I designed it as a decision-support pipeline: the model predicts cognitive-risk signals, estimates uncertainty, explains key predictors, and routes uncertain or high-risk cases to clinician review.

本作品整理自台大醫院家醫科 AI 輔助慢性病管理 pilot study，目標是探索多模態臨床資料是否能支援慢性病患者的認知風險早期篩檢。作品重點不是宣稱 AI 可取代醫師診斷，而是將模型設計成臨床決策支援流程：輸出認知風險訊號、估計預測不確定性、提供可解釋的關鍵因子，並將高風險或低信心個案導向人工審核。

## Core skills shown:
Clinical AI 

Multimodal data preprocessing

Tabular modeling

Image representation learning

Autoencoder feature extraction

Model robustness analysis

SHAP explainability

Uncertainty-aware decision rules

Human-in-the-loop triage

Medical AI ethics

## Structure
Risk-Aware Clinical AI Screening System

├── 1. Background

│   └── Why cognitive-risk screening matters

│

├── 2. Dataset

│   └── Multimodal data: tabular clinical data + face/tongue images + cognitive scores

│

├── 3. Data Pipeline

│   ├── image preprocessing

│   ├── tabular cleaning

│   ├── variable filtering

│   └── correlation-based feature grouping

│

├── 4. Modeling

│   ├── tabular → MoCA prediction

│   ├── tongue image → physiological indicators

│   └── model comparison

│

├── 5. Uncertainty & Risk Layer

│   ├── threshold risk

│   ├── bootstrap CI

│   ├── model disagreement

│   └── human review policy

│

├── 6. Explainability

│   ├── SHAP

│   ├── key predictors

│   └── clinical interpretation

│

├── 7. Demo

│   └── de-identified / synthetic patient risk dashboard

│

└── 8. Limitations

    ├── small sample size
    
    ├── cross-sectional design
    
    ├── no diagnosis replacement
    
    └── requires prospective validation
    
