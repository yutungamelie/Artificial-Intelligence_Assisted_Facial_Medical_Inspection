# Explainability and Model Interpretation

## 可解釋性與模型解讀 | Explainability and Model Interpretation

This document explains how model interpretability should be handled in the **Risk-Aware Clinical AI Screening System for Cognitive Function** project.

The goal is to clarify:

```text
1. why clinical AI needs explainability;
2. how tabular models can be interpreted;
3. how SHAP was used to interpret a neural network;
4. why TBW and platelet count are important predictors;
5. how image-model explanations should be interpreted cautiously;
6. why clinical interpretation is not the same as causal proof.
```

This document is written for a public portfolio repository. It does not release patient-level data, raw clinical images, hospital records, or identifiable information.

---

## 1. Why Clinical AI Needs Explainability

Clinical AI models should not only produce predictions. They should also help users understand why a prediction was made and whether the prediction is trustworthy enough to support follow-up.

In this project, explainability matters because the system is positioned as:

```text
risk-aware clinical AI screening
early cognitive-risk signal exploration
human-in-the-loop clinical decision support
```

not as:

```text
automatic diagnosis
clinician replacement
production-ready medical device
```

In clinical settings, a model output must be interpretable enough for clinicians to ask:

```text
Which variables contributed to this prediction?
Are the predictors clinically plausible?
Do different models point to similar signals?
Is the model using meaningful features or artifacts?
Should this case be reviewed by a clinician?
```

For this project, explainability is especially important because the data are multimodal:

```text
tabular physiological data
blood and urine biomarkers
psychological questionnaires
cognitive assessment results
face and tongue images
MRI / MRS brain-related data
```

A risk-aware AI workflow should therefore connect prediction, interpretation, uncertainty, and clinical review.

---

## 2. Explainability in the Original Clinical AI Vision

The original NTUH research proposal explicitly included explainable AI as one of the project goals.

The proposal aimed to use face and tongue images to predict physiological measurements or chronic disease clinical indicators, and then use XAI methods to understand which face or tongue features the CNN relied on.

Conceptual project vision:

```text
face / tongue image
→ CNN prediction of physiological or chronic disease indicators
→ XAI explanation of image regions or visual features
→ clinician interpretation
```

The proposal also emphasized a critical limitation:

> Different XAI methods may highlight different decision features, so domain expertise is still required to correctly interpret XAI results.

Portfolio interpretation:

> XAI is not used to let the model “explain itself” as if it were clinically authoritative. It is used to generate interpretable clues that clinicians and researchers can review.

---

## 3. Tabular Model Interpretation

The tabular modeling route is the most interpretable part of this portfolio project.

Route A:

```text
physiological / biochemical / psychological indicators
→ MoCA prediction
→ cognitive-risk screening signal
```

The thesis used several interpretable or partially interpretable modeling approaches:

```text
Best Subset Regression
Mediation Analysis
Lasso Regression
Neural Network with SHAP
```

Each method contributes a different type of interpretation.

---

## 4. Best Subset Regression Interpretation

Best subset regression was used to identify the most informative combination of predictors for MoCA total score.

### 4.1 Why Best Subset Regression Is Interpretable

Best subset regression is useful because it produces:

```text
a selected predictor set
coefficient estimates
direction of association
p-values
model-level adjusted R²
```

This makes it easier to explain the model to clinical collaborators.

### 4.2 Main Best Subset Finding

The best subset regression model explained approximately:

```text
Adjusted R² = 0.3763
```

or about:

```text
38% of MoCA score variation
```

The selected predictors included:

```text
Age
Body Height (BH)
Systolic Blood Pressure (SBP)
Fat-Free Mass (FFM)
Conscientiousness
WHO-5
Total Body Water (TBW)
Total Cholesterol (TCHO)
Triglycerides (TG)
HDL
Hemoglobin (Hb)
Fasting Glucose (GluAC)
Platelet Count (Plt)
```

### 4.3 Interpretation of Coefficients

The most clinically meaningful predictors were:

```text
Age
Total Body Water (TBW)
Platelet Count (Plt)
Fat-Free Mass (FFM)
```

Interpretation pattern:

```text
positive coefficient
→ higher predictor value is associated with higher MoCA score

negative coefficient
→ higher predictor value is associated with lower MoCA score
```

