# Image-to-Physiology Findings

## 舌頭影像到生理指標預測結果整理 | Image-to-Physiology Findings

This report summarizes the tongue-image modeling findings for the **Risk-Aware Clinical AI Screening System for Cognitive Function** portfolio project.

The purpose of this report is to explain how tongue images were transformed into low-dimensional features, how two autoencoder designs were compared, how feature quality was inspected through reconstruction and visualization, and how the extracted features were used to predict physiological targets.

This report is a **portfolio reconstruction**. It does not release raw tongue images, patient-level data, or identifiable clinical information.

---

## 1. Goal | 目標

The goal of the tongue-image modeling route was:

```text
tongue image
→ low-dimensional image features
→ physiological target prediction
```

The project aimed to test whether tongue images can contain predictive signals related to physiological states.

More specifically, the modeling pipeline was designed to:

```text
1. compress tongue images into low-dimensional features;
2. preserve enough visual information for image reconstruction;
3. compare different RGB encoding strategies;
4. visualize extracted image-feature structure;
5. use image-derived features to predict physiological targets;
6. evaluate whether tongue images may provide useful screening signals.
```

Portfolio framing:

> This route does not claim that tongue images can diagnose disease. It explores whether standardized tongue images can be converted into useful image features that may predict measurable physiological indicators.

---

## 2. Clinical and Conceptual Motivation | 臨床與概念動機

The tongue-image route is motivated by the broader idea that visual inspection may contain health-related signals.

In traditional Chinese medicine, tongue appearance is often discussed in relation to internal physiological states. The slides specifically highlight the intuition:

```text
Tongue color → circulation
black / purple / white color patterns
```

From an AI / ML perspective, the question becomes:

> Can image features extracted from tongue photos capture visual patterns that are statistically associated with objective physiological measurements?

For this portfolio project, the safest interpretation is:

```text
tongue image
→ possible visual proxy for physiological state
→ exploratory predictive signal
→ not diagnostic evidence
```

---

## 3. Image Input and Preprocessing | 影像輸入與前處理

The modeling route used cropped tongue images as input.

The image input dimension was:

```text
[3 x 128 x 128]
```

This means:

```text
3 color channels: R / G / B
128 pixels height
128 pixels width
```

Conceptual preprocessing flow:

```text
raw tongue image
→ crop tongue region
→ resize to 128 x 128
→ normalize RGB image
→ feed image into autoencoder
→ extract latent features
```

The model should be sensitive to image preprocessing quality because tongue color and texture may be affected by:

```text
lighting
camera angle
crop quality
tongue position
background artifacts
manual vs automatic crop differences
```

Risk-aware note:

> If the image crop or lighting is unreliable, the extracted image features should be treated as less reliable and should increase downstream uncertainty.

---

## 4. Autoencoder Design | Autoencoder 設計

The project used an autoencoder to compress tongue images into lower-dimensional representations.

Conceptual structure:

```text
Input Tongue Image
→ Encoder
→ Low-Dimensional Latent Features
→ Shared Decoder
→ Reconstructed Tongue Image
```

The purpose of the autoencoder was:

```text
dimension reduction
feature extraction
reconstruction quality check
image representation learning
```

Why autoencoder was used:

```text
raw images are high-dimensional
sample size is limited
low-dimensional features are easier to use in downstream prediction
reconstruction checks help verify whether the latent features preserve visual information
```

Portfolio interpretation:

> The autoencoder serves as a bridge between raw clinical images and structured machine-learning models.

---

## 5. RGB-Separate vs. RGB-Joint Encoders | RGB 分離與 RGB 聯合 Encoder 比較

Two autoencoder feature-extraction routes were compared.

---

### 5.1 Route 1: RGB-Separate Encoders

Route 1 processed the R, G, and B channels separately.

Conceptual design:

```text
R channel → encoder → latent features
G channel → encoder → latent features
B channel → encoder → latent features
→ concatenate all channel-level features
```

Feature dimension:

```text
R / G / B encoders
10 dimensions for each channel
→ concatenated feature vector
```

The slides describe the final Route 1 representation as:

```text
RGB-Separate Encoders
R / G / B encoders → concatenate into 60-dimensional features
```

Interpretation:

> RGB-separate encoding allows each color channel to preserve its own structure before being combined into one feature vector.

This design is especially meaningful for tongue images because color differences may carry important information.

---

### 5.2 Route 2: RGB-Joint Encoder

Route 2 processed the full RGB image together.

Conceptual design:

```text
full RGB image
→ single encoder
→ 64-dimensional feature vector
```

Feature dimension:

```text
RGB-joint encoder
→ 64-dimensional features
```

Interpretation:

> RGB-joint encoding treats the image as one integrated color image and lets the model learn color-channel interactions directly.

---

### 5.3 Why Compare These Routes?

The comparison matters because different image representation strategies may preserve different signals.

```text
RGB-separate encoder
→ may preserve color-channel-specific information

RGB-joint encoder
→ may capture integrated image-level patterns

comparison
→ helps decide which representation is more useful for physiological prediction
```

