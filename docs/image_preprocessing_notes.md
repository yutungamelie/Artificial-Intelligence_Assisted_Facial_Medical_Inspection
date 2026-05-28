# Image Preprocessing Notes

## 影像前處理筆記 | Image Preprocessing Notes

This document explains how face and tongue images in the **Risk-Aware Clinical AI Screening System for Cognitive Function** project can be transformed from raw clinical images into model-ready inputs.

The goal is to document the image preprocessing logic, quality-control considerations, and portfolio-safe reconstruction strategy. This repository should not publish real patient images. Instead, it should describe the workflow and provide mock code templates for face and tongue preprocessing.

---

## 1. Purpose | 目的

In a clinical AI screening pipeline, image preprocessing is not only a technical step. It is part of risk control.

For this project, image preprocessing aims to:

```text
raw face / tongue images
→ standardized region of interest
→ quality-checked image crops
→ resized tensors
→ low-dimensional image features
→ physiological or cognitive-risk modeling
```

Image preprocessing matters because:

```text
cropping error
lighting variation
wrong region of interest
poor alignment
background artifacts
manual adjustment inconsistency
```

can directly affect model prediction reliability.

---

## 2. Source Image Types | 原始影像類型

The image collection workflow was designed to capture five standardized image types:

```text
1. On the tongue / supralingual image / 舌上
2. Under the tongue / sublingual image / 舌下
3. Frontal face / 正臉
4. 45-degree left profile / 左 45 度側臉
5. 45-degree right profile / 右 45 度側臉
```

The Flutter photo app README specifies that the app allows subject ID input, captures the five image types, saves images to the device, and includes a light sensor value in the photo filename.

Portfolio-safe note:

```text
Do not publish raw participant images.
Use mock paths, generated images, or placeholder tensors only.
```

---

## 3. Face Image Preprocessing | 臉部影像前處理

The face preprocessing reference materials describe a general face-recognition workflow with four major steps:

```text
1. Face detection
2. Face transformation, alignment, and crop
3. Face feature extraction
4. Face feature comparison
```

In the referenced face-recognition notebooks, the workflow uses:

```text
MTCNN
→ face detection / bounding box
FaceNet
→ 128-dimensional face embedding
SVM
→ identity classifier for demonstration
```

For this clinical AI portfolio, the goal is not identity recognition. The useful part is the preprocessing logic:

```text
detect the face region
crop the face
align / normalize the input
resize to the model input size
extract image features or feed to downstream model
```

### 3.1 Why Generic ImageNet Classification Was Not Enough

The face preprocessing reference first shows that a general ImageNet-pretrained ResNet50 may classify a girl image as objects such as `ping-pong_ball`, `bubble`, or `Band_Aid`.

This is an important modeling lesson:

> A pretrained image classifier does not necessarily understand the clinical or anatomical region we care about. It maps images to classes it was trained on.

Therefore, for clinical face images, preprocessing must explicitly locate and standardize the face region before downstream modeling.

### 3.2 Face Detection and Crop Logic

The MTCNN-based face detection workflow returns bounding boxes:

```text
x1, y1, x2, y2, confidence_score
```

Then the face region is cropped using the detected bounding box:

```python
cropped_face = frame[y1:y2, x1:x2, :]
```

The face crop can then be:

```text
resized
normalized / prewhitened
converted into a tensor
passed into FaceNet or another image model
```

### 3.3 Suggested Public Module

This logic maps to:

```text
src/image_preprocessing/face_crop_quality_check.py
```

Suggested responsibilities:

```text
load image
detect face bounding box
crop face region
check whether a face was detected
check bounding box validity
resize image
compute brightness / blur / crop-size flags
return crop + quality metadata
```

Example output:

```json
{
  "image_id": "synthetic_face_001",
  "face_detected": true,
  "bbox": [80, 85, 234, 271],
  "crop_valid": true,
  "brightness_flag": "ok",
  "blur_flag": "ok",
  "quality_level": "usable"
}
```

---