Important note:

> Regression coefficients describe associations in the model. They do not automatically prove causal mechanisms.

---

## 5. Key Predictor: Total Body Water

Total body water (TBW) was one of the most important predictors in the tabular model.

### 5.1 Modeling Finding

In the best subset model:

```text
TBW had a positive association with MoCA.
```

Interpretation:

```text
higher TBW
→ associated with higher cognitive function score
```

### 5.2 Clinical Intuition

TBW may reflect:

```text
hydration status
body composition
physiological resilience
metabolic balance
circulatory support
```

The thesis literature review discusses hydration imbalance as a possible contributor to cognitive vulnerability in chronic disease populations.

### 5.3 Portfolio Interpretation

Safe interpretation:

> TBW may serve as a routinely measurable physiological signal associated with cognitive-risk screening.

Unsafe interpretation:

> Increasing TBW will directly improve cognitive function.

The second statement is causal and should not be claimed based on this cross-sectional modeling result.

---

## 6. Key Predictor: Platelet Count

Platelet count (Plt) was the most stable predictor across multiple analyses.

### 6.1 Modeling Finding

Platelet count appeared as an important predictor in:

```text
Best Subset Regression
Mediation Analysis
Robustness comparison
Neural Network with SHAP interpretation
```

The thesis reported that platelet count was positively associated with MoCA and mediated part of the age–cognition association.

### 6.2 Clinical Intuition

Platelet count may be connected to:

```text
microcirculatory function
systemic inflammation
vascular health
oxygen and nutrient delivery
age-related physiological vulnerability
```

The thesis discusses platelet-related pathways in relation to inflammation and microvascular function.

### 6.3 Portfolio Interpretation

Safe interpretation:

> Platelet count is a clinically accessible physiological marker that showed stable association with MoCA and may support early cognitive-risk screening.

Unsafe interpretation:

> Platelet count is a proven causal biomarker of cognitive decline.

The latter requires stronger causal evidence, such as longitudinal or experimental validation.

---

## 7. Lasso Regression Interpretation

Lasso regression was used as a robustness check.

### 7.1 Why Lasso Helps Interpretation

Lasso uses L1 regularization to shrink less stable coefficients toward zero.

This helps answer:

```text
Does the predictor still matter when the model penalizes complexity?
Do selected variables remain stable under regularization?
Are best subset findings robust under a different modeling assumption?
```

### 7.2 Portfolio Interpretation

If a predictor appears in both best subset regression and Lasso, it provides stronger evidence than appearing in only one model.

Interpretation rule:

```text
single-model signal
→ weaker evidence

cross-model signal
→ stronger screening signal

model disagreement
→ uncertainty should increase
```

This connects model interpretation to the uncertainty triage policy.

---

## 8. SHAP Explanation for Neural Network

The thesis used a neural network with SHAP to interpret nonlinear relationships between physiological predictors and MoCA.

### 8.1 Why SHAP Was Used

Neural networks can capture nonlinear relationships, but they are harder to interpret than regression models.

SHAP was used to estimate how each feature contributed to model predictions.

Conceptual workflow:

```text
tabular predictors
→ neural network prediction of MoCA
→ SHAP values
→ feature contribution ranking
→ comparison with regression-based findings
```

### 8.2 What SHAP Explains

SHAP helps answer:

```text
Which variables contributed most to the neural network prediction?
Did a variable push the prediction upward or downward?
Are important features consistent with regression findings?
Do nonlinear models reinforce or contradict simpler models?
```

### 8.3 What SHAP Does Not Explain

SHAP does not prove:

```text
causal mechanism
clinical diagnosis
physiological truth
treatment effect
```

SHAP explains model behavior, not the real-world causal system.

### 8.4 Portfolio Interpretation

Safe interpretation:

> SHAP was used to inspect whether nonlinear neural-network predictions relied on physiologically plausible variables and whether those variables were consistent with simpler statistical models.

Unsafe interpretation:

> SHAP proves that the highlighted variable causes cognitive decline.

---

## 9. Model Consistency and Predictor Stability

The thesis compared findings across:

```text
Best Subset Regression
Lasso Regression
Neural Network with SHAP
Mediation Analysis
```

This comparison is important because clinical AI should not rely on a single model result.

### 9.1 Why Consistency Matters

