# Modeling Strategy

## 建模策略 | Modeling Strategy

This document explains the modeling strategy for the **Risk-Aware Clinical AI Screening System for Cognitive Function** project.

The project was developed from a clinical AI pilot study with multimodal data, including physiological measurements, blood and urine biomarkers, psychological and behavioral questionnaires, cognitive assessment scores, and face / tongue images. The long-term vision was to explore whether low-burden AI-assisted signals could support chronic disease management, remote care, and early cognitive-risk screening.

For a public GitHub portfolio, the modeling strategy should be presented as a **portfolio reconstruction** rather than a production medical system. The goal is to demonstrate how the modeling problem was decomposed into interpretable, clinically cautious, and risk-aware routes.

---

## 1. Modeling Overview | 建模總覽

The modeling strategy is organized into two major routes:

```text
Route A:
Tabular Clinical Data
→ MoCA Prediction
→ Cognitive-Risk Screening
→ Interpretable Physiological Predictors

Route B:
Tongue Image
→ Image Feature Extraction
→ Physiological Target Prediction
→ Possible Bridge Toward Cognitive-Risk Modeling
```

The two routes answer different questions.

| Route | Input | Output | Main Question |
|---|---|---|---|
| Route A | physiological, biochemical, psychological, behavioral tabular data | MoCA / cognitive-risk signal | Which clinical indicators are associated with cognitive function? |
| Route B | tongue images | physiological targets | Can tongue image features predict health-related physiological signals? |

The portfolio framing is:

> Route A provides the interpretable clinical-risk modeling backbone, while Route B explores whether images can recover physiological signals that may later connect to cognitive-risk screening.

---

## 2. Why Not Directly Start with Image-to-Cognition | 為什麼不直接從影像預測認知功能開始

Although the original clinical AI project envisioned using face / tongue / brain images to predict chronic disease status or physiological outcomes, directly modeling:

```text
face / tongue image
→ cognitive score
```

is risky as the first modeling route.

### 2.1 Small-Sample Constraint

The pilot study collected multimodal data from 110 participants. This is valuable for proof-of-concept analysis, but it is relatively small for training robust deep-learning models directly from images to cognitive outcomes.

A direct CNN route may overfit because:

```text
image dimensionality is high
sample size is limited
clinical outcomes are noisy
image quality varies
standardized photo conditions may still differ
```

### 2.2 Weak Interpretability for Clinical Use

A direct image-to-cognition model may produce a prediction, but it is harder to explain why the model made that prediction.

For clinical AI, this matters because the output should not only be accurate; it should also be:

```text
interpretable
auditable
clinically meaningful
safe under uncertainty
```

### 2.3 Unclear Biological Pathway

A more cautious clinical modeling path is:

```text
tongue / face image
→ physiological signals
→ cognitive-risk markers
→ triage decision
```

instead of:

```text
tongue / face image
→ cognitive impairment
```

The first path is easier to interpret because it separates the image representation task from the clinical-risk interpretation task.

### 2.4 Risk-Aware Modeling Principle

The system should avoid jumping from a high-dimensional image directly to a clinical conclusion.

A safer modeling strategy is:

```text
1. Use tabular clinical data to identify interpretable predictors of cognition.
2. Use image models to explore whether visual signals can recover related physiological markers.
3. Connect both routes only after validating reliability, uncertainty, and clinical plausibility.
```

---

## 3. Route A: Tabular Clinical Data → MoCA Prediction

## Route A：表格臨床資料 → MoCA 認知功能預測

Route A is the core modeling route for cognitive-risk screening.

### 3.1 Objective

The goal is to identify physiological and psychological predictors associated with cognitive function in chronic disease patients.

Target variable:

```text
MoCA total score
```

Clinical interpretation:

```text
MoCA ≥ 26
→ generally considered normal cognitive function

MoCA < 26
→ possible risk of mild cognitive impairment
```

The model output should be interpreted as a screening signal, not a diagnosis.

### 3.2 Data Inputs

The tabular dataset included:

```text
demographic variables
body composition metrics
blood and urine biomarkers
chronic disease indicators
psychological and behavioral questionnaire scores
cognitive assessment results
```

Examples of predictors:

```text
Age
Sex
TBW
Plt
A1C
GluAC
LDL
HDL
TG
Cr
GFR
UACR
hsCRP
Ferritin
CES-D
CPSQI
WHO-5
Big Five personality traits
```

### 3.3 Preprocessing

Before modeling, the thesis workflow removed:

```text
highly homogeneous variables
questionnaire sub-items represented by total scores
subjective self-reported items that were not stable enough for modeling
```

Continuous variables were standardized using Z-score normalization:

```text
mean = 0
standard deviation = 1
```

Binary categorical variables, such as sex, retained their original binary encoding.

### 3.4 Model 1: Best Subset Regression

Best subset regression was used as the primary interpretable modeling method.

Purpose:

```text
exhaustively search predictor combinations
identify the most informative predictors
compare candidate models using adjusted R²
support clinical interpretation
```

Conceptual equation:

```text
MoCA = β1X1 + β2X2 + ... + βkXk + ε
```

Why this model is useful:

```text
clear predictor set
interpretable coefficients
useful for small-sample exploratory analysis
helps identify stable physiological candidates
```

Portfolio-safe interpretation:

> Best subset regression was used to identify a compact and interpretable group of physiological predictors associated with MoCA scores.

### 3.5 Model 2: Mediation Analysis

After key predictors were selected, mediation analysis was used to explore whether age may affect cognition through modifiable physiological variables.

Conceptual pathway:

```text
Age
→ physiological marker
→ MoCA
```

The purpose was not to prove clinical causality definitively, but to explore possible mechanisms.

The thesis used:

```text
Baron and Kenny four-step method
Sobel test
mediation package based on potential outcomes framework
ACME / ADE estimation
```

Risk-aware interpretation:

> Mediation analysis can support mechanism-oriented thinking, but causal claims still require longitudinal or experimental validation.

### 3.6 Model 3: Lasso Regression

Lasso regression was used as a robustness check.

Purpose:

```text
penalize unstable coefficients
reduce overfitting risk
evaluate whether selected predictors remain relevant under regularization
compare with best subset findings
```

Why this is useful:

```text
handles multicollinearity better than ordinary regression alone
encourages sparse predictor selection
supports model consistency checks
```

### 3.7 Model 4: Neural Network with SHAP

A neural network combined with SHAP was used to examine nonlinear relationships and feature importance.

Purpose:

```text
capture nonlinear effects
compare with linear model findings
use SHAP to interpret feature contributions
evaluate predictor stability across modeling frameworks
```

Portfolio-safe interpretation:

> Neural network + SHAP was used as an exploratory robustness layer, not as a standalone clinical decision engine.

### 3.8 Main Route A Findings

The thesis results can be summarized as:

```text
Best subset model explained approximately 38% of MoCA variance.
Higher total body water (TBW) and platelet count (Plt) were stable predictors.
Platelet count mediated part of the age–cognition association.
Multimorbidity burden showed a potential dose-response relationship with cognitive risk.
```

Portfolio interpretation:

> Route A identifies clinically interpretable physiological signals that may support early cognitive-risk screening.

---

## 4. Route B: Tongue Image → Physiological Target Prediction

## Route B：舌頭影像 → 生理指標預測

Route B explores whether tongue images can provide predictive signals for physiological targets.

### 4.1 Objective

The goal is to convert tongue images into low-dimensional features that preserve useful visual information and can be used to predict physiological targets.

Conceptual route:

```text
tongue image
→ cropped / resized image
→ autoencoder feature extraction
→ physiological target prediction
```

### 4.2 Why Use Image Feature Extraction

Raw images are high-dimensional. For a small pilot dataset, directly using pixels as predictors is unstable.

Therefore, the tongue-image route first compresses images into compact features.

The tongue slides describe the goal as:

```text
compress images to low-dimensional features that still reconstruct well
```

### 4.3 Autoencoder Feature Learning

The tongue-image modeling route compared two feature-extraction designs.

