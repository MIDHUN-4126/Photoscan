"""Train PathoScan's EfficientNet-B0 CNN on an ImageFolder dataset.

Expected layout:
    data/
      MEL/*.jpg
      NV/*.jpg
      BCC/*.jpg
      ...
"""

from __future__ import annotations

import argparse
import json
from pathlib import Path

import torch
from torch import nn
from torch.utils.data import DataLoader, random_split
from torchvision import datasets, transforms

from classifier import CLASS_NAMES, build_model


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--data-dir", type=Path, required=True)
    parser.add_argument("--output", type=Path, default=Path("models/pathoscan_efficientnet_b0.pt"))
    parser.add_argument("--epochs", type=int, default=12)
    parser.add_argument("--batch-size", type=int, default=32)
    parser.add_argument("--learning-rate", type=float, default=3e-4)
    parser.add_argument("--val-ratio", type=float, default=0.2)
    parser.add_argument("--seed", type=int, default=42)
    return parser.parse_args()


def main() -> None:
    args = parse_args()
    if not 0 < args.val_ratio < 1:
        raise ValueError("--val-ratio must be between 0 and 1.")
    torch.manual_seed(args.seed)
    device = torch.device("cuda" if torch.cuda.is_available() else "cpu")

    train_transform = transforms.Compose(
        [
            transforms.Resize((224, 224)),
            transforms.RandomHorizontalFlip(),
            transforms.RandomVerticalFlip(),
            transforms.RandomRotation(20),
            transforms.ColorJitter(brightness=0.15, contrast=0.15, saturation=0.15),
            transforms.ToTensor(),
            transforms.Normalize((0.485, 0.456, 0.406), (0.229, 0.224, 0.225)),
        ]
    )
    eval_transform = transforms.Compose(
        [
            transforms.Resize((224, 224)),
            transforms.ToTensor(),
            transforms.Normalize((0.485, 0.456, 0.406), (0.229, 0.224, 0.225)),
        ]
    )
    base_dataset = datasets.ImageFolder(args.data_dir)
    unknown_classes = set(base_dataset.classes) - set(CLASS_NAMES)
    if unknown_classes:
        raise ValueError(f"Unexpected class folders: {sorted(unknown_classes)}")
    if len(base_dataset) < 10:
        raise ValueError("At least 10 labelled images are required.")
    class_to_idx = base_dataset.class_to_idx
    missing = set(CLASS_NAMES) - set(class_to_idx)
    if missing:
        raise ValueError(f"Missing class folders: {sorted(missing)}")

    val_size = max(1, int(len(base_dataset) * args.val_ratio))
    train_size = len(base_dataset) - val_size
    generator = torch.Generator().manual_seed(args.seed)
    train_indices, val_indices = random_split(
        range(len(base_dataset)), [train_size, val_size], generator=generator
    )
    train_dataset = datasets.ImageFolder(args.data_dir, transform=train_transform)
    val_dataset = datasets.ImageFolder(args.data_dir, transform=eval_transform)
    train_subset = torch.utils.data.Subset(train_dataset, train_indices.indices)
    val_subset = torch.utils.data.Subset(val_dataset, val_indices.indices)
    train_loader = DataLoader(train_subset, batch_size=args.batch_size, shuffle=True, num_workers=0)
    val_loader = DataLoader(val_subset, batch_size=args.batch_size, shuffle=False, num_workers=0)

    model = build_model(len(CLASS_NAMES), pretrained=True).to(device)
    train_labels = [base_dataset.targets[index] for index in train_indices.indices]
    label_counts = torch.bincount(
        torch.tensor(train_labels), minlength=len(base_dataset.classes)
    ).float()
    class_weights = label_counts.sum() / (len(label_counts) * label_counts.clamp_min(1))
    criterion = nn.CrossEntropyLoss(weight=class_weights.to(device))
    optimizer = torch.optim.AdamW(model.parameters(), lr=args.learning_rate, weight_decay=1e-4)
    best_accuracy = -1.0
    for epoch in range(args.epochs):
        model.train()
        for images, labels in train_loader:
            images, labels = images.to(device), labels.to(device)
            optimizer.zero_grad(set_to_none=True)
            criterion(model(images), labels).backward()
            optimizer.step()

        model.eval()
        correct = total = 0
        with torch.inference_mode():
            for images, labels in val_loader:
                predictions = model(images.to(device)).argmax(dim=1).cpu()
                correct += int((predictions == labels).sum())
                total += labels.numel()
        accuracy = correct / total
        print(f"epoch {epoch + 1}/{args.epochs}: validation_accuracy={accuracy:.4f}")
        if accuracy > best_accuracy:
            best_accuracy = accuracy
            args.output.parent.mkdir(parents=True, exist_ok=True)
            torch.save(
                {
                    "model_state_dict": model.state_dict(),
                    "class_names": list(base_dataset.classes),
                    "validation_accuracy": accuracy,
                    "dataset_classes": class_to_idx,
                },
                args.output,
            )

    print(json.dumps({"checkpoint": str(args.output), "best_validation_accuracy": best_accuracy}))


if __name__ == "__main__":
    main()
