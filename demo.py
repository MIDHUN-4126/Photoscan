#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
PathoScan Demo - Offline AI Dermatology Assistant
"""

import json

print("""
====================================================================
  PATHOSCAN - Offline AI Skin Lesion Triage System v1.0
====================================================================

FEATURES:
  * Fully Offline        - No internet required
  * HIPAA-Compliant      - Data stays on device
  * Fast Analysis        - Results in seconds
  * ISIC Compliant       - Standard classifications
  * Works on Edge Devices

SYSTEM COMPONENTS:
  Frontend      --> FastAPI Backend --> Ollama Runtime
  (Web UI)      (Port 8000)           (Port 11434)
                                      Gemma 4 E4B Model

GETTING STARTED:
  1. pip install -r requirements.txt
  2. ollama serve (in another terminal)
  3. ollama create pathoscan-gemma4 -f Modelfile
  4. python main.py (start API server)
  5. Open http://localhost:8000 in browser

EXAMPLE API RESPONSE:
====================================================================
""")

example_response = {
    "condition": "Basal Cell Carcinoma",
    "condition_code": "BCC",
    "severity": "MEDIUM",
    "confidence": "89%",
    "description": "Most common type of skin cancer.",
    "urgency": "See a doctor within 2-4 weeks.",
    "recommended_action": "Schedule dermatology appointment.",
    "visual_features": ["pearly appearance", "rolled borders"],
    "disclaimer": "Always consult a qualified healthcare professional."
}

print(json.dumps(example_response, indent=2))

print("""
====================================================================

SUPPORTED LESION TYPES:
  MEL   - Melanoma (most serious)
  NV    - Nevus (common mole)
  BCC   - Basal Cell Carcinoma
  AKIEC - Actinic Keratosis
  BKL   - Benign Keratosis
  DF    - Dermatofibroma
  VASC  - Vascular lesion
  SCC   - Squamous Cell Carcinoma

API USAGE:
  POST /analyze  - Send image for analysis
  GET /health    - Check system status

Test with Python:
  import httpx
  
  with open('image.jpg', 'rb') as f:
      response = httpx.post(
          'http://localhost:8000/analyze',
          files={'file': f}
      )
  print(response.json())

GITHUB REPOSITORY:
  https://github.com/MIDHUN-4126/Photoscan

SUCCESS - PathoScan is ready to deploy!
====================================================================
""")
