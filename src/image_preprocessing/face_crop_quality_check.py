"""
face_crop_quality_check.py

Portfolio-safe face image preprocessing and quality-check utilities for the
risk-aware-clinical-ai-screening project.

This module reconstructs the face-preprocessing idea from the project materials:
1. detect face bounding box;
2. crop face region;
3. check whether a face exists;
4. check image size / brightness / blur;
5. return quality flags for downstream uncertainty-aware triage.

The original project workflow used MTCNN for face detection, FaceNet for
128-dimensional face embeddings, and SVM for face recognition. This public
portfolio version intentionally keeps the code lightweight and privacy-safe:
- no patient images are included;
- no identity recognition is performed;
- OpenCV Haar cascade is used as an optional local detector when available;
- the functions return crop and quality metadata rather than diagnostic output.

This file is designed for synthetic, mock, or de-identified demo images only.
"""

from __future__ import annotations

from dataclasses import asdict, dataclass
from pathlib import Path
from typing import Any

import cv2
import numpy as np


@dataclass
class FaceQualityResult:
    """Structured output for face crop quality checks."""

    image_path: str
    image_loaded: bool
    image_height: int | None
    image_width: int | None
    n_faces_detected: int
    face_detected: bool
    selected_bbox_xyxy: tuple[int, int, int, int] | None
    crop_saved_path: str | None
    crop_valid: bool
    brightness_mean: float | None
    brightness_flag: str
    blur_laplacian_var: float | None
    blur_flag: str
    size_flag: str
    bbox_flag: str
    quality_level: str
    uncertainty_flag: str
    notes: list[str]


def read_image_rgb(image_path: str | Path) -> np.ndarray:
    """Read an image as RGB numpy array.

    Raises
    ------
    FileNotFoundError
        If the path does not exist.
    ValueError
        If OpenCV cannot decode the image.
    """

    path = Path(image_path)
    if not path.exists():
        raise FileNotFoundError(f"Image does not exist: {path}")

    bgr = cv2.imread(str(path), cv2.IMREAD_COLOR)
    if bgr is None:
        raise ValueError(f"Unable to decode image: {path}")

    return cv2.cvtColor(bgr, cv2.COLOR_BGR2RGB)


def detect_faces_haar(
    image_rgb: np.ndarray,
    *,
    scale_factor: float = 1.1,
    min_neighbors: int = 5,
    min_size: tuple[int, int] = (40, 40),
) -> list[tuple[int, int, int, int]]:
    """Detect face bounding boxes using OpenCV's Haar cascade.

    This is a lightweight fallback detector for a portfolio demo. In the original
    learning materials, the face-recognition pipeline used MTCNN followed by
    crop / alignment / feature extraction. For production clinical image work,
    use a validated detector and record detector version.

    Returns
    -------
    list[tuple[int, int, int, int]]
        Bounding boxes in (x1, y1, x2, y2) format.
    """

    cascade_path = cv2.data.haarcascades + "haarcascade_frontalface_default.xml"
    detector = cv2.CascadeClassifier(cascade_path)
    if detector.empty():
        return []

    gray = cv2.cvtColor(image_rgb, cv2.COLOR_RGB2GRAY)
    boxes_xywh = detector.detectMultiScale(
        gray,
        scaleFactor=scale_factor,
        minNeighbors=min_neighbors,
        minSize=min_size,
    )

    boxes_xyxy: list[tuple[int, int, int, int]] = []
    for x, y, w, h in boxes_xywh:
        boxes_xyxy.append((int(x), int(y), int(x + w), int(y + h)))

    return boxes_xyxy


def select_largest_bbox(
    boxes: list[tuple[int, int, int, int]],
) -> tuple[int, int, int, int] | None:
    """Select the largest detected face bounding box."""

    if not boxes:
        return None

    return max(boxes, key=lambda b: max(0, b[2] - b[0]) * max(0, b[3] - b[1]))


def expand_bbox(
    bbox: tuple[int, int, int, int],
    image_shape: tuple[int, int, int],
    *,
    margin_ratio: float = 0.15,
) -> tuple[int, int, int, int]:
    """Expand a bounding box by margin ratio and clamp to image bounds."""

    x1, y1, x2, y2 = bbox
    h, w = image_shape[:2]
    bw = x2 - x1
    bh = y2 - y1

    dx = int(round(bw * margin_ratio))
    dy = int(round(bh * margin_ratio))

    return (
        max(0, x1 - dx),
        max(0, y1 - dy),
        min(w, x2 + dx),
        min(h, y2 + dy),
    )


def crop_with_bbox(
    image_rgb: np.ndarray,
    bbox: tuple[int, int, int, int],
) -> np.ndarray:
    """Crop an RGB image with an xyxy bounding box."""

    x1, y1, x2, y2 = bbox
    return image_rgb[y1:y2, x1:x2, :]


