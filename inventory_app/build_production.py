#!/usr/bin/env python3
"""
Production Build Script for Mona Beauty Store Inventory Management System
Creates a professional .exe file with all dependencies included
"""

import os
import sys
import subprocess
import shutil
from pathlib import Path
import platform

class ProductionBuilder:
    def __init__(self):
        self.project_dir = Path(__file__).parent
        self.dist_dir = self.project_dir / "dist"
        self.build_dir = self.project_dir / "build"
        self.spec_file = self.project_dir / "MonaBeautyStore.spec"
        
    def clean_build_dirs(self):
        """Clean previous build directories"""
        print("Cleaning previous build directories...")
        for dir_path in [self.dist_dir, self.build_dir]:
            if dir_path.exists():
                shutil.rmtree(dir_path)
                print(f"Removed {dir_path}")
    
    def create_spec_file(self):
        """Create PyInstaller .spec file for advanced configuration"""
        spec_content = '''# -*- mode: python ; coding: utf-8 -*-

block_cipher = None

# Define data files to include
datas = [
    ('database', 'database'),
    ('ui', 'ui'),
    ('utils', 'utils'),
    ('generated_barcodes', 'generated_barcodes'),
    ('inventory.db', '.'),
    ('sample_qr_code.png', '.'),
]

# Hidden imports (modules that PyInstaller might miss)
hiddenimports = [
    'tkinter',
    'tkinter.ttk',
    'tkinter.messagebox',
    'tkinter.filedialog',
    'tkinter.simpledialog',
    'sqlite3',
    'matplotlib.backends.backend_tkagg',
    'matplotlib.figure',
    'matplotlib.backends._backend_tk',
    'PIL',
    'PIL.Image',
    'PIL.ImageTk',
    'cv2',
    'qrcode',
    'qrcode.image.pil',
    'pyzbar',
    'pyzbar.pyzbar',
    'pandas',
    'numpy',
    'seaborn',
    'openpyxl',
    'reportlab',
    'tkcalendar',
    'ttkthemes',
    'datetime',
    'json',
    'csv',
    'pathlib',
    'threading',
    'queue',
    'time',
    'calendar',
    'decimal',
    'collections',
    'functools',
    'itertools',
    'operator',
    're',
    'math',
    'statistics',
    'warnings',
    'logging',
    'traceback',
    'inspect',
    'types',
    'weakref',
    'copy',
    'pickle',
    'base64',
    'hashlib',
    'uuid',
    'random',
    'string',
    'io',
    'tempfile',
    'shutil',
    'glob',
    'fnmatch',
    'os',
    'sys',
    'platform',
    'subprocess',
    'argparse',
    'configparser',
    'xml',
    'html',
    'urllib',
    'http',
    'email',
    'smtplib',
    'zipfile',
    'tarfile',
    'gzip',
    'bz2',
    'lzma',
    'zlib',
    'binascii',
    'struct',
    'array',
    'mmap',
    'ctypes',
    'multiprocessing',
    'concurrent',
    'asyncio',
    'socket',
    'ssl',
    'ftplib',
    'poplib',
    'imaplib',
    'nntplib',
    'smtpd',
    'telnetlib',
    'socketserver',
    'wsgiref',
    'cgi',
    'cgitb',
    'wsgiref',
    'urllib3',
    'requests',
    'certifi',
    'charset_normalizer',
    'idna',
    'urllib3',
    'six',
    'python_dateutil',
    'pytz',
    'numpy',
    'pandas',
    'matplotlib',
    'seaborn',
    'PIL',
    'opencv-python',
    'qrcode',
    'pyzbar',
    'openpyxl',
    'reportlab',
    'tkcalendar',
    'ttkthemes'
]

a = Analysis(
    ['main.py'],
    pathex=[str(Path(__file__).parent)],
    binaries=[],
    datas=datas,
    hiddenimports=hiddenimports,
    hookspath=[],
    hooksconfig={},
    runtime_hooks=[],
    excludes=[],
    win_no_prefer_redirects=False,
    win_private_assemblies=False,
    cipher=block_cipher,
    noarchive=False,
)

pyz = PYZ(a.pure, a.zipped_data, cipher=block_cipher)

exe = EXE(
    pyz,
    a.scripts,
    a.binaries,
    a.zipfiles,
    a.datas,
    [],
    name='MonaBeautyStore_Inventory',
    debug=False,
    bootloader_ignore_signals=False,
    strip=False,
    upx=True,
    upx_exclude=[],
    runtime_tmpdir=None,
    console=False,
    disable_windowed_traceback=False,
    argv_emulation=False,
    target_arch=None,
    codesign_identity=None,
    entitlements_file=None,
    icon=None
)
'''
        
        with open(self.spec_file, 'w', encoding='utf-8') as f:
            f.write(spec_content)
        print(f"Created spec file: {self.spec_file}")
    
    def install_dependencies(self):
        """Install required dependencies"""
        print("Installing dependencies...")
        try:
            subprocess.run([sys.executable, "-m", "pip", "install", "-r", "requirements.txt"], 
                         check=True, cwd=self.project_dir)
            print("Dependencies installed successfully")
        except subprocess.CalledProcessError as e:
            print(f"Error installing dependencies: {e}")
            return False
        return True
    
    def build_executable(self):
        """Build the executable using PyInstaller"""
        print("Building executable...")
        try:
            # Use direct PyInstaller command instead of spec file
            cmd = [
                sys.executable, "-m", "PyInstaller",
                "--onefile",  # Single executable file
                "--windowed",  # No console window
                "--name=MonaBeautyStore_Inventory",
                "--add-data=database;database",  # Include database folder
                "--add-data=ui;ui",  # Include ui folder
                "--add-data=utils;utils",  # Include utils folder
                "--add-data=generated_barcodes;generated_barcodes",  # Include generated_barcodes folder
                "--add-data=inventory.db;.",  # Include database file
                "--add-data=sample_qr_code.png;.",  # Include sample QR code
                "--hidden-import=tkinter",
                "--hidden-import=tkinter.ttk",
                "--hidden-import=tkinter.messagebox",
                "--hidden-import=tkinter.filedialog",
                "--hidden-import=sqlite3",
                "--hidden-import=matplotlib.backends.backend_tkagg",
                "--hidden-import=PIL",
                "--hidden-import=PIL.Image",
                "--hidden-import=cv2",
                "--hidden-import=qrcode",
                "--hidden-import=pyzbar",
                "--hidden-import=pandas",
                "--hidden-import=numpy",
                "--hidden-import=openpyxl",
                "--hidden-import=reportlab",
                "--hidden-import=tkcalendar",
                "--hidden-import=ttkthemes",
                "main.py"
            ]
            
            result = subprocess.run(cmd, check=True, cwd=self.project_dir, 
                                  capture_output=True, text=True)
            print("Build completed successfully!")
            return True
        except subprocess.CalledProcessError as e:
            print(f"Build failed: {e}")
            print(f"Error output: {e.stderr}")
            return False
    
    def create_launcher_script(self):
        """Create a launcher script for the client"""
        launcher_content = '''@echo off
title Mona Beauty Store - Inventory Management System
echo Starting Mona Beauty Store Inventory System...
echo.

REM Check if the executable exists
if not exist "MonaBeautyStore_Inventory.exe" (
    echo ERROR: MonaBeautyStore_Inventory.exe not found!
    echo Please make sure the executable is in the same folder as this script.
    pause
    exit /b 1
)

REM Run the application
start "" "MonaBeautyStore_Inventory.exe"

REM Wait a moment and then close this window
timeout /t 3 /nobreak >nul
exit
'''
        
        launcher_path = self.dist_dir / "Start_Inventory_System.bat"
        with open(launcher_path, 'w') as f:
            f.write(launcher_content)
        print(f"Created launcher script: {launcher_path}")
    
    def create_readme(self):
        """Create a README file for the client"""
        readme_content = '''# Mona Beauty Store - Inventory Management System

## Quick Start Guide

### How to Run the Application:
1. Double-click on "Start_Inventory_System.bat" OR
2. Double-click on "MonaBeautyStore_Inventory.exe"

### First Time Setup:
- The application will automatically create a database on first run
- No additional setup required!

### Features:
- Product Management (Add, Edit, Delete Products)
- Barcode/QR Code Generation and Scanning
- Sales Management
- Inventory Tracking
- Reports and Analytics
- Data Export (Excel, PDF)

### System Requirements:
- Windows 10 or later
- At least 4GB RAM
- 100MB free disk space
- Webcam (for barcode/QR scanning)

### Troubleshooting:
- If the application doesn't start, try running as Administrator
- Make sure your antivirus isn't blocking the application
- For barcode scanning issues, ensure your webcam is working

### Support:
Contact your system administrator for technical support.

---
© 2024 Mona Beauty Store - Inventory Management System
'''
        
        readme_path = self.dist_dir / "README.txt"
        with open(readme_path, 'w') as f:
            f.write(readme_content)
        print(f"Created README: {readme_path}")
    
    def copy_additional_files(self):
        """Copy additional files needed for the application"""
        print("Copying additional files...")
        
        # Files to copy to dist directory
        files_to_copy = [
            "inventory.db",
            "sample_qr_code.png"
        ]
        
        for file_name in files_to_copy:
            src = self.project_dir / file_name
            dst = self.dist_dir / file_name
            if src.exists():
                shutil.copy2(src, dst)
                print(f"Copied {file_name}")
    
    def create_installer_package(self):
        """Create a complete installer package"""
        print("Creating installer package...")
        
        # Create a package directory
        package_dir = self.project_dir / "MonaBeautyStore_Package"
        if package_dir.exists():
            shutil.rmtree(package_dir)
        package_dir.mkdir()
        
        # Copy all files from dist to package
        for item in self.dist_dir.iterdir():
            if item.is_file():
                shutil.copy2(item, package_dir)
            elif item.is_dir():
                shutil.copytree(item, package_dir / item.name)
        
        print(f"Package created at: {package_dir}")
        return package_dir
    
    def build(self):
        """Main build process"""
        print("=" * 70)
        print("MONA BEAUTY STORE - PRODUCTION BUILD")
        print("=" * 70)
        
        # Step 1: Clean previous builds
        self.clean_build_dirs()
        
        # Step 2: Install dependencies
        if not self.install_dependencies():
            print("Failed to install dependencies. Aborting build.")
            return False
        
        # Step 3: Skip spec file (using direct PyInstaller command)
        
        # Step 4: Build executable
        if not self.build_executable():
            print("Build failed. Check error messages above.")
            return False
        
        # Step 5: Create additional files
        self.create_launcher_script()
        self.create_readme()
        self.copy_additional_files()
        
         # Step 6: Create installer package
        package_dir = self.create_installer_package()
        
        # Step 7: Show results
        exe_path = self.dist_dir / "MonaBeautyStore_Inventory.exe"
        if exe_path.exists():
            size_mb = exe_path.stat().st_size / (1024 * 1024)
            print(f"\n✅ BUILD SUCCESSFUL!")
            print(f"📁 Executable: {exe_path}")
            print(f"📊 Size: {size_mb:.2f} MB")
            print(f"📦 Package: {package_dir}")
            print(f"\n🚀 Ready for delivery to client!")
        else:
            print("❌ Build failed - executable not found")
            return False
        
        return True

def main():
    """Main function"""
    builder = ProductionBuilder()
    success = builder.build()
    
    if success:
        print("\n" + "=" * 70)
        print("BUILD COMPLETED SUCCESSFULLY!")
        print("=" * 70)
        print("\nNext steps:")
        print("1. Test the executable in the 'dist' folder")
        print("2. Copy the entire 'MonaBeautyStore_Package' folder to your client")
        print("3. Client can run 'Start_Inventory_System.bat' to start the application")
    else:
        print("\n" + "=" * 70)
        print("BUILD FAILED!")
        print("=" * 70)
        print("Please check the error messages above and try again.")

if __name__ == "__main__":
    main()