If different models with different assumptions identify similar predictors, the finding is more stable.

Example:

```text
Best Subset Regression identifies Plt.
Lasso supports Plt.
SHAP ranks Plt as important.
Mediation analysis finds Plt as a possible mediator.
```

This gives platelet count stronger interpretability value.

### 9.2 How to Use Consistency in the Portfolio

Model consistency can become an engineering signal:

```text
high model consistency
→ explanation confidence increases

low model consistency
→ uncertainty increases

conflicting explanations
→ clinician review required
```

This turns explainability into part of risk-aware model governance.

---

## 10. Image Model Explanation

The image route focuses on:

```text
tongue image
→ low-dimensional features
→ physiological target prediction
```

The tongue-image slides describe:

```text
AutoEncoder feature extraction
RGB-separate vs RGB-joint encoders
reconstruction MSE comparison
PCA / K-Means visualization
prediction of ~90 physiological targets
```

The image route is exploratory and should be interpreted differently from the tabular model route.

---

## 11. Autoencoder-Based Image Interpretation

Autoencoders compress tongue images into low-dimensional features.

Conceptual workflow:

```text
input image [3 x 128 x 128]
→ encoder
→ latent features
→ shared decoder
→ reconstructed image
```

The slides compared:

```text
Route 1: RGB-Separate Encoders
Route 2: RGB-Joint Encoder
```

Reported reconstruction MSE:

```text
RGB-Separate Encoders: 0.000572
RGB-Joint Encoder: 0.001158
```

Interpretation:

> The RGB-separate encoder preserved image information better in this exploratory setup, based on lower reconstruction error.

Caution:

> Reconstruction quality indicates how well the compressed feature retains visual information. It does not prove clinical relevance.

---

## 12. PCA / K-Means Visualization Interpretation

The tongue-image slides used:

```text
PCA visualization
K-Means clustering with k = 3
```

Purpose:

```text
inspect latent feature structure
compare RGB-separate and RGB-joint encoders
detect whether learned features form visible patterns
support debugging of image representation
```

Safe interpretation:

> PCA and clustering help inspect whether image features behave plausibly.

Unsafe interpretation:

> PCA clusters prove disease subtypes.

Visualization is a debugging tool, not clinical validation.

---

## 13. Image Model Explanation Limitations

Image-based explanations have several limitations.

### 13.1 Image Features May Capture Artifacts

The model may learn:

```text
lighting
camera angle
crop boundary
background artifacts
tongue exposure quality
manual correction differences
```

instead of true physiological patterns.

### 13.2 XAI Heatmaps Can Be Misleading

For CNN image models, heatmaps may highlight regions that influence the model, but this does not guarantee clinical meaning.

For example, a model may attend to:

```text
tongue color
mouth boundary
teeth
lips
shadow
image background
```

A highlighted region must be reviewed by domain experts.

### 13.3 Different XAI Methods May Disagree

The proposal explicitly notes that different XAI methods may highlight different decision features.

Policy:

```text
do not rely on a single heatmap;
compare multiple explanation methods when possible;
use clinician / domain expert review;
treat XAI as hypothesis generation.
```

### 13.4 Image Explanation Is Not Diagnosis

Safe wording:

```text
image-derived features may predict physiological targets;
XAI may highlight visual regions associated with model output;
these findings require validation.
```

Unsafe wording:

```text
the highlighted tongue region diagnoses disease;
the CNN found the true disease mechanism.
```

---

## 14. Clinical Interpretation Is Not Causal Proof

This is one of the most important interpretation rules for the repository.

### 14.1 Association vs. Causation

The thesis is based on a cross-sectional design.

It can identify:

```text
associations
predictive signals
model-selected variables
possible mediation pathways
```

It cannot definitively establish:

```text
causal effects
treatment mechanisms
future disease progression
intervention benefit
```

### 14.2 Mediation Analysis Requires Caution

The thesis used mediation analysis to explore whether platelet count mediated the age–MoCA relationship.

Safe interpretation:

> Platelet count may represent a physiological pathway related to age and cognitive function.

Unsafe interpretation:

> Platelet count causally explains cognitive decline.

The thesis itself notes that causal relationships require confirmation through longitudinal or experimental studies.

### 14.3 Explainability Does Not Equal Mechanism

A feature can be important to a model because it improves prediction.

