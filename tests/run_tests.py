# tests/run_tests.py

"""
Test runner script for ForecastEngine
"""

import sys
import subprocess
import argparse
from pathlib import Path

def run_tests(test_type="all", verbose=False, coverage=False):
    """Run tests with specified options"""
    
    # Base pytest command
    cmd = ["python", "-m", "pytest"]
    
    # Add verbosity
    if verbose:
        cmd.append("-v")
    else:
        cmd.append("-q")
    
    # Add coverage if requested
    if coverage:
        cmd.extend(["--cov=src", "--cov-report=html", "--cov-report=term"])
    
    # Select test type
    if test_type == "unit":
        cmd.extend(["-m", "unit"])
    elif test_type == "integration":
        cmd.extend(["-m", "integration"])
    elif test_type == "api":
        cmd.extend(["-m", "api"])
    elif test_type == "fast":
        cmd.extend(["-m", "not slow"])
    elif test_type != "all":
        # Specific test file or pattern
        cmd.append(test_type)
    
    # Add test directory
    cmd.append("tests/")
    
    print(f"Running command: {' '.join(cmd)}")
    
    # Run tests
    result = subprocess.run(cmd, cwd=Path(__file__).parent.parent)
    
    return result.returncode

def main():
    """Main CLI function"""
    parser = argparse.ArgumentParser(description="ForecastEngine Test Runner")
    
    parser.add_argument(
        "--type", "-t",
        choices=["all", "unit", "integration", "api", "fast"],
        default="all",
        help="Type of tests to run"
    )
    
    parser.add_argument(
        "--verbose", "-v",
        action="store_true",
        help="Verbose output"
    )
    
    parser.add_argument(
        "--coverage", "-c",
        action="store_true",
        help="Generate coverage report"
    )
    
    parser.add_argument(
        "--file", "-f",
        help="Run specific test file"
    )
    
    args = parser.parse_args()
    
    # Use specific file if provided
    test_type = args.file if args.file else args.type
    
    # Run tests
    exit_code = run_tests(
        test_type=test_type,
        verbose=args.verbose,
        coverage=args.coverage
    )
    
    sys.exit(exit_code)

if __name__ == "__main__":
    main()