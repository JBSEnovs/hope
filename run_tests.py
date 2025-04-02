import os
import sys
import pytest

if __name__ == "__main__":
    print("Running Medical AI Assistant tests...")
    # Add current directory to path
    sys.path.append(os.path.dirname(os.path.abspath(__file__)))
    
    # Run pytest with specified arguments
    exit_code = pytest.main(["-v", "tests/"])
    
    # Print summary
    if exit_code == 0:
        print("\n✅ All tests passed!")
    else:
        print(f"\n❌ Some tests failed (exit code: {exit_code})")
    
    sys.exit(exit_code) 