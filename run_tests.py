#!/usr/bin/env python3
"""Test runner script for local-agent project"""

import sys
import subprocess
from pathlib import Path

def run_tests():
    """Run the test suite with various options"""
    
    print("🧪 Running Local Agent Test Suite")
    print("=" * 50)
    
    # Basic test command
    cmd = ["pytest"]
    
    # Add command line arguments if provided
    if len(sys.argv) > 1:
        cmd.extend(sys.argv[1:])
    else:
        # Default: run with coverage
        cmd.extend(["-v", "--cov=.", "--cov-report=term-missing"])
    
    # Run tests
    result = subprocess.run(cmd)
    
    if result.returncode == 0:
        print("\n✅ All tests passed!")
        
        # Check if coverage report exists
        coverage_html = Path("htmlcov/index.html")
        if coverage_html.exists():
            print(f"📊 Coverage report available at: {coverage_html.absolute()}")
    else:
        print("\n❌ Some tests failed. Please review the output above.")
        sys.exit(1)

if __name__ == "__main__":
    run_tests()