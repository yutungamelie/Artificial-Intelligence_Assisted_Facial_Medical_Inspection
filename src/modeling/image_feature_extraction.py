"""
image_feature_extraction.py

Portfolio-safe image feature extraction demo for the
risk-aware-clinical-ai-screening project.

This module reconstructs the tongue-image feature extraction idea:
- input tongue image tensor with shape [3, 128, 128];
- Route 1: RGB-separate feature extraction;
- Route 2: RGB-joint feature extraction;
- output low-dimensional image features for downstream physiological prediction.

Original project context:
    The tongue-image slides compare RGB-separate vs RGB-joint encoders.
    Route 1 compresses R/G/B channels separately and concatenates features
    into a 60-dimensional representation. Route 2 uses the full RGB image to
    create a 64-dimensional representation. The slides also compare reconstruction
    MSE and use PCA / K-Means visualization.

Public portfolio design:
    To keep this repository lightweight and runnable without training a deep
    autoencoder, this module uses sklearn IncrementalPCA / PCA as a deterministic
    mock encoder. It demonstrates the engineering interface while avoiding any
    release of patient images.

This file is for synthetic or de-identified demo tensors only.
"""

from __future__ import annotations

from dataclasses import asdict, dataclass
from pathlib import Path
from typing import Literal

import joblib
import numpy as np
import pandas as pd
from sklearn.decomposition import IncrementalPCA, PCA
from sklearn.pipeline import Pipeline
from sklearn.preprocessing import StandardScaler


FeatureRoute = Literal["rgb_separate", "rgb_joint"]


@dataclass
class FeatureExtractionMetadata:
    """Metadata for image feature extraction."""

    route: str
    n_images: int
    input_shape: tuple[int, ...]
    output_feature_dim: int
    reconstruction_mse: float | None
    feature_column_prefix: str
    clinical_note: str


def load_tensor_file(path: str | Path) -> np.ndarray:
    """Load a tensor from .npy file.

    Expected single-image shape:
        [3, 128, 128] or [128, 128, 3]

    Expected batch shape:
        [N, 3, 128, 128] or [N, 128, 128, 3]
    """

    arr = np.load(path)
    return arr.astype(np.float32)


def ensure_batch_channel_first(tensors: np.ndarray) -> np.ndarray:
    """Ensure tensor shape is [N, 3, H, W]."""

    arr = np.asarray(tensors, dtype=np.float32)

    if arr.ndim == 3:
        # Single image.
        if arr.shape[0] == 3:
            arr = arr[None, ...]
        elif arr.shape[-1] == 3:
            arr = np.transpose(arr, (2, 0, 1))[None, ...]
        else:
            raise ValueError(f"Cannot infer channel dimension from shape {arr.shape}")

    elif arr.ndim == 4:
        if arr.shape[1] == 3:
            pass
        elif arr.shape[-1] == 3:
            arr = np.transpose(arr, (0, 3, 1, 2))
        else:
            raise ValueError(f"Cannot infer channel dimension from shape {arr.shape}")

    else:
        raise ValueError(f"Expected 3D or 4D tensor, got shape {arr.shape}")

    return arr


def flatten_rgb_joint(tensors_chw: np.ndarray) -> np.ndarray:
    """Flatten [N, 3, H, W] into [N, 3*H*W]."""

    return tensors_chw.reshape(tensors_chw.shape[0], -1)


def flatten_rgb_separate(tensors_chw: np.ndarray) -> list[np.ndarray]:
    """Flatten each RGB channel separately."""

    return [tensors_chw[:, c, :, :].reshape(tensors_chw.shape[0], -1) for c in range(3)]


def _make_pca(n_components: int, n_samples: int, n_features: int) -> PCA | IncrementalPCA:
    """Create PCA with safe component count for small synthetic datasets."""

    safe_components = int(max(1, min(n_components, n_samples, n_features)))
    if n_features > 5000 and n_samples > 1:
        return IncrementalPCA(n_components=safe_components, batch_size=max(10, safe_components * 2))
    return PCA(n_components=safe_components, random_state=42)


