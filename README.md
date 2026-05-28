# Risk-Aware Clinical AI Screening System for Cognitive Function
# 具風險意識的臨床 AI 認知功能早期篩檢系統

## A multimodal clinical AI portfolio project for cognitive-risk prediction, uncertainty-aware review prioritization, and interpretable decision support
## 一個用於認知風險預測、考量不確定性的人工複核優先順序判斷，以及可解釋決策支援的多模態臨床 AI 作品集專案
---

## Project Overview | 專案簡介

### English

This repository is a **portfolio reconstruction** of a clinical AI pilot study conducted in the Department of Family Medicine at National Taiwan University Hospital. The original research project explored whether multimodal clinical data could support chronic disease management, telemedicine, and mobile health care by helping clinicians interpret patient conditions through AI-assisted visual inspection and physiological modeling.

The broader pilot study collected multimodal data from patients with chronic diseases, including clinical interview records, physiological measurements, chronic disease indicators, face and tongue images, MRI/MRS brain imaging, and cognitive assessment results. Exploratory findings provide a clinically interpretable bridge between two modeling routes: tongue-image features showed predictive signal for total body water (SVR correlation = 0.636), while a best subset regression model using tabular clinical data explained 38% of the variance in MoCA scores and identified total body water and platelet count as important cognitive-function predictors, with platelet count retained across multiple modeling approaches. Together, these findings motivate a future image-to-physiology-to-cognitive-risk screening pathway rather than a direct diagnostic claim.

This portfolio version focuses on a more specific AI application question:

> Can multimodal clinical data be organized into a risk-aware AI screening pipeline for early cognitive-risk signals in patients with chronic diseases?

Instead of positioning the system as an automated diagnostic tool, this project frames it as a **clinical decision-support and risk-screening pipeline**. The goal is to generate cognitive-risk signals, estimate model uncertainty, provide interpretable risk factors, and support uncertainty-aware review prioritization recommendations for cases that may require professional review or further assessment.

### 中文

本程式碼儲存庫（repository）是根據臺大醫院家庭醫學部臨床人工智慧（AI）先導研究（pilot study）所整理出的**作品集重建版本**。原始研究計畫探討是否能利用多模態臨床資料，支援慢性病管理、遠距醫療與行動健康照護，並透過人工智慧輔助視診與生理狀態建模，協助臨床專業人員理解病人的健康狀況。

整體先導研究收集慢性病患者的多模態資料，包含臨床訪談紀錄、生理測量、慢性疾病指標、臉部與舌頭影像、磁振造影／磁振光譜（MRI/MRS）腦部影像，以及認知功能評估結果。探索性結果顯示，舌頭影像特徵對身體總水量（total body water, TBW）具有初步預測訊號；另一方面，使用表格式臨床資料建立的最佳子集迴歸模型可解釋蒙特婁認知評估（Montreal Cognitive Assessment, MoCA）總分 38% 的變異性，並辨識出身體總水量與血小板數量（platelet count, Plt）為重要的認知功能預測因子，其中血小板數量在多種建模方法中均被保留。這兩條建模路徑共同支持一項未來可驗證的方向：以影像取得生理訊號，再將生理訊號連結至認知風險篩檢，而非直接宣稱影像可以進行臨床診斷。

本作品集版本聚焦於一個更明確的人工智慧應用問題：

> 是否能將多模態臨床資料整理成一套具風險意識的人工智慧篩檢管線，用於偵測慢性病患者的早期認知風險訊號？

本專案**不將模型定位為自動診斷工具**，而是定位為一套**臨床決策支援與風險篩檢管線**。系統目標是產生認知風險訊號、估計模型不確定性、提供具可解釋性的風險因子，並針對可能需要專業複核或進一步評估的案例，提出考量不確定性的人工複核優先順序建議。

---

## Why This Project Matters | 臨床重要性

### English