```text
Route 1:
RGB-Separate Encoders
R / G / B encoders
→ concatenate features

Route 2:
RGB-Joint Encoder
single encoder on full RGB image
```

The input image dimension was:

```text
[3 x 128 x 128]
```

The reconstruction-check comparison reported:

```text
RGB-Separate Encoder Reconstruction MSE: 0.000572
RGB-Joint Encoder Reconstruction MSE: 0.001158
```

Interpretation:

> RGB-separate encoding produced lower reconstruction error in this exploratory setting, suggesting that separating color channels may preserve useful tongue-color information.

### 4.4 PCA and K-Means Visualization

After extracting image features, PCA visualization and K-Means clustering were used to inspect whether feature representations showed meaningful structure.

Purpose:

```text
visualize low-dimensional feature space
inspect image-feature clustering
compare RGB-separate and RGB-joint representations
detect possible outliers or data-quality issues
```

### 4.5 Physiological Target Prediction

The extracted tongue features were used to predict approximately 90 physiological targets.

Tasks included:

```text
classification
regression
```

Reported exploratory examples:

```text
SVM best accuracy: Insomnia = 0.95
SVR best correlation: TBW = 0.636
```

Portfolio-safe interpretation:

> The tongue-image route suggests that image-derived features may capture physiological signals, especially signals related to hydration, circulation, sleep, or metabolic state, but these findings require stronger validation before clinical use.

### 4.6 Route B Limitations

The tongue-image slides explicitly note several limitations:

```text
data quality
standardized photo specifications
data quantity
strict inclusion criteria for patient recruitment
```

These limitations should be kept in the repository documentation.

Risk-aware implication:

> Image models are only as reliable as the image acquisition and preprocessing pipeline. Crop quality, lighting, photo standardization, and sample size should be treated as uncertainty sources.

---

## 5. How Route A and Route B May Connect

## Route A 與 Route B 如何串聯

The two modeling routes can be connected through physiological targets.

A possible future pipeline is:

```text
Tongue Image
→ Physiological Signal Prediction
→ Cognitive-Risk Prediction
→ Uncertainty-Aware Triage
```

More specifically:

```text
Tongue Image
→ TBW / Plt / inflammation / sleep-related signals
→ MoCA risk estimation
→ clinician review or follow-up recommendation
```

This is clinically more cautious than:

```text
Tongue Image
→ Cognitive Diagnosis
```

because it preserves an intermediate physiological interpretation layer.

### 5.1 Example Bridge: TBW

Route A found total body water to be a stable predictor of MoCA.

Route B reported that tongue-image features achieved a relatively strong SVR correlation with TBW.

This suggests a possible bridge:

```text
tongue image
→ predicted TBW
→ cognitive-risk signal
```

However, this should be treated as a future hypothesis, not a validated clinical pathway.

### 5.2 Example Bridge: Circulation / Platelet-Related Signals

The tongue-image slides mention the traditional intuition that tongue color may relate to circulation, including black / purple / white color patterns.

Route A found platelet count to be a stable predictor of MoCA.

A cautious future research question is:

```text
Can tongue color / image features capture circulation-related or hematological signals that are associated with cognitive function?
```

This remains exploratory and should not be framed as causal proof.

---

## 6. Why This Strategy Fits a Small-Sample Pilot Study

## 為什麼這個策略適合小樣本 Pilot Study

A small clinical pilot dataset requires a modeling strategy that prioritizes interpretability and cautious claims.

### 6.1 Interpretable First

Route A starts from tabular clinical data and interpretable models.

This helps answer:

```text
Which variables matter?
Are predictors clinically plausible?
Do different models agree?
Can findings be explained to clinicians?
```

### 6.2 Representation Learning Second

Route B uses image feature learning, but does not immediately claim diagnostic ability.

This helps answer:

```text
Can images encode physiological information?
Which image representation is more stable?
Can image features predict measurable physiological targets?
```

### 6.3 Risk-Aware Integration Last

Only after Route A and Route B are separately evaluated should the system attempt integration.

Integration should include:

```text
model agreement
uncertainty estimation
image quality flags
near-threshold detection
human-in-the-loop review
```

### 6.4 Avoiding Overclaim

This staged strategy avoids overclaiming because it separates:

```text
prediction
interpretation
mechanism
clinical decision
```

---

## 7. Recommended Public Code Mapping

This modeling strategy maps to the following repository modules:

```text
src/modeling/
├── tabular_moca_prediction.py
├── image_feature_extraction.py
└── physiological_target_prediction.py

src/risk_triage/
├── cognitive_risk_score.py
├── uncertainty_score.py
└── clinical_triage_rule.py

src/evaluation/
├── bootstrap_ci.py
├── model_agreement_check.py
└── error_analysis.py
```

### 7.1 `tabular_moca_prediction.py`

Suggested responsibilities:

```text
load synthetic patient table
select tabular predictors
train or mock best-subset / Lasso-style regression
predict MoCA
export predicted score and key predictors
```

### 7.2 `image_feature_extraction.py`

Suggested responsibilities:

```text
load synthetic or placeholder tongue image tensor
apply mock encoder
return low-dimensional image features
compare RGB-separate vs RGB-joint feature structures
```

### 7.3 `physiological_target_prediction.py`

Suggested responsibilities:

```text
load image-derived features
predict synthetic physiological targets
support regression and classification examples
output target prediction and reliability metadata
```

### 7.4 `cognitive_risk_score.py`

Suggested responsibilities:

```text
convert predicted MoCA into risk class
apply screening threshold
return low / medium / high cognitive-risk label
```

### 7.5 `uncertainty_score.py`

Suggested responsibilities:

```text
detect prediction near threshold
check model disagreement
check image quality flags
increase uncertainty if input quality is weak
```

### 7.6 `clinical_triage_rule.py`

Suggested responsibilities:

```text
combine risk class and uncertainty level
return recommended triage action
ensure clinician review for high-risk or high-uncertainty cases
```

---

## 8. Evaluation Strategy

A risk-aware modeling strategy should evaluate more than accuracy.

Recommended evaluation dimensions:

### 8.1 Route A Evaluation

```text
Adjusted R²
cross-validation error
predictor stability
Lasso-selected predictors
SHAP feature importance
model agreement
clinical plausibility
```

### 8.2 Route B Evaluation

```text
reconstruction MSE
PCA / clustering visualization
classification accuracy
regression correlation
image quality sensitivity
manual-crop vs auto-crop comparison
```

### 8.3 Risk Layer Evaluation

```text
near-threshold cases
uncertainty score distribution
model disagreement
false-negative review
false-positive review
triage action consistency
clinician review rate
```

---

## 9. Clinical Safety Positioning

The modeling outputs should be communicated as screening and decision-support signals.

Safe wording:

```text
predicted cognitive-risk signal
possible early screening marker
physiological predictor associated with MoCA
human-in-the-loop triage recommendation
```

Avoid wording:

```text
AI diagnosis
automatic cognitive impairment detector
proven causal biomarker
clinically validated medical device
```

Suggested output format:

```json
{
  "predicted_moca": 23.4,
  "risk_class": "medium",
  "uncertainty_level": "high",
  "key_predictors": ["lower total body water", "lower platelet count"],
  "triage_action": "clinician_review_recommended",
  "clinical_note": "Screening signal only; not a diagnosis."
}
```

---

## 10. Portfolio Takeaway

The modeling strategy can be summarized as:

> This project uses a staged modeling strategy: first, interpretable tabular models identify physiological predictors of cognitive function; second, tongue-image models explore whether visual features can recover physiological targets; third, a future risk-aware integration layer can combine prediction, uncertainty, explainability, and clinician review for safer cognitive-risk screening.

中文版本：

> 這個專案的建模策略不是直接用影像做診斷，而是分階段進行：先用可解釋的表格臨床資料找出與認知功能相關的生理指標，再用舌頭影像模型探索影像是否能預測生理訊號，最後才考慮把兩條路線串成具不確定性評估與臨床人員審核的認知風險篩檢流程。

---
