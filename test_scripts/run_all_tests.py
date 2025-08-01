#!/usr/bin/env python3
"""
Comprehensive test runner for ChessPerm security analysis.
Runs all security tests and generates a report.
"""

import sys
import os
import time
import subprocess
from datetime import datetime

# Add backend to path
sys.path.append(os.path.join(os.path.dirname(__file__), '..', 'backend'))

def run_test(test_name, test_script, description=""):
    """Run a test and return results."""
    print(f"\n{'='*60}")
    print(f"Running {test_name}")
    print(f"{'='*60}")
    if description:
        print(f"Description: {description}")
    
    start_time = time.time()
    
    try:
        # Run the test script
        result = subprocess.run([sys.executable, test_script], 
                              capture_output=True, text=True, cwd=os.path.dirname(__file__))
        
        end_time = time.time()
        duration = end_time - start_time
        
        print(result.stdout)
        if result.stderr:
            print("STDERR:", result.stderr)
        
        success = result.returncode == 0
        print(f"\nTest completed in {duration:.2f} seconds")
        print(f"Status: {'✓ PASS' if success else '✗ FAIL'}")
        
        return {
            'name': test_name,
            'success': success,
            'duration': duration,
            'output': result.stdout,
            'error': result.stderr
        }
        
    except Exception as e:
        print(f"Error running {test_name}: {e}")
        return {
            'name': test_name,
            'success': False,
            'duration': 0,
            'output': '',
            'error': str(e)
        }

def generate_report(results):
    """Generate a comprehensive test report."""
    print(f"\n{'='*60}")
    print("CHESSPERM SECURITY TEST REPORT")
    print(f"{'='*60}")
    print(f"Generated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    
    # Summary
    total_tests = len(results)
    passed_tests = sum(1 for r in results if r['success'])
    failed_tests = total_tests - passed_tests
    total_duration = sum(r['duration'] for r in results)
    
    print(f"\nSUMMARY:")
    print(f"Total tests: {total_tests}")
    print(f"Passed: {passed_tests}")
    print(f"Failed: {failed_tests}")
    print(f"Success rate: {passed_tests/total_tests*100:.1f}%")
    print(f"Total duration: {total_duration:.2f} seconds")
    
    # Detailed results
    print(f"\nDETAILED RESULTS:")
    for result in results:
        status = "✓ PASS" if result['success'] else "✗ FAIL"
        print(f"{result['name']:30} {status:10} {result['duration']:6.2f}s")
    
    # Failed tests details
    failed_results = [r for r in results if not r['success']]
    if failed_results:
        print(f"\nFAILED TESTS DETAILS:")
        for result in failed_results:
            print(f"\n{result['name']}:")
            if result['error']:
                print(f"Error: {result['error']}")
    
    # Save report to file
    report_file = f"chessperm_security_report_{datetime.now().strftime('%Y%m%d_%H%M%S')}.txt"
    with open(report_file, 'w') as f:
        f.write("CHESSPERM SECURITY TEST REPORT\n")
        f.write("="*60 + "\n")
        f.write(f"Generated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n\n")
        
        f.write("SUMMARY:\n")
        f.write(f"Total tests: {total_tests}\n")
        f.write(f"Passed: {passed_tests}\n")
        f.write(f"Failed: {failed_tests}\n")
        f.write(f"Success rate: {passed_tests/total_tests*100:.1f}%\n")
        f.write(f"Total duration: {total_duration:.2f} seconds\n\n")
        
        f.write("DETAILED RESULTS:\n")
        for result in results:
            status = "PASS" if result['success'] else "FAIL"
            f.write(f"{result['name']}: {status} ({result['duration']:.2f}s)\n")
            if result['output']:
                f.write(f"Output:\n{result['output']}\n")
            if result['error']:
                f.write(f"Error:\n{result['error']}\n")
            f.write("-"*40 + "\n")
    
    print(f"\nDetailed report saved to: {report_file}")

def main():
    """Run all security tests."""
    print("CHESSPERM SECURITY TEST SUITE")
    print("="*60)
    print("This will run comprehensive security tests on the ChessPerm system.")
    print("Tests include collision detection, avalanche effect, timing analysis,")
    print("differential propagation, and performance benchmarking.")
    print("\nStarting tests...")
    
    # Define all tests
    tests = [
        {
            'name': 'Collision Test',
            'script': 'collision_test.py',
            'description': 'Tests for hash collisions in derived master keys'
        },
        {
            'name': 'Avalanche Test',
            'script': 'avalanche_test.py',
            'description': 'Tests avalanche effect and bit propagation'
        },
        {
            'name': 'Timing Analysis',
            'script': 'timing.py',
            'description': 'Analyzes timing characteristics for side-channel resistance'
        },
        {
            'name': 'Differential Propagation',
            'script': 'diff_probe.py',
            'description': 'Tests how single-bit changes propagate through the system'
        },
        {
            'name': 'Performance Benchmark',
            'script': 'bench.py',
            'description': 'Benchmarks throughput and performance characteristics'
        }
    ]
    
    # Run all tests
    results = []
    for test in tests:
        result = run_test(test['name'], test['script'], test['description'])
        results.append(result)
    
    # Generate report
    generate_report(results)
    
    print(f"\n{'='*60}")
    print("TEST SUITE COMPLETE")
    print(f"{'='*60}")
    print("Check the generated report for detailed results.")
    print("For randomness testing, use the generated key files with:")
    print("- NIST STS: niststs --input keys.bin --blocksize 32")
    print("- Dieharder: dieharder -a -g 202 -f keys.bin")

if __name__ == "__main__":
    main() 