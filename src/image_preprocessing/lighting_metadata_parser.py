"""
lighting_metadata_parser.py

Light-sensor metadata parser for the risk-aware-clinical-ai-screening project.

Since the captured photo filenames include a light sensor value, this module provides portfolio-safe helper functions to:
- parse light sensor value from filenames;
- infer image type from filename;
- create image-level metadata records;
- flag missing or abnormal lighting metadata for downstream uncertainty scoring.

This file does not require patient images or hospital data.
"""

from __future__ import annotations

from dataclasses import asdict, dataclass
from pathlib import Path
import re
from typing import Iterable


IMAGE_TYPE_ALIASES: dict[str, str] = {
    "tongue_up": "supralingual",
    "supralingual": "supralingual",
    "on_tongue": "supralingual",
    "舌上": "supralingual",
    "tongue_down": "sublingual",
    "sublingual": "sublingual",
    "under_tongue": "sublingual",
    "舌下": "sublingual",
    "front_face": "frontal_face",
    "frontal": "frontal_face",
    "frontal_face": "frontal_face",
    "face_front": "frontal_face",
    "正臉": "frontal_face",
    "left45": "left_45_face",
    "left_45": "left_45_face",
    "45_left": "left_45_face",
    "左側臉": "left_45_face",
    "right45": "right_45_face",
    "right_45": "right_45_face",
    "45_right": "right_45_face",
    "右側臉": "right_45_face",
}

# Flexible patterns because filenames are usually project-specific.
# Supported examples:
#   subject001_supralingual_light312.4.jpg
#   001_舌上_lux_285.6.png
#   face_front_light-sensor=410.jpeg
#   light_123
LIGHT_VALUE_PATTERNS: tuple[re.Pattern[str], ...] = (
    re.compile(r"(?:light[_ -]?sensor|lightsensor|light|lux|照度)[_ :=-]*([0-9]+(?:\.[0-9]+)?)", re.IGNORECASE),
    re.compile(r"(?:^|[_ -])L([0-9]+(?:\.[0-9]+)?)(?:[_ -]|\.)", re.IGNORECASE),
)


@dataclass
class ImageMetadata:
    """Image-level metadata parsed from filename."""

    filename: str
    stem: str
    suffix: str
    subject_id: str | None
    image_type: str | None
    light_sensor_value: float | None
    light_metadata_flag: str
    lighting_quality_flag: str
    uncertainty_flag: str
    notes: list[str]


def parse_light_sensor_from_filename(filename: str) -> float | None:
    """Parse light sensor value from a filename.

    Returns
    -------
    float | None
        Parsed value if found; otherwise None.

    Examples
    --------
    >>> parse_light_sensor_from_filename("001_舌上_light312.4.jpg")
    312.4
    >>> parse_light_sensor_from_filename("001_front_lux_285.png")
    285.0
    >>> parse_light_sensor_from_filename("001_front.jpg") is None
    True
    """

    name = Path(filename).name

    for pattern in LIGHT_VALUE_PATTERNS:
        match = pattern.search(name)
        if match:
            try:
                return float(match.group(1))
            except ValueError:
                return None

    return None


def infer_image_type_from_filename(filename: str) -> str | None:
    """Infer image type from filename using English and Chinese aliases."""

    lower_name = Path(filename).name.lower()

    # First handle aliases with Chinese strings or exact case-sensitive tokens.
    for alias, canonical in IMAGE_TYPE_ALIASES.items():
        if alias in filename or alias.lower() in lower_name:
            return canonical

    return None


def parse_subject_id_from_filename(filename: str) -> str | None:
    """Parse a likely subject ID from filename.

    This is intentionally conservative. It avoids assuming that all numbers are
    subject IDs because filenames may also contain light values and dates.
    """

    stem = Path(filename).stem

    # Explicit subject prefixes.
    explicit = re.search(r"(?:subject|subj|sid|id)[_ -]*([A-Za-z0-9]+)", stem, flags=re.IGNORECASE)
    if explicit:
        return explicit.group(1)

    # Fallback: first token before underscore/hyphen if it contains letters or is short numeric.
    first_token = re.split(r"[_ -]+", stem)[0]
    if first_token and not re.search(r"(light|lux)", first_token, flags=re.IGNORECASE):
        if re.fullmatch(r"[A-Za-z0-9]+", first_token):
            return first_token

    return None


