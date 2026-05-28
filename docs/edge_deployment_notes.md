# Edge Deployment Notes

## Edge Deployment Notes | Camera / Edge Device 未來部署筆記

This document describes a possible future edge-deployment direction for the **Risk-Aware Clinical AI Screening System for Cognitive Function** project.

The purpose is to explain how this project could eventually move from offline research modeling toward a camera-based, on-device inference workflow.

This is a **future deployment direction**, not an implemented production system.

```text
Current status:
concept note only

Not yet implemented:
production camera pipeline
real-time clinical inference
medical-device validation
edge model optimization
hospital workflow integration
```

---

## 1. Why Edge Deployment Matters

The original research motivation was to reduce the burden of manual clinical screening by exploring whether facial or tongue images could support early warning signals for chronic-disease and cognitive-risk screening.

A future edge-deployment direction is meaningful because the system vision is naturally camera-based:

```text
camera / mobile app
→ standardized face or tongue photo capture
→ local image preprocessing
→ model inference
→ risk-aware output
→ clinician-reviewed triage
```

Edge deployment may be useful for:

```text
1. reducing latency;
2. allowing inference near the camera;
3. supporting mobile-health or telemedicine scenarios;
4. reducing the need to upload raw images to a server;
5. improving privacy by keeping sensitive images local;
6. enabling real-time feedback on image quality, lighting, and crop validity.
```

However, in a clinical context, edge deployment should not mean automatic diagnosis. The safer framing is:

```text
edge device
→ screening support
→ quality check
→ risk signal
→ human-in-the-loop clinical review
```

---

## 2. Possible Device: Jetson Nano

A possible future device is the NVIDIA Jetson Nano or Jetson Orin Nano.

The Jetson course material introduces a workflow for:

```text
setting up Jetson Nano / Jetson Orin Nano
using camera input
running JupyterLab on the device
training image-classification models
training image-regression models
running inference on a live camera feed
```

The course outline includes three major sections:

```text
1. Setting Up Your Jetson Nano / Jetson Orin
2. Image Classification
3. Image Regression
```

This is relevant to this project because the clinical AI prototype also depends on image input and model inference.

Potential device role:

```text
Jetson Nano / Orin Nano
→ local camera input
→ image preprocessing
→ image-quality check
→ image feature extraction
→ physiological target prediction
→ risk-aware triage output
```

Portfolio framing:

> Jetson Nano is a possible future edge-computing platform for testing camera-based inference, not a completed deployment target in the current repository.

---

## 3. Existing Image Acquisition Foundation

The existing image-acquisition design already supports a camera-based workflow.

The Flutter Photo App README describes a photo app demo with the following functions:

```text
1. input subject ID;
2. capture five photo types;
3. save captured photos to device;
4. include light sensor value in the photo name.
```

The five photo types are:

```text
on the tongue / 舌上
under the tongue / 舌下
frontal face / 正臉
45-degree left profile / 45 度左側臉
45-degree right profile / 45 度右側臉
```

This is useful for future deployment because it already defines:

```text
standardized photo categories
subject-level image organization
local image capture
lighting metadata through filename
```

In the current portfolio repository, this connects to:

```text
src/image_preprocessing/
├── face_crop_quality_check.py
├── tongue_image_preprocessing.py
└── lighting_metadata_parser.py
```

---

## 4. Camera-Based Inference Workflow

A future camera-based inference workflow could look like:

```text
Step 1. Capture image
    mobile app or Jetson-connected camera captures face / tongue image

Step 2. Parse metadata
    subject ID, image type, and light sensor value are parsed from filename

Step 3. Quality check
    lighting, blur, crop validity, and image type are checked

Step 4. Preprocess image
    face or tongue region is cropped and resized

Step 5. Run image model
    image feature extractor or CNN runs locally

Step 6. Predict physiological target
    model estimates intermediate physiological signals, such as TBW

Step 7. Combine with tabular model
    physiological signal feeds into cognitive-risk screening logic

Step 8. Estimate uncertainty
    image quality, model agreement, and near-threshold risk are used to score uncertainty

Step 9. Output triage recommendation
    system returns screening signal and clinician-review recommendation
```

A safer edge inference output should look like:

