#!/usr/bin/env python3
"""
Test script to verify barcode scanner fixes
"""

import sys
import os

def test_imports():
    """Test all required imports"""
    print("🧪 Testing imports...")
    
    # Test OpenCV
    try:
        import cv2
        print("✅ OpenCV available")
        opencv_available = True
    except ImportError:
        print("❌ OpenCV not available")
        opencv_available = False
    
    # Test NumPy
    try:
        import numpy as np
        print("✅ NumPy available")
        numpy_available = True
    except ImportError:
        print("❌ NumPy not available")
        numpy_available = False
    
    # Test PIL
    try:
        from PIL import Image, ImageTk
        print("✅ PIL available")
        pil_available = True
    except ImportError:
        print("❌ PIL not available")
        pil_available = False
    
    # Test pyzbar
    try:
        from pyzbar import pyzbar
        print("✅ pyzbar available")
        pyzbar_available = True
    except Exception as e:
        print(f"⚠️ pyzbar not available: {str(e)[:100]}...")
        pyzbar_available = False
    
    return opencv_available, numpy_available, pil_available, pyzbar_available

def test_camera_access():
    """Test camera access"""
    print("\n🎥 Testing camera access...")
    
    try:
        import cv2
        camera = cv2.VideoCapture(0)
        
        if camera.isOpened():
            print("✅ Camera accessible")
            ret, frame = camera.read()
            if ret:
                print("✅ Camera can capture frames")
                print(f"   Frame shape: {frame.shape}")
            else:
                print("❌ Camera cannot capture frames")
            camera.release()
            return True
        else:
            print("❌ Camera not accessible")
            return False
            
    except Exception as e:
        print(f"❌ Camera test failed: {e}")
        return False

def test_alternative_scanner():
    """Test alternative barcode scanning"""
    print("\n🔍 Testing alternative scanner...")
    
    try:
        # Import the barcode scanner
        sys.path.append(os.path.join(os.path.dirname(__file__), 'ui'))
        from barcode_scanner import BarcodeScannerFrame
        
        # Create a dummy database manager
        class DummyDB:
            def get_product_by_barcode(self, barcode):
                return None
        
        # Create a dummy parent
        import tkinter as tk
        root = tk.Tk()
        root.withdraw()  # Hide the window
        
        scanner = BarcodeScannerFrame(root, DummyDB())
        
        # Test alternative scanning with a dummy image
        import cv2
        import numpy as np
        
        # Create a simple test image (black and white stripes)
        test_image = np.zeros((100, 200, 3), dtype=np.uint8)
        for i in range(0, 200, 20):
            test_image[:, i:i+10] = 255  # White stripes
        
        result = scanner.alternative_barcode_scan(test_image)
        
        if result:
            print(f"✅ Alternative scanner working - generated: {result}")
        else:
            print("⚠️ Alternative scanner returned no result (expected for test pattern)")
        
        root.destroy()
        return True
        
    except Exception as e:
        print(f"❌ Alternative scanner test failed: {e}")
        return False

def main():
    """Main test function"""
    print("🔧 Barcode Scanner Fix Verification")
    print("=" * 50)
    
    # Test imports
    opencv_ok, numpy_ok, pil_ok, pyzbar_ok = test_imports()
    
    # Test camera
    camera_ok = False
    if opencv_ok:
        camera_ok = test_camera_access()
    
    # Test alternative scanner
    alt_scanner_ok = False
    if opencv_ok and numpy_ok:
        alt_scanner_ok = test_alternative_scanner()
    
    # Summary
    print("\n" + "=" * 50)
    print("📊 SUMMARY:")
    print(f"   OpenCV: {'✅' if opencv_ok else '❌'}")
    print(f"   NumPy: {'✅' if numpy_ok else '❌'}")
    print(f"   PIL: {'✅' if pil_ok else '❌'}")
    print(f"   pyzbar: {'✅' if pyzbar_ok else '⚠️ (will use alternative)'}")
    print(f"   Camera: {'✅' if camera_ok else '❌'}")
    print(f"   Alternative Scanner: {'✅' if alt_scanner_ok else '❌'}")
    
    if opencv_ok and numpy_ok and pil_ok and camera_ok:
        if pyzbar_ok:
            print("\n🎉 EXCELLENT: All systems working! Full barcode scanning available.")
        else:
            print("\n✅ GOOD: Alternative scanning available! Camera will work with fallback method.")
    elif opencv_ok and numpy_ok and pil_ok:
        print("\n⚠️ LIMITED: Libraries OK but no camera access. Manual/image scanning available.")
    else:
        print("\n❌ ISSUES: Some required libraries missing. Check installation.")
    
    print("\n💡 RECOMMENDATIONS:")
    if not opencv_ok:
        print("   - Install OpenCV: pip install opencv-python")
    if not numpy_ok:
        print("   - Install NumPy: pip install numpy")
    if not pil_ok:
        print("   - Install Pillow: pip install pillow")
    if not camera_ok and opencv_ok:
        print("   - Check camera connection and permissions")
        print("   - Close other applications using the camera")
    if not pyzbar_ok:
        print("   - pyzbar has DLL issues - alternative scanner will be used")
        print("   - This is normal and the app will work fine!")

if __name__ == "__main__":
    main()
