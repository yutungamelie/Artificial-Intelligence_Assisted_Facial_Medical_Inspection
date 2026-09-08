# Research evidence and interpretation

[Project overview](../README.md) · [繁體中文](../README.zh-TW.md) · [Architecture and roadmap](architecture-and-roadmap.md)

This page distinguishes original research results from the public reconstruction and the proposed tongue-image → TBW/Plt → MoCA system. Reported results have not been reproduced by running the public code against the original clinical dataset.

## Primary research source

Yu-Tung Ke. *Physiological Predictors of Cognitive Functions in Patients with Chronic Diseases*. Master's thesis, National Taiwan University, 2025. [DOI: 10.6342/NTU202503365](https://doi.org/10.6342/NTU202503365).

The thesis is a tabular-modeling branch of **Artificial Intelligence-Assisted Facial Medical Inspection**, not an alternative title for the full project. Page references below use the thesis's printed page numbers, not the PDF viewer's page index.

Research scripts were reviewed separately from this public repository. Relevant files are the normalization script, Table 4.2 best-subset script, Figures 4.6–4.7 Lasso script, Figures 4.8–4.9 PyTorch/SHAP script, and Tables 4.4–4.5 mediation script in the companion research materials. The scripts, clinical CSVs, and trained artifacts are not redistributed here.

## Evidence ledger

| Item | Reported result or verified implementation detail | Interpretation |
| --- | --- | --- |
| Cohort | 110 participants recruited; 106 complete cases retained for thesis modeling. | Keep recruitment and analysis denominators separate. |
| Acquisition scope | Figure 3.1, p. 12: physiological measurements, interviews/records, questionnaires, and imaging; facial acquisition includes three views and tongue acquisition includes upper/lower surfaces. | An acquisition protocol, not evidence that all imaging modalities entered the MoCA model or that a five-view quality gate has been validated. |
| Best subset model | Table 4.2, p. 47: 13 predictors, R² = 0.4528, adjusted R² = 0.3763. | In-sample fit after variable selection. Not held-out predictive accuracy, a percentage improvement over other studies, or the performance of a TBW/Plt-only model. |
| Neural-network architecture | Section 4.4.2, p. 55 and reviewed Python code: a single 32-unit hidden layer with Tanh, learning rate 0.0001; the supplied preprocessing selects 38 predictors plus the MoCA target. | A small tabular MLP. The derived 38 → 32 → 1 architecture has 1,281 trainable parameters, including biases; this is an architecture calculation, not a device-memory benchmark. |
| Neural-network error | Section 4.4.2, p. 55: selected LOOCV MSE 0.5296; SVR 0.9339; KNN 1.1283. | Historical thesis-reported results on standardized MoCA. They are not errors in raw MoCA points and are not an independently nested assessment of the selected model. |
| Final neural-network fit | Section 4.4.2, p. 55: R² = 0.4751. The script fits and scores the final model on the complete dataset. | Training fit, not evidence of generalization to new participants. |
| Plt | Sections 4.4.1–4.4.3, pp. 51–60: appears in best-subset and final Lasso selections and among prominent neural-network SHAP features. | A recurring predictive signal; this does not establish that a tongue image can accurately measure Plt. |
| TBW | Sections 4.4.2–4.4.3, pp. 55–60: selected in best subset regression and prominent in SHAP, but excluded from the final Lasso selection. | Do not describe TBW as retained in every final model. |
| Mediation | Tables 4.4–4.5, p. 50: the fitted age–Plt–MoCA analysis reports a significant estimated indirect effect and an estimated mediated proportion of 18.24%. TBW's estimated proportion is 1.02%, with no significant indirect effect reported. | Exploratory, assumption-dependent findings. Neither proves a biological causal pathway or an intervention benefit. |
| Historical tongue-image experiment | The earlier repository overview reports an SVR correlation of 0.636 for image-derived TBW prediction. | This is a previously reported exploratory result, not a benchmark reproduced here. The original split protocol, raw predictions, encoder weights, and corresponding image-to-Plt evaluation are not included in this repository. |
| New integrated system | No benchmark yet. | Separate image-to-TBW, image-to-Plt, and downstream MoCA evaluation is required. No inherited R², risk accuracy, causal effect, or deployment latency is assigned to it. |

