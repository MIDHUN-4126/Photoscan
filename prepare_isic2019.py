r"""Prepare ISIC 2019 images and one-hot labels for train_cnn.py.

Download the official ISIC 2019 training images and
ISIC_2019_Training_GroundTruth.csv, then run:

    python prepare_isic2019.py --images-dir data\ISIC_2019_Training_Input ^
      --labels data\ISIC_2019_Training_GroundTruth.csv --output-dir data\isic2019

The output is an ImageFolder-compatible directory with one folder per diagnosis.
"""

from __future__ import annotations

import argparse
import csv
import shutil
from pathlib import Path


CLASS_NAMES = ("MEL", "NV", "BCC", "AKIEC", "BKL", "DF", "VASC", "SCC")


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--images-dir", type=Path, required=True)
    parser.add_argument("--labels", type=Path, required=True)
    parser.add_argument("--output-dir", type=Path, required=True)
    parser.add_argument(
        "--mode",
        choices=("copy", "hardlink"),
        default="copy",
        help="Copy images, or create same-volume hard links to save disk space.",
    )
    return parser.parse_args()


def diagnosis(row: dict[str, str], image_id: str) -> str:
    present = [name for name in CLASS_NAMES if row.get(name, "").strip() == "1.0"]
    if len(present) != 1:
        raise ValueError(f"{image_id} does not have exactly one positive diagnosis: {present}")
    return present[0]


def main() -> None:
    args = parse_args()
    if not args.images_dir.is_dir():
        raise FileNotFoundError(f"Image directory not found: {args.images_dir}")
    if not args.labels.is_file():
        raise FileNotFoundError(f"Labels CSV not found: {args.labels}")

    for class_name in CLASS_NAMES:
        (args.output_dir / class_name).mkdir(parents=True, exist_ok=True)

    processed = missing = 0
    with args.labels.open(newline="", encoding="utf-8-sig") as file:
        reader = csv.DictReader(file)
        required = {"image"} | set(CLASS_NAMES)
        if not required.issubset(reader.fieldnames or set()):
            raise ValueError(
                f"Labels must contain columns {sorted(required)}; "
                f"found {reader.fieldnames}"
            )
        for row in reader:
            image_id = row["image"].strip()
            source = args.images_dir / f"{image_id}.jpg"
            if not source.is_file():
                missing += 1
                continue
            target = args.output_dir / diagnosis(row, image_id) / source.name
            if target.exists():
                continue
            if args.mode == "hardlink":
                target.hardlink_to(source)
            else:
                shutil.copy2(source, target)
            processed += 1

    print(f"Prepared {processed} images in {args.output_dir}")
    if missing:
        print(f"Skipped {missing} label rows without a matching .jpg file")


if __name__ == "__main__":
    main()
