# Uncertainty Extension Proposal

## 不確定性風險評估延伸提案 | Uncertainty-Aware Risk Assessment Extension

This report proposes how to extend the **Risk-Aware Clinical AI Screening System for Cognitive Function** from a predictive modeling project into an uncertainty-aware clinical AI screening workflow.

The purpose of this document is to upgrade the original modeling results into a safer AI application design:

```text
model prediction
→ uncertainty estimation
→ risk interpretation
→ human-in-the-loop prioritization recommendation
→ future validation plan
```

This report is written for a public GitHub portfolio repository. It does not release patient-level data, hospital raw files, clinical images, or identifiable information.

---

## 1. Why Existing Model Output Is Not Enough

The existing modeling work used tabular clinical data to identify physiological predictors associated with cognitive function. The modeling results showed that total body water (TBW) and platelet count (Plt) were important predictors of MoCA scores, and that platelet count mediated part of the observed association between age and cognitive function.


However, a model output such as:

```text
predicted_moca = 23.8
```

is not enough for clinical AI use.

A clinical AI screening system needs to answer additional questions:

```text
How reliable is this prediction?
Is this patient near a clinical cutoff?
Do multiple models agree?
Are key predictors missing?
Is this input similar to the training population?
Should the system recommend routine monitoring, follow-up, or clinician review?
```

In other words, the system should not only estimate risk. It should also estimate whether the risk estimate itself is trustworthy.

---

## 2. Existing Modeling Foundation

The original thesis modeling pipeline provides a strong foundation for an uncertainty-aware extension.

### 2.1 Target Outcome

The main cognitive outcome is:

```text
MoCA total score
```

Clinical interpretation:

```text
MoCA >= 26
→ generally interpreted as normal cognitive function

MoCA < 26
→ possible risk of mild cognitive impairment
```

### 2.2 Data Sources

The dataset included:

```text
physiological measurements
blood and urine markers
body composition metrics
psychological questionnaires
chronic disease indicators
cognitive assessment results
```

### 2.3 Modeling Methods

The modeling workflow included:

```text
Best Subset Regression
Mediation Analysis
Lasso Regression
Neural Network with SHAP
```

Using multiple modeling approaches provides a useful basis for comparing whether important predictors remain consistent across methods. As a proposed portfolio extension, disagreement across predictive models could also be examined as one uncertainty signal for identifying cases that may require more cautious interpretation or prioritized human review.

### 2.4 Key Findings

The main findings were:

```text
Best subset regression explained approximately 38% of MoCA variance.
Higher TBW was associated with higher MoCA.
Higher platelet count was associated with higher MoCA.
Platelet count mediated approximately 18% of the age–cognition association.
Multimorbidity showed a potential dose-response relationship with cognitive risk.
```

These findings suggest useful screening signals, but they should not be treated as clinical diagnosis or causal proof.

---

## 3. Why Risk-Aware Extension Is Needed

A risk-aware extension is needed because clinical AI errors have asymmetric consequences.

### 3.1 False Reassurance Risk

If the model predicts low risk when the patient is actually at cognitive risk:

```text
formal assessment may be delayed;
follow-up may be missed;
the system may create false reassurance.
```

### 3.2 False Alarm Risk

If the model predicts high risk when the patient is actually low risk:

```text
unnecessary anxiety may increase;
clinical workload may increase;
patients may receive unnecessary follow-up.
```

### 3.3 Borderline Risk

A patient with predicted MoCA near 26 may change risk class with a small model error.

Example:

```text
predicted_moca = 25.8
```

This is technically below the cutoff, but it is close enough that the system should be cautious.

### 3.4 Pilot Study Risk

The dataset is a pilot clinical dataset, not a large externally validated production dataset.

Therefore:

```text
single-point predictions should not be overtrusted;
model uncertainty should be explicitly reported;
high-risk or high-uncertainty cases should be routed to clinicians.
```

---

## 4. Causal Caution: Prediction Is Not Intervention Evidence

A risk-screening model can identify patterns associated with cognitive function, but it cannot by itself establish what would happen if a physiological factor were actively changed. Predictive associations describe which variables help estimate risk; causal effects require evidence about how outcomes would differ under a specific intervention or counterfactual condition.

This distinction is essential for interpreting the findings in this clinical AI project.

The model may identify findings such as:

```text
TBW is associated with MoCA.
Plt is associated with MoCA.
Multimorbidity is associated with cognitive risk.
```

However, these predictive findings do not by themselves demonstrate that:

```text
Changing TBW will improve MoCA scores.
Changing platelet count will improve cognitive function.
Treating one biomarker will causally reduce cognitive risk.
```

The system should therefore communicate model outputs as:

```text
Risk-screening signals
Predictive associations
Potential screening markers
Hypothesis-generating evidence
```

rather than as:

```text
Treatment recommendations
Causal intervention effects
Diagnostic conclusions
```

Portfolio principle:

> Prediction models can support risk screening and review prioritization, but causal claims about interventions require stronger empirical evidence, such as randomized experiments, longitudinal studies, natural experiments, or causal-inference designs supported by credible assumptions.

---

## 5. Proposed Uncertainty Signals

The proposed system should combine multiple uncertainty signals.

```text
Uncertainty Score
├── near-threshold uncertainty
├── bootstrap confidence interval
├── model disagreement
├── missingness / data-quality uncertainty
├── feature reliability uncertainty
├── image-quality uncertainty if image features are used
└── out-of-distribution uncertainty
```

The output should be:

```text
low uncertainty
medium uncertainty
high uncertainty
```

---

## 6. Signal 1: Bootstrap Confidence Interval

### 6.1 Motivation

A single predicted MoCA value gives a false sense of precision.

Example:

```text
predicted_moca = 25.4
```

This looks precise, but the real model uncertainty may be large.

A bootstrap confidence interval can show a plausible range of predictions.

Example:

```text
predicted_moca = 25.4
bootstrap 95% CI = [22.8, 27.1]
```

This interval crosses the clinical cutoff of 26.

Interpretation:

```text
the patient may plausibly fall on either side of the cutoff;
the screening classification is uncertain;
clinician review or follow-up is safer.
```

### 6.2 Proposed Implementation

Suggested module:

```text
src/evaluation/bootstrap_ci.py
```

Suggested steps:

```text
1. resample the training data with replacement;
2. refit or simulate the model across bootstrap samples;
3. predict MoCA for the same synthetic patient;
4. compute lower and upper percentiles;
5. check whether the interval crosses the MoCA cutoff.
```

Example pseudocode:

```python
def bootstrap_prediction_interval(model_fn, X_train, y_train, x_patient, n_boot=1000):
    predictions = []

    for _ in range(n_boot):
        X_b, y_b = bootstrap_sample(X_train, y_train)
        model = model_fn().fit(X_b, y_b)
        predictions.append(model.predict(x_patient)[0])

    lower = np.percentile(predictions, 2.5)
    upper = np.percentile(predictions, 97.5)

    return lower, upper
```

### 6.3 Threshold-Crossing Rule

```python
if ci_lower < 26 and ci_upper >= 26:
    uncertainty_signal = "high"
else:
    uncertainty_signal = "lower"
```

Portfolio note:

> Bootstrap CI should be presented as a reliability extension, not as a clinically validated uncertainty estimator.

---

## 7. Signal 2: Model Disagreement

### 7.1 Motivation

The thesis used multiple modeling methods:

```text
Best Subset Regression
Lasso Regression
Neural Network with SHAP
```

Each model makes different assumptions.

If these models agree, the signal is more stable.

If these models disagree, the system should be cautious.

### 7.2 Proposed Model Agreement Check

Suggested module:

```text
src/evaluation/model_agreement_check.py
```

Example:

```json
{
  "best_subset_prediction": 23.9,
  "lasso_prediction": 24.3,
  "neural_network_prediction": 27.2
}
```

This suggests disagreement because one model predicts normal-range cognition while others predict risk.

### 7.3 Agreement Levels

```text
High agreement:
all models predict the same risk class

Moderate agreement:
models differ by neighboring risk classes

Low agreement:
models strongly disagree or cross the clinical cutoff
```

### 7.4 Policy Rule

```python
if model_agreement == "low":
    uncertainty_level = "high"

elif model_agreement == "moderate" and near_threshold:
    uncertainty_level = "high"

elif model_agreement == "moderate":
    uncertainty_level = "medium"
```

Interpretation:

> Model disagreement is not failure. It is information that the system should escalate the case to human review.

---

## 8. Signal 3: Near-Threshold Risk

### 8.1 Motivation

The MoCA cutoff of 26 creates a clinically meaningful boundary.

Predictions near this boundary are fragile.

Example:

```text
predicted_moca = 25.7
```

A small error of 0.4 points could change the risk label.

### 8.2 Proposed Rule

```python
distance_to_cutoff = abs(predicted_moca - 26)

if distance_to_cutoff <= 1:
    near_threshold = True
    uncertainty_signal = "increase"
```

### 8.3 Triage Implication

Near-threshold cases should not be automatically labeled as safe or unsafe.

Suggested action:

```text
follow-up monitoring
or clinician review
or formal MoCA reassessment
```

Portfolio framing:

> Near-threshold risk is where uncertainty-aware triage is most valuable.

---

## 9. Signal 4: Missingness and Data-Quality Risk

### 9.1 Motivation

Clinical data are often incomplete or noisy.

A prediction based on missing or imputed key predictors should be less trusted.

Important predictors from the thesis include:

```text
Age
TBW
Plt
FFM
WHO-5
GluAC
TCHO
HDL
Hb
```

If TBW or platelet count is missing, the model should not report the same confidence level.

### 9.2 Proposed Data Quality Flags

Suggested module:

```text
src/evaluation/error_analysis.py
```

Suggested flags:

```text
missing_key_predictor
high_missingness_patient
out_of_range_value
inconsistent_disease_medication_coding
imputed_core_variable
```

### 9.3 Policy Rule

```python
if missing_key_predictor:
    uncertainty_level = max(uncertainty_level, "medium")

if multiple_key_predictors_missing:
    uncertainty_level = "high"
```

---

## 10. Signal 5: Image-Quality Risk

If image-derived features are later integrated, image quality should become part of uncertainty estimation.

Risk factors:

```text
face or tongue crop failed
manual crop correction required
lighting metadata missing
overexposure or underexposure
tongue region not clearly visible
image not standardized
```

Suggested rule:

```text
good image quality
→ normal uncertainty

manual crop / lighting concern
→ increase uncertainty

failed crop
→ do not predict; request recollection or manual review
```

This connects image preprocessing to clinical safety.

---

## 11. Human-in-the-Loop Review Prioritization

The final decision should combine:

```text
predicted risk
uncertainty level
model agreement
bootstrap CI
near-threshold status
data quality
image quality
```

### 11.1 Proposed Risk Classes

```text
Low risk:
predicted MoCA >= 26

Medium risk:
23 <= predicted MoCA < 26

High risk:
predicted MoCA < 23
```

These thresholds are for portfolio demonstration only and would require clinical validation before any real-world use.

### 11.2 Proposed Follow-up Recommendations

```text
routine_monitoring
follow_up_monitoring
formal_cognitive_assessment_recommended
clinician_review_required
request_additional_data
insufficient_data
```

### 11.3 Review Prioritization Policy Table

| Predicted Risk | Uncertainty Level | Suggested Follow-up Recommendation                 |
| -------------- | ----------------: | -------------------------------------------------- |
| Low            |               Low | Routine monitoring                                 |
| Low            |            Medium | Routine monitoring or follow-up monitoring         |
| Low            |              High | Request additional data or prioritize human review |
| Medium         |               Low | Follow-up monitoring                               |
| Medium         |            Medium | Follow-up monitoring or prioritize human review    |
| Medium         |              High | Prioritized human review                           |
| High           |               Low | Formal cognitive assessment recommended            |
| High           |            Medium | Prioritized human review                           |
| High           |              High | Prioritized human review before further action     |


### 11.4 Core Policy

```text
High predicted risk should not be dismissed.
High uncertainty should not lead to an automated confident recommendation.
High predicted risk combined with high uncertainty should be prioritized for human review.
```
> This review prioritization policy is presented as a portfolio-level design proposal. It illustrates how predicted cognitive-risk signals and uncertainty indicators could be translated into safer follow-up recommendations, rather than serving as a clinically validated decision rule.
---

## 12. Example Output

A public demo output may look like:

```json
{
  "patient_id": "synthetic_001",
  "predicted_moca": 25.4,
  "risk_class": "medium",
  "bootstrap_ci": [22.8, 27.1],
  "threshold_crossing": true,
  "model_agreement": "moderate",
  "missingness_flags": ["none"],
  "image_quality_flags": ["not_used"],
  "uncertainty_level": "high",
  "triage_action": "clinician_review_required",
  "clinical_note": "This is a screening signal, not a diagnosis."
}
```

This output is more responsible than:

```json
{
  "diagnosis": "cognitive impairment",
  "confidence": "95%"
}
```

because it communicates uncertainty and routes risky cases to human review.

---

## 13. Future Validation Plan

This extension should be validated in stages.

### 13.1 Stage 1: Internal Synthetic Demo

Goal:

```text
demonstrate logic and engineering structure
```

Tasks:

```text
create synthetic patient examples
mock model predictions
implement uncertainty scoring
generate sample triage outputs
```

Deliverables:

```text
examples/sample_risk_outputs.json
examples/sample_triage_cases.md
src/risk_triage/
src/evaluation/
```

### 13.2 Stage 2: Internal Retrospective Validation

Goal:

```text
test uncertainty logic on de-identified internal data
```

Tasks:

```text
evaluate prediction error by uncertainty level
test threshold-crossing logic
compare model disagreement with actual error
review false-negative cases
review false-positive cases
```

Key questions:

```text
Do high-uncertainty cases actually have higher error?
Does model disagreement predict unreliable cases?
Are near-threshold cases more frequently misclassified?
```

### 13.3 Stage 3: External Validation

Goal:

```text
evaluate generalizability on independent cohorts
```

Tasks:

```text
test model on external clinical dataset
compare calibration across cohorts
evaluate subgroup performance
assess missingness patterns
validate triage thresholds
```