def fit_rgb_joint_encoder(
    tensors: np.ndarray,
    *,
    n_components: int = 64,
) -> Pipeline:
    """Fit a mock RGB-joint encoder using PCA."""

    x = flatten_rgb_joint(ensure_batch_channel_first(tensors))
    pca = _make_pca(n_components, n_samples=x.shape[0], n_features=x.shape[1])
    return Pipeline([("scaler", StandardScaler(with_mean=True)), ("pca", pca)]).fit(x)


def fit_rgb_separate_encoders(
    tensors: np.ndarray,
    *,
    n_components_per_channel: int = 20,
) -> list[Pipeline]:
    """Fit three mock encoders, one for each RGB channel.

    The default 20 components per channel yields 60 dimensions total, matching
    the final route described in the tongue-image slides.
    """

    channels = flatten_rgb_separate(ensure_batch_channel_first(tensors))
    encoders: list[Pipeline] = []

    for x_channel in channels:
        pca = _make_pca(
            n_components_per_channel,
            n_samples=x_channel.shape[0],
            n_features=x_channel.shape[1],
        )
        encoders.append(Pipeline([("scaler", StandardScaler(with_mean=True)), ("pca", pca)]).fit(x_channel))

    return encoders


def transform_rgb_joint(tensors: np.ndarray, encoder: Pipeline) -> np.ndarray:
    """Transform images with RGB-joint encoder."""

    x = flatten_rgb_joint(ensure_batch_channel_first(tensors))
    return encoder.transform(x).astype(np.float32)


def transform_rgb_separate(tensors: np.ndarray, encoders: list[Pipeline]) -> np.ndarray:
    """Transform images with RGB-separate encoders and concatenate features."""

    channels = flatten_rgb_separate(ensure_batch_channel_first(tensors))
    feats = [encoder.transform(x_channel) for encoder, x_channel in zip(encoders, channels)]
    return np.concatenate(feats, axis=1).astype(np.float32)


def inverse_rgb_joint(features: np.ndarray, encoder: Pipeline, original_shape: tuple[int, int, int, int]) -> np.ndarray:
    """Approximate reconstruction from RGB-joint PCA features."""

    flat_recon = encoder.inverse_transform(features)
    return flat_recon.reshape(original_shape)


def inverse_rgb_separate(features: np.ndarray, encoders: list[Pipeline], original_shape: tuple[int, int, int, int]) -> np.ndarray:
    """Approximate reconstruction from RGB-separate PCA features."""

    n = original_shape[0]
    channel_features = np.array_split(features, len(encoders), axis=1)
    reconstructed_channels = []

    for feat, encoder in zip(channel_features, encoders):
        flat = encoder.inverse_transform(feat)
        reconstructed_channels.append(flat.reshape(n, original_shape[2], original_shape[3]))

    return np.stack(reconstructed_channels, axis=1)


def reconstruction_mse(original: np.ndarray, reconstructed: np.ndarray) -> float:
    """Mean squared reconstruction error."""

    return float(np.mean((original - reconstructed) ** 2))


def fit_image_feature_extractor(
    tensors: np.ndarray,
    *,
    route: FeatureRoute = "rgb_separate",
    joint_dim: int = 64,
    channel_dim: int = 20,
) -> tuple[Pipeline | list[Pipeline], FeatureExtractionMetadata]:
    """Fit mock image feature extractor and return metadata."""

    tensors_chw = ensure_batch_channel_first(tensors)

    if route == "rgb_joint":
        encoder = fit_rgb_joint_encoder(tensors_chw, n_components=joint_dim)
        features = transform_rgb_joint(tensors_chw, encoder)
        recon = inverse_rgb_joint(features, encoder, tensors_chw.shape)
        mse = reconstruction_mse(tensors_chw, recon)
        metadata = FeatureExtractionMetadata(
            route=route,
            n_images=int(tensors_chw.shape[0]),
            input_shape=tuple(tensors_chw.shape),
            output_feature_dim=int(features.shape[1]),
            reconstruction_mse=mse,
            feature_column_prefix="rgb_joint",
            clinical_note="Image features are exploratory physiological signals, not diagnostic outputs.",
        )
        return encoder, metadata

    if route == "rgb_separate":
        encoders = fit_rgb_separate_encoders(tensors_chw, n_components_per_channel=channel_dim)
        features = transform_rgb_separate(tensors_chw, encoders)
        recon = inverse_rgb_separate(features, encoders, tensors_chw.shape)
        mse = reconstruction_mse(tensors_chw, recon)
        metadata = FeatureExtractionMetadata(
            route=route,
            n_images=int(tensors_chw.shape[0]),
            input_shape=tuple(tensors_chw.shape),
            output_feature_dim=int(features.shape[1]),
            reconstruction_mse=mse,
            feature_column_prefix="rgb_sep",
            clinical_note="Image features are exploratory physiological signals, not diagnostic outputs.",
        )
        return encoders, metadata

    raise ValueError(f"Unknown route: {route}")