```json
{
  "image_id": "synthetic_tongue_001",
  "image_type": "supralingual",
  "lighting_quality_flag": "ok",
  "image_quality_flag": "usable",
  "predicted_physiological_signal": {
    "TBW": 0.62
  },
  "risk_output": {
    "cognitive_risk_class": "medium",
    "uncertainty_level": "high",
    "triage_action": "clinician_review_required"
  },
  "clinical_note": "Screening signal only; not a diagnosis."
}
```

The output should not look like:

```json
{
  "diagnosis": "cognitive impairment"
}
```

---

## 5. Image Classification and Image Regression Tasks

The Jetson course material distinguishes image classification and image regression.

This distinction maps naturally to this clinical AI project.

---

### 5.1 Image Classification

Image classification predicts a discrete category.

Examples in a public demo:

```text
image quality pass / fail
tongue image type classification
face view classification
usable vs. unusable image
high vs. low uncertainty image
```

Possible clinical-research classification tasks:

```text
insomnia risk class
chronic disease indicator class
screening category
```

The tongue-image exploratory analysis reported:

```text
SVM best accuracy: Insomnia = 0.95
```

Safe interpretation:

> This is an exploratory image-to-physiology classification result, not a validated diagnostic claim.

---

### 5.2 Image Regression

Image regression predicts a continuous value.

Examples:

```text
TBW estimate
physiological marker estimate
image-quality score
crop-coordinate regression
lighting-adjusted correction value
```

The tongue-image exploratory analysis reported:

```text
SVR best correlation: TBW = 0.636
```

This is especially relevant because the tabular MoCA model identified TBW as a meaningful physiological predictor of cognitive function.

Potential future chain:

```text
tongue image
→ TBW prediction
→ cognitive-risk screening signal
→ uncertainty-aware triage
```

Safe interpretation:

> Image regression may help estimate intermediate physiological signals, but it requires validation before clinical use.

---

## 6. Model Compression Considerations

Edge deployment usually requires smaller and faster models than offline research modeling.

Possible model-compression considerations:

```text
1. reduce input image resolution when clinically acceptable;
2. use lightweight CNN or MobileNet-style backbones;
3. export models to ONNX or TensorRT-compatible formats;
4. apply quantization if accuracy remains acceptable;
5. benchmark inference latency on the target device;
6. measure memory usage and thermal stability;
7. compare edge output with offline reference output;
8. preserve uncertainty and quality-check logic even after compression.
```

Important safety principle:

> Compression should not only be evaluated by speed. It should also be evaluated by prediction stability, calibration, subgroup performance, and error behavior.

For this project, a compressed model should still output:

```text
prediction
uncertainty
quality flags
clinical caution note
```

not just a raw class label or score.

---

## 7. Privacy Benefit: Local Inference

Clinical face and tongue images are sensitive.

A major benefit of edge deployment is that raw images may remain on the local device.

Potential privacy benefits:

```text
raw images do not need to be uploaded by default;
only derived features or risk summaries may be exported;
image quality can be checked locally;
lighting and crop metadata can be stored without sharing raw images;
clinicians may review only flagged cases;
data minimization becomes easier.
```

A privacy-aware deployment design could separate:

```text
local device:
    raw image
    crop
    quality check
    local inference

server or research database:
    de-identified features
    prediction summary
    uncertainty flags
    audit logs
```

However, privacy requires implementation details beyond local inference.

Additional requirements would include:

```text
encryption
access control
audit logging
consent management
data retention policy
de-identification protocol
hospital IRB / governance review
```

---

## 8. Edge Deployment Architecture Concept

A possible future architecture:

```text
Camera / Mobile App
        │
        ▼
Image Capture Layer
        │
        ├── subject ID format check
        ├── image type check
        └── light sensor metadata capture
        │
        ▼
Edge Preprocessing Layer
        │
        ├── face crop quality check
        ├── tongue preprocessing
        ├── lighting metadata parser
        └── image-quality flags
        │
        ▼
Edge Model Layer
        │
        ├── image feature extractor
        ├── image classification model
        └── image regression model
        │
        ▼
Risk-Aware Layer
        │
        ├── cognitive risk score
        ├── uncertainty score
        ├── clinical triage rule
        └── causal caution note
        │
        ▼
Clinician / Research Interface
        │
        ├── screening summary
        ├── quality warnings
        ├── uncertainty explanation
        └── recommendation for review / follow-up
```

---