Chronic diseases are a major healthcare challenge, especially in aging societies. They require long-term monitoring, but face-to-face clinical visits may be reduced or interrupted in pandemic and post-pandemic contexts. In telemedicine or mobile health settings, clinicians may lose access to traditional physical examination cues, including visual inspection.

At the same time, chronic diseases may affect cognitive function through multiple physiological pathways, including multimorbidity burden, hydration imbalance, systemic inflammation, and neurovascular dysfunction. Cognitive assessments such as the Montreal Cognitive Assessment (MoCA) are clinically meaningful, but they require trained personnel and administration time, limiting their scalability in routine or community-based screening.

This project explores whether low-burden multimodal signals—such as physiological indicators, psychological and behavioral questionnaires, body composition metrics, and image-derived features—can be used to support early cognitive-risk screening.

### 中文

慢性病是高齡化社會中重要的醫療挑戰，且慢性病管理需要長期追蹤。然而，在疫情或後疫情時代，病患可能減少面對面就醫，遠距醫療與行動健康照護的重要性因此提升。在這些情境下，醫師較難進行傳統視診、觸診、叩診與聽診，因此 AI 輔助視診與臨床決策支援具有潛在價值。

另一方面，慢性疾病可能透過多重共病負擔、體液平衡失調、全身性發炎反應與神經血管功能受損等機制影響認知功能。MoCA 等認知測驗雖具臨床意義，但需要受訓人員施測且耗費時間，因此在常規篩檢、社區篩檢或大規模追蹤中有執行限制。

本專案探索是否能利用低負擔的多模態訊號，例如生理指標、心理行為問卷、身體組成資料與影像特徵，協助進行認知風險的早期篩檢。

---

## My Contributions | 我負責的內容

### English

My work focused on translating the clinical research question into an executable data science and AI workflow. The main contributions included:

1. **Multimodal data workflow support**  
   Collected and organized the overall AI pilot-study workflow involving clinical, physiological, questionnaire, cognitive, and image-based data.

2. **Image preprocessing support**  
   Conducted preprocessing logic for face and tongue images, including crop / segmentation concepts, image quality considerations, and the role of lighting metadata.

3. **Tabular data preprocessing**  
   Cleaned and organized clinical tabular data, including physiological markers, blood and urine indicators, body composition variables, and psychological / behavioral questionnaire scores.

4. **Correlation-based feature exploration**  
   Used pairwise correlation structure to group related clinical indicators and reduce redundant modeling targets.

5. **Modeling strategy reframing**  
   Reframed the modeling direction from directly predicting all clinical indicators from images to a more practical two-route strategy:
   - Tabular clinical data → cognitive function prediction
   - Tongue / face image features → physiological target prediction

6. **Cognitive-risk prediction modeling**  
   Developed and interpreted a statistical / ML modeling framework for predicting MoCA scores using physiological and psychological variables.

7. **Explainability and robustness perspective**  
   Used model comparison and interpretability concepts, including best subset regression, Lasso regression, neural networks, and SHAP-based explanation.

8. **Risk-aware AI extension**  
   Designed a portfolio-level extension that converts model outputs into risk categories, uncertainty levels, and human-in-the-loop review prioritization recommendations.

9. **Future deployment exploration**  
   Explored future deployment possibilities for camera-based screening workflows and edge-device settings such as Jetson Nano.

### 中文

我在此專案中的主要工作，是將臨床研究問題轉換成可執行的資料科學與 AI workflow。具體貢獻包含：

1. **多模態資料流程支援**  
   蒐集資料並整理臨床、生理、問卷、認知測驗與影像資料所組成的 AI pilot-study workflow。

2. **影像前處理支援**  
   執行臉部與舌頭影像前處理邏輯，包含裁切 / segmentation 概念、影像品質考量，以及環境光 metadata 的潛在用途。

3. **Tabular data 前處理**  
   整理表格式臨床資料 (tabular clinical data)，包含生理測量、血液與尿液指標、身體組成變數，以及心理 / 行為問卷分數。