def transform_image_features(
    tensors: np.ndarray,
    encoder: Pipeline | list[Pipeline],
    *,
    route: FeatureRoute,
) -> np.ndarray:
    """Transform tensors into low-dimensional image features."""

    if route == "rgb_joint":
        if not isinstance(encoder, Pipeline):
            raise TypeError("RGB-joint route expects a single sklearn Pipeline.")
        return transform_rgb_joint(tensors, encoder)

    if route == "rgb_separate":
        if not isinstance(encoder, list):
            raise TypeError("RGB-separate route expects a list of three encoders.")
        return transform_rgb_separate(tensors, encoder)

    raise ValueError(f"Unknown route: {route}")


def features_to_dataframe(
    features: np.ndarray,
    *,
    prefix: str,
    image_ids: list[str] | None = None,
) -> pd.DataFrame:
    """Convert feature matrix to dataframe."""

    columns = [f"{prefix}_{i:03d}" for i in range(features.shape[1])]
    df = pd.DataFrame(features, columns=columns)

    if image_ids is not None:
        if len(image_ids) != len(df):
            raise ValueError("Length of image_ids must match number of feature rows.")
        df.insert(0, "image_id", image_ids)

    return df


def save_feature_extractor(encoder: Pipeline | list[Pipeline], path: str | Path) -> None:
    """Save fitted encoder."""

    path = Path(path)
    path.parent.mkdir(parents=True, exist_ok=True)
    joblib.dump(encoder, path)


def load_feature_extractor(path: str | Path) -> Pipeline | list[Pipeline]:
    """Load fitted encoder."""

    return joblib.load(path)


def main() -> None:
    """Command-line interface.

    Example:
        python src/modeling/image_feature_extraction.py \
            --tensor-npy examples/synthetic_tongue_tensors.npy \
            --route rgb_separate \
            --features-out examples/synthetic_image_features.csv \
            --metadata-out reports/image_feature_extraction_metadata.json \
            --encoder-out models/rgb_separate_pca.joblib
    """

    import argparse
    import json

    parser = argparse.ArgumentParser(description="Extract mock low-dimensional image features from tongue tensors.")
    parser.add_argument("--tensor-npy", required=True, help="Input .npy tensor file.")
    parser.add_argument("--route", choices=["rgb_separate", "rgb_joint"], default="rgb_separate")
    parser.add_argument("--features-out", required=True, help="CSV output path for image features.")
    parser.add_argument("--metadata-out", default=None, help="Optional JSON metadata output path.")
    parser.add_argument("--encoder-out", default=None, help="Optional fitted encoder joblib output path.")
    parser.add_argument("--image-id-prefix", default="synthetic_tongue", help="Prefix for generated image IDs.")
    args = parser.parse_args()

    tensors = load_tensor_file(args.tensor_npy)
    encoder, metadata = fit_image_feature_extractor(tensors, route=args.route)
    features = transform_image_features(tensors, encoder, route=args.route)

    image_ids = [f"{args.image_id_prefix}_{i:03d}" for i in range(features.shape[0])]
    feature_df = features_to_dataframe(features, prefix=metadata.feature_column_prefix, image_ids=image_ids)

    out_path = Path(args.features_out)
    out_path.parent.mkdir(parents=True, exist_ok=True)
    feature_df.to_csv(out_path, index=False)

    if args.metadata_out:
        metadata_path = Path(args.metadata_out)
        metadata_path.parent.mkdir(parents=True, exist_ok=True)
        metadata_path.write_text(json.dumps(asdict(metadata), indent=2, ensure_ascii=False), encoding="utf-8")

    if args.encoder_out:
        save_feature_extractor(encoder, args.encoder_out)


if __name__ == "__main__":
    main()
