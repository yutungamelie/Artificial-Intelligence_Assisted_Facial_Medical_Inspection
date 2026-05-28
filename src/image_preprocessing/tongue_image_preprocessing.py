"""
tongue_image_preprocessing.py

Portfolio-safe tongue image preprocessing utilities for the
risk-aware-clinical-ai-screening project.

This module reconstructs the tongue-image preprocessing logic:
1. load tongue image;
2. optionally crop or apply a placeholder mask;
3. resize to 128 x 128;
4. normalize RGB;
5. output a tensor with shape [3, 128, 128].

The tongue modeling slides describe the model input as [3 x 128 x 128] and use
autoencoders for dimension reduction. This file focuses only on preprocessing
and quality metadata. It does not include patient images or clinical diagnosis.

Designed for synthetic, mock, or de-identified demo images only.
"""

from __future__ import annotations

from dataclasses import asdict, dataclass
from pathlib import Path
from typing import Literal

import cv2
import numpy as np


CropMethod = Literal["none", "manual_xyxy", "center_square", "fixed_supralingual_1024"]


@dataclass
class TonguePreprocessResult:
    """Structured output for tongue image preprocessing."""

    image_path: str
    image_loaded: bool
    image_height: int | None
    image_width: int | None
    image_type: str
    crop_method: str
    crop_box_xyxy: tuple[int, int, int, int] | None
    manual_adjusted: bool
    output_tensor_shape: tuple[int, int, int] | None
    output_tensor_dtype: str | None
    output_image_path: str | None
    crop_valid: bool
    brightness_mean: float | None
    brightness_flag: str
    rgb_mean: tuple[float, float, float] | None
    rgb_std: tuple[float, float, float] | None
    quality_level: str
    uncertainty_flag: str
    notes: list[str]


def read_image_rgb(image_path: str | Path) -> np.ndarray:
    """Read image as RGB array."""

    path = Path(image_path)
    if not path.exists():
        raise FileNotFoundError(f"Image does not exist: {path}")

    bgr = cv2.imread(str(path), cv2.IMREAD_COLOR)
    if bgr is None:
        raise ValueError(f"Unable to decode image: {path}")

    return cv2.cvtColor(bgr, cv2.COLOR_BGR2RGB)


def xyxy_to_int_tuple(box: tuple[int | float, int | float, int | float, int | float]) -> tuple[int, int, int, int]:
    """Convert a bounding box into int xyxy tuple."""

    x1, y1, x2, y2 = box
    return int(round(x1)), int(round(y1)), int(round(x2)), int(round(y2))


def clamp_crop_box(
    box: tuple[int, int, int, int],
    image_shape: tuple[int, int, int],
) -> tuple[int, int, int, int]:
    """Clamp crop box to image bounds."""

    x1, y1, x2, y2 = box
    h, w = image_shape[:2]
    return max(0, x1), max(0, y1), min(w, x2), min(h, y2)


def crop_image(
    image_rgb: np.ndarray,
    crop_box_xyxy: tuple[int, int, int, int] | None,
) -> tuple[np.ndarray, bool]:
    """Crop image with optional xyxy box."""

    if crop_box_xyxy is None:
        return image_rgb.copy(), True

    x1, y1, x2, y2 = clamp_crop_box(crop_box_xyxy, image_rgb.shape)
    if x2 <= x1 or y2 <= y1:
        return image_rgb.copy(), False

    crop = image_rgb[y1:y2, x1:x2, :]
    return crop, crop.size > 0


def center_square_crop_box(image_shape: tuple[int, int, int], scale: float = 0.75) -> tuple[int, int, int, int]:
    """Return a center square crop box.

    This is a placeholder strategy for public demos when no segmentation model
    is available.
    """

    h, w = image_shape[:2]
    side = int(min(h, w) * scale)
    cx = w // 2
    cy = h // 2
    x1 = cx - side // 2
    y1 = cy - side // 2
    return clamp_crop_box((x1, y1, x1 + side, y1 + side), image_shape)