4. **相關性結構探索**  
   使用 pairwise correlation matrix 檢視臨床指標之間的相關性結構，協助將高度相關變數分群，降低重複建模目標。

5. **模型策略重新定義**  
   將原本「影像直接預測所有臨床指標」的方向，重新整理為更可執行的雙路線策略：
   - 表格式臨床資料 (tabular clinical data) → 認知功能預測
   - 舌頭 / 臉部影像特徵 → 生理指標預測

6. **認知風險預測建模**  
   建立並解釋以生理與心理行為變數預測 MoCA 分數的統計 / 機器學習建模框架。

7. **可解釋性與穩健性分析視角**  
   使用 best subset regression、Lasso regression、neural network 與 SHAP explanation 等方法概念，檢視模型結果與關鍵預測因子的穩定性。

8. **具風險意識的 AI 延伸設計**  
   將模型輸出延伸為作品集中的風險類別、不確定性程度與人工參與的複核優先順序建議。

9. **未來部署方向探索**  
   初步探索以影像擷取裝置為基礎的篩檢流程 (camera-based screening workflow) 與 Jetson Nano 等邊緣裝置部署(edge-device deployment)的可能方向。



## Scope of Implementation and Proposed Extensions | 實作範圍與延伸設計說明

The original hands-on work in this project focused on tongue-image preprocessing and modeling experiments, together with the interpretation of tabular clinical modeling findings related to cognitive function. The uncertainty-aware review prioritization policy, causal-inference direction, and edge-device deployment notes are presented as portfolio-level extensions motivated by the observed findings, rather than as clinically validated or deployed systems.

本專案中實際參與的工作，主要聚焦於舌頭影像前處理與建模實驗，以及與認知功能相關之表格式臨床資料建模結果的理解與整理。考量不確定性的人工複核優先排序政策、因果推論方向與邊緣裝置部署筆記，則是根據研究結果提出的作品集層級延伸設計，並非已完成臨床驗證或實際部署之系統。


---

## System Positioning | 系統定位

This project should be understood as:

```text
Clinical multimodal data
→ data preprocessing
→ cognitive-risk prediction
→ uncertainty estimation
→ explainability
→ clinician review / prioritization recommendations
```

It should **not** be understood as:

```text
Raw patient data
→ AI diagnosis
→ automated medical decision
```

### Key Positioning | 核心定位

- **Clinical decision support, not clinical diagnosis**  
  臨床決策支援，而非臨床診斷工具。

- **Risk screening, not disease labeling**  
  認知風險篩檢，而非疾病標籤判定。

- **Uncertainty-aware prioritization recommendations, not automatic replacement of clinicians**  
  具不確定性意識的人工複核優先順序建議，而非取代臨床人員。

- **Synthetic-data public demo, not release of patient-level data**  
  公開展示版本使用合成資料，不釋出病人層級資料。

---

## Modeling Routes | 建模路線

### Route A: Tabular Clinical Data → Cognitive Function Prediction

This route uses physiological markers, body composition metrics, blood / urine indicators, psychological questionnaires, and behavioral measures to predict cognitive function, using MoCA total score as the main cognitive outcome.

Key modeling methods include:

- Best subset regression
- Lasso regression
- Neural network modeling
- SHAP-based model interpretation
- Mediation analysis for hypothesis generation

Main findings from the thesis-level analysis showed that total body water and platelet count were stable predictors across comparison models, and that platelet count partially mediated the association between age and cognition. These findings are treated as predictive and hypothesis-generating rather than causal proof.

### Route B: Face / Tongue Image Features → Physiological Target Prediction

This route explores whether face or tongue images can be transformed into useful feature representations for predicting physiological indicators. In the portfolio version, this direction is documented as an image-to-physiology modeling pathway using mock or synthetic examples.

Potential components include:

- Image preprocessing
- Face / tongue crop quality checks
- Lighting metadata parsing
- CNN or autoencoder-based feature extraction
- Physiological target prediction
- Image quality and uncertainty flags

---

## Risk-Aware Decision Layer | 具風險意識的決策層

A central design goal of this repository is to show how an AI model output can be converted into a safer clinical decision-support workflow.

### Example Risk Output

```json
{
  "patient_id": "synthetic_001",
  "predicted_moca": 23.4,
  "risk_class": "medium",
  "uncertainty_level": "high",
  "key_predictors": [
    "low total body water",
    "low platelet count"
  ],
  "recommended_follow_up": "prioritized_human_review"
}
```

### Example Recommendation Prioritization Logic

```text
High predicted risk + low uncertainty
→ recommend formal cognitive assessment

High predicted risk + high uncertainty
→ clinician review required

Medium predicted risk
→ follow-up monitoring

Low predicted risk + high uncertainty
→ request additional data or manual review

Insufficient data quality
→ do not produce confident recommendation
```

### Proposed Uncertainty Signals for Review Prioritization  
### 用於人工複核優先排序的擬議不確定性訊號

To extend the original predictive study into a risk-aware AI application design, this portfolio proposes several uncertainty signals that could help identify cases requiring cautious interpretation, additional data, or prioritized human review.

為將原始預測研究延伸為具風險意識的 AI 應用設計，本作品集提出以下不確定性訊號，用於辨識哪些案例需要更審慎解讀、補充資料，或優先交由人工複核：

- **Prediction near the cognitive-risk threshold**  
  預測結果接近認知風險判定門檻，代表小幅誤差就可能改變風險分類。

- **Bootstrap interval crossing the risk threshold**  
  Bootstrap 推估區間跨越風險門檻，代表模型對案例的判斷方向可能不穩定。

- **Disagreement across multiple models**  
  多個模型對同一案例的預測結果不一致，代表結論可能依賴模型選擇。

- **Missing or low-quality input variables**  
  關鍵表格式臨床資料缺失或品質不佳，可能降低風險預測的可信程度。

- **Poor image quality or unstable lighting conditions**  
  影像品質不佳或拍攝光線不穩定，可能影響影像特徵與後續預測結果。

- **Out-of-distribution clinical profiles**  
  新個案特徵與建模資料分布差異過大時，模型可能處於較不熟悉的情境，應降低對輸出的信任程度。

---

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

---

## Directory Guide | 資料夾說明

### `docs/`

Design and methodology notes for the portfolio reconstruction. This folder explains the clinical framing, multimodal data pipeline, image preprocessing strategy, tabular clinical data preprocessing, modeling choices, uncertainty-aware review prioritization policy, explainability, causal-inference direction, edge-device deployment notes, and ethics / privacy limitations.

此資料夾放置作品集重建版本的設計與方法文件，說明臨床問題定義、多模態資料管線、影像前處理策略、表格式臨床資料前處理、建模選擇、考量不確定性的人工複核優先排序政策、可解釋性、因果推論延伸方向、邊緣裝置部署，以及倫理與隱私限制。

### `examples/`

Synthetic examples only. This folder contains mock patient input schemas, synthetic patient rows, sample model outputs, and review prioritization scenarios. No real patient-level data is included.

此資料夾僅放置合成範例（synthetic examples），包含模擬病人輸入格式、合成病人資料列、模型輸出範例，以及人工複核優先排序情境。不包含任何真實病人層級資料。

### `src/`

Simplified and reconstructed demo code. The code is designed to demonstrate modular AI engineering logic, not to reproduce the original hospital research environment.

此資料夾放置簡化並重建後的示範程式碼，用於展示模組化人工智慧工程邏輯，並非用於重現原始醫院研究環境或完整研究程式碼。

### `reports/`

Portfolio-level reports summarizing the pilot study, tabular modeling findings, image-to-physiology findings, uncertainty extension, and project reflection.

