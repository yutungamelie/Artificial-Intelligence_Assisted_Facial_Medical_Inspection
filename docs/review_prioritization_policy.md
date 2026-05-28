# Uncertainty-Aware Review Prioritization Policy

## 考量不確定性的人工複核優先排序政策 | Uncertainty-Aware Review Prioritization Policy

This document defines an uncertainty-aware review prioritization policy for the **Risk-Aware Clinical AI Screening System for Cognitive Function** project.

The goal is to convert model outputs into clinically cautious, human-in-the-loop decision rules. Instead of treating a model prediction as a final diagnosis, this policy asks:

```text
How risky is the predicted case?
How uncertain is the model?
Do different models agree?
Is the patient near a clinical threshold?
Should the system recommend monitoring, follow-up, or clinician review?
```

This document is written for a public portfolio repository and should be implemented using synthetic or mock data only.

---

## 1. Why Clinical AI Needs Uncertainty-Aware Review Prioritization

Clinical AI systems should not only predict outcomes. They should also communicate when their predictions are uncertain.

In a clinical screening context, overconfident prediction is risky because:

```text
false reassurance may delay evaluation;
false alarm may create unnecessary anxiety or workload;
small pilot datasets may not generalize;
missing data may distort prediction;
image quality or measurement quality may affect reliability;
correlation-based models may be mistaken for causal evidence.
```

For this project, the model should not output:

```text
diagnosis = cognitive impairment
```

Instead, it should output:

```text
risk signal + uncertainty level + suggested follow-up recommendation
```

This reflects the core clinical safety principle:

> The model supports screening and prioritization; clinicians remain responsible for interpretation and decision-making.

---

## 2. System Output Design

The final output of the risk-aware screening system should include five elements:

```text
1. predicted_moca_score
2. cognitive_risk_class
3. uncertainty_level
4. explanation / key predictors
5. recommended_follow_up
```

Example output:

```json
{
  "patient_id": "synthetic_001",
  "predicted_moca_score": 23.8,
  "cognitive_risk_class": "medium",
  "uncertainty_level": "high",
  "key_predictors": ["lower TBW", "lower platelet count", "older age"],
  "model_agreement": "moderate",
  "recommended_follow_up": "prioritized_human_review",
  "clinical_note": "Screening signal only; not a diagnosis."
}
```

---

## 3. Prediction Risk Score

The prediction risk score estimates cognitive-risk level from the model prediction.

The target outcome is:

```text
MoCA total score
```

The thesis uses the standard clinical cutoff:

```text
MoCA >= 26
→ generally interpreted as normal cognitive function

MoCA < 26
→ possible risk of mild cognitive impairment
```

For this portfolio system, the predicted MoCA score can be converted into a three-level risk class.

### 3.1 Cognitive Risk Class

Suggested rule:

```text
predicted_moca_score >= 26
→ low risk

23 <= predicted_moca_score < 26
→ medium risk

predicted_moca_score < 23
→ high risk
```

The exact thresholds should be treated as portfolio-demo logic, not clinical policy. In a real system, thresholds would require clinical validation.

### 3.2 Risk Score Formula

A simple normalized cognitive-risk score can be defined as:

```python
risk_score = max(0, min(1, (26 - predicted_moca_score) / 8))
```

Interpretation:

```text
risk_score near 0
→ predicted MoCA is safely above cutoff

risk_score near 1
→ predicted MoCA is far below cutoff
```

Portfolio note:

> This score is a demo representation of risk severity, not a clinically validated scale.

---

## 4. Uncertainty Score

The uncertainty score estimates how much the model prediction should be trusted.

A useful uncertainty score should combine several signals:

```text
1. near-threshold uncertainty
2. model agreement / disagreement
3. bootstrap confidence interval
4. missingness / data quality
5. image quality if image features are used
6. out-of-distribution or unusual input pattern
```

Suggested uncertainty output:

```text
low uncertainty
medium uncertainty
high uncertainty
```

---

## 5. Near-Threshold Uncertainty

Predictions near the clinical cutoff should be treated cautiously.