Risk-aware interpretation:

> The better route should not be selected only by downstream prediction accuracy. It should also preserve image information, show interpretable feature structure, and behave robustly under preprocessing variation.

---

## 6. Reconstruction Check | 重建品質檢查

After encoding images into low-dimensional features, the decoder reconstructed the image.

The reconstruction check evaluated whether compressed features still preserved enough visual information.

### 6.1 Reconstruction MSE Results

The slide reports:

| Route | Encoder Design | Feature Representation | Reconstruction MSE |
|---|---|---:|---:|
| Route 1 | RGB-Separate Encoders | concatenated RGB-channel features | 0.000572 |
| Route 2 | RGB-Joint Encoder | full RGB 64d features | 0.001158 |

### 6.2 Interpretation

Lower reconstruction MSE means the compressed representation retained more information needed to reconstruct the original image.

In this comparison:

```text
Route 1 MSE = 0.000572
Route 2 MSE = 0.001158
```

Route 1 had lower reconstruction error.

Portfolio interpretation:

> RGB-separate encoding appeared to preserve tongue-image information better than the RGB-joint encoder in this exploratory setup.

Risk-aware caution:

> Reconstruction quality does not guarantee clinical usefulness. It only shows that the feature representation retains visual information. Downstream physiological prediction and validation are still required.

---

## 7. PCA / K-Means Visualization | PCA 與 K-Means 視覺化

After feature extraction, PCA and K-Means clustering were used to inspect the structure of the learned image features.

### 7.1 Visualization Method

The slides used:

```text
PCA visualization in 2D
K-Means clustering with k = 3
```

The purpose was to project high-dimensional image features into a 2D space and inspect whether clusters or patterns appeared.

### 7.2 Route Comparison

Both routes were visualized:

```text
Route 1: RGB-Separate Encoders
Route 2: RGB-Joint Encoder
```

The slides marked Route 1 as the preferred route.

Reasonable interpretation:

```text
Route 1 had better reconstruction MSE
Route 1 showed more interpretable or useful PCA / clustering structure
Route 1 was selected for downstream prediction
```

### 7.3 Image-Overlay PCA Visualization

The final slide shows a PCA visualization with tongue image thumbnails embedded in the 2D feature space.

This is useful because it allows visual inspection of whether neighboring points in feature space correspond to visually similar tongue images.

Portfolio interpretation:

> PCA with image thumbnails is a model-debugging tool. It helps check whether learned features reflect visible tongue-image variation rather than arbitrary numerical compression.

---

## 8. Predicting Physiological Targets | 生理指標預測

The extracted image features were used to predict approximately 90 physiological targets.

The targets included both:

```text
regression targets
classification targets
```

Examples of possible target types:

```text
body composition markers
blood markers
urine markers
sleep-related labels
physiological or chronic disease indicators
```

### 8.1 Classification Task

The slides report:

```text
SVM best accuracy: Insomnia = 0.95
```

Interpretation:

> Using tongue-image features, the best classification result was insomnia prediction with SVM accuracy of 0.95 in this exploratory analysis.

Risk-aware caution:

> A high accuracy in a pilot setting may be affected by sample size, class imbalance, preprocessing choices, or overfitting. It should be treated as a promising signal, not clinical validation.

### 8.2 Regression Task

The slides report:

```text
SVR best correlation: TBW = 0.636
```

Interpretation:

> The best regression result was total body water prediction, with SVR achieving a correlation of 0.636.

This result is especially relevant to the overall clinical AI portfolio because the tabular modeling route identified total body water as an important predictor of MoCA cognitive function.

Possible connection:

```text
tongue image
→ predicted TBW
→ cognitive-risk screening signal
```

Risk-aware caution:

> This bridge is a future hypothesis. It should not be presented as proof that tongue images can directly estimate cognitive function.

---

## 9. Relationship to Cognitive-Risk Modeling | 與認知風險建模的關係

The tongue-image route and the tabular MoCA route can be connected conceptually.

The tabular model found:

```text
TBW and platelet count
→ important physiological predictors of MoCA
```

The tongue-image model found:

```text
tongue image features
→ useful signal for predicting TBW
```

Together, this suggests a possible future modeling chain:

```text
Tongue Image
→ Image-Derived Physiological Signal
→ Cognitive-Risk Model
→ Uncertainty-Aware Review Prioritization
```

This is safer and more interpretable than:

```text
Tongue Image
→ Direct Cognitive Diagnosis
```

Portfolio interpretation:

> Tongue images may be useful as an upstream physiological-signal source, while tabular clinical models provide the more interpretable cognitive-risk layer.

---

## 10. Key Technical Observations and Design Implications | 關鍵技術觀察與設計意涵

### 10.1 Representation Matters

Different image encoders can produce different feature quality.

Lesson:

```text
RGB representation should be treated as a modeling decision,
not just an image-loading detail.
```

### 10.2 Reconstruction Is a Useful Sanity Check

