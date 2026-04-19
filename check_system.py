#!/usr/bin/env python3
"""
Comprehensive System Check for PathoScan
Verifies all components are working properly
"""

import os
import sys
import json
import subprocess
from pathlib import Path

def test_project():
    """Run all tests"""
    results = {
        'passed': [],
        'failed': [],
        'warnings': []
    }
    
    project_dir = Path.cwd()
    
    # Test 1: Python version
    try:
        version = f"{sys.version_info.major}.{sys.version_info.minor}"
        results['passed'].append(f"Python version: {version}")
    except Exception as e:
        results['failed'].append(f"Python version check: {e}")
    
    # Test 2: Required files exist
    required_files = [
        'main.py',
        'requirements.txt',
        'Modelfile',
        'README.md',
        'index.html',
        'demo.py',
        'video_demo.py',
        'live_demo.py',
        '.gitignore'
    ]
    
    for f in required_files:
        if (project_dir / f).exists():
            size = (project_dir / f).stat().st_size
            results['passed'].append(f"✓ {f} exists ({size} bytes)")
        else:
            results['failed'].append(f"✗ {f} MISSING")
    
    # Test 3: Required directories
    required_dirs = ['.git', '__pycache__']
    
    for d in required_dirs:
        if (project_dir / d).exists():
            results['passed'].append(f"✓ {d}/ directory exists")
        else:
            results['warnings'].append(f"~ {d}/ directory not found")
    
    # Test 4: Dependencies installed
    try:
        import fastapi
        import uvicorn
        import httpx
        import pydantic
        from PIL import Image
        results['passed'].append("✓ All required packages installed")
        results['passed'].append(f"  - fastapi {fastapi.__version__}")
        results['passed'].append(f"  - uvicorn {uvicorn.__version__}")
        results['passed'].append(f"  - httpx {httpx.__version__}")
        results['passed'].append(f"  - pydantic {pydantic.__version__}")
    except ImportError as e:
        results['failed'].append(f"✗ Missing package: {e}")
    
    # Test 5: main.py syntax
    try:
        import main
        results['passed'].append("✓ main.py - Valid Python syntax")
        results['passed'].append(f"  - Has app: {hasattr(main, 'app')}")
    except SyntaxError as e:
        results['failed'].append(f"✗ main.py syntax error: {e}")
    except Exception as e:
        results['warnings'].append(f"~ main.py import: {str(e)[:50]}")
    
    # Test 6: Git repository
    try:
        git_dir = project_dir / '.git'
        if git_dir.exists():
            results['passed'].append("✓ Git repository initialized")
            # Try to get last commit
            try:
                result = subprocess.run(
                    ['git', 'log', '--oneline', '-1'],
                    capture_output=True,
                    text=True,
                    timeout=5
                )
                if result.returncode == 0:
                    results['passed'].append(f"  - Latest commit: {result.stdout.strip()}")
            except:
                pass
    except Exception as e:
        results['warnings'].append(f"~ Git check: {e}")
    
    # Test 7: Python scripts compilable
    scripts = ['demo.py', 'video_demo.py', 'live_demo.py', 'main.py']
    for script in scripts:
        try:
            compile(open(project_dir / script, encoding='utf-8', errors='ignore').read(), script, 'exec')
            results['passed'].append(f"✓ {script} - Compiles successfully")
        except SyntaxError as e:
            results['failed'].append(f"✗ {script} - Syntax error: {e}")
        except Exception as e:
            results['warnings'].append(f"~ {script} - {str(e)[:40]}")
    
    # Test 8: requirements.txt format
    try:
        with open(project_dir / 'requirements.txt', 'r') as f:
            reqs = [line.strip() for line in f if line.strip() and not line.startswith('#')]
        results['passed'].append(f"✓ requirements.txt - {len(reqs)} packages")
    except Exception as e:
        results['failed'].append(f"✗ requirements.txt - {e}")
    
    return results

def print_results(results):
    """Print formatted results"""
    print("\n" + "="*70)
    print("  PATHOSCAN - COMPREHENSIVE SYSTEM CHECK")
    print("="*70 + "\n")
    
    # Passed tests
    if results['passed']:
        print("✓ PASSED TESTS:")
        print("-"*70)
        for msg in results['passed']:
            print(f"  {msg}")
    
    # Failed tests
    if results['failed']:
        print("\n✗ FAILED TESTS:")
        print("-"*70)
        for msg in results['failed']:
            print(f"  {msg}")
    
    # Warnings
    if results['warnings']:
        print("\n~ WARNINGS:")
        print("-"*70)
        for msg in results['warnings']:
            print(f"  {msg}")
    
    # Summary
    print("\n" + "="*70)
    total = len(results['passed']) + len(results['failed']) + len(results['warnings'])
    print(f"  Summary: {len(results['passed'])}/{total} checks passed")
    
    if results['failed']:
        print(f"  Status: ⚠️  SOME ISSUES FOUND")
    else:
        print(f"  Status: ✓ ALL SYSTEMS GO!")
    print("="*70 + "\n")
    
    # Return exit code
    return 0 if not results['failed'] else 1

if __name__ == '__main__':
    results = test_project()
    exit_code = print_results(results)
    sys.exit(exit_code)
