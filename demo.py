"""
PathoScan Demo - Interactive demonstration of the offline skin lesion triage system
"""

import asyncio
import json
import sys
from pathlib import Path

print("""
╔════════════════════════════════════════════════════════════════╗
║           🔬 PATHOSCAN - Offline AI Dermatology Demo          ║
║                Skin Lesion Triage System v1.0                 ║
╚════════════════════════════════════════════════════════════════╝

PathoScan is a fully offline AI dermatology assistant that helps
community health workers identify and triage skin lesions.

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
 FEATURES
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

✓ Fully Offline     - No internet connection required
✓ Edge Device      - Runs on laptop or local hardware
✓ HIPAA-Ready      - No data leaves the device
✓ Fast Analysis    - Results in seconds
✓ ISIC Compliant   - Classifies using standard skin lesion codes
✓ Structured Output - JSON responses for integration

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
 SYSTEM ARCHITECTURE
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

┌─────────────────────────────────────────────────────────────┐
│                      OFFLINE DEVICE                         │
│                                                             │
│  ┌──────────────┐    ┌──────────────┐  ┌────────────────┐  │
│  │   Frontend   │───→│  FastAPI     │─→│    Ollama      │  │
│  │  (HTML/JS)   │    │  Backend     │  │    Runtime     │  │
│  │  Camera +    │←───│  Port 8000   │←─│  Port 11434    │  │
│  │  Result UI   │    │              │  │                │  │
│  └──────────────┘    │ Receives:    │  │ PathoScan      │  │
│                      │ - Image file │  │ (Gemma 4 E4B)  │  │
│                      │ - Returns:   │  │                │  │
│                      │ - Condition  │  │ Fine-tuned on  │  │
│                      │ - Severity   │  │ ISIC dataset   │  │
│                      │ - Confidence │  │                │  │
│  └──────────────────┘    └────────────┘  └────────────────┘  │
│                                                             │
└─────────────────────────────────────────────────────────────┘

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
 GETTING STARTED
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

1. INSTALL DEPENDENCIES:
   pip install -r requirements.txt

2. START OLLAMA (required - runs the model):
   - Download from: https://ollama.ai
   - Run: ollama serve

3. LOAD THE MODEL:
   ollama create pathoscan-gemma4 -f Modelfile

4. START THE API SERVER:
   python main.py

5. OPEN IN BROWSER:
   http://localhost:8000
   
   (API docs available at http://localhost:8000/docs)

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
 EXAMPLE API RESPONSE
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

POST /analyze
Content-Type: multipart/form-data

Response:
""")

example_response = {
    "condition": "Basal Cell Carcinoma",
    "condition_code": "BCC",
    "severity": "MEDIUM",
    "confidence": "89%",
    "description": "Most common type of skin cancer. Rarely metastasizes but causes local tissue damage.",
    "urgency": "See a doctor within 2–4 weeks.",
    "recommended_action": "Schedule dermatology appointment. Surgical removal is typically curative.",
    "visual_features": ["pearly appearance", "rolled borders", "central depression"],
    "disclaimer": "AI-assisted screening tool. Always consult a qualified healthcare professional."
}

print(json.dumps(example_response, indent=2))

print("""
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
 LESION CLASSIFICATIONS
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

PathoScan can identify:

  MEL  - Melanoma (most serious)
  NV   - Nevus (common mole)
  BCC  - Basal Cell Carcinoma
  AKIEC- Actinic Keratosis
  BKL  - Benign Keratosis
  DF   - Dermatofibroma
  VASC - Vascular lesion
  SCC  - Squamous Cell Carcinoma

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
 DEPLOYMENT OPTIONS
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

✓ Local Laptop       - Fastest, full offline capability
✓ Raspberry Pi       - Low-power edge device
✓ Docker Container   - Easy deployment to any system
✓ Cloud (Optional)   - Can be deployed to cloud with models

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
 FOR DEVELOPERS
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

API Endpoints:

  GET  /health           - Check system status
  POST /analyze          - Analyze skin lesion image
  
  
Test with cURL:

  curl -X POST http://localhost:8000/analyze \\
    -F "file=@path/to/image.jpg"

Test with Python:

  import httpx
  
  with open("image.jpg", "rb") as f:
      response = httpx.post(
          "http://localhost:8000/analyze",
          files={"file": f}
      )
  print(response.json())

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
 GITHUB REPOSITORY
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

🔗 GitHub: https://github.com/[YOUR_USERNAME]/pathoscan
📄 License: Apache 2.0
🎓 Track: Gemma 4 Good Hackathon 2026 - Health & Sciences

To push to GitHub:
  bash GITHUB_SETUP.sh

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
 SUPPORT & RESOURCES
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

📖 Ollama Docs:         https://ollama.ai
🤗 Gemma Model:         https://huggingface.co/google/gemma-7b
🔬 ISIC Dataset:        https://www.isic-archive.com
🏥 FastAPI Docs:        https://fastapi.tiangolo.com

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

✓ PathoScan is ready to deploy!
✓ No internet required - Full offline capability
✓ HIPAA-compliant - All data remains on-device
✓ Fast inference - Results in seconds

Start the server: python main.py
Access at: http://localhost:8000

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
""")
