# Tabular Model Findings

## 表格模型結果整理 | Tabular Model Findings

This report summarizes the tabular modeling results from the thesis **Physiological Predictors of Cognitive Functions in Patients with Chronic Diseases** and reframes them for the `risk-aware-clinical-ai-screening` portfolio project.

The goal of this report is to explain how physiological, biochemical, psychological, and chronic-disease indicators were used to model cognitive function, what predictors were most informative, how the findings were checked for robustness, and how the results should be interpreted in a risk-aware clinical AI screening context.

This report is a **portfolio reconstruction**. It does not release patient-level data, raw hospital tables, or identifiable clinical information.

---

## 1. Objective | 研究目標

The main modeling objective was:

```text
physiological / biochemical / psychological / chronic disease indicators
→ MoCA total score prediction
→ cognitive-risk screening signal
```

The central research question was:

> Which routinely available physiological indicators are most strongly associated with cognitive function in patients with chronic diseases?

The clinical motivation was that formal cognitive assessment tools such as the Montreal Cognitive Assessment (MoCA) are clinically useful, but they require trained personnel and administration time. If routinely collected clinical indicators can help identify possible cognitive risk, they may support earlier screening, follow-up prioritization, and human-in-the-loop triage.

Portfolio framing:

> The tabular model is not a diagnostic model. It is an exploratory screening model that uses structured clinical indicators to estimate cognitive-risk signals and identify interpretable physiological predictors.

---

## 2. Dataset | 資料集

The thesis used a cross-sectional multimodal dataset collected from patients at the Family Medicine Department of National Taiwan University Hospital.

### 2.1 Study Sample

```text
N = 110 participants
Setting = NTUH Family Medicine Department
Population = patients with chronic diseases
Age range = 23–75 years
Average age = 58 years
Sex distribution = 60 males, 50 females
```

After preprocessing and exclusion of missing values for specific modeling tasks, the main regression model used:

```text
N = 106 valid cases
```

### 2.2 Target Variable

The main target variable was:

```text
MoCA total score
```

MoCA interpretation:

```text
MoCA >= 26
→ generally interpreted as normal cognitive function

MoCA < 26
→ possible risk of mild cognitive impairment
```

In the sample:

```text
77 participants scored >= 26
33 participants scored < 26
mean MoCA = 26.16
median MoCA = 27
```

### 2.3 Input Feature Groups

The dataset included three major categories of structured features.

#### Demographic, Physiological, and Vital Features

```text
Age
Sex
Body Height (BH)
Waist Circumference (WC)
Body Weight (BW)
Fat-Free Mass (FFM)
Body Fat Mass (BFM)
Body Fat Percentage (BFP)
Total Body Water (TBW)
Systolic Blood Pressure (SBP)
Diastolic Blood Pressure (DBP)
```

#### Clinical Biochemical and Organ Function Markers

```text
Creatinine (Cr)
eGFR
UACR
Uric Acid (UA)
FIB-4
ALT
AST
Total Bilirubin
Direct Bilirubin
Total Cholesterol (TCHO)
LDL
HDL
Triglycerides (TG)
HbA1c
Fasting Glucose (GluAC)
Platelet Count (Plt)
Hemoglobin (Hb)
Insulin
hsCRP
Ferritin
```

#### Psychological and Behavioral Questionnaires

```text
CPSQI
CES-D
WHO-5
Big Five / TIPI-B5 personality dimensions
```

### 2.4 Chronic Disease Variables

Chronic disease status was operationalized using physiological indicators and medication proxies.

Conditions included:

```text
Hypertension
Type 2 Diabetes Mellitus
Hyperlipidemia
Chronic Kidney Disease
Liver Fibrosis / NAFLD Risk
Sleep Disorders
Depressive Tendencies
```

A multimorbidity count was also derived to represent cumulative chronic disease burden.

---

## 3. Data Preprocessing | 資料前處理

Before modeling, the dataset was cleaned and standardized.

### 3.1 Variable Removal

Variables were removed or excluded when they were:

```text
highly homogeneous
questionnaire sub-items already represented by total scores
self-reported lifestyle items judged too subjective for the main analysis
inconsistent or difficult to interpret reliably
```

This preprocessing decision was important for clinical interpretability and model stability.

### 3.2 Standardization

Continuous variables were standardized using Z-score normalization:

```text
z = (x - mean) / standard deviation
```

Reason:

```text
remove scale differences
make coefficients more comparable
improve model stability
support regularized models such as Lasso
```

Binary categorical variables, such as sex, retained their original 0 / 1 encoding.

---

## 4. Methods | 建模方法

The thesis used a multi-method strategy:

```text
1. Descriptive statistics
2. Best subset regression
3. Mediation analysis
4. Lasso regression
5. Neural network with SHAP
6. Modeling consistency and predictor stability comparison
```