def classify_lighting_quality(
    light_sensor_value: float | None,
    *,
    low_threshold: float = 50.0,
    high_threshold: float = 1000.0,
) -> str:
    """Classify lighting condition from light sensor value.

    Thresholds are demo defaults. Real thresholds should be calibrated from the
    photo app and camera environment.
    """

    if light_sensor_value is None:
        return "unknown"

    if light_sensor_value < low_threshold:
        return "possibly_too_dark"

    if light_sensor_value > high_threshold:
        return "possibly_too_bright"

    return "ok"


def build_light_metadata_flag(light_sensor_value: float | None) -> str:
    """Return whether light metadata is present."""

    return "present" if light_sensor_value is not None else "missing"


def build_uncertainty_flag(
    *,
    light_metadata_flag: str,
    lighting_quality_flag: str,
) -> tuple[str, list[str]]:
    """Convert lighting metadata status into uncertainty flag and notes."""

    notes: list[str] = []

    if light_metadata_flag == "missing":
        notes.append("light sensor value missing from filename")
        return "increase", notes

    if lighting_quality_flag != "ok":
        notes.append(f"lighting quality issue: {lighting_quality_flag}")
        return "increase", notes

    return "normal", notes


def parse_image_metadata(filename: str | Path) -> ImageMetadata:
    """Parse image metadata from filename."""

    path = Path(filename)
    light_value = parse_light_sensor_from_filename(path.name)
    light_metadata_flag = build_light_metadata_flag(light_value)
    lighting_quality_flag = classify_lighting_quality(light_value)
    uncertainty_flag, notes = build_uncertainty_flag(
        light_metadata_flag=light_metadata_flag,
        lighting_quality_flag=lighting_quality_flag,
    )

    image_type = infer_image_type_from_filename(path.name)
    if image_type is None:
        notes.append("image type could not be inferred from filename")

    subject_id = parse_subject_id_from_filename(path.name)
    if subject_id is None:
        notes.append("subject id could not be inferred from filename")

    return ImageMetadata(
        filename=path.name,
        stem=path.stem,
        suffix=path.suffix,
        subject_id=subject_id,
        image_type=image_type,
        light_sensor_value=light_value,
        light_metadata_flag=light_metadata_flag,
        lighting_quality_flag=lighting_quality_flag,
        uncertainty_flag=uncertainty_flag,
        notes=notes,
    )


def parse_metadata_for_directory(
    image_dir: str | Path,
    *,
    extensions: Iterable[str] = (".jpg", ".jpeg", ".png", ".bmp", ".webp"),
) -> list[dict]:
    """Parse filename metadata for all images in a directory."""

    image_dir = Path(image_dir)
    ext_set = {ext.lower() for ext in extensions}
    records: list[dict] = []

    for path in sorted(image_dir.iterdir()):
        if path.is_file() and path.suffix.lower() in ext_set:
            records.append(asdict(parse_image_metadata(path.name)))

    return records


def main() -> None:
    """Command-line interface.

    Examples:
        python src/image_preprocessing/lighting_metadata_parser.py \
            --filename synthetic_001_舌上_light312.4.jpg

        python src/image_preprocessing/lighting_metadata_parser.py \
            --directory demo/images \
            --output reports/image_metadata.csv
    """

    import argparse
    import json
    import pandas as pd

    parser = argparse.ArgumentParser(description="Parse light sensor metadata from image filenames.")
    group = parser.add_mutually_exclusive_group(required=True)
    group.add_argument("--filename", help="Single filename to parse.")
    group.add_argument("--directory", help="Directory of image files to parse.")
    parser.add_argument("--output", help="Optional CSV output path for directory mode.")
    args = parser.parse_args()

    if args.filename:
        print(json.dumps(asdict(parse_image_metadata(args.filename)), indent=2, ensure_ascii=False))
        return

    records = parse_metadata_for_directory(args.directory)
    if args.output:
        output_path = Path(args.output)
        output_path.parent.mkdir(parents=True, exist_ok=True)
        pd.DataFrame(records).to_csv(output_path, index=False)
    else:
        print(json.dumps(records, indent=2, ensure_ascii=False))


if __name__ == "__main__":
    main()
