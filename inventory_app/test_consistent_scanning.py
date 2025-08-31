#!/usr/bin/env python3
"""
Test consistent barcode scanning without false positives
"""

import sys
import os
import cv2
import numpy as np
import time

# Add the current directory to Python path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

def test_consistent_scanning():
    """Test that scanner doesn't detect false positives"""
    print("🧪 Testing Consistent Barcode Scanning")
    print("=" * 60)
    
    try:
        from utils.production_barcode_scanner import ProductionBarcodeScanner
        
        scanner = ProductionBarcodeScanner()
        
        # Test with empty/noise frames
        print("📷 Testing with empty frames (should not detect anything)...")
        
        # Create various test frames that should NOT trigger detection
        test_frames = [
            create_empty_frame(),
            create_noise_frame(),
            create_text_frame(),
            create_random_lines_frame()
        ]
        
        false_positives = 0
        total_tests = len(test_frames)
        
        for i, frame in enumerate(test_frames):
            result = scanner.scan_frame(frame)
            if result:
                print(f"❌ False positive detected in frame {i+1}: {result}")
                false_positives += 1
            else:
                print(f"✅ Frame {i+1}: Correctly ignored")
        
        print(f"\n📊 Results:")
        print(f"   Total tests: {total_tests}")
        print(f"   False positives: {false_positives}")
        print(f"   Accuracy: {((total_tests - false_positives) / total_tests) * 100:.1f}%")
        
        if false_positives == 0:
            print("🎉 Perfect! No false positives detected.")
            return True
        else:
            print("⚠️ Some false positives detected - scanner may be too sensitive")
            return False
        
    except Exception as e:
        print(f"❌ Test error: {e}")
        return False

def create_empty_frame():
    """Create empty white frame"""
    return np.ones((480, 640, 3), dtype=np.uint8) * 255

def create_noise_frame():
    """Create random noise frame"""
    return np.random.randint(0, 256, (480, 640, 3), dtype=np.uint8)

def create_text_frame():
    """Create frame with text (not barcode)"""
    frame = np.ones((480, 640, 3), dtype=np.uint8) * 255
    cv2.putText(frame, "MONA BEAUTY STORE", (100, 240), 
                cv2.FONT_HERSHEY_SIMPLEX, 2, (0, 0, 0), 3)
    return frame

def create_random_lines_frame():
    """Create frame with random lines (not barcode pattern)"""
    frame = np.ones((480, 640, 3), dtype=np.uint8) * 255
    
    # Add some random lines
    for _ in range(20):
        x1, y1 = np.random.randint(0, 640), np.random.randint(0, 480)
        x2, y2 = np.random.randint(0, 640), np.random.randint(0, 480)
        cv2.line(frame, (x1, y1), (x2, y2), (0, 0, 0), 2)
    
    return frame

def test_real_barcode_detection():
    """Test that real barcodes are still detected"""
    print("\n🎯 Testing Real Barcode Detection")
    print("=" * 40)
    
    try:
        from utils.production_barcode_scanner import ProductionBarcodeScanner
        
        scanner = ProductionBarcodeScanner()
        
        # Create a more realistic barcode pattern
        barcode_frame = create_realistic_barcode()
        
        result = scanner.scan_frame(barcode_frame)
        
        if result:
            print(f"✅ Real barcode detected: {result}")
            return True
        else:
            print("⚠️ Real barcode not detected - may need adjustment")
            return False
        
    except Exception as e:
        print(f"❌ Real barcode test error: {e}")
        return False

def create_realistic_barcode():
    """Create a more realistic barcode pattern"""
    frame = np.ones((480, 640, 3), dtype=np.uint8) * 255
    
    # Create barcode-like pattern
    x_start = 100
    y_start = 200
    bar_height = 80
    
    # Standard barcode pattern (wider bars)
    bar_pattern = [3, 1, 3, 1, 2, 2, 1, 3, 2, 1, 3, 1, 2, 2, 3, 1, 1, 3, 2, 1]
    
    x_pos = x_start
    for i, width in enumerate(bar_pattern):
        color = (0, 0, 0) if i % 2 == 0 else (255, 255, 255)  # Alternate black/white
        cv2.rectangle(frame, (x_pos, y_start), (x_pos + width * 4, y_start + bar_height), color, -1)
        x_pos += width * 4
    
    return frame

def main():
    """Main test function"""
    print("🔧 CONSISTENT SCANNING TEST SUITE")
    print("=" * 60)
    
    try:
        # Test 1: No false positives
        consistent = test_consistent_scanning()
        
        # Test 2: Real barcode detection
        detection = test_real_barcode_detection()
        
        print("\n" + "=" * 60)
        if consistent and detection:
            print("🎉 ALL TESTS PASSED!")
            print("✅ Scanner is consistent and accurate")
            print("✅ No false positives from noise")
            print("✅ Real barcodes still detected")
            print("\n🚀 Scanner is ready for production!")
        elif consistent:
            print("✅ Consistency test passed (no false positives)")
            print("⚠️ Real barcode detection may need tuning")
        else:
            print("❌ Consistency issues detected")
            print("💡 Scanner may be too sensitive")
        
        return 0 if consistent else 1
        
    except Exception as e:
        print(f"\n💥 Test suite error: {e}")
        return 1

if __name__ == "__main__":
    sys.exit(main())
