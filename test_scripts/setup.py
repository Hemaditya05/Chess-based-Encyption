#!/usr/bin/env python3
"""
Setup script for ChessPerm security test suite.
Automates virtual environment creation and package installation.
"""

import os
import sys
import subprocess
import venv
from pathlib import Path

def create_venv(venv_path):
    """Create virtual environment if it doesn't exist."""
    if not venv_path.exists():
        print(f"Creating virtual environment at {venv_path}...")
        venv.create(venv_path, with_pip=True)
        print("✓ Virtual environment created")
    else:
        print("✓ Virtual environment already exists")

def install_packages(venv_path):
    """Install required packages in virtual environment."""
    python_exe = venv_path / "Scripts" / "python.exe" if os.name == "nt" else venv_path / "bin" / "python"
    pip_exe = venv_path / "Scripts" / "pip.exe" if os.name == "nt" else venv_path / "bin" / "pip"
    
    print("Installing required packages...")
    
    # Install packages from requirements.txt
    try:
        subprocess.run([str(pip_exe), "install", "-r", "requirements.txt"], check=True)
        print("✓ Packages installed successfully")
    except subprocess.CalledProcessError as e:
        print(f"✗ Error installing packages: {e}")
        return False
    
    return True

def test_installation(venv_path):
    """Test that the installation works."""
    python_exe = venv_path / "Scripts" / "python.exe" if os.name == "nt" else venv_path / "bin" / "python"
    
    print("Testing installation...")
    
    try:
        # Test simple import
        result = subprocess.run([str(python_exe), "simple_test.py"], 
                              capture_output=True, text=True, cwd=Path(__file__).parent)
        
        if result.returncode == 0:
            print("✓ Installation test passed")
            print("Sample output:")
            print(result.stdout)
            return True
        else:
            print("✗ Installation test failed")
            print("Error output:")
            print(result.stderr)
            return False
            
    except Exception as e:
        print(f"✗ Error testing installation: {e}")
        return False

def main():
    """Main setup function."""
    print("ChessPerm Security Test Suite Setup")
    print("="*50)
    
    # Get current directory
    current_dir = Path(__file__).parent
    venv_path = current_dir.parent / "chessperm_test_env"
    
    print(f"Current directory: {current_dir}")
    print(f"Virtual environment path: {venv_path}")
    
    # Create virtual environment
    create_venv(venv_path)
    
    # Install packages
    if not install_packages(venv_path):
        print("Setup failed during package installation")
        return False
    
    # Test installation
    if not test_installation(venv_path):
        print("Setup failed during testing")
        return False
    
    print("\n" + "="*50)
    print("✓ Setup completed successfully!")
    print("\nTo activate the virtual environment:")
    if os.name == "nt":
        print(f"  {venv_path}\\Scripts\\activate")
    else:
        print(f"  source {venv_path}/bin/activate")
    
    print("\nTo run tests:")
    print("  python simple_test.py          # Basic functionality test")
    print("  python collision_test.py       # Collision detection")
    print("  python avalanche_test.py       # Avalanche effect test")
    print("  python timing.py               # Timing analysis")
    print("  python diff_probe.py           # Differential propagation")
    print("  python bench.py                # Performance benchmark")
    print("  python gen_keys.py             # Generate key samples")
    print("  python run_all_tests.py        # Run all tests")
    
    print("\nFor external randomness testing:")
    print("  python gen_keys.py             # Generate key files")
    print("  niststs --input pgn_keys.bin --blocksize 32")
    print("  dieharder -a -g 202 -f pgn_keys.bin")
    
    return True

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1) 