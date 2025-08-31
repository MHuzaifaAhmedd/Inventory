#!/usr/bin/env python3
"""
Build script for creating Windows executable
Uses PyInstaller to create .exe file
"""

import os
import sys
import subprocess
from pathlib import Path

def build_executable():
    """Build Windows executable using PyInstaller"""

    print("Building Mona Beauty Store Inventory Management System...")

    # Ensure we're in the right directory
    project_dir = Path(__file__).parent
    os.chdir(project_dir)

    # PyInstaller command
    cmd = [
        "pyinstaller",
        "--onefile",  # Single executable file
        "--windowed",  # No console window
        "--name=MonaBeautyStore_Inventory",
        "--icon=assets/icon.ico",  # Icon file (if exists)
        "--add-data=assets;assets",  # Include assets folder
        "main.py"
    ]

    try:
        # Run PyInstaller
        result = subprocess.run(cmd, check=True, capture_output=True, text=True)

        print("Build completed successfully!")
        print("Executable created: dist/MonaBeautyStore_Inventory.exe")

        # Copy additional files if needed
        exe_path = project_dir / "dist" / "MonaBeautyStore_Inventory.exe"
        if exe_path.exists():
            print(f"Executable size: {exe_path.stat().st_size / (1024*1024):.2f} MB")

        return True

    except subprocess.CalledProcessError as e:
        print(f"Build failed: {e}")
        print(f"Error output: {e.stderr}")
        return False
    except FileNotFoundError:
        print("PyInstaller not found. Please install it with: pip install pyinstaller")
        return False

def create_requirements_file():
    """Create requirements file for the project"""
    requirements = [
        "tkinter",
        "sqlite3",
        "matplotlib==3.8.0",
        "seaborn==0.12.2",
        "pandas==2.0.3",
        "numpy==1.24.3",
        "pillow==10.0.0",
        "opencv-python==4.8.0.76",
        "pyzbar==0.1.9",
        "openpyxl==3.1.2",
        "reportlab==4.0.4",
        "tkcalendar==1.6.1",
        "ttkthemes==3.2.0",
        "pyinstaller==6.3.0"
    ]

    with open("requirements.txt", "w") as f:
        f.write("\n".join(requirements))

    print("Created requirements.txt")

def main():
    """Main build function"""
    print("=" * 60)
    print("MONA BEAUTY STORE - INVENTORY SYSTEM BUILDER")
    print("=" * 60)

    # Create requirements file
    create_requirements_file()

    # Build executable
    success = build_executable()

    if success:
        print("\n" + "=" * 60)
        print("BUILD SUCCESSFUL!")
        print("Your executable is ready at: dist/MonaBeautyStore_Inventory.exe")
        print("=" * 60)

        # Instructions
        print("\nTo run the application:")
        print("1. Copy the .exe file to your desired location")
        print("2. Double-click to run")
        print("3. The database will be created automatically on first run")
    else:
        print("\n" + "=" * 60)
        print("BUILD FAILED!")
        print("Please check the error messages above.")
        print("=" * 60)

if __name__ == "__main__":
    main()