此資料夾放置作品集層級的報告，整理先導研究、表格式臨床資料建模結果、影像至生理訊號預測結果、不確定性延伸設計，以及專案反思。

### `demo/`

Screenshots and optional demo video notes for public portfolio presentation. All visual materials should be synthetic or fully de-identified.

此資料夾放置公開作品集展示用的畫面截圖與選用的示範影片說明。所有視覺材料皆應使用合成內容，或完成充分去識別化處理。

---

# Reusable Concepts and Practical Capabilities | 可延伸應用的概念與實作能力

This repository organizes the project into reusable ideas and implementation patterns that can be adapted to other risk-sensitive AI applications, especially those involving multimodal data, uncertain predictions, and human-reviewed decision support.

本作品集將專案中的方法整理為可延伸應用的概念與實作模式，適合參考於其他涉及多模態資料、不確定預測，以及人工複核決策支援的高風險人工智慧應用情境。

### AI / ML Engineering | 人工智慧與機器學習工程

- **From domain problem to AI workflow**  
  A reusable approach for translating a clinical screening question into data preparation, modeling, uncertainty assessment, and follow-up recommendation components.  
  將臨床篩檢問題轉化為資料準備、模型建立、不確定性評估與後續處理建議元件的可重用方法。

- **Multimodal data pipeline design**  
  A structured way to organize image data and tabular clinical data for separate processing and future integration.  
  將影像資料與表格式臨床資料分別處理，並為後續整合建模建立清楚資料管線的設計方式。

- **Modular preprocessing and modeling components**  
  An example of separating data cleaning, image preprocessing, modeling, evaluation, and decision-layer logic into reusable modules.  
  將資料清理、影像前處理、模型建立、評估與決策層邏輯拆分為可重用模組的實作範例。

- **Separation of prediction, uncertainty, and follow-up recommendation**  
  A safer system-design pattern that distinguishes model prediction from uncertainty estimation and human-review prioritization recommendations.  
  將模型預測、不確定性估計與人工複核優先順序建議分開處理的較安全系統設計模式。

- **From exploratory analysis to reusable pipeline thinking**  
  A practical transition from one-off notebook experiments toward documented and maintainable AI workflow components.  
  從一次性的分析實驗，延伸為具文件紀錄、可維護且可重用之人工智慧流程元件的實務思維。

### Data Science and Statistical Modeling | 資料科學與統計建模

- **Tabular clinical data preprocessing**  
  A preprocessing framework for handling structured clinical variables such as biochemical, body-composition, lifestyle, psychological, and cognitive-assessment indicators.  
  處理生化檢驗、身體組成、生活型態、心理行為與認知評估等表格式臨床變數的前處理架構。

- **Correlation-based feature exploration**  
  An exploratory approach for identifying related variable groups and informing target-selection or modeling priorities.  
  透過相關性探索辨識彼此關聯的變數群組，並作為選擇預測目標或安排建模優先順序的參考方式。

- **Interpretable feature-selection strategies**  
  Examples of using best subset regression and Lasso-style methods to identify compact and interpretable predictor sets.  
  以最佳子集迴歸與類似 Lasso 的方法，找出較精簡且具可解釋性的預測變數組合。

- **Modeling with explainability**  
  An example of combining neural-network modeling with interpretation methods to examine important predictive signals.  
  將神經網路模型與解釋方法結合，用於檢視重要預測訊號的建模方式。

- **Mediation analysis for hypothesis generation**  
  A cautious use of mediation analysis to explore possible physiological pathways without presenting association as causal proof.  
  謹慎運用中介分析探索可能的生理途徑，同時避免將關聯性結果過度解讀為因果證明。

### Risk-Aware AI Application Design | 具風險意識的人工智慧應用設計

- **Prediction as screening support, not diagnosis**  
  A design principle for presenting model outputs as risk-screening signals rather than automated clinical conclusions.  
  將模型輸出定位為風險篩檢訊號，而非自動化臨床診斷結論的設計原則。