This structure is useful for a risk-aware AI portfolio because it does not rely on a single model result. Instead, it checks whether the same physiological signals remain meaningful across different modeling assumptions.

---

## 5. Descriptive Findings | 描述統計結果

### 5.1 MoCA Distribution

MoCA scores were left-skewed, with most participants concentrated in the higher range.

Summary:

```text
MoCA mean = 26.16
MoCA median = 27
MoCA mode = 27
70% scored >= 26
30% scored < 26
```

Portfolio interpretation:

> Most participants had normal-range cognitive scores, but a meaningful subgroup fell below the MoCA clinical cutoff. This makes the task relevant for early cognitive-risk screening rather than diagnosis.

### 5.2 Chronic Disease and Multimorbidity Pattern

Participants with chronic diseases tended to show lower MoCA distributions compared with those without the condition. The pattern was especially visible for chronic kidney disease and depression.

The multimorbidity visualization showed a dose-response-like pattern:

```text
more chronic conditions
→ MoCA distribution shifts lower
→ higher cognitive-risk concentration
```

Portfolio interpretation:

> Cognitive risk appears multifactorial. Disease burden may matter more than a single diagnosis alone.

### 5.3 Psychological and Behavioral Patterns

Psychological and behavioral questionnaire results were visualized against MoCA. Some variables showed clinically plausible directions, while CPSQI-related sleep variables showed a counterintuitive association and were excluded from primary statistical modeling.

Risk-aware lesson:

> Not every collected variable should be used simply because it is available. Variables that produce counterintuitive or unstable patterns should be reviewed before entering the model.

---

## 6. Best Subset Regression: Physiological Predictors → MoCA

## 最佳子集迴歸：生理指標預測 MoCA

### 6.1 Purpose

Best subset regression was used to identify the most informative combination of predictors for MoCA total score.

Why this method was chosen:

```text
exhaustively searches predictor combinations
does not rely only on prior assumptions
supports interpretable variable selection
uses adjusted R² to balance fit and model complexity
```

### 6.2 Main Model Performance

The best subset regression model using physiological predictors achieved:

```text
Adjusted R² = 0.3763
Multiple R² = 0.4528
F-statistic = 5.919
p-value = 7.378e-08
```

Interpretation:

> The selected physiological and psychological predictors explained approximately 38% of the variance in MoCA total scores.

### 6.3 Selected Predictors

The best subset regression selected the following predictors:

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

### 6.4 Most Important Predictors

The most interpretable and stable predictors were:

```text
Age
Total Body Water (TBW)
Platelet Count (Plt)
Fat-Free Mass (FFM)
```

Key coefficients from the best subset model:

| Predictor | Direction | Estimate | p-value | Interpretation |
|---|---:|---:|---:|---|
| Age | negative | -0.378 | < .001 | older age associated with lower MoCA |
| TBW | positive | 1.31 | .001 | higher total body water associated with better MoCA |
| Plt | positive | 0.244 | .009 | higher platelet count associated with better MoCA |
| FFM | negative | -1.673 | .001 | higher fat-free mass associated with lower MoCA in this model |
| BH | positive | 0.427 | .041 | body height showed a modest positive association |

Portfolio interpretation:

> TBW and platelet count are clinically interpretable physiological signals that may support cognitive-risk screening because they are routinely measurable and plausibly connected to hydration status, microcirculation, inflammation, and systemic resilience.

---

## 7. Best Subset Regression: Chronic Disease Variables → MoCA

## 最佳子集迴歸：慢性病變數預測 MoCA

A second best subset regression model used chronic disease variables and multimorbidity count to predict MoCA total score.

### 7.1 Model Performance

The chronic-disease model achieved:

```text
Adjusted R² = 0.05964
Multiple R² = 0.07738
p-value = 0.01517
```

This was much lower than the physiological-predictor model:

```text
physiological model Adjusted R² = 0.3763
chronic-disease model Adjusted R² = 0.05964
```

### 7.2 Selected Chronic Disease Predictors

The selected variables included:

```text
Chronic Kidney Disease (CKD)
Liver Disease (LD)
```

CKD retained statistical significance in the continuous MoCA model.

Portfolio interpretation:

> Disease labels alone were less informative than physiological measurements for explaining MoCA variation. This suggests that continuous physiological markers may capture finer cognitive-risk signals than diagnosis categories alone.

---

## 8. MoCA Subdomain Modeling | MoCA 子領域建模

Best subset regression was also applied to MoCA subdomains.

Several predictors reappeared across subdomains:

```text
Age
TBW
FFM
Plt
```

Observed patterns:

```text
Age
→ consistently negative across Abstraction, Delayed Recall, Memory, and Visuospatial/Executive domains

TBW
→ generally positive, especially in Abstraction and Memory

FFM
→ negative in several domains but positive in Attention

Plt
→ positive in Abstraction, Language, and Visuospatial/Executive domains
```

Portfolio interpretation:

> Cognitive function is not a single uniform outcome. Different physiological predictors may relate differently to memory, abstraction, attention, language, and executive function.

This supports future domain-specific cognitive-risk modeling.

---

## 9. Mediation Analysis | 中介分析

### 9.1 Purpose

Mediation analysis was used to explore whether selected physiological predictors partially explain the relationship between age and MoCA.

Conceptual pathway:

```text
Age
→ physiological marker
→ MoCA
```

This is clinically meaningful because age itself cannot be modified, while physiological markers may be measurable or potentially modifiable.

### 9.2 Methods

The thesis used two mediation approaches:

```text
1. Baron and Kenny four-step method
2. mediation package based on the potential outcomes framework
```

The potential-outcomes-based mediation model estimated:

```text
ACME = Average Causal Mediation Effect
ADE = Average Direct Effect
Total Effect
Proportion Mediated
```

### 9.3 Main Finding

Among the selected predictors, only platelet count showed a statistically significant mediation effect.

Summary:

```text
Mediator = Platelet Count (Plt)
Proportion mediated ≈ 18.24%
Interpretation = part of age's association with MoCA was indirectly transmitted through Plt
```

Additional notes:

```text
Plt, GluAC, and TCHO were associated with both age and MoCA.
However, only Plt yielded a significant ACME.
```

Risk-aware interpretation:

> Platelet count may be a meaningful intermediate physiological marker in the age–cognition relationship, but this does not prove causality because the study is cross-sectional.

---

## 10. Robustness Analysis | 穩健性分析

The thesis used two additional methods to check whether key predictors remained relevant across modeling frameworks.

```text
1. Lasso regression
2. Neural network with SHAP
```

### 10.1 Lasso Regression

Lasso regression was used as a linear robustness check.

Why Lasso was useful:

```text
adds L1 regularization
shrinks unstable coefficients toward zero
performs variable selection
reduces overfitting risk
supports comparison with best subset regression
```

Implementation summary:

```text
R package = glmnet
training/testing split = 80% / 20%
LOOCV used within training set
λmin selected by minimizing cross-validated MSE
final model refit using full dataset
```

Portfolio interpretation:

> Lasso helped test whether predictors selected by best subset regression were stable under regularized linear modeling.

### 10.2 Neural Network with SHAP

A neural network was used to explore nonlinear relationships between predictors and MoCA.

The model was interpreted using SHAP.

Implementation summary:

```text
Python
PyTorch
Skorch
Scikit-learn
SHAP
one-hidden-layer feedforward neural network
GridSearchCV with LOOCV
ReLU / tanh activation functions
early stopping
DeepSHAP interpretation
```

Why this was useful:

```text
captures nonlinear relationships
provides feature importance using SHAP
compares nonlinear evidence with linear model findings
supports model interpretability
```

### 10.3 Predictor Stability Across Models

Across best subset regression, Lasso regression, and neural network with SHAP:

```text
Platelet count was consistently identified as a robust predictor.
Total body water demonstrated predictive value, although its selection was less consistent across models.
```

Portfolio interpretation:

> The most reliable signal is not merely the predictor selected by one model, but the predictor that remains meaningful across different modeling assumptions.

This idea directly connects to risk-aware AI:

```text
single-model finding
→ weaker evidence

multi-model agreement
→ stronger screening signal

model disagreement
→ higher uncertainty / needs review
```

---

## 11. Main Predictors | 主要預測因子整理

### 11.1 Total Body Water (TBW)

TBW was positively associated with MoCA in the best subset regression model.

Clinical interpretation:

```text
TBW may reflect hydration status
hydration may relate to cerebral perfusion
hydration may support metabolic balance
hydration imbalance may increase cognitive vulnerability
```

Portfolio framing:

> TBW is a routinely measurable physiological signal that may support low-burden cognitive-risk screening.

### 11.2 Platelet Count (Plt)

Platelet count was positively associated with MoCA and showed the strongest cross-model robustness.

Clinical interpretation:

```text
Plt may reflect inflammation-related or microcirculatory processes
platelet-related pathways may affect cerebral oxygen and nutrient delivery
Plt partially mediated the age–MoCA relationship
```

Portfolio framing:

> Platelet count is the strongest tabular modeling signal in this thesis because it appeared in best subset regression, mediation analysis, Lasso / SHAP robustness checks, and clinical interpretation.

### 11.3 Age

Age was negatively associated with MoCA.

Portfolio framing:

> Age is important as a distal risk factor, but it is not modifiable. The modeling goal is to identify intermediate physiological indicators that may help stratify risk or guide follow-up.

### 11.4 Multimorbidity

Multimorbidity showed a dose-response-like association with cognitive risk.

Portfolio framing:

> Cognitive vulnerability in chronic disease populations is likely cumulative and multifactorial, so a risk-aware AI system should consider disease burden rather than only isolated diagnoses.

---

## 12. Clinical Interpretation | 臨床解讀

The findings suggest that cognitive function in chronic disease patients may be associated with multiple physiological domains:

```text
hydration status
microcirculatory function
systemic inflammation
multimorbidity burden
age-related physiological vulnerability
```

The most clinically useful interpretation is:

> TBW and platelet count are not diagnostic biomarkers by themselves, but they may serve as scalable, routinely available indicators for early cognitive-risk screening.

Possible clinical workflow:

```text
routine clinical measurements
→ model estimates cognitive-risk signal
→ uncertainty and model agreement are checked
→ high-risk or high-uncertainty cases are flagged
→ clinician decides whether formal MoCA or follow-up is needed
```

This supports the portfolio's larger theme:

```text
prediction
+ interpretability
+ uncertainty
+ human-in-the-loop triage
```

---

## 13. AI / ML Engineering Interpretation | AI/ML 工程角度整理

This tabular model can be translated into an AI/ML engineering module as:

```text
src/modeling/tabular_moca_prediction.py
```

Potential inputs:

```text
Age
Sex
TBW
Plt
FFM
GluAC
TCHO
HDL
Hb
WHO-5
Conscientiousness
other selected clinical indicators
```

Potential outputs:

```json
{
  "predicted_moca": 23.8,
  "risk_class": "medium",
  "key_predictors": ["lower TBW", "lower Plt", "older age"],
  "model_agreement": "moderate",
  "clinical_note": "Screening signal only; not a diagnosis."
}
```

Engineering modules connected to this report:

```text
src/modeling/tabular_moca_prediction.py
src/risk_triage/cognitive_risk_score.py
src/risk_triage/uncertainty_score.py
src/evaluation/model_agreement_check.py
src/evaluation/error_analysis.py
```

---

## 14. Limitations | 限制

The thesis explicitly requires cautious interpretation.

### 14.1 Cross-Sectional Design

The study is cross-sectional, so temporal relationships cannot be established.

Implication:

```text
association ≠ causation
prediction ≠ mechanism proof
mediation result ≠ confirmed causal pathway
```

### 14.2 Modest Sample Size

The sample size was 110 participants, with 106 valid cases for the main regression model after preprocessing.

Implication:

```text
limited generalizability
limited subgroup analysis
possible instability in model selection
external validation required
```

### 14.3 Residual Confounding

Even though major confounders were considered, unmeasured factors may still influence the results.

Examples:

```text
genetic predisposition
early-life exposures
unmeasured lifestyle factors
medication complexity
measurement variation
```

### 14.4 Not a Diagnostic Model

The model identifies predictive associations, not definitive clinical diagnoses.

Safe interpretation:

```text
screening signal
risk stratification support
hypothesis generation
clinician-reviewed triage
```

Unsafe interpretation:

```text
AI diagnosis
confirmed causal biomarker
replacement for formal MoCA
production medical device
```

### 14.5 Need for Longitudinal and Interventional Validation

Future research should test:

```text
whether TBW and Plt predict future cognitive decline
whether modifying hydration or inflammation changes cognitive outcomes
whether model performance generalizes to external cohorts
whether risk alerts improve clinical workflow
```

---

## 15. Portfolio Takeaway | 作品集總結

> The tabular model identified total body water and platelet count as the most clinically meaningful physiological predictors of MoCA scores in chronic disease patients. Best subset regression explained approximately 38% of MoCA variance, platelet count partially mediated the age–cognition relationship, and robustness analyses using Lasso and SHAP-supported neural networks reinforced platelet count as a stable predictor. For the portfolio, these results support a risk-aware cognitive screening pipeline that uses routinely available clinical indicators to generate interpretable, uncertainty-aware, clinician-reviewed risk signals.

中文版本：

> 這份 tabular modeling 的核心發現是：在慢性病患者中，身體總水量與血小板數量是最具臨床解釋性的 MoCA 認知功能預測因子。最佳子集迴歸可解釋約 38% 的 MoCA 變異，血小板數量部分中介年齡與認知功能的關係，而 Lasso 與 SHAP neural network 的穩健性分析也支持血小板數量是跨模型穩定的預測因子。放在作品集裡，這些結果可以支撐一個利用常規臨床指標進行認知風險早期篩檢、不確定性評估與臨床人員審核分流的 AI pipeline。

---


