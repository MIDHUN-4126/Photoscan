"""Local CNN inference for PathoScan skin-lesion classification."""

from __future__ import annotations

from pathlib import Path
from typing import Any

from PIL import Image
import torch
from torchvision import models, transforms


CLASS_NAMES = ("MEL", "NV", "BCC", "AKIEC", "BKL", "DF", "VASC", "SCC")
CLASS_LABELS = {
    "MEL": ("Melanoma", "HIGH", "Seek dermatology care promptly."),
    "NV": ("Nevus (common mole)", "LOW", "Arrange routine clinical review if it changes."),
    "BCC": ("Basal Cell Carcinoma", "MEDIUM", "Arrange a dermatology appointment."),
    "AKIEC": ("Actinic Keratosis", "MEDIUM", "Arrange clinical review for treatment."),
    "BKL": ("Benign Keratosis", "LOW", "Arrange routine clinical review if it changes."),
    "DF": ("Dermatofibroma", "LOW", "Arrange routine clinical review if it changes."),
    "VASC": ("Vascular Lesion", "MEDIUM", "Arrange a clinical review."),
    "SCC": ("Squamous Cell Carcinoma", "HIGH", "Seek dermatology care promptly."),
}

DISCLAIMER = (
    "This is an AI-assisted screening tool. Always consult a qualified healthcare "
    "professional for diagnosis and treatment."
)


def build_model(num_classes: int = len(CLASS_NAMES), pretrained: bool = False) -> torch.nn.Module:
    """Build the EfficientNet-B0 CNN used by training and inference."""
    weights = models.EfficientNet_B0_Weights.IMAGENET1K_V1 if pretrained else None
    model = models.efficientnet_b0(weights=weights)
    model.classifier[1] = torch.nn.Linear(model.classifier[1].in_features, num_classes)
    return model


def _transform() -> transforms.Compose:
    return transforms.Compose(
        [
            transforms.Resize(256),
            transforms.CenterCrop(224),
            transforms.ToTensor(),
            transforms.Normalize(
                mean=(0.485, 0.456, 0.406),
                std=(0.229, 0.224, 0.225),
            ),
        ]
    )


class SkinLesionClassifier:
    """Loads a trained checkpoint once and predicts the most likely lesion class."""

    def __init__(self, checkpoint_path: str | Path, device: str | None = None) -> None:
        self.checkpoint_path = Path(checkpoint_path)
        if not self.checkpoint_path.is_file():
            raise FileNotFoundError(
                f"CNN checkpoint not found: {self.checkpoint_path}. "
                "Train it with train_cnn.py or set PATHOSCAN_CNN_MODEL."
            )
        self.device = torch.device(device or ("cuda" if torch.cuda.is_available() else "cpu"))
        checkpoint: dict[str, Any] = torch.load(
            self.checkpoint_path, map_location=self.device, weights_only=False
        )
        class_names = tuple(checkpoint.get("class_names", CLASS_NAMES))
        if not class_names:
            raise ValueError("CNN checkpoint contains no class names.")
        self.class_names = class_names
        self.model = build_model(len(class_names))
        state_dict = checkpoint.get("model_state_dict", checkpoint)
        self.model.load_state_dict(state_dict)
        self.model.to(self.device)
        self.model.eval()
        self.transform = _transform()

    @torch.inference_mode()
    def predict(self, image: Image.Image) -> dict[str, Any]:
        tensor = self.transform(image.convert("RGB")).unsqueeze(0).to(self.device)
        probabilities = torch.softmax(self.model(tensor), dim=1)[0]
        confidence, index = torch.max(probabilities, dim=0)
        code = self.class_names[index.item()]
        label, severity, action = CLASS_LABELS.get(
            code, (code, "MEDIUM", "Arrange a clinical review.")
        )
        confidence_percent = round(float(confidence) * 100)
        return {
            "condition": label,
            "condition_code": code,
            "severity": severity,
            "confidence": f"{confidence_percent}%",
            "description": (
                f"The CNN classified the image as {label}. This result is a screening "
                "estimate, not a diagnosis."
            ),
            "urgency": "Prompt review recommended." if severity == "HIGH" else "Routine review recommended.",
            "recommended_action": action,
            "visual_features": [],
            "disclaimer": DISCLAIMER,
        }
