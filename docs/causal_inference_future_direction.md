# Causal Inference Future Direction

## 因果推論未來方向 | Causal Inference Future Direction

This document describes the future causal-inference direction for the **Risk-Aware Clinical AI Screening System for Cognitive Function** project.

The key future research question is whether the current predictive chain can be developed into a more credible causal framework:

```text
Tongue Image
→ Physiological Signals
→ Cognitive Risk
```

However, this document intentionally avoids causal overclaiming. The current project should be framed as:

```text
predictive
associative
hypothesis-generating
risk-screening oriented
```

not as:

```text
causal proof
diagnostic evidence
treatment recommendation
evidence that tongue images cause cognitive decline
evidence that tongue images diagnose cognitive decline
```

---

## 1. Current Evidence: Predictive and Associative

The current project contains two related modeling directions.

### 1.1 Tabular Physiological Model

The thesis model used physiological, biochemical, psychological, and chronic-disease indicators to predict MoCA cognitive function scores.

Conceptual route:

```text
physiological / biochemical / psychological indicators
→ MoCA prediction
→ cognitive-risk screening signal
```

Main findings from the thesis:

```text
Best subset regression explained approximately 38% of MoCA variance.
Higher total body water (TBW) was associated with higher MoCA.
Higher platelet count (Plt) was associated with higher MoCA.
Platelet count mediated approximately 18% of the age–cognition association.
Multimorbidity showed a potential dose-response relationship with cognitive risk.
```

Safe interpretation:

> TBW and platelet count may serve as physiological screening signals associated with cognitive function in chronic disease patients.

Unsafe interpretation:

> TBW or platelet count has been proven to causally determine cognitive function.

The thesis itself states that causal relationships still require confirmation through longitudinal or experimental studies.

---

### 1.2 Tongue Image to Physiological Signal Model

The tongue-image route explored whether tongue images can be compressed into low-dimensional features and used to predict physiological targets.

Conceptual route:

```text
tongue image
→ low-dimensional image features
→ physiological target prediction
```

The tongue-image modeling slides describe:

```text
Input image dimension = [3 x 128 x 128]
AutoEncoder for dimension reduction
Comparison of RGB-separate vs. RGB-joint encoders
Use of extracted features to predict approximately 90 physiological targets
Regression and classification tasks
```

The exploratory results included:

```text
SVM best accuracy: Insomnia = 0.95
SVR best correlation: TBW = 0.636
```

Safe interpretation:

> Tongue images may contain predictive signals related to physiological indicators such as total body water.

Unsafe interpretation:

> Tongue images causally affect physiological state or directly diagnose cognitive decline.

---

## 2. Hypothesized Causal Pathway

The future causal hypothesis can be written as:

```text
Tongue Image Features
→ Physiological Signals
→ Cognitive Risk
```

More specifically:

```text
Tongue Image Features
→ TBW / Plt / inflammation-related or circulation-related physiological markers
→ MoCA / cognitive-risk screening signal
```

A more clinically interpretable version is:

```text
Visual tongue patterns may reflect physiological conditions;
physiological conditions may be associated with cognitive vulnerability;
therefore, tongue images may serve as upstream proxy signals for cognitive-risk screening.
```

Important caution:

> In this framework, tongue images are not treated as causes of cognitive decline. They are treated as possible visual proxies for underlying physiological states.

---

## 3. Why Causal Inference Is Needed

Prediction and causation answer different questions.

### 3.1 Predictive Question

A predictive question asks:

```text
Can this input help predict the outcome?
```

Examples:

```text
Can TBW help predict MoCA?
Can Plt help predict MoCA?
Can tongue-image features help predict TBW?
```

This is useful for screening and triage.

---

### 3.2 Causal Question

A causal question asks:

```text
What would happen to the outcome if we intervened on a variable?
```

Examples:

```text
Would improving hydration status improve MoCA?
Would changing inflammation or platelet-related physiology change cognitive function?
Would an intervention on chronic disease burden reduce cognitive-risk trajectory?
```

This requires stronger evidence than prediction.

---

### 3.3 Why This Distinction Matters

The Applied Econometrics course emphasizes that causality has two key features:

```text
1. Causes are asymmetrical.
2. Causes are effective.
```

This means that if X causes Y, the direction matters, and the relationship should not merely be an accidental correlation.

The course also emphasizes:

```text
correlation is not causality
```

and explains that confounding factors can create co-movement between X and Y even when X has no causal effect on Y.

For this project, this is critical.

A model may find:

```text
tongue image features predict TBW
TBW predicts MoCA
Plt predicts MoCA
```

but this does not prove:

```text
tongue image features cause TBW
TBW causes cognitive change
Plt causes cognitive change
```

---

## 4. Mediation Analysis as a Starting Point

The thesis used mediation analysis to explore whether selected physiological predictors may partially explain the relationship between age and MoCA.

Conceptual mediation path:

```text
Age
→ Physiological Marker
→ MoCA
```

The key result was:

```text
Platelet count mediated approximately 18% of the age–cognition association.
```

This is important because age is a non-modifiable distal factor, while physiological markers may be more clinically actionable or monitorable.

