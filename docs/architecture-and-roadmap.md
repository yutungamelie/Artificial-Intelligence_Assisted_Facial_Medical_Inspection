# Architecture and development roadmap

[Project overview](../README.md) · [繁體中文](../README.zh-TW.md) · [Research evidence](research-evidence.md)

This document describes the proposed application and its acceptance criteria. Milestones below are planned work, not completed features or a claim of clinical readiness.

## Target: two stages, three predictive models

Given a tongue image I, the intended prediction stack is:

```text
Model A: tbw_estimate = f_tbw(I)
Model B: plt_estimate = f_plt(I)
Model C: moca_estimate = g(tbw_estimate, plt_estimate)
```

Models A and B are separate target predictors. They can initially use the same image features; sharing a learned encoder later is an experimental choice, not an implemented architecture. Model C must be trained and evaluated for its two-input task; neither the thesis's 13-feature regression nor its 38-feature MLP can be reused by simply dropping the remaining inputs.

The desired inference input can be image-only, but training and evaluation require matched tongue images, measured TBW, measured Plt, and observed MoCA. Verify participant identifiers, measurement timing, and units. If a later model also needs age or other clinical inputs at inference, name and evaluate that version separately.

### Relationship to current modules

| Proposed component | Current foundation | Missing work |
| --- | --- | --- |
| Quality gate and image preparation | [Tongue preprocessing](../src/image_preprocessing/tongue_image_preprocessing.py), [lighting metadata](../src/image_preprocessing/lighting_metadata_parser.py), and separate [face checks](../src/image_preprocessing/face_crop_quality_check.py). | Validate tongue-specific quality criteria against reviewed images; test device and lighting variation. |
| Image representation | [PCA/IncrementalPCA mock encoders](../src/modeling/image_feature_extraction.py). | Supply and validate a real image representation for physiological prediction; original autoencoder code/weights are not included. |
| TBW and Plt estimators | [Generic physiological target modeling](../src/modeling/physiological_target_prediction.py). | Fit the two target models, record their errors, and export their complete preprocessing/model artifacts. |
| Two-input MoCA model | [Tabular regression utilities](../src/modeling/tabular_moca_prediction.py). | Establish the measured-value baseline and train/evaluate the image-estimate stack. |
| Reliability and review | [Evaluation](../src/evaluation) and [review-prioritization](../src/review_prioritization) modules. | Propagate both image-model errors; validate uncertainty and review behavior, including missing/invalid inputs. |
| API, agent, and edge runtime | Architectural proposal only. | Implement and benchmark after the reference model pipeline is reliable. |

## Causal research: a new model, not a relabeled prediction graph

The proposed research question is whether TBW and Plt have a defensible role in mechanisms related to cognition, and whether tongue-image estimates provide useful measurements of those variables. The thesis's age-mediation analysis motivates questions but does not identify the causal effects of this new system.

Keep three kinds of variables distinct:

| Variable type | Examples | Role |
| --- | --- | --- |
| Underlying/measured physiology | TBW, Plt | Candidate physiological variables in the biological model. |
| Image observations and estimates | Tongue features, estimated TBW/Plt | Measurements/proxies and computational outputs; they are not automatically equivalent to true physiology. |
| Candidate common causes and acquisition factors | Age, body composition, disease history, other justified covariates; camera/lighting | Potential sources of shared variation or measurement error, with roles decided from a causal graph and timing information. |

The initial causal work should compare plausible mechanisms, including a model where shared health factors explain biomarker–MoCA associations without direct biomarker effects. Do not add an arrow from TBW or Plt to cognition solely because it improves prediction. Do not interpret the image-to-biomarker prediction direction as evidence that an image causes a biological change.

Before estimating effects, specify:

1. The causal estimand and a meaningful exposure/intervention contrast, rather than only the prediction target.
2. A candidate DAG with timing and common causes; distinguish measured covariates from possible unmeasured causes.
3. The assumptions required for identification, and which remain unsupported by the small cross-sectional dataset.
4. The measurement-error model linking estimated and measured biomarkers. Errors from the same tongue image may be correlated.
5. Sensitivity analyses and, where feasible, longitudinal or additional data needed to discriminate competing mechanisms.

