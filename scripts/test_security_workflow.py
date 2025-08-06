#!/usr/bin/env python3
"""
Local test script to simulate the security-scan.yml workflow
This allows testing the workflow steps locally without Docker/act
"""

import subprocess
import sys
import os
from pathlib import Path
import json
from datetime import datetime

def run_command(cmd, description):
    """Run a command and return success status"""
    print(f"\n🔧 {description}")
    print(f"Running: {cmd}")
    try:
        # Use shlex to safely parse shell commands
        import shlex
        if isinstance(cmd, str):
            cmd_parts = shlex.split(cmd)
        else:
            cmd_parts = cmd
        
        result = subprocess.run(cmd_parts, shell=False, capture_output=True, text=True)
        if result.returncode == 0:
            print(f"✅ {description} - SUCCESS")
            if result.stdout.strip():
                print(f"Output: {result.stdout.strip()}")
            return True
        else:
            print(f"❌ {description} - FAILED")
            print(f"Error: {result.stderr.strip()}")
            return False
    except Exception as e:
        print(f"❌ {description} - ERROR: {e}")
        return False

def test_security_scan_workflow():
    """Test the security-scan workflow steps locally"""
    print("🚀 Testing Security Scan Workflow Locally")
    print("=" * 50)
    
    # Track results
    results = {
        "security_scan": False,
        "code_quality": False,
        "dependency_update": False,
        "build_test": False
    }
    
    # Step 1: Security Vulnerability Scan
    print("\n📊 STEP 1: Security Vulnerability Scan")
    print("-" * 30)
    
    # Check if Safety CLI action would work (simulate)
    print("🔍 Simulating Safety CLI action...")
    print("✅ Safety CLI action would run with SAFETY_API_KEY")
    
    # Run Bandit
    results["security_scan"] = run_command(
        "bandit -r src/ -f json -o bandit-report.json",
        "Bandit security scan"
    )
    
    # Run Semgrep
    results["security_scan"] = run_command(
        "semgrep ci --config auto --json --output semgrep-report.json",
        "Semgrep static analysis"
    ) and results["security_scan"]
    
    # Run pip-audit
    results["security_scan"] = run_command(
        "pip-audit --format json --output pip-audit-report.json",
        "pip-audit vulnerability check"
    ) and results["security_scan"]
    
    # Step 2: Code Quality & Testing
    print("\n📊 STEP 2: Code Quality & Testing")
    print("-" * 30)
    
    # Run Black
    results["code_quality"] = run_command(
        "black --check --diff src/ tests/ main.py",
        "Black code formatting check"
    )
    
    # Run isort
    results["code_quality"] = run_command(
        "isort --check-only --diff src/ tests/ main.py",
        "isort import sorting check"
    ) and results["code_quality"]
    
    # Run Flake8
    results["code_quality"] = run_command(
        "flake8 src/ tests/ main.py --max-line-length=88 --extend-ignore=E203,W503",
        "Flake8 linting"
    ) and results["code_quality"]
    
    # Run MyPy
    results["code_quality"] = run_command(
        "mypy src/ --ignore-missing-imports --disallow-untyped-defs",
        "MyPy type checking"
    ) and results["code_quality"]
    
    # Run Pylint
    results["code_quality"] = run_command(
        "pylint src/ --disable=C0114,C0116 --max-line-length=88",
        "Pylint code analysis"
    ) and results["code_quality"]
    
    # Run tests (non-GUI)
    results["code_quality"] = run_command(
        "python -m pytest tests/ -m 'not gui' --cov=src --cov-report=xml --cov-report=html",
        "pytest (non-GUI tests)"
    ) and results["code_quality"]
    
    # Step 3: Dependency Update Check
    print("\n📊 STEP 3: Dependency Update Check")
    print("-" * 30)
    
    # Check for outdated packages
    results["dependency_update"] = run_command(
        "pip list --outdated --format=json > outdated-packages.json",
        "Check for outdated packages"
    )
    
    # Step 4: Build & Package Test
    print("\n📊 STEP 4: Build & Package Test")
    print("-" * 30)
    
    # Test package installation
    results["build_test"] = run_command(
        "pip install -e .",
        "Package installation test"
    )
    
    # Test import
    results["build_test"] = run_command(
        "python -c 'import src; print(\"Package imported successfully\")'",
        "Package import test"
    ) and results["build_test"]
    
    # Test PyInstaller (if available)
    if Path("sendapi.spec").exists():
        results["build_test"] = run_command(
            "pyinstaller --onefile main.py --name sendapi",
            "PyInstaller build test"
        ) and results["build_test"]
    else:
        print("⚠️ PyInstaller spec file not found, skipping build test")
    
    # Generate Summary Report
    print("\n📊 WORKFLOW SUMMARY")
    print("=" * 50)
    
    total_steps = len(results)
    passed_steps = sum(results.values())
    
    for step, passed in results.items():
        status = "✅ PASS" if passed else "❌ FAIL"
        print(f"{step.replace('_', ' ').title()}: {status}")
    
    print(f"\nOverall: {passed_steps}/{total_steps} steps passed")
    
    if passed_steps == total_steps:
        print("🎉 All workflow steps passed!")
        return True
    else:
        print("⚠️ Some workflow steps failed")
        return False

def main():
    """Main function"""
    print("🔧 Local Security Workflow Test")
    print("This script simulates the security-scan.yml workflow locally")
    print("=" * 60)
    
    # Check if we're in the right directory
    if not Path("src").exists():
        print("❌ Error: src/ directory not found. Please run from project root.")
        sys.exit(1)
    
    # Run the workflow test
    success = test_security_scan_workflow()
    
    if success:
        print("\n✅ Workflow test completed successfully!")
        sys.exit(0)
    else:
        print("\n❌ Workflow test had failures")
        sys.exit(1)

if __name__ == "__main__":
    main() 