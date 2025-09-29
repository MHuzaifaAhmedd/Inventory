#!/usr/bin/env python3
"""
Test script to validate the build process and executable
"""

import os
import sys
import subprocess
from pathlib import Path
import time

def test_python_environment():
    """Test if Python environment is ready for building"""
    print("Testing Python environment...")
    
    # Check Python version
    python_version = sys.version_info
    print(f"Python version: {python_version.major}.{python_version.minor}.{python_version.micro}")
    
    if python_version < (3, 8):
        print("❌ Python 3.8 or later required")
        return False
    
    print("✅ Python version OK")
    return True

def test_dependencies():
    """Test if all required dependencies are installed"""
    print("\nTesting dependencies...")
    
    required_modules = [
        'tkinter', 'sqlite3', 'matplotlib', 'pandas', 'numpy', 
        'PIL', 'cv2', 'qrcode', 'pyzbar', 'openpyxl', 
        'reportlab', 'tkcalendar', 'ttkthemes', 'PyInstaller'
    ]
    
    missing_modules = []
    
    for module in required_modules:
        try:
            __import__(module)
            print(f"✅ {module}")
        except ImportError:
            print(f"❌ {module} - MISSING")
            missing_modules.append(module)
    
    if missing_modules:
        print(f"\nMissing modules: {', '.join(missing_modules)}")
        print("Run: pip install -r requirements.txt")
        return False
    
    print("✅ All dependencies OK")
    return True

def test_project_structure():
    """Test if project structure is correct"""
    print("\nTesting project structure...")
    
    required_files = [
        'main.py',
        'requirements.txt',
        'build_production.py',
        'database/db_manager.py',
        'ui/main_window.py',
        'ui/qr_scanner.py',
        'utils/barcode_generator.py',
        'utils/qr_generator.py'
    ]
    
    missing_files = []
    
    for file_path in required_files:
        if not Path(file_path).exists():
            print(f"❌ {file_path} - MISSING")
            missing_files.append(file_path)
        else:
            print(f"✅ {file_path}")
    
    if missing_files:
        print(f"\nMissing files: {', '.join(missing_files)}")
        return False
    
    print("✅ Project structure OK")
    return True

def test_build_script():
    """Test if build script can be imported and run"""
    print("\nTesting build script...")
    
    try:
        # Import the build script
        import build_production
        print("✅ Build script imports OK")
        
        # Check if main classes exist
        if hasattr(build_production, 'ProductionBuilder'):
            print("✅ ProductionBuilder class found")
        else:
            print("❌ ProductionBuilder class not found")
            return False
        
        return True
        
    except Exception as e:
        print(f"❌ Build script error: {e}")
        return False

def test_executable_exists():
    """Test if executable was created successfully"""
    print("\nTesting executable...")
    
    exe_path = Path("dist/MonaBeautyStore_Inventory.exe")
    if exe_path.exists():
        size_mb = exe_path.stat().st_size / (1024 * 1024)
        print(f"✅ Executable found: {exe_path}")
        print(f"📊 Size: {size_mb:.2f} MB")
        
        if size_mb < 10:
            print("⚠️  Warning: Executable seems too small")
        elif size_mb > 500:
            print("⚠️  Warning: Executable seems too large")
        else:
            print("✅ Executable size looks reasonable")
        
        return True
    else:
        print("❌ Executable not found")
        return False

def test_package_creation():
    """Test if client package was created"""
    print("\nTesting client package...")
    
    package_dir = Path("MonaBeautyStore_Package")
    if package_dir.exists():
        print("✅ Package directory created")
        
        required_package_files = [
            "MonaBeautyStore_Inventory.exe",
            "Start_Inventory_System.bat",
            "README.txt"
        ]
        
        for file_name in required_package_files:
            file_path = package_dir / file_name
            if file_path.exists():
                print(f"✅ {file_name}")
            else:
                print(f"❌ {file_name} - MISSING")
                return False
        
        return True
    else:
        print("❌ Package directory not found")
        return False

def run_build_test():
    """Run a complete build test"""
    print("=" * 60)
    print("MONA BEAUTY STORE - BUILD TEST")
    print("=" * 60)
    
    tests = [
        ("Python Environment", test_python_environment),
        ("Dependencies", test_dependencies),
        ("Project Structure", test_project_structure),
        ("Build Script", test_build_script),
    ]
    
    all_passed = True
    
    for test_name, test_func in tests:
        try:
            if not test_func():
                all_passed = False
        except Exception as e:
            print(f"❌ {test_name} failed with error: {e}")
            all_passed = False
    
    if all_passed:
        print("\n" + "=" * 60)
        print("✅ ALL TESTS PASSED - READY TO BUILD")
        print("=" * 60)
        print("\nTo build the executable, run:")
        print("  python build_production.py")
        print("  OR")
        print("  build.bat")
    else:
        print("\n" + "=" * 60)
        print("❌ SOME TESTS FAILED - FIX ISSUES FIRST")
        print("=" * 60)
    
    return all_passed

def test_after_build():
    """Test after build is complete"""
    print("\n" + "=" * 60)
    print("POST-BUILD TEST")
    print("=" * 60)
    
    tests = [
        ("Executable Creation", test_executable_exists),
        ("Package Creation", test_package_creation),
    ]
    
    all_passed = True
    
    for test_name, test_func in tests:
        try:
            if not test_func():
                all_passed = False
        except Exception as e:
            print(f"❌ {test_name} failed with error: {e}")
            all_passed = False
    
    if all_passed:
        print("\n✅ BUILD SUCCESSFUL - READY FOR DELIVERY")
    else:
        print("\n❌ BUILD ISSUES DETECTED - CHECK ABOVE")
    
    return all_passed

def main():
    """Main test function"""
    if len(sys.argv) > 1 and sys.argv[1] == "--post-build":
        return test_after_build()
    else:
        return run_build_test()

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)