def fixed_supralingual_crop_box_for_1024() -> tuple[int, int, int, int]:
    """Fixed supralingual crop from the user's TongueCrop-style workflow.

    The notebook resized source images to 1024 x 1024 and used a fixed region:
        x_start = 330
        x_end   = 680
        y_start = 670
        y_end   = 820

    This is included as a reproducible placeholder for portfolio documentation,
    not as a universal clinical rule.
    """

    return (330, 670, 680, 820)


def build_crop_box(
    image_rgb: np.ndarray,
    *,
    crop_method: CropMethod,
    manual_crop_box_xyxy: tuple[int, int, int, int] | None = None,
) -> tuple[tuple[int, int, int, int] | None, list[str]]:
    """Build crop box according to selected crop method."""

    notes: list[str] = []

    if crop_method == "none":
        return None, notes

    if crop_method == "manual_xyxy":
        if manual_crop_box_xyxy is None:
            notes.append("manual crop method requested but no crop box was provided")
            return None, notes
        return clamp_crop_box(xyxy_to_int_tuple(manual_crop_box_xyxy), image_rgb.shape), notes

    if crop_method == "center_square":
        notes.append("using center-square crop placeholder")
        return center_square_crop_box(image_rgb.shape), notes

    if crop_method == "fixed_supralingual_1024":
        # Resize to 1024 first so the fixed notebook coordinates make sense.
        notes.append("resized to 1024x1024 before applying fixed supralingual crop")
        return fixed_supralingual_crop_box_for_1024(), notes

    raise ValueError(f"Unknown crop_method: {crop_method}")


def resize_to_model_input(image_rgb: np.ndarray, size: tuple[int, int] = (128, 128)) -> np.ndarray:
    """Resize image to model input resolution."""

    return cv2.resize(image_rgb, size, interpolation=cv2.INTER_AREA)


def normalize_rgb(image_rgb: np.ndarray, mode: Literal["zero_one", "minus_one_one", "imagenet"] = "zero_one") -> np.ndarray:
    """Normalize RGB image for model input."""

    arr = image_rgb.astype(np.float32)

    if mode == "zero_one":
        return arr / 255.0

    if mode == "minus_one_one":
        return (arr / 127.5) - 1.0

    if mode == "imagenet":
        # RGB ImageNet mean/std.
        mean = np.array([0.485, 0.456, 0.406], dtype=np.float32)
        std = np.array([0.229, 0.224, 0.225], dtype=np.float32)
        return (arr / 255.0 - mean) / std

    raise ValueError(f"Unknown normalization mode: {mode}")


def to_channel_first_tensor(image_rgb_normalized: np.ndarray) -> np.ndarray:
    """Convert HWC RGB image to CHW tensor [3, H, W]."""

    return np.transpose(image_rgb_normalized, (2, 0, 1)).astype(np.float32)


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
    """Classify brightness condition."""

    if brightness_mean is None:
        return "unknown"
    if brightness_mean < dark_threshold:
        return "too_dark"
    if brightness_mean > bright_threshold:
        return "too_bright"
    return "ok"


def compute_rgb_stats(image_rgb: np.ndarray) -> tuple[tuple[float, float, float], tuple[float, float, float]]:
    """Compute RGB channel mean and standard deviation on 0-255 scale."""

    means = tuple(float(x) for x in image_rgb.reshape(-1, 3).mean(axis=0))
    stds = tuple(float(x) for x in image_rgb.reshape(-1, 3).std(axis=0))
    return means, stds


def build_quality_level(
    *,
    image_loaded: bool,
    crop_valid: bool,
    brightness_flag: str,
    manual_adjusted: bool,
    crop_method: str,
) -> tuple[str, str, list[str]]:
    """Combine quality flags into downstream uncertainty labels."""

    notes: list[str] = []

    if not image_loaded:
        return "unusable", "do_not_predict", ["image could not be loaded"]

    if not crop_valid:
        return "unusable", "do_not_predict", ["crop box invalid"]

    if brightness_flag != "ok":
        notes.append(f"brightness issue: {brightness_flag}")

    if manual_adjusted:
        notes.append("manual crop adjustment was used; log reviewer and reason")

    if crop_method in {"center_square", "fixed_supralingual_1024"}:
        notes.append(f"crop method is heuristic: {crop_method}")

    if not notes:
        return "usable", "normal", notes

    return "usable_with_caution", "increase", notes


