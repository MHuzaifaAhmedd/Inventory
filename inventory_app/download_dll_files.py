#!/usr/bin/env python3
"""
Helper script to download missing DLL files for barcode scanning
"""

import os
import urllib.request
import sys

def download_file(url, filename):
    """Download a file from URL"""
    try:
        print(f"Downloading {filename}...")
        urllib.request.urlretrieve(url, filename)
        print(f"✅ Downloaded {filename}")
        return True
    except Exception as e:
        print(f"❌ Failed to download {filename}: {e}")
        return False

def main():
    print("🔧 DLL File Downloader for Barcode Scanning")
    print("=" * 50)
    
    # DLL files needed
    dll_files = {
        "libzbar-64.dll": "https://raw.githubusercontent.com/NaturalHistoryMuseum/pyzbar/master/libzbar-64/libzbar-64.dll",
        "libiconv.dll": "https://raw.githubusercontent.com/NaturalHistoryMuseum/pyzbar/master/libzbar-64/libiconv.dll"
    }
    
    print("This script will download the missing DLL files needed for camera barcode scanning.")
    print("\nFiles to download:")
    for filename in dll_files.keys():
        print(f"  • {filename}")
    
    print("\nAfter downloading, you need to:")
    print("1. Copy these files to C:\\Windows\\System32\\")
    print("2. Restart your computer")
    print("3. Camera scanning will work!")
    
    response = input("\nDo you want to download these files? (y/n): ").lower().strip()
    
    if response != 'y':
        print("Download cancelled.")
        return
    
    # Create downloads directory
    download_dir = "dll_downloads"
    if not os.path.exists(download_dir):
        os.makedirs(download_dir)
    
    print(f"\nDownloading to: {download_dir}/")
    
    # Download files
    success_count = 0
    for filename, url in dll_files.items():
        filepath = os.path.join(download_dir, filename)
        if download_file(url, filepath):
            success_count += 1
    
    print(f"\n{'='*50}")
    if success_count == len(dll_files):
        print("🎉 All files downloaded successfully!")
        print(f"\nNext steps:")
        print(f"1. Go to folder: {os.path.abspath(download_dir)}")
        print(f"2. Copy both .dll files to: C:\\Windows\\System32\\")
        print(f"3. Restart your computer")
        print(f"4. Run the inventory app - camera scanning will work!")
    else:
        print(f"⚠️ Only {success_count}/{len(dll_files)} files downloaded successfully.")
        print("Some files may need to be downloaded manually.")
    
    print(f"\nManual download links:")
    for filename, url in dll_files.items():
        print(f"  {filename}: {url}")

if __name__ == "__main__":
    main()