That does not mean it is a biological cause.

Example:

```text
model importance
→ useful for prediction

biological mechanism
→ requires domain knowledge and causal evidence
```

---

## 15. Recommended Interpretation Framework

For each model finding, use the following interpretation levels.

| Level | Question | Example |
|---|---|---|
| Statistical association | Is the variable related to the outcome in this dataset? | TBW positively associated with MoCA |
| Predictive usefulness | Does it improve model prediction? | Plt appears in best subset / SHAP |
| Robustness | Does it remain important across models? | Plt appears across multiple methods |
| Clinical plausibility | Does the variable make physiological sense? | Platelets relate to inflammation / circulation |
| Causal evidence | Does changing the variable change the outcome? | Requires longitudinal or experimental study |
| Clinical actionability | Should clinicians act on it? | Requires validation and clinical protocol |

Portfolio rule:

> Most findings in this project reach the association / prediction / plausibility levels, but not definitive causal or clinical-action levels.

---

## 16. Suggested Public Code Mapping

This document maps to the following repository modules:

```text
src/evaluation/
├── model_agreement_check.py
└── error_analysis.py

src/risk_triage/
└── uncertainty_score.py

reports/
├── tabular_model_findings.md
├── image_to_physiology_findings.md
└── uncertainty_extension_proposal.md
```

Potential future public module:

```text
src/explainability/
├── shap_summary_demo.py
├── feature_importance_report.py
└── image_xai_placeholder.py
```

### 16.1 `shap_summary_demo.py`

Suggested responsibilities:

```text
load synthetic tabular data;
fit or mock a neural network / tree model;
compute SHAP-like feature importance;
export feature ranking;
compare with selected predictors.
```

### 16.2 `feature_importance_report.py`

Suggested responsibilities:

```text
combine regression coefficients, Lasso selection, and SHAP ranking;
generate a model-consistency table;
flag stable predictors.
```

### 16.3 `image_xai_placeholder.py`

Suggested responsibilities:

```text
show how image explanation would be represented;
avoid releasing real patient images;
use synthetic or placeholder images only;
include warning that heatmaps are not clinical proof.
```

---

## 17. Public Portfolio Safety Rules

For a public GitHub repository:

### 17.1 Safe to Include

```text
synthetic SHAP example
feature importance table with mock data
method explanation
interpretation policy
model consistency framework
conceptual XAI workflow
```

### 17.2 Do Not Include

```text
real patient-level SHAP outputs
raw face or tongue images
patient-specific heatmaps
hospital raw data
identifiable image metadata
clinical diagnosis claims
```

---

## 18. Recommended Output Format

A portfolio-safe explanation output could look like:

```json
{
  "patient_id": "synthetic_001",
  "predicted_moca": 23.8,
  "risk_class": "medium",
  "top_explanatory_features": [
    {
      "feature": "TBW",
      "direction": "lower TBW contributed to lower predicted MoCA",
      "interpretation": "possible hydration-related cognitive-risk signal"
    },
    {
      "feature": "Plt",
      "direction": "lower platelet count contributed to lower predicted MoCA",
      "interpretation": "possible inflammation / microcirculation-related signal"
    }
  ],
  "model_consistency": {
    "best_subset": true,
    "lasso": true,
    "shap_nn": true
  },
  "clinical_note": "Explanation describes model behavior, not causal proof."
}
```

---

## 19. Key Takeaway

> Explainability in this project should be used to make model predictions reviewable, not to make the model look clinically authoritative. Tabular interpretation identifies TBW and platelet count as stable physiological predictors of MoCA; SHAP helps inspect nonlinear neural-network behavior; image explanation can support visual-model debugging, but may be affected by crop quality, lighting, and artifacts. Most importantly, model interpretation is not causal proof and must remain part of a human-in-the-loop clinical screening workflow.

中文版本：

> 本專案中的可解釋性，目的是讓模型預測可以被審核，而不是讓模型看起來像具有臨床權威。表格模型解讀指出身體總水量與血小板數量是穩定的 MoCA 生理預測因子；SHAP 可協助檢查 neural network 是否依賴合理的變數；影像模型解釋則可用於 debugging，但會受到裁切品質、光線與雜訊影響。最重要的是，模型解釋不是因果證明，必須保留在 human-in-the-loop 的臨床篩檢流程中。

---