A structural equation or Bayesian joint model is a candidate implementation after those decisions. Model fit or a significant coefficient alone does not verify a causal direction. A prediction stack can still be evaluated when a causal effect is not identifiable. See [Pearl's overview](https://ftp.cs.ucla.edu/pub/stat_ser/r350.pdf) and [causal mediation methodology](https://imai.fas.harvard.edu/research/files/BaronKenny.pdf).

The biological intermediate representation is related to [concept bottleneck models](https://proceedings.mlr.press/v119/koh20a.html). Replacing an estimated biomarker with a measured value tests a **correction to the model's information**. It does not estimate the effect of changing that biomarker in a person.

## Milestone 0 — Reproducible reference modules

Acceptance: a documented environment can run a small synthetic demonstration, and failures or training-only results cannot be mistaken for held-out performance.

- [ ] Add explicit dependencies, synthetic fixtures, and one documented entry point.
- [ ] Fix the literal "numeric" column selector in the tabular module's ColumnTransformer; it currently names a column rather than selecting all numeric columns.
- [ ] Remove or explicitly label fallback training metrics when cross-validation fails in tabular/physiological modeling. Do not silently substitute them for validation results.
- [ ] Align metric calls with the selected scikit-learn version, including RMSE calculation.
- [ ] Require validated participant/image joins. The current physiological-target helper can align by row order when identifiers are absent; the integrated pipeline must not rely on that fallback.
- [ ] Define and test behavior for missing fields, invalid numeric values, unknown review states, and unusable images.
- [ ] Resolve research-script/model-export inconsistencies described in the [evidence notes](research-evidence.md#research-script-consistency) in the companion research workflow.

## Milestone 1 — Measured-biomarker baseline and image prediction stack

Acceptance: the new system has a participant-level evaluation report with original-scale outcomes, explicit denominators, and separately evaluated TBW/Plt predictions.

| Experiment | Purpose |
| --- | --- |
| Measured TBW + measured Plt → MoCA | Establish the two-biomarker reference model. This is a benchmark, not a guaranteed upper bound. |
| Estimated TBW + estimated Plt → MoCA | Evaluate the intended image-derived bottleneck. |
| Estimated TBW only / estimated Plt only → MoCA | Measure the incremental value of each predicted biomarker. |
| Tongue image/features → MoCA | Compare predictive performance with a direct-image route. |
| Simple reference such as mean prediction or age-only prediction | Check whether the proposed model adds value beyond simple alternatives. |

- [ ] Group all images/views from the same participant in the same outer split.
- [ ] Fit preprocessing, learned image features, feature selection, and hyperparameter tuning using only training data within each outer evaluation split.
- [ ] For the prediction stack, generate out-of-fold TBW/Plt estimates inside the outer training data to train Model C; refit the upstream models on the outer training data and evaluate the whole pipeline on untouched outer participants.
- [ ] Keep biological causal-effect estimation distinct from stacking on predicted values; account for measurement error when interpreting physiological effects.
- [ ] Report TBW/Plt MAE, RMSE, bias, and units; report MoCA MAE/RMSE in raw score points. Record missing-data exclusions and sample counts for every version.
- [ ] Assess joint upstream error and interval coverage/width if uncertainty intervals are produced. A bootstrap of only the final regression does not cover the whole cascade automatically.
- [ ] If reporting sensitivity/specificity, predeclare the reference label and threshold. Separate observed-MoCA grouping from disease diagnosis.

## Milestone 2 — Versioned model delivery and inference API

Acceptance: a new synthetic case can be processed by loading saved models without retraining, with predictable input validation and traceable outputs.

- [ ] Save weights/coefficients, feature names and order, units, preprocessing parameters, target mean/standard deviation, model version, and environment metadata.
- [ ] Restore standardized MoCA outputs to the original score scale before applying original-scale rules; verify agreement with the research implementation on fixed cases.
- [ ] Load models once at service startup. Separate training, bootstrap refitting, and global SHAP analysis from routine prediction requests.
- [ ] Define a typed input/output contract and implement a small inference API, for example with FastAPI. No API exists in this repository yet.
- [ ] Return biomarker estimates and their source, predicted MoCA, model version, data-quality flags, and the reason for any requested review. Do not manufacture an interval or a calibrated probability when one is unavailable.

## Milestone 3 — Edge-device benchmark

Acceptance: the same inference contract works on a named device, and the performance report states what was timed and whether model outputs remained consistent.

- [ ] Establish a desktop CPU baseline before choosing optimizations.
- [ ] Run on available Jetson hardware with a compatible ARM64 dependency stack; record device, memory, power mode, software versions, and input shape.
- [ ] Measure startup time, preprocessing, each biomarker model, downstream MoCA prediction, and total request time; report P50/P95, peak memory, failures, sample count, and warm-up policy.
- [ ] Check desktop/device prediction agreement using fixed test inputs and a declared tolerance.
- [ ] Compare ONNX/TensorRT or precision changes only if a measured bottleneck warrants them; recheck output agreement and evaluation quality after conversion.

For hardware planning, the original Jetson Nano's JetPack 4 stack is EOL; check the [NVIDIA support FAQ](https://developer.nvidia.com/embedded/faq) before selecting dependencies or new hardware. Agent execution may remain on a desktop/internal server while image processing and predictive models run on the edge.

## Milestone 4 — Agent-assisted workflow

Acceptance: scripted cases demonstrate correct tool use, faithful summaries, and explicit handling of failed or incomplete inputs.

- [ ] Begin with a controlled tool workflow, for example using LangGraph, after the inference API is stable.
- [ ] Expose tools for input/quality validation, prediction, explanation retrieval, and requesting review. Compute scores and review rules in typed application code.
- [ ] Preserve the source of each biomarker: image estimate or measured value. If a measured value becomes available, record the correction and recompute the prediction.
- [ ] Test missing inputs, low-quality images, model/API errors, boundary cases, and correction of estimated biomarkers.
- [ ] Report workflow-case counts, expected routing agreement, tool-call success, numeric fidelity, and end-to-end latency. Count failures as well as successful runs.
- [ ] Keep summaries of causal hypotheses explicit about their assumptions; changing a model input is not evidence of a treatment effect.

## Repository responsibilities

| Repository | Intended responsibility |
| --- | --- |
| [multimodal-cognition-repro-2025](https://github.com/yutungamelie/multimodal-cognition-repro-2025) | Research preprocessing, training, statistical/causal analysis, evaluation, and controlled export of authorized model artifacts. Access may be restricted. |
| This repository | Public documentation and reconstruction; future synthetic demonstration, model interfaces, application integration, agent workflow, and edge benchmarks. |

Only publish performance claims after the corresponding evaluation report is available. Synthetic demonstrations can establish engineering behavior, but their metrics do not establish clinical performance.