Before using image features for downstream prediction, it is useful to check whether the autoencoder can reconstruct the original image.

Lesson:

```text
if the compressed feature cannot reconstruct the image,
it may not preserve enough information for prediction.
```

### 10.3 Visualization Helps Debug Image Features

PCA and K-Means visualization helped inspect whether the latent space had meaningful structure.

Lesson:

```text
visualization is not proof,
but it helps identify whether learned features behave plausibly.
```

### 10.4 Physiological Targets Are Better Intermediate Goals Than Direct Diagnosis

Predicting physiological targets from tongue images is more cautious than predicting disease or cognitive impairment directly.

Lesson:

```text
image → physiology → risk
is safer and more interpretable than
image → diagnosis.
```

### 10.5 Data Quality Is a Major Bottleneck

The slides explicitly list limitations:

```text
data quality
standardized photo specifications
data quantity
strict inclusion criteria for patient recruitment
```

Insight:

> Image modeling performance depends heavily on data acquisition and preprocessing quality.

---

## 11. Limitations | 限制

### 11.1 Data Quality

Tongue images can vary due to:

```text
lighting
camera device
tongue position
crop quality
patient movement
background artifacts
manual correction inconsistency
```

This affects feature extraction and prediction reliability.

### 11.2 Standardized Photo Specifications

The slides identify standardized photo specifications as a limitation.

Risk:

```text
without strict standardization,
the model may learn camera or lighting artifacts rather than physiological patterns.
```

### 11.3 Data Quantity

Pilot data may be too small to support strong clinical claims.

Risk:

```text
overfitting
unstable performance estimates
limited generalizability
class imbalance
```

### 11.4 Strict Inclusion Criteria

Strict inclusion criteria protect data quality and clinical safety, but they may reduce generalizability.

Risk:

```text
model may not generalize to broader patient populations.
```

### 11.5 No Diagnostic Claim

The reported SVM and SVR results should not be interpreted as clinical diagnostic performance.

Safe claim:

```text
exploratory image-derived signals may predict some physiological targets.
```

Unsafe claim:

```text
tongue image can diagnose insomnia or cognitive impairment.
```

---

## 12. Portfolio Engineering Interpretation | AI/ML 工程角度整理

This report maps to the following repository modules:

```text
src/modeling/
├── image_feature_extraction.py
└── physiological_target_prediction.py

src/image_preprocessing/
└── tongue_image_preprocessing.py

src/evaluation/
├── error_analysis.py
└── model_agreement_check.py
```

### 12.1 `image_feature_extraction.py`

Suggested responsibilities:

```text
load preprocessed tongue image tensor
run RGB-separate encoder mock pipeline
run RGB-joint encoder mock pipeline
return low-dimensional latent features
compare reconstruction MSE
```

### 12.2 `physiological_target_prediction.py`

Suggested responsibilities:

```text
load image-derived features
train or mock SVM / SVR models
predict physiological targets
report accuracy or correlation
return target-level performance summary
```

### 12.3 `error_analysis.py`

Suggested responsibilities:

```text
compare performance by crop quality
compare auto-crop vs manual-crop images
flag outlier feature points in PCA
inspect high-error physiological targets
```

---

## 13. Suggested Public Output Format | 建議公開輸出格式

A portfolio-safe example output could look like:

```json
{
  "image_id": "synthetic_tongue_001",
  "feature_extraction_route": "rgb_separate_encoder",
  "latent_dim": 60,
  "reconstruction_mse": 0.000572,
  "predicted_targets": {
    "TBW": {
      "task_type": "regression",
      "model": "SVR",
      "correlation": 0.636,
      "interpretation": "exploratory physiological signal"
    },
    "Insomnia": {
      "task_type": "classification",
      "model": "SVM",
      "accuracy": 0.95,
      "interpretation": "exploratory classification result"
    }
  },
  "clinical_note": "This is a research demonstration, not a diagnostic output."
}
```

---

## 14. Key Takeaway | 核心重點

> The tongue-image modeling route explored whether standardized tongue images could be compressed into low-dimensional features and used to predict physiological targets. RGB-separate encoders showed better reconstruction quality than RGB-joint encoding in this exploratory setup, and the extracted features produced promising pilot results for insomnia classification and total body water regression. For a risk-aware clinical AI portfolio, the most important value is not claiming diagnosis, but showing how image features may serve as upstream physiological signals that can later connect to interpretable cognitive-risk screening.

中文版本：

> 舌頭影像模型的重點，是探索標準化舌頭照片能否被壓縮成低維度特徵，並用來預測生理指標。在這個探索性設定中，RGB 分離式 encoder 的重建效果比 RGB-joint encoder 好，而萃取出的影像特徵在失眠分類與身體總水量迴歸上有初步可觀察的訊號。放在 risk-aware clinical AI 作品集中，重點不是宣稱舌頭照片可以診斷疾病，而是展示影像特徵如何作為上游的生理訊號，未來可能與可解釋的認知風險篩檢流程串接。

---