- **Uncertainty-aware interpretation of model outputs**  
  A framework for considering threshold proximity, confidence intervals, model disagreement, missing inputs, and image quality before acting on predictions.  
  在採取後續處理前，綜合考量門檻接近程度、信賴區間、模型預測不一致、輸入資料缺失與影像品質的判讀架構。

- **Human-review prioritization recommendations**  
  A decision-support pattern for identifying cases that may require prioritized human review, additional data, or formal cognitive assessment.  
  用於辨識哪些案例可能需要優先人工複核、補充資料或接受正式認知評估的決策支援模式。

- **Model agreement and boundary cases as risk signals**  
  An evaluation idea that treats disagreement across models and predictions near decision thresholds as indicators of reduced reliability.  
  將多個模型結果不一致，以及預測接近判定門檻的案例，視為可信程度降低訊號的評估概念。

- **Human-reviewed decision support rather than autonomous medical authority**  
  A responsible AI framing in which model outputs inform review priorities and follow-up considerations while final judgment remains with qualified professionals.  
  將模型輸出用於支援複核優先順序與後續評估考量，最終判斷仍由具專業資格的人員負責的人工智慧應用定位。

---

## Privacy, Ethics, and Clinical Safety Notice | 隱私、倫理與臨床安全聲明

This repository is a **portfolio demonstration** and does not release any patient-level clinical data, face images, tongue images, MRI/MRS data, hospital records, or identifiable information.

All public examples are synthetic, reconstructed, or de-identified demonstrations. The repository is not intended to reproduce the original clinical research environment or release any confidential hospital materials.

This project is **not intended for clinical diagnosis, medical decision-making, or direct patient care**. Any AI-assisted screening workflow in clinical settings would require institutional review, prospective validation, clinician oversight, and compliance with medical data privacy regulations.

本程式碼儲存庫（repository）僅供**作品集展示用途**，不釋出任何病人層級臨床資料、臉部影像、舌頭影像、磁振造影／磁振光譜（MRI/MRS）資料、醫院病歷或任何可識別個人身分之資訊。

所有公開範例皆為合成資料（synthetic data）、重建內容（reconstructed content）或完成去識別化處理的示範資料。本儲存庫不以重現原始臨床研究環境為目的，亦不釋出任何機密或未經授權公開之醫院資料。

本專案**不應用於臨床診斷、醫療決策或直接病人照護**。任何於臨床場域中導入的人工智慧輔助篩檢流程，皆須經過研究倫理審查、前瞻性驗證、臨床專業人員監督，並遵循醫療資料隱私與相關法規要求。

---

## Limitations | 限制

- The original clinical dataset was small and cross-sectional.
- Predictive associations should not be interpreted as causal evidence.
- Model outputs require prospective validation before clinical use.
- Cognitive-risk screening is not equivalent to formal cognitive diagnosis.
- Image-based modeling can be affected by lighting, alignment, cropping, camera hardware, and data quality.
- Public code in this repository is a simplified reconstruction and does not reproduce the original hospital research environment.

---

## Future Directions | 未來方向

Potential next steps include:

1. Develop a synthetic end-to-end demo pipeline.
2. Add uncertainty estimation with bootstrap confidence intervals.
3. Implement model-agreement checks across regression, Lasso, and neural network models.
4. Add SHAP-based explanation for tabular model predictions.
5. Design a clinician-facing triage dashboard using synthetic data.
6. Explore camera-based screening workflow with edge-device constraints.
7. Extend the predictive framework with longitudinal or causal-inference study designs.

---

## License | 授權

The code in this reconstructed portfolio repository is released under the MIT License.

The license applies only to the reconstructed demo code in this repository. It does not grant rights to patient data, clinical images, hospital records, research documents, internal code, third-party materials, institutional assets, or medical use.