### 4.1 Why Mediation Is Useful

Mediation analysis helps move from:

```text
Age is associated with MoCA.
```

toward:

```text
Part of the age–MoCA association may operate through physiological pathways.
```

This provides a possible mechanism-oriented interpretation.

### 4.2 Why Mediation Is Not Enough

The thesis is based on a cross-sectional design.

Therefore, mediation results should be treated as:

```text
mechanism-oriented evidence
hypothesis-generating evidence
possible pathway exploration
```

not as:

```text
confirmed causal mechanism
intervention evidence
proof that changing Plt changes cognition
```

Safe wording:

> Platelet count may represent a physiological pathway related to age and cognitive function.

Unsafe wording:

> Platelet count causes cognitive decline.

---

## 5. Future Causal Framework

A future causal framework can separate the project into three layers.

---

### 5.1 Layer 1: Image-to-Physiology Proxy Layer

Question:

```text
Do tongue-image features reliably reflect physiological indicators?
```

Potential target variables:

```text
TBW
Plt
insomnia / sleep-related indicators
circulation-related markers
inflammation-related markers
```

Current evidence:

```text
Tongue-image features showed exploratory predictive signal for TBW and insomnia.
```

Future validation:

```text
standardize photo acquisition
increase sample size
externally validate image-to-physiology prediction
test stability across lighting, devices, and crop quality
```

Causal caution:

> This layer is mostly a measurement/proxy problem, not a causal proof problem.

---

### 5.2 Layer 2: Physiology-to-Cognitive-Risk Layer

Question:

```text
Are physiological indicators associated with cognitive function?
```

Current evidence:

```text
TBW and Plt were associated with MoCA.
Plt was stable across several modeling approaches.
Plt mediated part of the age–MoCA relationship.
```

Future validation:

```text
collect longitudinal MoCA follow-up
track TBW / Plt changes over time
test whether earlier physiological markers predict later cognitive decline
```

Causal caution:

> Cross-sectional association cannot establish whether changing physiology changes cognition.

---

### 5.3 Layer 3: Intervention / Clinical Decision Layer

Question:

```text
Would acting on the model output improve patient outcomes or clinical workflow?
```

Examples:

```text
Would AI-assisted screening increase early cognitive assessment?
Would high-risk alerts improve follow-up prioritization?
Would hydration or inflammation-related interventions change cognitive trajectories?
```

Future validation:

```text
prospective workflow study
clinician-in-the-loop evaluation
randomized or quasi-experimental study if feasible
clinical outcome follow-up
```

Causal caution:

> A model that predicts risk is not automatically an intervention that improves outcomes.

---

## 6. Candidate Future Study Designs

### 6.1 Longitudinal Cohort Study

A longitudinal study would follow patients over time.

Possible design:

```text
Baseline:
  tongue images
  TBW / Plt / physiological markers
  MoCA score
  chronic disease indicators

Follow-up:
  repeated MoCA
  repeated physiological measures
  cognitive decline trajectory
```

Main questions:

```text
Do baseline TBW and Plt predict future MoCA decline?
Do changes in TBW or Plt precede changes in MoCA?
Do tongue-image features predict future physiological or cognitive change?
```

Why useful:

> Longitudinal data help establish temporal ordering, which is necessary for stronger causal reasoning.

---

### 6.2 Prospective Clinical Workflow Study

A workflow study would test whether the screening system improves clinical practice.

Possible design:

```text
Clinicians use standard workflow
vs.
Clinicians use AI-assisted risk triage
```

Outcomes:

```text
formal MoCA follow-up rate
time to cognitive-risk identification
clinician workload
false alarm burden
missed high-risk cases
patient follow-up adherence
```

Why useful:

> This tests whether the AI system improves decision support, not just prediction accuracy.

---

### 6.3 Randomized Experiment

A randomized experiment would provide stronger causal evidence if ethically and practically feasible.

Example:

```text
Randomize clinics or clinicians to:
  standard screening workflow
  AI-assisted screening workflow
```

Potential outcome:

```text
earlier cognitive-risk detection
more appropriate follow-up
reduced administrative burden
```

Caution:

> Randomization should apply to workflow exposure, not to withholding necessary medical care.

---

### 6.4 Matching or Causal Machine Learning

If randomization is not possible, observational causal methods may be used.

Possible methods:

```text
matching
propensity score weighting
double selection
causal machine learning
```

Potential use:

```text
construct comparable patient groups
adjust for observed confounders
estimate associations closer to causal effects under assumptions
```

Caution:

> These methods only help when assumptions are credible and relevant confounders are measured.

---

### 6.5 Difference-in-Differences or Synthetic Control

If the hospital introduces AI-assisted screening at a particular time, quasi-experimental methods may become possible.

Possible scenario:

```text
Before AI screening implementation
vs.
After AI screening implementation
```

Potential comparison:

```text
similar clinic without AI screening
or synthetic control built from non-treated units
```

Possible outcomes:

```text
follow-up completion
screening efficiency
clinician workload
cognitive-risk detection rate
```

Caution:

> Difference-in-differences requires a credible comparison trend in the absence of intervention.

---

## 7. Confounders to Consider