## 4. Tongue Image Capture and Crop | 舌頭影像擷取與裁切

Tongue images were processed separately for:

```text
supralingual images / 舌上
sublingual images / 舌下
```

The uploaded `TongueCrop.ipynb` shows a practical cropping workflow based on OpenCV, Matplotlib, PIL, and manual visual inspection.

Core workflow:

```text
load sorted image files
display all images in grid view
resize images for inspection
define bounding-box crop coordinates
crop tongue region
review abnormal / weird cases
replace problematic crops
resize final images to model input size
inspect RGB distributions
```

### 4.1 Automatic Bounding-Box Crop

For supralingual images, the notebook defines fixed crop coordinates after resizing images to a standard size.

Example logic:

```python
img = cv2.imread(img_path)
img = cv2.resize(img, (1024, 1024))
img_rgb = cv2.cvtColor(img, cv2.COLOR_BGR2RGB)

x_start = 330
x_end = 680
y_start = 670
y_end = 820

cropped = img[y_start:y_end, x_start:x_end]
```

This fixed-box strategy is useful when images are captured under similar composition and camera setup.

However, clinical images may still vary due to:

```text
different tongue position
mouth opening differences
camera angle
lighting
background artifacts
partial occlusion
patient movement
```

Therefore, automatic cropping should be treated as a first-pass method, not a guaranteed final result.

### 4.2 Manual Review of Weird Cases

The notebook separates unusual images into special categories such as:

```text
upper
lower
other
weird cases
```

and applies case-specific crop coordinates for selected images.

This reflects an important real-world lesson:

> In medical image preprocessing, automated cropping may fail or include unwanted artifacts, so visual review and manual correction may be necessary.

### 4.3 Manual Correction with Fiji

Some automatically cropped tongue images still contained artifacts or failed to isolate the ideal tongue region. In these cases, manual correction was performed using **Fiji**.

Recommended documentation:

```text
1. Run automated crop.
2. Review crop grid.
3. Flag bad crops.
4. Open bad crops or raw images in Fiji.
5. Manually adjust the crop region.
6. Save corrected crop to a separate folder.
7. Replace the auto-crop only after review.
8. Keep a log of manually adjusted files.
```

Suggested manual-adjustment log:

| image_id | issue | correction_method | reviewer_note |
|---|---|---|---|
| synthetic_017 | background artifact | Fiji manual crop | removed lower-mouth noise |
| synthetic_056 | tongue off-center | Fiji manual crop | adjusted bounding box |
| synthetic_107 | auto-crop failed | Fiji manual crop | retained usable tongue region |

Risk-aware note:

> Manual correction improves image quality but introduces reviewer-dependent variability. Therefore, manually adjusted files should be logged and separated from fully automated crops.

### 4.4 File Replacement Workflow

The notebook includes a file replacement step:

```python
folder_a = ".../weird/other"      # corrected replacement files
folder_b = ".../crop_supralingual_rgb"  # target folder

common_files = files_in_a.intersection(files_in_b)

for file_name in common_files:
    shutil.copy2(file_a_path, file_b_path)
```

This workflow replaces problematic automatically cropped images with manually corrected crops.

Recommended public implementation:

```text
do not overwrite without logging
save original auto-crop
save manually corrected crop
write replacement metadata
```

---

## 5. Image Resizing and Model-Ready Tensor | 影像 resize 與模型輸入格式

The tongue-image modeling slides define the image input dimension as:

```text
[3 x 128 x 128]
```

The TongueCrop notebook also includes resizing logic:

```python
with Image.open(original_path) as img:
    resized_img = img.resize((256, 256))
    resized_img.save(output_file)
```

and later analyzes images under a 128-sized folder.

Recommended model-ready preprocessing:

```text
1. crop tongue region
2. resize to 128 x 128
3. convert BGR to RGB
4. normalize pixel values
5. convert to channel-first tensor [3, 128, 128]
6. save quality metadata
```

Suggested public module:

```text
src/image_preprocessing/tongue_image_preprocessing.py
```