Example:

```text
predicted_moca_score = 25.8
```

Even though this is below 26, it is close enough to the cutoff that a small model error may change the risk class.

Suggested rule:

```text
abs(predicted_moca_score - 26) <= 1
→ increase uncertainty level
```

Reason:

```text
near-threshold cases are clinically fragile;
small prediction errors may change the suggested follow-up recommendation;
human review or follow-up is safer than automatic classification.
```

---

## 6. Model Agreement Signal

The thesis used multiple modeling strategies:

```text
Best Subset Regression
Lasso Regression
Neural Network with SHAP
Mediation Analysis for mechanism-oriented interpretation
```

This is useful because different models make different assumptions.

In a risk-aware review prioritization framework, we can treat model agreement as an uncertainty signal.

### 6.1 Why Model Agreement Matters

If multiple models point to the same conclusion, the signal is more stable.

```text
Best Subset Regression → high risk
Lasso Regression → high risk
Neural Network → high risk
```

This suggests stronger agreement.

If models disagree:

```text
Best Subset Regression → low risk
Lasso Regression → medium risk
Neural Network → high risk
```

the system should not force a confident conclusion.

### 6.2 Suggested Agreement Levels

```text
high agreement
→ all or most models predict the same risk class

moderate agreement
→ models differ by one neighboring risk level

low agreement
→ models strongly disagree or produce conflicting outputs
```

### 6.3 Model Agreement Policy

Suggested rule:

```text
high agreement
→ do not increase uncertainty

moderate agreement
→ increase uncertainty by one level if prediction is near threshold

low agreement
→ set uncertainty to high
```

Portfolio interpretation:

> Model disagreement does not mean the model failed. It means the case should be handled with more caution.

---

## 7. Bootstrap Confidence Interval

A bootstrap confidence interval can represent prediction uncertainty by repeatedly resampling the data and recalculating model predictions.

### 7.1 Why Bootstrap CI Is Useful

A single predicted MoCA score may look precise, but clinical decisions should consider the range of plausible predictions.

Example:

```text
predicted_moca_score = 25.4
bootstrap 95% CI = [22.8, 27.1]
```

This interval crosses the clinical cutoff of 26.

Interpretation:

```text
the patient may plausibly fall on either side of the screening threshold;
the follow-up recommendation should be more cautious;
clinician review or follow-up may be appropriate.
```

### 7.2 Suggested Rule

```python
if ci_lower < 26 and ci_upper >= 26:
    uncertainty_level = "high"
```

### 7.3 Bootstrap Output Example

```json
{
  "predicted_moca_score": 25.4,
  "bootstrap_ci": [22.8, 27.1],
  "threshold_crossing": true,
  "uncertainty_signal": "high"
}
```

Portfolio note:

> Bootstrap CI is an extension proposal for the repository. It should be implemented as a reliability layer using synthetic data in the public version.

---

## 8. Data Quality and Missingness Signal

Clinical AI uncertainty is not only about model statistics. It also depends on input quality.

### 8.1 Tabular Data Quality Signals

Increase uncertainty when:

```text
important predictors are missing;
many variables are imputed;
biomarker values are outside plausible ranges;
disease-medication coding is inconsistent;
the patient profile is very different from the training sample.
```

Important predictors in the thesis include:

```text
Age
Total Body Water (TBW)
Platelet Count (Plt)
Fat-Free Mass (FFM)
physiological and psychological markers
```

If TBW or Plt is missing, the model should not behave as if confidence is unchanged.

### 8.2 Image Data Quality Signals

If image features are used, increase uncertainty when:

```text
face or tongue crop failed;
manual crop correction was required;
lighting metadata is missing or abnormal;
tongue or face region is partially occluded;
image is blurry or overexposed;
input image is not standardized.
```

This links image preprocessing directly to the safety of review prioritization recommendations.

---

## 9. Causal Caution Policy

Empirical research should distinguish causality from correlation and that applied practitioners need credible methods.

This is important for the clinical AI portfolio because the thesis model is primarily predictive and associative.

### 9.1 Prediction Is Not Causation