Any future causal analysis should carefully consider confounding variables.

Potential confounders include:

```text
Age
Sex
education
baseline chronic disease burden
medication use
hydration habits
kidney function
liver function
diabetes status
sleep quality
depressive symptoms
lifestyle factors
image acquisition quality
clinical follow-up frequency
```

For the tongue-image pathway, additional technical confounders include:

```text
lighting
camera device
image crop quality
tongue position
manual vs automatic preprocessing
photo acquisition environment
```

Reason:

> Without accounting for confounding, the model may learn signals caused by patient selection, imaging conditions, or clinical workflow rather than physiology.

---

## 8. Proposed Causal Diagram

A simplified causal diagram can be documented as:

```text
Age ───────────────► Cognitive Risk / MoCA
 │                         ▲
 │                         │
 ▼                         │
Physiological State ───────┘
 │
 ▼
Tongue Appearance / Image Features
```

A more operational AI version:

```text
Age / chronic disease burden / lifestyle / medications
          │
          ▼
Physiological state: TBW, Plt, inflammation, circulation
          │
          ├────────► MoCA / cognitive-risk trajectory
          │
          ▼
Tongue appearance captured by image features
```

Important interpretation:

```text
Tongue image features may be downstream visual proxies of physiological state.
They should not be treated as upstream causes of cognitive decline.
```

---

## 9. Avoiding Causal Overclaim

### 9.1 Safe Claims

The public portfolio can safely say:

```text
This project explores predictive signals for cognitive-risk screening.
Tongue images may contain information related to physiological indicators.
TBW and Plt were associated with MoCA in a cross-sectional pilot dataset.
Plt showed a mediation signal in the age–MoCA relationship.
Future longitudinal or experimental studies are needed for causal validation.
```

### 9.2 Unsafe Claims

The portfolio should avoid saying:

```text
Tongue images diagnose cognitive decline.
Tongue images cause cognitive decline.
TBW causes cognitive improvement.
Platelet count causes cognitive function change.
The model proves a biological mechanism.
The model provides treatment recommendations.
```

### 9.3 Recommended Wording

Use:

```text
associated with
predictive signal
screening marker
proxy signal
hypothesis-generating
requires validation
```

Avoid:

```text
causes
proves
diagnoses
treats
guarantees
```

---

## 10. Connection to Risk-Aware AI Engineering

This causal future direction connects to the engineering repository through the uncertainty and triage modules.

Relevant modules:

```text
src/risk_triage/
├── cognitive_risk_score.py
├── uncertainty_score.py
└── clinical_triage_rule.py

src/evaluation/
├── bootstrap_ci.py
├── model_agreement_check.py
└── error_analysis.py
```

Why this matters:

```text
causal uncertainty
→ should increase clinical caution

model disagreement
→ should trigger review

cross-sectional evidence
→ should avoid intervention claims

hypothesis-generating result
→ should be routed to future validation
```

A risk-aware system should therefore output:

```text
risk signal
uncertainty level
explanation
triage action
causal caution note
```

not:

```text
diagnosis
causal claim
automatic treatment decision
```

---

## 11. Suggested Public Demo Extension

A public GitHub demo can include a synthetic causal-future-direction example.

Example output:

```json
{
  "current_evidence_level": "predictive_association",
  "hypothesized_pathway": "tongue_image_features -> physiological_signals -> cognitive_risk",
  "supported_links": [
    {
      "link": "tongue_image_features -> TBW",
      "evidence": "exploratory image-to-physiology prediction",
      "causal_status": "not causal evidence"
    },
    {
      "link": "TBW / Plt -> MoCA",
      "evidence": "cross-sectional association and predictive modeling",
      "causal_status": "requires longitudinal or experimental validation"
    },
    {
      "link": "Age -> Plt -> MoCA",
      "evidence": "mediation analysis",
      "causal_status": "hypothesis-generating"
    }
  ],
  "recommended_next_study": "longitudinal validation",
  "clinical_note": "This project supports risk screening and hypothesis generation, not diagnosis or treatment."
}
```

---

## 12. Portfolio Takeaway

> The future causal-inference direction is to move carefully from prediction toward mechanism-oriented validation. The current project suggests a plausible chain in which tongue-image features may reflect physiological signals, and physiological signals such as TBW and platelet count may be associated with cognitive-risk screening. However, because the current evidence is cross-sectional and predictive, it should be treated as hypothesis-generating rather than causal proof. Future work should use longitudinal, experimental, or credible quasi-experimental designs to test whether these physiological signals truly precede or influence cognitive change.

中文版本：

> 這份 causal inference future direction 的核心，是把目前的模型從「能不能預測」逐步推進到「是否存在可信的生理機制」，但不能過度宣稱因果。目前專案支持一個合理假設：舌頭影像特徵可能反映某些生理訊號，而 TBW、Plt 等生理訊號可能與認知風險有關。不過，目前證據主要是橫斷面、預測性與關聯性，因此只能作為 hypothesis-generating evidence。未來需要縱貫性、實驗性或可信的準實驗設計，才能檢驗這些生理訊號是否真的早於或影響認知功能變化。

---