Suggested function:

```python
def preprocess_tongue_image(image_path: str, crop_box: tuple | None = None) -> dict:
    """
    Load a tongue image, apply crop, resize to 128x128,
    normalize RGB channels, and return tensor plus quality metadata.
    """
```

---

## 6. RGB Distribution Check | RGB 分布檢查

The TongueCrop notebook includes an RGB-distribution inspection step.

Conceptual workflow:

```text
load all cropped images
convert BGR to RGB
split red / green / blue channels
flatten pixel intensities
plot histograms for each channel
```

Purpose:

```text
detect lighting shifts
detect color distribution abnormalities
inspect whether images are comparable
identify possible preprocessing artifacts
```

This is especially relevant because tongue-color information may be meaningful for downstream physiological prediction.

Risk-aware note:

> If the model relies on color-related signals, lighting variation and RGB distribution shifts can become a source of prediction instability.

---

## 7. Lighting Metadata | 光線資訊與照片 metadata

The Flutter photo app README states that the app includes the light sensor value in the photo name.

This is important because lighting can affect:

```text
tongue color
face color
image brightness
model features
image reconstruction quality
downstream prediction
```

Recommended metadata fields:

```json
{
  "image_id": "synthetic_tongue_001",
  "subject_id": "synthetic_001",
  "image_type": "supralingual",
  "light_sensor_value": 312.4,
  "crop_method": "auto",
  "manual_adjusted": false,
  "quality_flag": "usable"
}
```

Suggested public module:

```text
src/image_preprocessing/lighting_metadata_parser.py
```

Suggested function:

```python
def parse_light_sensor_from_filename(filename: str) -> float | None:
    ...
```

---

## 8. Tongue Image Feature Extraction | 舌頭影像特徵萃取

The tongue modeling slides describe the downstream goal:

```text
tongue image
→ low-dimensional image features
→ physiological target prediction
```

The stated goal is to compress images into low-dimensional features that still reconstruct well. Two autoencoder routes were compared:

```text
Route 1: RGB-Separate Encoders
R/G/B encoders → concatenate features

Route 2: RGB-Joint Encoder
single encoder on full RGB image
```

The slide reports a reconstruction-check comparison:

```text
RGB-Separate Encoders: Reconstruction MSE = 0.000572
RGB-Joint Encoder: Reconstruction MSE = 0.001158
```

The slides also describe PCA visualization and K-Means clustering to inspect whether extracted features show meaningful structure.

Final downstream task:

```text
image features
→ predict approximately 90 physiological targets
→ regression and classification
```

Reported examples from the slides:

```text
SVM best accuracy: Insomnia = 0.95
SVR best correlation: TBW = 0.636
```

Portfolio-safe framing:

> These results should be described as exploratory and interview / portfolio discussion materials, not as validated clinical claims.

---

## 9. Image Quality Check | 影像品質檢查

Recommended image quality checks:

### 9.1 General Checks

```text
file exists
image can be loaded
image has expected color channels
image size is valid
image is not empty or corrupted
```

### 9.2 Crop Checks

```text
crop box is within image bounds
crop size is not too small
tongue / face region is centered enough
background artifact ratio is acceptable
manual crop flag is recorded
```

### 9.3 Visual Checks

```text
grid view of all crops
side-by-side raw vs cropped comparison
flag weird cases
review manually adjusted files
```

### 9.4 Color / Lighting Checks

```text
brightness range
RGB histogram
light sensor value
overexposure / underexposure flag
white-balance concerns
```

### 9.5 Face-Specific Checks

```text
face detected
number of faces detected
bounding box confidence
face not out of range
alignment success
```

### 9.6 Tongue-Specific Checks

```text
tongue region visible
crop does not include excessive lips / teeth / background
sufficient tongue surface area
supralingual vs sublingual label is correct
manual correction log exists if adjusted
```

---

## 10. Why Image Preprocessing Matters for Clinical AI Risk | 為什麼影像前處理會影響臨床 AI 風險

