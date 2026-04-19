#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
PathoScan Live API Demo - Tests the actual running API
"""

import asyncio
import httpx
import sys

async def main():
    print("""
====================================================================
  PATHOSCAN - LIVE API DEMO
====================================================================

Make sure to run 'python main.py' in another terminal first!

Connecting to API...""")
    
    try:
        async with httpx.AsyncClient(timeout=5.0) as client:
            response = await client.get("http://localhost:8000/health")
            
            if response.status_code == 200:
                health = response.json()
                print("\nSUCCESS - API is running!\n")
                print(f"Status: {health.get('status')}")
                print(f"Ollama: {health.get('ollama')}")
                print(f"Model Loaded: {health.get('model_loaded')}")
                print(f"Model Name: {health.get('model_name')}")
                print(f"Offline Capable: {health.get('offline_capable')}")
                
                print("""
====================================================================

API IS READY - Next Steps:

1. Test the API with an image:
   
   curl -X POST http://localhost:8000/analyze \\
        -F 'file=@your_image.jpg'

2. Or use Python:
   
   import httpx
   
   with open('image.jpg', 'rb') as f:
       response = httpx.post(
           'http://localhost:8000/analyze',
           files={'file': f}
       )
   print(response.json())

3. Visit interactive docs:
   
   http://localhost:8000/docs

====================================================================
""")
                return 0
            else:
                print(f"\nERROR: API returned status {response.status_code}")
                return 1
    
    except httpx.ConnectError:
        print("\nERROR: Cannot connect to API!")
        print("\nMake sure to run:")
        print("  1. python main.py  (in another terminal)")
        print("  2. Ollama must be running on port 11434")
        return 1
    
    except Exception as e:
        print(f"\nERROR: {e}")
        return 1

if __name__ == "__main__":
    exit_code = asyncio.run(main())
    sys.exit(exit_code)