## 9. Suggested Repository Mapping

Current or future files connected to edge deployment:

```text
docs/
├── edge_deployment_notes.md
├── uncertainty_triage_policy.md
└── ethics_privacy_and_limitations.md

src/image_preprocessing/
├── face_crop_quality_check.py
├── tongue_image_preprocessing.py
└── lighting_metadata_parser.py

src/modeling/
├── image_feature_extraction.py
└── physiological_target_prediction.py

src/risk_triage/
├── cognitive_risk_score.py
├── uncertainty_score.py
└── clinical_triage_rule.py

demo/
├── screenshots/
└── demo_video_link.md
```

Potential future files:

```text
deployment/
├── jetson_setup_notes.md
├── camera_inference_demo.py
├── edge_inference_config.yaml
├── model_export_onnx.md
└── latency_benchmark_template.md
```

---

## 10. Minimum Viable Edge Demo

A minimum viable public demo could be implemented without clinical data.

### 10.1 Input

```text
synthetic or sample non-clinical image
mock filename with light sensor value
mock trained model
```

Example filename:

```text
synthetic_001_supralingual_light312.4.jpg
```

### 10.2 Demo Flow

```text
1. parse filename metadata;
2. preprocess image to [3 x 128 x 128];
3. run mock image feature extractor;
4. run mock physiological target prediction;
5. attach uncertainty flags from image quality;
6. output JSON risk-screening summary.
```

### 10.3 Demo Output

```json
{
  "image_id": "synthetic_001_supralingual_light312.4",
  "device": "future_edge_demo",
  "light_sensor_value": 312.4,
  "image_quality_flag": "usable",
  "model_output": {
    "predicted_TBW_signal": 0.62
  },
  "uncertainty": {
    "level": "medium",
    "reason": ["edge demo only", "mock model"]
  },
  "triage": {
    "action": "clinician_review_required"
  },
  "status": "concept_demo_only"
}
```

---

## 11. Current Status

This document is intentionally honest about the project status.

Implemented in the portfolio repository:

```text
documentation of edge deployment direction
image preprocessing utilities
lighting metadata parser
risk-aware triage policy
synthetic / mock model interfaces
```

Not implemented yet:

```text
Jetson Nano deployment
real-time camera inference
TensorRT / ONNX model export
latency benchmark
production mobile app integration
clinical validation
medical device compliance
hospital workflow integration
```

Current status statement:

> This is a future deployment direction, not an implemented production system.

---

## 12. Risks and Limitations

### 12.1 Technical Risks

```text
camera hardware differences
lighting variation
motion blur
crop failure
thermal throttling on edge device
model drift
latency constraints
limited memory
edge/offline model mismatch
```

### 12.2 Clinical Risks

```text
false reassurance
false alarm burden
overconfidence in image-derived signals
lack of external validation
insufficient subgroup testing
unclear clinical action pathway
```

### 12.3 Privacy and Governance Risks

```text
raw image storage risk
face-image identifiability
consent limitations
device loss
insecure local storage
unclear retention policy
```

### 12.4 Mitigation Direction

```text
do not store raw images unless required;
use local inference where possible;
log image-quality flags;
route high-uncertainty cases to clinician review;
validate with synthetic data before de-identified data;
perform external validation before any real clinical workflow use.
```

---

## 13. Portfolio Takeaway

> Edge deployment is a future direction for turning this project into a camera-based AI screening workflow. Jetson Nano or Jetson Orin Nano could support local camera input, image classification, image regression, and live inference. The existing Flutter photo app design already supports standardized face and tongue photo capture with light sensor metadata. However, the current project has not implemented production edge deployment. The correct portfolio framing is that this document proposes how future local inference could improve latency, privacy, and image-quality feedback while preserving uncertainty-aware, human-in-the-loop clinical triage.

中文版本：

> Edge deployment 是這個專案未來從研究模型走向 camera-based AI screening workflow 的延伸方向。Jetson Nano / Jetson Orin Nano 可以作為未來本地端 camera input、image classification、image regression 與 live inference 的測試平台；而既有 Flutter photo app 已經具備標準化臉部與舌頭拍照、subject ID 與 light sensor metadata 的資料蒐集基礎。不過，目前尚未完成 production edge deployment，因此作品集應誠實定位為 future deployment concept note，而不是已上線的臨床系統。

---