Image preprocessing is a risk-control layer because model predictions can change when the input region changes.

Potential failure modes:

| Failure Mode | Risk |
|---|---|
| wrong crop | model learns background, lips, teeth, or skin instead of tongue |
| poor lighting | color-based signals become unreliable |
| face not aligned | model features reflect pose rather than health signal |
| tongue off-center | autoencoder features may capture crop artifact |
| manual correction not logged | reproducibility becomes weak |
| raw patient image released | privacy and biometric risk |
| generic pretrained model used blindly | output may reflect irrelevant ImageNet classes |

Risk-aware principle:

> The system should not treat all images as equally reliable. Image quality flags should flow into the downstream uncertainty and triage layer.

Example:

```text
good crop + stable lighting
→ normal modeling path

manual crop + uncertain lighting
→ prediction allowed, but uncertainty increased

failed crop or poor visibility
→ do not predict; request recollection or manual review
```

---

## 11. Suggested Public Code Mapping | 對應 Repo 程式模組

This document maps to the following repository modules:

```text
src/image_preprocessing/
├── face_crop_quality_check.py
├── tongue_image_preprocessing.py
└── lighting_metadata_parser.py
```

### 11.1 `face_crop_quality_check.py`

Suggested responsibilities:

```text
load image
detect face bounding box
crop face
check face count
check bounding box validity
resize crop
return quality metadata
```

### 11.2 `tongue_image_preprocessing.py`

Suggested responsibilities:

```text
load tongue image
apply automatic crop
support manual crop override
resize to 128x128
normalize RGB
record crop method
return model-ready tensor
```

### 11.3 `lighting_metadata_parser.py`

Suggested responsibilities:

```text
parse light sensor value from filename
validate metadata
attach lighting value to image record
flag missing lighting metadata
```

---

## 12. Recommended Public Demo Strategy | 公開展示策略

Because face and tongue images are sensitive biometric and clinical data, the public GitHub repository should not release real images.

Safe public materials:

```text
mock image paths
synthetic image metadata
placeholder crop diagrams
code templates
quality-check examples
manually written workflow notes
```

Do not release:

```text
raw face images
raw tongue images
manually cropped patient images
image filenames containing real subject IDs
light-sensor metadata linked to real participants
```

Suggested README statement:

> This repository does not release raw clinical images. Image preprocessing code is provided as a portfolio-safe reconstruction using mock paths and synthetic metadata only.

---

## 13. Suggested Implementation Workflow | 建議實作流程

Recommended public workflow:

```text
1. Prepare mock image metadata CSV.
2. Load mock image paths.
3. Parse image type and light sensor value.
4. Run face or tongue preprocessing branch.
5. Apply auto-crop.
6. Run quality checks.
7. If failed, mark as manual_review_required.
8. If manually adjusted, record correction metadata.
9. Resize final crop to model input size.
10. Export model-ready tensor path and quality metadata.
```

Example metadata output:

```json
{
  "image_id": "synthetic_tongue_001",
  "image_type": "supralingual",
  "crop_method": "manual_fiji",
  "manual_adjusted": true,
  "light_sensor_value": 285.6,
  "model_input_shape": [3, 128, 128],
  "quality_level": "usable_with_caution",
  "uncertainty_flag": "increase"
}
```

---

## 14. Key Takeaway | 核心重點

> Image preprocessing is not just a preparation step before modeling. In a clinical AI system, it is a reliability and risk-control layer. Face and tongue images must be standardized, cropped, quality-checked, and documented before they can be used as model inputs; when automatic cropping fails, manual correction such as Fiji adjustment should be logged and reflected in downstream uncertainty.

中文版本：

> 影像前處理不是單純把照片丟進模型前的準備動作，而是臨床 AI 的可靠性與風險控管層。臉與舌頭照片必須經過標準化、裁切、品質檢查與紀錄，才適合進入模型；當自動化裁切失敗時，用 Fiji 等工具手動修正可以改善品質，但也必須被記錄，並反映到後續的不確定性評估。

---