def resize_rgb(
    image_rgb: np.ndarray,
    size: tuple[int, int] = (160, 160),
) -> np.ndarray:
    """Resize RGB image to model-ready shape."""

    return cv2.resize(image_rgb, size, interpolation=cv2.INTER_CUBIC)


def compute_brightness_mean(image_rgb: np.ndarray) -> float:
    """Return mean grayscale brightness."""

    gray = cv2.cvtColor(image_rgb, cv2.COLOR_RGB2GRAY)
    return float(gray.mean())


def classify_brightness(
    brightness_mean: float | None,
    *,
    dark_threshold: float = 40.0,
    bright_threshold: float = 220.0,
) -> str:
    """Classify brightness quality."""

    if brightness_mean is None:
        return "unknown"
    if brightness_mean < dark_threshold:
        return "too_dark"
    if brightness_mean > bright_threshold:
        return "too_bright"
    return "ok"


def compute_blur_laplacian_variance(image_rgb: np.ndarray) -> float:
    """Return Laplacian variance as a simple blur metric.

    Lower values usually indicate blur.
    """

    gray = cv2.cvtColor(image_rgb, cv2.COLOR_RGB2GRAY)
    return float(cv2.Laplacian(gray, cv2.CV_64F).var())


def classify_blur(
    laplacian_var: float | None,
    *,
    blur_threshold: float = 80.0,
) -> str:
    """Classify blur quality using Laplacian variance."""

    if laplacian_var is None:
        return "unknown"
    if laplacian_var < blur_threshold:
        return "possibly_blurry"
    return "ok"


def classify_image_size(
    height: int,
    width: int,
    *,
    min_height: int = 128,
    min_width: int = 128,
) -> str:
    """Classify whether source image is large enough for processing."""

    if height < min_height or width < min_width:
        return "too_small"
    return "ok"


def classify_bbox(
    bbox: tuple[int, int, int, int] | None,
    image_shape: tuple[int, int, int] | None,
    *,
    min_face_area_ratio: float = 0.01,
    max_face_area_ratio: float = 0.90,
) -> str:
    """Classify face bounding-box validity."""

    if bbox is None or image_shape is None:
        return "no_face"

    x1, y1, x2, y2 = bbox
    h, w = image_shape[:2]

    if x1 < 0 or y1 < 0 or x2 > w or y2 > h or x2 <= x1 or y2 <= y1:
        return "out_of_bounds"

    face_area = (x2 - x1) * (y2 - y1)
    image_area = h * w
    area_ratio = face_area / image_area if image_area else 0.0

    if area_ratio < min_face_area_ratio:
        return "face_too_small"
    if area_ratio > max_face_area_ratio:
        return "face_too_large"
    return "ok"


def combine_quality_flags(
    *,
    image_loaded: bool,
    face_detected: bool,
    crop_valid: bool,
    brightness_flag: str,
    blur_flag: str,
    size_flag: str,
    bbox_flag: str,
    n_faces_detected: int,
) -> tuple[str, str, list[str]]:
    """Combine low-level flags into quality and uncertainty labels."""

    notes: list[str] = []

    if not image_loaded:
        return "unusable", "do_not_predict", ["image could not be loaded"]

    if size_flag != "ok":
        notes.append(f"image size issue: {size_flag}")

    if not face_detected:
        notes.append("no face detected")
        return "unusable", "do_not_predict", notes

    if n_faces_detected > 1:
        notes.append(f"multiple faces detected: {n_faces_detected}")

    if bbox_flag != "ok":
        notes.append(f"bounding box issue: {bbox_flag}")

    if not crop_valid:
        notes.append("face crop invalid")
        return "unusable", "do_not_predict", notes

    if brightness_flag != "ok":
        notes.append(f"brightness issue: {brightness_flag}")

    if blur_flag != "ok":
        notes.append(f"blur issue: {blur_flag}")

    if not notes:
        return "usable", "normal", notes

    if any("multiple faces" in n for n in notes) or brightness_flag != "ok" or blur_flag != "ok":
        return "usable_with_caution", "increase", notes

    return "review_recommended", "increase", notes