The system may find:

```text
TBW is associated with MoCA
Plt is associated with MoCA
multimorbidity is associated with lower MoCA
```

but it should not automatically conclude:

```text
changing TBW will improve cognition
changing Plt will improve cognition
```

### 9.2 Mediation Analysis Caution

The thesis found that platelet count mediated part of the age–MoCA relationship.

This is useful for hypothesis generation, but the study is cross-sectional.

Safe wording:

```text
Plt may represent a physiological pathway related to age and cognitive function.
```

Unsafe wording:

```text
Plt causes cognitive decline or improvement.
```

### 9.3 Policy Rule

Any output involving physiological explanation should include:

```text
"associated with"
"predictive signal"
"screening marker"
"requires longitudinal or experimental validation"
```

and avoid:

```text
"causes"
"diagnoses"
"proves"
"treatment recommendation"
```

---

## 10. Human-in-the-Loop Decision Rule

The review prioritization framework should combine:

```text
predicted risk
uncertainty level
model agreement
data quality
threshold crossing
```

to decide what action to recommend.

### 10.1 Proposed Follow-up Recommendations

Recommended follow-up labels:

```text
routine_monitoring
follow_up_monitoring
formal_cognitive_assessment_recommended
clinician_review_required
request_additional_data
insufficient_data
```

### 10.2 Core Decision Logic

Suggested logic:

```python
if data_quality == "insufficient":
    action = "request_additional_data"

elif predicted_risk == "high" and uncertainty == "low":
    action = "formal_cognitive_assessment_recommended"

elif predicted_risk == "high" and uncertainty in ["medium", "high"]:
    action = "clinician_review_required"

elif predicted_risk == "medium" and uncertainty == "low":
    action = "follow_up_monitoring"

elif predicted_risk == "medium" and uncertainty in ["medium", "high"]:
    action = "clinician_review_required"

elif predicted_risk == "low" and uncertainty == "high":
    action = "request_additional_data_or_manual_review"

else:
    action = "routine_monitoring"
```

### 10.3 Policy Table

| Cognitive Risk | Uncertainty | Suggested Action | Reason |
|---|---:|---|---|
| Low | Low | Routine monitoring | Low-risk and reliable prediction |
| Low | Medium | Routine monitoring or follow-up | Mild uncertainty; no immediate alarm |
| Low | High | Request additional data or manual review | Prediction may be unreliable |
| Medium | Low | Follow-up monitoring | Possible cognitive-risk signal |
| Medium | Medium | Follow-up monitoring / clinician review | Needs caution |
| Medium | High | Clinician review required | Uncertain borderline case |
| High | Low | Formal cognitive assessment recommended | Strong high-risk signal |
| High | Medium | Clinician review required | High-risk but uncertain |
| High | High | Clinician review required | Do not automate decision |

---

## 11. Example Review Prioritization Cases

### Case 1: Low Risk, Low Uncertainty

```json
{
  "predicted_moca_score": 27.8,
  "cognitive_risk_class": "low",
  "uncertainty_level": "low",
  "model_agreement": "high",
  "recommended_follow_up": "routine_monitoring"
}
```

Interpretation:

> The model predicts normal-range cognitive function and the prediction is stable. Routine monitoring is appropriate.

---

### Case 2: Medium Risk, Near Threshold

```json
{
  "predicted_moca_score": 25.4,
  "cognitive_risk_class": "medium",
  "uncertainty_level": "high",
  "reason": ["near MoCA cutoff", "bootstrap CI crosses threshold"],
  "recommended_follow_up": "prioritized_human_review"
}
```

Interpretation:

> The case is close to the screening threshold. Because small model error may change the conclusion, clinician review is safer.

---

### Case 3: High Risk, Low Uncertainty

```json
{
  "predicted_moca_score": 21.8,
  "cognitive_risk_class": "high",
  "uncertainty_level": "low",
  "model_agreement": "high",
  "recommended_follow_up": "formal_cognitive_assessment_recommended"
}
```

Interpretation:

> The model consistently flags high risk. Formal cognitive assessment should be recommended.

---

### Case 4: High Risk, High Uncertainty

```json
{
  "predicted_moca_score": 22.3,
  "cognitive_risk_class": "high",
  "uncertainty_level": "high",
  "reason": ["missing platelet count", "model disagreement"],
  "recommended_follow_up": "prioritized_human_review"
}
```

Interpretation:

> The case may be high risk, but the prediction is unreliable. The system should not provide a confident automated recommendation.

---

### Case 5: Low Risk, Poor Data Quality

```json
{
  "predicted_moca_score": 27.1,
  "cognitive_risk_class": "low",
  "uncertainty_level": "high",
  "reason": ["missing TBW", "image quality failed"],
  "recommended_follow_up": "request_additional_data_or_prioritized_human_review"
}
```

Interpretation:

> Even though the predicted risk is low, the input quality is weak. The safe action is to collect more data or request manual review.

---

## 12. Suggested Implementation Mapping

This policy maps to the following repository modules:

```text
src/review_prioritization/
├── cognitive_risk_score.py
├── uncertainty_score.py
└── review_prioritization_rule.py

src/evaluation/
├── bootstrap_ci.py
├── model_agreement_check.py
└── error_analysis.py
```

### 12.1 `cognitive_risk_score.py`

Suggested responsibilities:

```text
convert predicted MoCA into low / medium / high risk;
apply MoCA threshold logic;
return risk score and risk class.
```

### 12.2 `uncertainty_score.py`

Suggested responsibilities:

```text
detect near-threshold predictions;
check bootstrap CI threshold crossing;
incorporate missingness and image-quality flags;
combine signals into low / medium / high uncertainty.
```

### 12.3 `review_prioritization_rule.py`

Suggested responsibilities:

```text
combine risk class and uncertainty level;
return recommended follow-up action;
force human review when uncertainty is high.
```

### 12.4 `model_agreement_check.py`

Suggested responsibilities:

```text
compare predictions from best subset, Lasso, and neural network;
estimate agreement level;
flag model disagreement as uncertainty.
```

### 12.5 `bootstrap_ci.py`

Suggested responsibilities:

```text
generate bootstrap prediction intervals;
check whether interval crosses MoCA cutoff;
return CI-based uncertainty signal.
```

---

## 13. Minimum Viable Public Demo

The public GitHub repository can implement a simple version using synthetic data.

Recommended files:

```text
examples/synthetic_patient_examples.csv
examples/sample_risk_outputs.json
examples/sample_review_prioritization_cases.md
src/review_prioritization/cognitive_risk_score.py
src/review_prioritization/uncertainty_score.py
src/review_prioritization/review_prioritization_rule.py
```

Minimal demo flow:

```text
1. load synthetic patient row;
2. produce or mock predicted MoCA;
3. assign cognitive-risk class;
4. compute uncertainty score;
5. apply review prioritization rule;
6. output JSON report.
```

---

## 14. Safety and Ethics Notes

This review prioritization policy should always include the following disclaimer:

> This system is not a diagnostic tool. It is a risk-screening and decision-support prototype. Model outputs should not be used for medical decision-making without clinician review and external validation.

中文版本：

> 本系統不是診斷工具，而是風險篩檢與決策支援原型。模型輸出不應在缺乏臨床人員審核與外部驗證的情況下，用於醫療決策。

---

## 15. Key Takeaway

> The uncertainty-aware review prioritization policy turns model prediction into a safer clinical workflow. Instead of asking only whether the model predicts MoCA, the system asks whether the prediction is reliable enough to act on. High-risk and high-uncertainty cases are prioritized for human review, while low-risk and low-uncertainty cases can remain under routine monitoring.

中文版本：

> 考量不確定性的人工複核優先排序政策之核心，是把模型預測轉成更安全的臨床流程：系統不只問「模型預測的 MoCA 是多少」，而是進一步問「這個預測是否可靠到足以採取行動」。高風險或高不確定性的案例必須交由臨床人員審核，低風險且低不確定性的案例才適合維持例行追蹤。

---

