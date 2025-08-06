#!/usr/bin/env python3
"""
Security scanning script for SendApi project
This script runs various security checks locally
"""

import json
import subprocess
import sys
import os
from pathlib import Path
from typing import Dict, List, Any
import argparse
import yaml


class SecurityScanner:
    """Security scanner for the SendApi project"""
    
    def __init__(self, project_root: str = "."):
        self.project_root = Path(project_root)
        self.reports_dir = self.project_root / "security-reports"
        self.reports_dir.mkdir(exist_ok=True)
        
    def run_safety_check(self) -> Dict[str, Any]:
        """Run Safety dependency vulnerability check"""
        print("🔍 Running Safety dependency vulnerability check...")
        try:
            # Use 'safety scan' instead of 'safety check'
            result = subprocess.run(
                ["safety", "scan", "--json"],
                capture_output=True,
                text=True,
                cwd=self.project_root
            )
            
            if result.returncode == 0:
                with open(self.reports_dir / "safety-report.json", "w") as f:
                    f.write(result.stdout)
                print("✅ Safety scan passed")
                return {"status": "passed", "output": result.stdout}
            else:
                with open(self.reports_dir / "safety-report.json", "w") as f:
                    f.write(result.stdout)
                print("⚠️ Safety scan found vulnerabilities")
                return {"status": "failed", "output": result.stderr}
                
        except FileNotFoundError:
            print("❌ Safety not installed. Install with: pip install safety")
            return {"status": "error", "message": "Safety not installed"}
    
    def run_bandit_check(self) -> Dict[str, Any]:
        """Run Bandit security linter"""
        print("🔍 Running Bandit security linter...")
        try:
            result = subprocess.run([
                "bandit", "-r", "src/", "-f", "json", 
                "-o", str(self.reports_dir / "bandit-report.json")
            ], capture_output=True, text=True, cwd=self.project_root)
            
            if result.returncode == 0:
                print("✅ Bandit check passed")
                return {"status": "passed", "output": result.stdout}
            else:
                print("⚠️ Bandit found security issues")
                return {"status": "failed", "output": result.stderr}
                
        except FileNotFoundError:
            print("❌ Bandit not installed. Install with: pip install bandit")
            return {"status": "error", "message": "Bandit not installed"}
    
    def run_semgrep_check(self) -> Dict[str, Any]:
        """Run Semgrep static analysis"""
        print("🔍 Running Semgrep static analysis...")
        try:
            result = subprocess.run([
                "semgrep", "ci", "--config", "auto", "--json",
                "--output", str(self.reports_dir / "semgrep-report.json")
            ], capture_output=True, text=True, cwd=self.project_root)
            
            if result.returncode == 0:
                print("✅ Semgrep check passed")
                return {"status": "passed", "output": result.stdout}
            else:
                print("⚠️ Semgrep found issues")
                return {"status": "failed", "output": result.stderr}
                
        except FileNotFoundError:
            print("❌ Semgrep not installed. Install with: pip install semgrep")
            return {"status": "error", "message": "Semgrep not installed"}
    
    def run_pip_audit(self) -> Dict[str, Any]:
        """Run pip-audit for package vulnerabilities"""
        print("🔍 Running pip-audit...")
        try:
            result = subprocess.run([
                "pip-audit", "--format", "json",
                "--output", str(self.reports_dir / "pip-audit-report.json")
            ], capture_output=True, text=True, cwd=self.project_root)
            
            if result.returncode == 0:
                print("✅ pip-audit check passed")
                return {"status": "passed", "output": result.stdout}
            else:
                print("⚠️ pip-audit found vulnerabilities")
                return {"status": "failed", "output": result.stderr}
                
        except FileNotFoundError:
            print("❌ pip-audit not installed. Install with: pip install pip-audit")
            return {"status": "error", "message": "pip-audit not installed"}
    
    def run_code_quality_checks(self) -> Dict[str, Any]:
        """Run code quality checks"""
        print("🔍 Running code quality checks...")
        results = {}
        
        # Black formatting check
        try:
            result = subprocess.run(
                ["black", "--check", "--diff", "src/", "tests/", "main.py"],
                capture_output=True,
                text=True,
                cwd=self.project_root
            )
            results["black"] = {
                "status": "passed" if result.returncode == 0 else "failed",
                "output": result.stdout if result.returncode == 0 else result.stderr
            }
        except FileNotFoundError:
            results["black"] = {"status": "error", "message": "Black not installed"}
        
        # Flake8 linting
        try:
            result = subprocess.run([
                "flake8", "src/", "tests/", "main.py",
                "--max-line-length=88", "--extend-ignore=E203,W503"
            ], capture_output=True, text=True, cwd=self.project_root)
            results["flake8"] = {
                "status": "passed" if result.returncode == 0 else "failed",
                "output": result.stdout if result.returncode == 0 else result.stderr
            }
        except FileNotFoundError:
            results["flake8"] = {"status": "error", "message": "Flake8 not installed"}
        
        # MyPy type checking
        try:
            result = subprocess.run([
                "mypy", "src/", "--ignore-missing-imports", "--disallow-untyped-defs"
            ], capture_output=True, text=True, cwd=self.project_root)
            results["mypy"] = {
                "status": "passed" if result.returncode == 0 else "failed",
                "output": result.stdout if result.returncode == 0 else result.stderr
            }
        except FileNotFoundError:
            results["mypy"] = {"status": "error", "message": "MyPy not installed"}
        
        return results
    
    def run_tests(self) -> Dict[str, Any]:
        """Run test suite"""
        print("🔍 Running tests...")
        try:
            result = subprocess.run([
                "python", "-m", "pytest", "tests/", "-v", "--cov=src", 
                "--cov-report=html:" + str(self.reports_dir / "htmlcov"),
                "--cov-report=xml:" + str(self.reports_dir / "coverage.xml")
            ], capture_output=True, text=True, cwd=self.project_root)
            
            if result.returncode == 0:
                print("✅ Tests passed")
                return {"status": "passed", "output": result.stdout}
            else:
                print("❌ Tests failed")
                return {"status": "failed", "output": result.stderr}
                
        except Exception as e:
            return {"status": "error", "message": str(e)}
    
    def generate_summary_report(self, results: Dict[str, Any]) -> None:
        """Generate a summary report"""
        print("\n" + "="*60)
        print("🔒 SECURITY SCAN SUMMARY")
        print("="*60)
        
        summary = {
            "timestamp": subprocess.run(["date"], capture_output=True, text=True).stdout.strip(),
            "project": "SendApi",
            "results": results
        }
        
        # Save detailed report
        with open(self.reports_dir / "security-summary.json", "w") as f:
            json.dump(summary, f, indent=2)
        
        # Print summary
        for check_name, result in results.items():
            status = result.get("status", "unknown")
            if status == "passed":
                print(f"✅ {check_name}: PASSED")
            elif status == "failed":
                print(f"❌ {check_name}: FAILED")
            else:
                print(f"⚠️ {check_name}: ERROR")
        
        print(f"\n📁 Detailed reports saved to: {self.reports_dir}")
        print("="*60)
    
    def run_all_checks(self) -> Dict[str, Any]:
        """Run all security checks"""
        print("🚀 Starting comprehensive security scan...")
        
        results = {
            "safety": self.run_safety_check(),
            "bandit": self.run_bandit_check(),
            "semgrep": self.run_semgrep_check(),
            "pip_audit": self.run_pip_audit(),
            "code_quality": self.run_code_quality_checks(),
            "tests": self.run_tests()
        }
        
        self.generate_summary_report(results)
        return results


def main():
    """Main function"""
    parser = argparse.ArgumentParser(description="Security scanner for SendApi project")
    parser.add_argument("--project-root", default=".", help="Project root directory")
    parser.add_argument("--check", choices=["safety", "bandit", "semgrep", "pip-audit", "quality", "tests", "all"], 
                       default="all", help="Specific check to run")
    
    args = parser.parse_args()
    
    scanner = SecurityScanner(args.project_root)
    
    if args.check == "all":
        scanner.run_all_checks()
    elif args.check == "safety":
        scanner.run_safety_check()
    elif args.check == "bandit":
        scanner.run_bandit_check()
    elif args.check == "semgrep":
        scanner.run_semgrep_check()
    elif args.check == "pip-audit":
        scanner.run_pip_audit()
    elif args.check == "quality":
        scanner.run_code_quality_checks()
    elif args.check == "tests":
        scanner.run_tests()


if __name__ == "__main__":
    main() 