The historical image claim can be traced to the [previous README](https://github.com/yutungamelie/Risk-Aware_Clinical_AI_Screening_System_for_Cognitive_Function/blob/679a6987f3caeb3c9fb1321dec842ab1f319fa41/README.md). It is retained here as provenance rather than promoted as a validated application result.

## What the public code reconstructs

- The [tabular MoCA module](../src/modeling/tabular_moca_prediction.py) uses scikit-learn Lasso/Ridge/linear regression, not the exact thesis R models or saved PyTorch network.
- The [image feature module](../src/modeling/image_feature_extraction.py) uses PCA/IncrementalPCA as mock encoders. Its configured RGB-separate/joint dimensions do not establish the presence of trained autoencoders.
- The [physiological target module](../src/modeling/physiological_target_prediction.py) provides generic regression/classification code. It does not contain trained tongue-image TBW and Plt models or their end-to-end connection to MoCA.
- The [review modules](../src/review_prioritization) contain demonstration policies. A normalized risk score is not a calibrated probability of cognitive disease.
- The [bootstrap utility](../src/evaluation/bootstrap_ci.py) resamples training rows, refits a model, and summarizes fitted predictions. These intervals do not automatically include outcome noise or upstream image-model error, and their individual-outcome coverage has not been established.

## Reproducibility work before a new benchmark

The supplied research scripts and public reconstruction have different preprocessing, estimators, and execution assumptions. A new application benchmark must state which implementation it evaluates.

### Preprocessing and outcome scale

The research normalization script scales every selected column except Sex, including **MoCA**. Store the fitted feature transformations and target mean/standard deviation alongside the model. Restore the prediction before applying any rule expressed in original MoCA points:

```text
predicted_moca_raw = predicted_moca_z * saved_target_sd + saved_target_mean
```

Use the saved parameters consistently across R/Python and deployment. Do not silently refit a scaler on a new case or assume that two libraries use identical scaling conventions.

The reviewed scripts standardize the full dataset before splitting or cross-validation. For new performance estimates, fit preprocessing and feature selection within training folds; separate hyperparameter selection from outer evaluation. [scikit-learn's leakage guidance](https://scikit-learn.org/stable/common_pitfalls.html) explains the same principle.

### Research-script consistency

- The normalization script defines an output path for the scaled CSV but writes using a different path variable before that variable is defined in a clean session.
- The PyTorch script selects CUDA device 3 before checking availability, and contains a SHAP wrapper call before its inputs are initialized.
- The script saves the grid-search estimator, then trains a separate final model for SHAP. A release must identify the exact model used for exported weights, evaluation, and explanation.
- The Lasso script samples 90 training cases from 106 complete cases, while the thesis methods describe an 80/20 split. Resolve this discrepancy before claiming exact reproduction.

These are source-review findings, not newly executed clinical experiments. The original research files are maintained separately; this documentation update does not change them.

## How future results should be reported

| Question | Evidence to record |
| --- | --- |
| Can tongue images estimate each biomarker? | Participant-held-out MAE/RMSE and bias for TBW and Plt, with verified units, sample counts, and uncertainty. Correlation alone is insufficient to describe agreement. |
| Do both biomarkers help? | Measured-value baseline, image-estimate stack, single-biomarker ablations, and a direct-image comparator under the same outer participant splits. |
| Does the full system predict MoCA? | MAE/RMSE in original MoCA points; uncertainty-interval coverage and width if intervals are reported. |
| Does a score-based flag identify the chosen reference group? | Sensitivity/specificity against a predeclared reference, such as observed MoCA groups. Such a reference does not establish disease-diagnosis accuracy. |
| Is a causal interpretation supported? | A defined estimand, candidate DAG, identification assumptions, effect intervals, and sensitivity to common causes and measurement error. Prediction improvement alone is not causal evidence. |
| Is the application deployable? | Device/software configuration, cold/warm timing boundaries, request count, failures, P50/P95 latency, peak memory, and reference-output agreement. |

Future result tables should identify the cohort, split protocol, model version, dataset version, and whether the benchmark used synthetic or clinical data. Unmeasured results remain marked **not yet evaluated**.
