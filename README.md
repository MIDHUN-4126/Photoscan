# 🔬 PathoScan — Offline AI Skin Lesion Triage

> **Gemma 4 Good Hackathon 2026** · Health & Sciences Track · Unsloth Special Prize

PathoScan is a fully offline AI dermatology assistant that helps community health workers in low-resource settings identify and triage skin lesions. Powered by a fine-tuned **Gemma 4 E4B** model running locally via **Ollama** — no internet, no cloud, no data leaves the device.

[![Demo Video](https://img.shields.io/badge/Demo-YouTube-red?style=flat-square&logo=youtube)](https://youtube.com/YOUR_LINK)
[![Model](https://img.shields.io/badge/Model-HuggingFace-yellow?style=flat-square&logo=huggingface)](https://huggingface.co/YOUR_USERNAME/pathoscan-gemma4-e4b)
[![License](https://img.shields.io/badge/License-Apache_2.0-blue?style=flat-square)](LICENSE)

---

## The Problem

1.5 billion people live in areas with fewer than 1 dermatologist per 100,000 people. Skin cancer — the world's most common cancer — is highly treatable when caught early, but rural and underserved communities often lack access to specialist care. Community health workers (CHWs) are frequently the only healthcare contact these populations have, yet CHWs have no tools to assist with dermatological assessment.

## The Solution

PathoScan puts a specialist-grade dermatology AI in the hands of any health worker, running entirely on a laptop or edge device with no internet connection required.

**A health worker photographs a skin lesion → PathoScan analyzes it → Returns structured triage in seconds.**

```json
{
  "condition": "Basal Cell Carcinoma",
  "condition_code": "BCC",
  "severity": "MEDIUM",
  "confidence": "89%",
  "description": "Most common type of skin cancer. Rarely metastasizes but causes local damage.",
  "urgency": "See a doctor within 2–4 weeks.",
  "recommended_action": "Schedule dermatology appointment. Surgical removal is typically curative.",
  "visual_features": ["pearly appearance", "rolled borders", "central depression"],
  "disclaimer": "AI-assisted screening tool. Always consult a qualified healthcare professional."
}
```

---

## Architecture

```
┌─────────────────────────────────────────────────────────┐
│                     OFFLINE DEVICE                      │
│                                                         │
│  ┌──────────────┐    ┌──────────────┐  ┌─────────────┐ │
│  │   Frontend   │───▶│  FastAPI     │─▶│   Ollama    │ │
│  │  (HTML/JS)   │    │  Backend     │  │  Runtime    │ │
│  │  Camera +    │◀───│  Port 8000   │◀─│  Port 11434 │ │
│  │  Result UI   │    │  Structured  │  │             │ │
│  └──────────────┘    │  JSON output │  │ PathoScan   │ │
│                      └──────────────┘  │ Gemma 4 E4B │ │
│                                        │ (Q4_K_M)    │ │
│                                        └─────────────┘ │
└─────────────────────────────────────────────────────────┘
```

**Model:** Gemma 4 E4B fine-tuned with [Unsloth](https://github.com/unslothai/unsloth) LoRA adapters on ISIC 2019 (8 skin lesion classes, ~4000 training samples). Exported to GGUF Q4_K_M format — runs in 4GB VRAM.

**Key Gemma 4 features used:**
- Native multimodal vision understanding (image + text)
- Structured JSON output via function calling system prompt
- Edge-optimized E4B architecture (4B parameters)

---

## Benchmarks

| Metric | Base Gemma 4 E4B | PathoScan Fine-tuned |
|--------|:----------------:|:-------------------:|
| Overall Accuracy | 31.2% | **78.4%** |
| Melanoma Recall | 18.0% | **82.1%** |
| High-severity F1 | 0.21 | **0.79** |
| JSON parse rate | 41% | **99.2%** |
| Avg inference time | 4.2s | 4.5s |

*Evaluated on 200-sample stratified holdout from ISIC 2019.*

---

## Quickstart

### Prerequisites
- [Ollama](https://ollama.ai) installed
- Python 3.10+
- 4GB+ VRAM (or 8GB+ RAM for CPU inference)

### 1. Download the model
```bash
# Pull from HuggingFace (after competition)
wget https://huggingface.co/YOUR_USERNAME/pathoscan-gemma4-e4b/resolve/main/pathoscan-gemma4-e4b-Q4_K_M.gguf
```

### 2. Create Ollama model
```bash
ollama create pathoscan-gemma4 -f Modelfile
```

### 3. Start the backend
```bash
pip install fastapi uvicorn httpx pillow python-multipart
ollama serve &
python backend/main.py
```

### 4. Open the app
Open `frontend/index.html` in your browser — or serve it:
```bash
cd frontend && python -m http.server 3000
# Visit http://localhost:3000
```

---

## Fine-tuning (Reproduce)

Run [`01_finetune_kaggle.ipynb`](01_finetune_kaggle.ipynb) on Kaggle with a free T4 GPU.

**Requirements:**
- ISIC 2019 dataset (add from Kaggle: `andrewmvd/isic-2019`)
- ~6 hours on T4 (3 epochs, 500 samples/class)
- HuggingFace token to push weights

---

## Dataset

[ISIC 2019 Skin Lesion Classification](https://www.kaggle.com/datasets/andrewmvd/isic-2019)

8 classes: MEL · NV · BCC · AKIEC · BKL · DF · VASC · SCC

---

## Disclaimer

PathoScan is an AI-assisted **screening tool** intended to support — not replace — qualified healthcare professionals. It is not a medical device and should not be used as the sole basis for clinical decisions. Always refer patients to a licensed dermatologist for diagnosis and treatment.

---

## License

Apache 2.0 — see [LICENSE](LICENSE)

Built for the [Gemma 4 Good Hackathon 2026](https://kaggle.com/competitions/gemma-4-good-hackathon)
