#!/usr/bin/env python3
"""
PathoScan Live Demo - Tests the actual API
Run this while the server is running: python main.py
"""

import asyncio
import httpx
import json
import sys
from pathlib import Path

async def main():
    print("\n" + "="*70)
    print("  PATHOSCAN - LIVE API DEMO")
    print("="*70)
    
    # Configuration
    API_URL = "http://localhost:8000"
    
    print("\n1. Testing API Health...")
    print("-" * 70)
    
    try:
        async with httpx.AsyncClient(timeout=5.0) as client:
            response = await client.get(f"{API_URL}/health")
            
            if response.status_code == 200:
                health = response.json()
                print("✓ API is running!")
                print(f"  Status: {health.get('status')}")
                print(f"  Ollama: {health.get('ollama')}")
                print(f"  Model Loaded: {health.get('model_loaded')}")
                print(f"  Model Name: {health.get('model_name')}")
                print(f"  Offline Capable: {health.get('offline_capable')}")
            else:
                print(f"✗ API returned error: {response.status_code}")
                sys.exit(1)
    
    except httpx.ConnectError:
        print("✗ Cannot connect to API!")
        print("\nMake sure to run: python main.py")
        print("In another terminal")
        sys.exit(1)
    
    except Exception as e:
        print(f"✗ Error: {e}")
        sys.exit(1)
    
    print("\n2. API Status")
    print("-" * 70)
    print("✓ Server is ready to analyze images!")
    print("\nTo test the /analyze endpoint:")
    print("  curl -X POST http://localhost:8000/analyze \\")
    print("       -F 'file=@your_image.jpg'")
    print("\nOr use Python:")
    print("""
  import httpx
  
  with open('image.jpg', 'rb') as f:
      response = httpx.post(
          'http://localhost:8000/analyze',
          files={'file': f}
      )
  print(response.json())
    """)
    
    print("\n3. API Documentation")
    print("-" * 70)
    print("Visit: http://localhost:8000/docs")
    print("For interactive API testing with Swagger UI")
    
    print("\n" + "="*70)
    print("  ✓ Demo Complete!")
    print("="*70 + "\n")

if __name__ == "__main__":
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        print("\n\nDemo interrupted by user")
