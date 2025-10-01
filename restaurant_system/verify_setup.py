#!/usr/bin/env python3
"""
Setup Verification Script

Run this script to verify that your system is ready to run the
Restaurant Order Management System.
"""

import sys
import os


def check_python_version():
    """Check Python version."""
    print("🔍 Checking Python version...")
    version = sys.version_info
    print(f"   Python {version.major}.{version.minor}.{version.micro}")
    
    if version >= (3, 8):
        print("   ✅ Python version is adequate")
        return True
    else:
        print("   ❌ Python 3.8+ required")
        return False


def check_tkinter():
    """Check if tkinter is available."""
    print("\n🔍 Checking tkinter (GUI library)...")
    try:
        import tkinter as tk
        root = tk.Tk()
        root.withdraw()  # Hide window
        root.destroy()
        print("   ✅ tkinter is available")
        return True
    except ImportError:
        print("   ❌ tkinter not found")
        print("   Install with:")
        print("     Ubuntu/Debian: sudo apt-get install python3-tk")
        print("     Fedora/RHEL: sudo dnf install python3-tkinter")
        print("     macOS: brew install python-tk")
        return False
    except Exception as e:
        print(f"   ⚠️  tkinter found but error occurred: {e}")
        return False


def check_files():
    """Check if all required files exist."""
    print("\n🔍 Checking project files...")
    required_files = [
        'main.py',
        'gui.py',
        'shared_buffer.py',
        'producer.py',
        'consumer.py',
        'order.py',
        'config.py',
        'utils.py',
        'README.md',
        'requirements.txt'
    ]
    
    all_present = True
    for filename in required_files:
        if os.path.exists(filename):
            print(f"   ✅ {filename}")
        else:
            print(f"   ❌ {filename} missing")
            all_present = False
    
    return all_present


def check_imports():
    """Check if all modules can be imported."""
    print("\n🔍 Checking module imports...")
    modules = [
        ('config', 'config.py'),
        ('order', 'order.py'),
        ('shared_buffer', 'shared_buffer.py'),
        ('producer', 'producer.py'),
        ('consumer', 'consumer.py'),
        ('utils', 'utils.py'),
        ('gui', 'gui.py')
    ]
    
    all_ok = True
    for module_name, filename in modules:
        try:
            __import__(module_name)
            print(f"   ✅ {filename}")
        except Exception as e:
            print(f"   ❌ {filename}: {str(e)}")
            all_ok = False
    
    return all_ok


def check_threading():
    """Check threading support."""
    print("\n🔍 Checking threading support...")
    try:
        import threading
        
        # Test basic threading
        def test_func():
            pass
        
        t = threading.Thread(target=test_func)
        t.start()
        t.join()
        
        print("   ✅ Threading works")
        return True
    except Exception as e:
        print(f"   ❌ Threading error: {e}")
        return False


def main():
    """Run all verification checks."""
    print("=" * 60)
    print("🍽️  Restaurant Order Management System")
    print("    Setup Verification")
    print("=" * 60)
    
    checks = []
    
    # Run all checks
    checks.append(("Python Version", check_python_version()))
    checks.append(("Tkinter", check_tkinter()))
    checks.append(("Project Files", check_files()))
    checks.append(("Module Imports", check_imports()))
    checks.append(("Threading Support", check_threading()))
    
    # Summary
    print("\n" + "=" * 60)
    print("📊 SUMMARY")
    print("=" * 60)
    
    all_passed = True
    for check_name, passed in checks:
        status = "✅ PASS" if passed else "❌ FAIL"
        print(f"{status:12} {check_name}")
        if not passed:
            all_passed = False
    
    print("=" * 60)
    
    if all_passed:
        print("\n🎉 All checks passed! You're ready to run the application.")
        print("\nTo start the application, run:")
        print("    python3 main.py")
        return 0
    else:
        print("\n⚠️  Some checks failed. Please fix the issues above.")
        return 1


if __name__ == "__main__":
    sys.exit(main())