def check_face_crop_quality(
    image_path: str | Path,
    *,
    output_crop_path: str | Path | None = None,
    manual_bbox_xyxy: tuple[int, int, int, int] | None = None,
    crop_size: tuple[int, int] = (160, 160),
    margin_ratio: float = 0.15,
) -> FaceQualityResult:
    """Detect / crop a face and return quality metadata.

    Parameters
    ----------
    image_path:
        Input image path.
    output_crop_path:
        Optional path to save resized face crop.
    manual_bbox_xyxy:
        Optional user-provided bounding box. If provided, detection is skipped.
        This is useful for controlled demos or manually reviewed images.
    crop_size:
        Final crop size. The original FaceNet examples used 160x160 as model input.
    margin_ratio:
        Expansion margin around detected face before cropping.

    Returns
    -------
    FaceQualityResult
    """

    image_path = Path(image_path)

    try:
        image_rgb = read_image_rgb(image_path)
        image_loaded = True
        h, w = image_rgb.shape[:2]
    except Exception as exc:
        return FaceQualityResult(
            image_path=str(image_path),
            image_loaded=False,
            image_height=None,
            image_width=None,
            n_faces_detected=0,
            face_detected=False,
            selected_bbox_xyxy=None,
            crop_saved_path=None,
            crop_valid=False,
            brightness_mean=None,
            brightness_flag="unknown",
            blur_laplacian_var=None,
            blur_flag="unknown",
            size_flag="unknown",
            bbox_flag="no_image",
            quality_level="unusable",
            uncertainty_flag="do_not_predict",
            notes=[str(exc)],
        )

    size_flag = classify_image_size(h, w)
    brightness = compute_brightness_mean(image_rgb)
    brightness_flag = classify_brightness(brightness)
    blur = compute_blur_laplacian_variance(image_rgb)
    blur_flag = classify_blur(blur)

    if manual_bbox_xyxy is not None:
        boxes = [manual_bbox_xyxy]
        selected_bbox = manual_bbox_xyxy
    else:
        boxes = detect_faces_haar(image_rgb)
        selected_bbox = select_largest_bbox(boxes)

    face_detected = selected_bbox is not None
    expanded_bbox = expand_bbox(selected_bbox, image_rgb.shape, margin_ratio=margin_ratio) if selected_bbox else None
    bbox_flag = classify_bbox(expanded_bbox, image_rgb.shape)

    crop_valid = False
    crop_saved_path: str | None = None

    if expanded_bbox is not None and bbox_flag == "ok":
        crop = crop_with_bbox(image_rgb, expanded_bbox)
        crop_valid = crop.size > 0 and crop.shape[0] > 0 and crop.shape[1] > 0

        if crop_valid:
            crop_resized = resize_rgb(crop, crop_size)
            if output_crop_path is not None:
                output_path = Path(output_crop_path)
                output_path.parent.mkdir(parents=True, exist_ok=True)
                # Convert back to BGR for cv2.imwrite.
                cv2.imwrite(str(output_path), cv2.cvtColor(crop_resized, cv2.COLOR_RGB2BGR))
                crop_saved_path = str(output_path)

    quality_level, uncertainty_flag, notes = combine_quality_flags(
        image_loaded=image_loaded,
        face_detected=face_detected,
        crop_valid=crop_valid,
        brightness_flag=brightness_flag,
        blur_flag=blur_flag,
        size_flag=size_flag,
        bbox_flag=bbox_flag,
        n_faces_detected=len(boxes),
    )

    return FaceQualityResult(
        image_path=str(image_path),
        image_loaded=image_loaded,
        image_height=h,
        image_width=w,
        n_faces_detected=len(boxes),
        face_detected=face_detected,
        selected_bbox_xyxy=expanded_bbox,
        crop_saved_path=crop_saved_path,
        crop_valid=crop_valid,
        brightness_mean=brightness,
        brightness_flag=brightness_flag,
        blur_laplacian_var=blur,
        blur_flag=blur_flag,
        size_flag=size_flag,
        bbox_flag=bbox_flag,
        quality_level=quality_level,
        uncertainty_flag=uncertainty_flag,
        notes=notes,
    )


def batch_check_face_quality(
    image_paths: list[str | Path],
    *,
    output_dir: str | Path | None = None,
) -> list[dict[str, Any]]:
    """Run face quality check on multiple images and return dict records."""

    records: list[dict[str, Any]] = []

    for path in image_paths:
        output_crop_path = None
        if output_dir is not None:
            output_crop_path = Path(output_dir) / f"{Path(path).stem}_face_crop.png"

        result = check_face_crop_quality(path, output_crop_path=output_crop_path)
        records.append(asdict(result))

    return records


def main() -> None:
    """Command-line interface.

    Example:
        python src/image_preprocessing/face_crop_quality_check.py \
            --input demo/synthetic_face.png \
            --output-crop data/processed/synthetic_face_crop.png \
            --metadata reports/face_quality_metadata.json
    """

    import argparse
    import json

    parser = argparse.ArgumentParser(description="Face crop and image quality check.")
    parser.add_argument("--input", required=True, help="Input face image path.")
    parser.add_argument("--output-crop", default=None, help="Optional crop output path.")
    parser.add_argument("--metadata", default=None, help="Optional JSON metadata output path.")
    args = parser.parse_args()

    result = check_face_crop_quality(args.input, output_crop_path=args.output_crop)

    if args.metadata:
        metadata_path = Path(args.metadata)
        metadata_path.parent.mkdir(parents=True, exist_ok=True)
        metadata_path.write_text(json.dumps(asdict(result), indent=2, ensure_ascii=False), encoding="utf-8")
    else:
        print(json.dumps(asdict(result), indent=2, ensure_ascii=False))


if __name__ == "__main__":
    main()
