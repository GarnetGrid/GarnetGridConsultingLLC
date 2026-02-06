import unittest
import sys
import os

# Add parent directory to path to import app modules if needed
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

def run_suite():
    loader = unittest.TestLoader()
    suite = unittest.TestSuite()

    # Discover and add tests from the current directory (tests/)
    # Pattern "test_*.py" covers standard tests
    # Pattern "verify_*.py" *might* not be standard unittest files, so we need to be careful.
    # If verify files are scripts, we should run them as subprocesses.
    
    # Let's assume test_*.py are unittests.
    print("=== 1. Running Unit Tests (test_*.py) ===")
    test_suite = loader.discover(start_dir='tests', pattern='test_*.py')
    suite.addTests(test_suite)

    runner = unittest.TextTestRunner(verbosity=2)
    result = runner.run(suite)
    
    return result.wasSuccessful()

def run_verification_scripts():
    print("\n=== 2. Running Verification Scripts (verify_*.py) ===")
    import subprocess
    
    scripts = [
        "tests/verify_memory_rag.py",
        "tests/verify_ui_backend.py"
    ]
    
    all_passed = True
    
    for script in scripts:
        print(f"\n--- Executing {script} ---")
        try:
            # Running with python3
            result = subprocess.run(["python3", script], check=True, capture_output=True, text=True)
            print("STATUS: PASS")
            print("OUTPUT:")
            print(result.stdout)
        except subprocess.CalledProcessError as e:
            print("STATUS: FAIL")
            print("ERROR:")
            print(e.stderr)
            print("STDOUT:")
            print(e.stdout)
            all_passed = False
        except Exception as e:
            print(f"STATUS: CRASH ({e})")
            all_passed = False
            
    return all_passed

if __name__ == "__main__":
    current_dir = os.getcwd()
    print(f"Starting System Audit from {current_dir}")
    
    # 1. Run Unit Tests
    unit_success = run_suite()
    
    # 2. Run Verification Scripts
    verify_success = run_verification_scripts()
    
    print("\n\n=== AUDIT SUMMARY ===")
    print(f"Unit Tests: {'PASS' if unit_success else 'FAIL'}")
    print(f"Verification Scripts: {'PASS' if verify_success else 'FAIL'}")
    
    if unit_success and verify_success:
        print("OVERALL STATUS: GREEN")
        sys.exit(0)
    else:
        print("OVERALL STATUS: RED")
        sys.exit(1)