def preprocess_tongue_image(
    image_path: str | Path,
    *,
    image_type: str = "supralingual",
    crop_method: CropMethod = "center_square",
    manual_crop_box_xyxy: tuple[int, int, int, int] | None = None,
    manual_adjusted: bool = False,
    output_image_path: str | Path | None = None,
    tensor_output_path: str | Path | None = None,
    normalization: Literal["zero_one", "minus_one_one", "imagenet"] = "zero_one",
) -> tuple[np.ndarray | None, TonguePreprocessResult]:
    """Load, crop, resize, normalize, and tensorize a tongue image.

    Returns
    -------
    tuple[np.ndarray | None, TonguePreprocessResult]
        Tensor shape is [3, 128, 128] when preprocessing succeeds.
    """

    image_path = Path(image_path)

    try:
        image_rgb = read_image_rgb(image_path)
        image_loaded = True
        h, w = image_rgb.shape[:2]
    except Exception as exc:
        result = TonguePreprocessResult(
            image_path=str(image_path),
            image_loaded=False,
            image_height=None,
            image_width=None,
            image_type=image_type,
            crop_method=crop_method,
            crop_box_xyxy=None,
            manual_adjusted=manual_adjusted,
            output_tensor_shape=None,
            output_tensor_dtype=None,
            output_image_path=None,
            crop_valid=False,
            brightness_mean=None,
            brightness_flag="unknown",
            rgb_mean=None,
            rgb_std=None,
            quality_level="unusable",
            uncertainty_flag="do_not_predict",
            notes=[str(exc)],
        )
        return None, result

    working_image = image_rgb
    crop_notes: list[str] = []

    if crop_method == "fixed_supralingual_1024":
        working_image = cv2.resize(image_rgb, (1024, 1024), interpolation=cv2.INTER_AREA)

    crop_box, crop_notes = build_crop_box(
        working_image,
        crop_method=crop_method,
        manual_crop_box_xyxy=manual_crop_box_xyxy,
    )
    cropped, crop_valid = crop_image(working_image, crop_box)

    if crop_valid:
        model_image = resize_to_model_input(cropped, size=(128, 128))
        brightness = compute_brightness_mean(model_image)
        brightness_flag = classify_brightness(brightness)
        rgb_mean, rgb_std = compute_rgb_stats(model_image)
        normalized = normalize_rgb(model_image, mode=normalization)
        tensor = to_channel_first_tensor(normalized)

        saved_image_path = None
        if output_image_path is not None:
            output_path = Path(output_image_path)
            output_path.parent.mkdir(parents=True, exist_ok=True)
            cv2.imwrite(str(output_path), cv2.cvtColor(model_image, cv2.COLOR_RGB2BGR))
            saved_image_path = str(output_path)

        if tensor_output_path is not None:
            tensor_path = Path(tensor_output_path)
            tensor_path.parent.mkdir(parents=True, exist_ok=True)
            np.save(str(tensor_path), tensor)

        quality_level, uncertainty_flag, quality_notes = build_quality_level(
            image_loaded=image_loaded,
            crop_valid=crop_valid,
            brightness_flag=brightness_flag,
            manual_adjusted=manual_adjusted,
            crop_method=crop_method,
        )

        result = TonguePreprocessResult(
            image_path=str(image_path),
            image_loaded=True,
            image_height=h,
            image_width=w,
            image_type=image_type,
            crop_method=crop_method,
            crop_box_xyxy=crop_box,
            manual_adjusted=manual_adjusted,
            output_tensor_shape=tuple(tensor.shape),
            output_tensor_dtype=str(tensor.dtype),
            output_image_path=saved_image_path,
            crop_valid=crop_valid,
            brightness_mean=brightness,
            brightness_flag=brightness_flag,
            rgb_mean=rgb_mean,
            rgb_std=rgb_std,
            quality_level=quality_level,
            uncertainty_flag=uncertainty_flag,
            notes=crop_notes + quality_notes,
        )
        return tensor, result

    quality_level, uncertainty_flag, quality_notes = build_quality_level(
        image_loaded=image_loaded,
        crop_valid=False,
        brightness_flag="unknown",
        manual_adjusted=manual_adjusted,
        crop_method=crop_method,
    )

    result = TonguePreprocessResult(
        image_path=str(image_path),
        image_loaded=True,
        image_height=h,
        image_width=w,
        image_type=image_type,
        crop_method=crop_method,
        crop_box_xyxy=crop_box,
        manual_adjusted=manual_adjusted,
        output_tensor_shape=None,
        output_tensor_dtype=None,
        output_image_path=None,
        crop_valid=False,
        brightness_mean=None,
        brightness_flag="unknown",
        rgb_mean=None,
        rgb_std=None,
        quality_level=quality_level,
        uncertainty_flag=uncertainty_flag,
        notes=crop_notes + quality_notes,
    )
    return None, result