### 13.4 Stage 4: Prospective Clinical Workflow Study

Goal:

```text
test whether the system improves screening workflow
```

Tasks:

```text
embed model output into clinician review workflow
measure clinician acceptance
measure follow-up recommendation accuracy
evaluate alert burden
compare workflow with and without AI triage
```

### 13.5 Stage 5: Causal and Longitudinal Study

Goal:

```text
separate prediction from causal mechanism
```

Potential designs:

```text
longitudinal follow-up
mediation analysis with temporal ordering
randomized intervention if clinically appropriate
quasi-experimental design if natural variation exists
causal machine learning for heterogeneous treatment effects
```

This stage is necessary before claiming that modifying a physiological marker would change cognitive outcomes.

---

##  14. Causal Interpretation Boundary and Future Validation | 因果解讀界線與未來驗證方向

This portfolio positions the current modeling results as **predictive and hypothesis-generating evidence**, rather than evidence of a causal intervention effect.

The tabular modeling route identified clinically interpretable signals associated with cognitive function, including total body water (TBW) and platelet count (Plt). The mediation analysis further suggested that platelet count may help explain part of the observed association between age and cognitive function. These findings provide a meaningful basis for risk-screening design and future investigation.

However, the current results do not establish that changing an identified physiological factor would improve cognitive outcomes. For example:

```text
Observed modeling finding:
TBW and platelet count are associated with MoCA scores.

Not established by the current study:
Actively changing TBW or platelet count will improve cognition.
```

This distinction shapes the design of the portfolio system:

```text
Predictive associations
→ interpretable cognitive-risk signals
→ uncertainty-aware review prioritization recommendations

Causal intervention claims
→ require additional validation and stronger study designs
```

Accordingly, the current system is framed as a risk-screening and decision-support prototype, not a treatment recommendation system or an automated clinical decision-maker.

Future Validation Direction

If future work aims to evaluate whether identified physiological factors play a causal role in cognitive outcomes, the next step would require study designs and data that are appropriate for causal evaluation, such as longitudinal follow-up, carefully defined comparison groups, prospective validation, or other causal-inference approaches supported by credible assumptions.

In this portfolio, causal reasoning is therefore used to define a responsible boundary:

>The model may help identify risk signals and prioritize cases for human review, but it should not claim that intervening on a predicted factor will improve cognitive outcomes without additional causal evidence.
---

## 15. Recommended Repository Implementation

This report maps to the following files:

```text
docs/
├── uncertainty_triage_policy.md
├── explainability_and_model_interpretation.md
└── causal_inference_future_direction.md

src/
├── risk_triage/
│   ├── cognitive_risk_score.py
│   ├── uncertainty_score.py
│   └── clinical_triage_rule.py
│
└── evaluation/
    ├── bootstrap_ci.py
    ├── model_agreement_check.py
    └── error_analysis.py

examples/
├── sample_risk_outputs.json
└── sample_triage_cases.md
```

Minimum viable implementation:

```text
1. create synthetic patient input;
2. mock predicted MoCA from tabular model;
3. compute distance to cutoff;
4. compute bootstrap CI or mock CI;
5. compare predictions from mock model ensemble;
6. compute uncertainty level;
7. apply triage policy;
8. export JSON risk report.
```

---

## 16. Limitations of This Proposal

This proposal is an extension design, not a validated clinical system.

Limitations:

```text
thresholds require clinical validation;
bootstrap CI may underestimate real-world uncertainty;
model disagreement depends on model diversity;
small pilot data may not represent broader populations;
uncertainty score must be calibrated;
triage actions require clinician workflow testing;
causal claims require longitudinal or experimental evidence.
```

Safe portfolio statement:

> This uncertainty extension demonstrates how the original modeling results can be translated into a risk-aware clinical AI design. It is not a validated medical device or diagnostic system.

---

## 17. Portfolio Takeaway

> The uncertainty extension upgrades the project from “a model that predicts MoCA” into “a risk-aware clinical AI screening workflow.” It combines predicted cognitive risk with uncertainty signals such as bootstrap confidence intervals, model disagreement, near-threshold risk, missingness, and data quality. The output is not a diagnosis; it is a triage recommendation that decides whether the case should receive routine monitoring, follow-up, formal assessment, additional data collection, or clinician review.

中文版本：

> 這份不確定性延伸提案，將專案從「預測 MoCA 的模型」升級成「具風險意識的臨床 AI 篩檢流程」。它把認知風險預測與 bootstrap 信賴區間、模型不一致、接近臨床 cutoff、缺失值與資料品質等不確定性訊號結合起來。系統輸出的不是診斷，而是分流建議：哪些案例可以例行追蹤，哪些需要後續追蹤、正式認知測驗、補資料，或交由臨床人員審核。

---

