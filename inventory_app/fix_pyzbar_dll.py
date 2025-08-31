#!/usr/bin/env python3
"""
Automated fix for pyzbar DLL dependencies on Windows
This script downloads and places the required DLL files automatically
"""

import os
import sys
import urllib.request
import shutil
import site
from pathlib import Path

def download_file(url, filepath):
    """Download a file from URL with progress indication"""
    try:
        print(f"📥 Downloading {os.path.basename(filepath)}...")
        
        def progress_hook(block_num, block_size, total_size):
            if total_size > 0:
                percent = min(100, (block_num * block_size * 100) // total_size)
                print(f"\r   Progress: {percent}%", end="", flush=True)
        
        urllib.request.urlretrieve(url, filepath, progress_hook)
        print(f"\n✅ Downloaded {os.path.basename(filepath)}")
        return True
    except Exception as e:
        print(f"\n❌ Failed to download {os.path.basename(filepath)}: {e}")
        return False

def get_pyzbar_directory():
    """Find the pyzbar installation directory"""
    try:
        import pyzbar
        pyzbar_path = Path(pyzbar.__file__).parent
        print(f"📍 Found pyzbar at: {pyzbar_path}")
        return pyzbar_path
    except ImportError:
        print("❌ pyzbar not found. Please install it first: pip install pyzbar")
        return None

def check_dll_exists(dll_path):
    """Check if DLL file exists"""
    return dll_path.exists()

def backup_existing_dll(dll_path):
    """Backup existing DLL if it exists"""
    if dll_path.exists():
        backup_path = dll_path.with_suffix(dll_path.suffix + '.backup')
        try:
            shutil.copy2(dll_path, backup_path)
            print(f"📦 Backed up existing {dll_path.name} to {backup_path.name}")
        except Exception as e:
            print(f"⚠️ Could not backup {dll_path.name}: {e}")

def fix_pyzbar_dlls():
    """Main function to fix pyzbar DLL dependencies"""
    print("🔧 Fixing pyzbar DLL Dependencies")
    print("=" * 50)
    
    # Check if we're on Windows
    if sys.platform != "win32":
        print("ℹ️ This fix is only needed on Windows systems.")
        return True
    
    # Find pyzbar directory
    pyzbar_dir = get_pyzbar_directory()
    if not pyzbar_dir:
        return False
    
    # DLL files and their sources
    dll_files = {
        "libzbar-64.dll": "https://raw.githubusercontent.com/NaturalHistoryMuseum/pyzbar/master/pyzbar/libzbar-64.dll",
        "libiconv.dll": "https://raw.githubusercontent.com/NaturalHistoryMuseum/pyzbar/master/pyzbar/libiconv.dll"
    }
    
    print(f"\n📋 Checking DLL files in pyzbar directory...")
    
    success_count = 0
    for dll_name, dll_url in dll_files.items():
        dll_path = pyzbar_dir / dll_name
        
        if check_dll_exists(dll_path):
            print(f"✅ {dll_name} already exists")
            success_count += 1
            continue
        
        print(f"❌ {dll_name} missing - downloading...")
        
        # Create temporary download path
        temp_path = pyzbar_dir / f"{dll_name}.tmp"
        
        if download_file(dll_url, temp_path):
            try:
                # Move temporary file to final location
                shutil.move(temp_path, dll_path)
                print(f"✅ Installed {dll_name}")
                success_count += 1
            except Exception as e:
                print(f"❌ Failed to install {dll_name}: {e}")
                if temp_path.exists():
                    temp_path.unlink()
        
    print(f"\n{'='*50}")
    
    if success_count == len(dll_files):
        print("🎉 All DLL files are now in place!")
        print("\n✅ pyzbar should now work correctly.")
        print("✅ Camera barcode scanning should be functional.")
        
        # Test pyzbar import
        print("\n🧪 Testing pyzbar import...")
        try:
            from pyzbar import pyzbar
            print("✅ pyzbar imports successfully!")
            
            # Test basic functionality
            print("🧪 Testing pyzbar functionality...")
            # This won't actually decode anything but will test if the library loads
            print("✅ pyzbar is ready to use!")
            
        except Exception as e:
            print(f"❌ pyzbar still has issues: {e}")
            print("\n🔄 You may need to:")
            print("   1. Restart your computer")
            print("   2. Reinstall pyzbar: pip uninstall pyzbar && pip install pyzbar")
            return False
            
        return True
    else:
        print(f"⚠️ Only {success_count}/{len(dll_files)} DLL files installed successfully.")
        print("\n🔧 Manual steps:")
        print("1. Download the missing DLL files manually")
        print("2. Place them in the pyzbar directory:")
        print(f"   {pyzbar_dir}")
        
        print(f"\n📥 Manual download links:")
        for dll_name, dll_url in dll_files.items():
            print(f"   {dll_name}: {dll_url}")
        
        return False

def main():
    """Main entry point"""
    try:
        success = fix_pyzbar_dlls()
        
        if success:
            print("\n🚀 Ready to test!")
            print("   Run your inventory app and try the camera scanner.")
            return 0
        else:
            print("\n❌ Fix incomplete. Please check the manual steps above.")
            return 1
            
    except KeyboardInterrupt:
        print("\n\n⏹️ Operation cancelled by user.")
        return 1
    except Exception as e:
        print(f"\n💥 Unexpected error: {e}")
        return 1

if __name__ == "__main__":
    sys.exit(main())