def create_placeholder_mask(
    image_shape: tuple[int, int],
    *,
    mask_type: Literal["ellipse", "full"] = "ellipse",
) -> np.ndarray:
    """Create a simple placeholder tongue mask.

    This is not a medical segmentation algorithm. It is included only to show
    where a future tongue segmentation model or manual mask would connect.
    """

    h, w = image_shape
    mask = np.zeros((h, w), dtype=np.uint8)

    if mask_type == "full":
        mask[:, :] = 1
        return mask

    if mask_type == "ellipse":
        center = (w // 2, h // 2)
        axes = (int(w * 0.35), int(h * 0.45))
        cv2.ellipse(mask, center, axes, angle=0, startAngle=0, endAngle=360, color=1, thickness=-1)
        return mask

    raise ValueError(f"Unknown mask_type: {mask_type}")


def main() -> None:
    """Command-line interface.

    Example:
        python src/image_preprocessing/tongue_image_preprocessing.py \
            --input demo/synthetic_tongue.png \
            --output-image data/processed/synthetic_tongue_128.png \
            --output-tensor data/processed/synthetic_tongue_tensor.npy \
            --metadata reports/tongue_preprocess_metadata.json
    """

    import argparse
    import json

    parser = argparse.ArgumentParser(description="Preprocess tongue image into [3, 128, 128] tensor.")
    parser.add_argument("--input", required=True, help="Input tongue image path.")
    parser.add_argument("--image-type", default="supralingual", help="Image type label.")
    parser.add_argument(
        "--crop-method",
        choices=["none", "manual_xyxy", "center_square", "fixed_supralingual_1024"],
        default="center_square",
    )
    parser.add_argument("--manual-crop", nargs=4, type=int, metavar=("X1", "Y1", "X2", "Y2"), default=None)
    parser.add_argument("--manual-adjusted", action="store_true")
    parser.add_argument("--output-image", default=None, help="Optional preprocessed 128x128 image path.")
    parser.add_argument("--output-tensor", default=None, help="Optional .npy tensor output path.")
    parser.add_argument("--metadata", default=None, help="Optional JSON metadata path.")
    args = parser.parse_args()

    tensor, result = preprocess_tongue_image(
        args.input,
        image_type=args.image_type,
        crop_method=args.crop_method,
        manual_crop_box_xyxy=tuple(args.manual_crop) if args.manual_crop else None,
        manual_adjusted=args.manual_adjusted,
        output_image_path=args.output_image,
        tensor_output_path=args.output_tensor,
    )

    metadata = asdict(result)
    if args.metadata:
        metadata_path = Path(args.metadata)
        metadata_path.parent.mkdir(parents=True, exist_ok=True)
        metadata_path.write_text(json.dumps(metadata, indent=2, ensure_ascii=False), encoding="utf-8")
    else:
        print(json.dumps(metadata, indent=2, ensure_ascii=False))


if __name__ == "__main__":
    main()
