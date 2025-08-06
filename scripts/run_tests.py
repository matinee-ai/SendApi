#!/usr/bin/env python3
"""
Test runner for SendApi application.
"""

import unittest
import sys
import os
import argparse
from pathlib import Path

# Add the project root to the Python path
project_root = Path(__file__).parent
sys.path.insert(0, str(project_root))

def run_unit_tests():
    """Run all unit tests."""
    print("Running unit tests...")
    
    # Discover and run unit tests
    loader = unittest.TestLoader()
    start_dir = project_root / 'tests'
    suite = loader.discover(start_dir, pattern='test_*.py')
    
    runner = unittest.TextTestRunner(verbosity=2)
    result = runner.run(suite)
    
    return result.wasSuccessful()

def run_integration_tests():
    """Run integration tests."""
    print("Running integration tests...")
    
    # Run integration tests specifically
    loader = unittest.TestLoader()
    start_dir = project_root / 'tests'
    suite = loader.discover(start_dir, pattern='test_integration.py')
    
    runner = unittest.TextTestRunner(verbosity=2)
    result = runner.run(suite)
    
    return result.wasSuccessful()

def run_specific_test(test_name):
    """Run a specific test."""
    print(f"Running specific test: {test_name}")
    
    loader = unittest.TestLoader()
    start_dir = project_root / 'tests'
    suite = loader.discover(start_dir, pattern=f'{test_name}.py')
    
    runner = unittest.TextTestRunner(verbosity=2)
    result = runner.run(suite)
    
    return result.wasSuccessful()

def run_all_tests():
    """Run all tests (unit and integration)."""
    print("Running all tests...")
    
    # Run unit tests
    unit_success = run_unit_tests()
    print("\n" + "="*50 + "\n")
    
    # Run integration tests
    integration_success = run_integration_tests()
    
    return unit_success and integration_success

def main():
    """Main test runner function."""
    parser = argparse.ArgumentParser(description='Run SendApi tests')
    parser.add_argument('--unit', action='store_true', help='Run only unit tests')
    parser.add_argument('--integration', action='store_true', help='Run only integration tests')
    parser.add_argument('--test', type=str, help='Run a specific test file (without .py extension)')
    parser.add_argument('--all', action='store_true', help='Run all tests (default)')
    
    args = parser.parse_args()
    
    # Default to running all tests if no specific option is provided
    if not any([args.unit, args.integration, args.test]):
        args.all = True
    
    success = True
    
    try:
        if args.unit:
            success = run_unit_tests()
        elif args.integration:
            success = run_integration_tests()
        elif args.test:
            success = run_specific_test(args.test)
        elif args.all:
            success = run_all_tests()
        
        print("\n" + "="*50)
        if success:
            print("✅ All tests passed!")
            sys.exit(0)
        else:
            print("❌ Some tests failed!")
            sys.exit(1)
            
    except KeyboardInterrupt:
        print("\n\nTest run interrupted by user.")
        sys.exit(1)
    except Exception as e:
        print(f"\n\nError running tests: {e}")
        sys.exit(1)

if __name__ == "__main__":
    main() 