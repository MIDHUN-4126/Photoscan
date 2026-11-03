"""Download the Kaggle ISIC 2019 dataset and prepare it for local training."""

from __future__ import annotations

import argparse
from pathlib import Path

from prepare_isic2019 import prepare_dataset


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--output-dir", type=Path, default=Path("data/isic2019"))
    parser.add_argument("--mode", choices=("copy", "hardlink"), default="copy")
    parser.add_argument("--force-download", action="store_true")
    return parser.parse_args()


def find_dataset_files(download_dir: Path) -> tuple[Path, Path]:
    labels = next(download_dir.rglob("ISIC_2019_Training_GroundTruth.csv"), None)
    if labels is None:
        raise FileNotFoundError(
            f"Ground-truth CSV was not found below {download_dir}. "
            "Inspect the Kaggle dataset version and file names."
        )
    image_dirs = [
        path for path in download_dir.rglob("*")
        if path.is_dir() and any(path.glob("*.jpg"))
    ]
    if not image_dirs:
        raise FileNotFoundError(
            f"No JPG image directory was found below {download_dir}."
        )
    return image_dirs[0], labels


def main() -> None:
    args = parse_args()
    try:
        import kagglehub
    except ImportError as exc:
        raise SystemExit(
            "Install KaggleHub first: python -m pip install kagglehub"
        ) from exc

    download_dir = Path(
        kagglehub.dataset_download(
            "andrewmvd/isic-2019",
            force_download=args.force_download,
        )
    )
    images_dir, labels = find_dataset_files(download_dir)
    print(f"KaggleHub cache: {download_dir}")
    print(f"Images: {images_dir}")
    print(f"Labels: {labels}")
    prepare_dataset(images_dir, labels, args.output_dir, args.mode)


if __name__ == "__main__":
    main()
