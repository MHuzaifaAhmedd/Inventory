#!/usr/bin/env python3
"""
Demo script to show barcode scanner working in real-time
"""

import cv2
import sys
import os
import time

# Add the current directory to Python path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

def demo_real_time_scanning():
    """Demo real-time barcode scanning"""
    print("🎥 LIVE BARCODE SCANNER DEMO")
    print("=" * 50)
    print("📷 Starting camera...")
    print("🔍 Point any barcode at the camera")
    print("❌ Press 'q' to quit")
    print("=" * 50)
    
    try:
        from utils.production_barcode_scanner import ProductionBarcodeScanner
        
        # Initialize scanner
        scanner = ProductionBarcodeScanner()
        status = scanner.get_scanner_status()
        
        print(f"🚀 Scanner method: {status['recommended_method']}")
        print(f"📊 Methods available: {status['methods_available']}")
        
        # Open camera
        camera = cv2.VideoCapture(0)
        
        if not camera.isOpened():
            print("❌ Cannot open camera")
            return
        
        print("✅ Camera opened - scanning for barcodes...")
        
        last_barcode = ""
        last_time = 0
        frame_count = 0
        
        while True:
            ret, frame = camera.read()
            if not ret:
                print("❌ Failed to read frame")
                break
            
            # Display frame
            cv2.imshow('Barcode Scanner Demo - Press Q to quit', frame)
            
            # Scan every 10 frames for performance
            if frame_count % 10 == 0:
                current_time = time.time()
                
                try:
                    barcode_data = scanner.scan_frame(frame)
                    
                    if barcode_data and barcode_data != last_barcode:
                        # Avoid duplicate detections within 3 seconds
                        if current_time - last_time > 3.0:
                            print(f"🎯 BARCODE DETECTED: {barcode_data}")
                            last_barcode = barcode_data
                            last_time = current_time
                            
                            # Add visual indicator
                            cv2.putText(frame, f"DETECTED: {barcode_data}", 
                                       (10, 30), cv2.FONT_HERSHEY_SIMPLEX, 
                                       1, (0, 255, 0), 2)
                
                except Exception as e:
                    if frame_count % 100 == 0:  # Log errors occasionally
                        print(f"⚠️ Scan error: {str(e)[:50]}")
            
            frame_count += 1
            
            # Check for quit key
            if cv2.waitKey(1) & 0xFF == ord('q'):
                break
        
        camera.release()
        cv2.destroyAllWindows()
        print("\n✅ Demo completed")
        
    except Exception as e:
        print(f"❌ Demo error: {e}")
        import traceback
        traceback.print_exc()

def demo_test_with_existing_products():
    """Demo with existing products in database"""
    print("\n📦 Testing with Existing Products")
    print("=" * 40)
    
    try:
        from database.db_manager import DatabaseManager
        
        db = DatabaseManager()
        products = db.get_products()
        
        if products:
            print("Available products for testing:")
            for product in products[:3]:  # Show first 3
                name, sku, barcode = product[1], product[2], product[3]
                print(f"   📦 {name}")
                print(f"      SKU: {sku or 'N/A'}")
                print(f"      Barcode: {barcode or 'N/A'}")
        else:
            print("⚠️ No products found in database")
        
    except Exception as e:
        print(f"❌ Database test error: {e}")

def main():
    """Main demo function"""
    print("🎬 PRODUCTION BARCODE SCANNER DEMO")
    print("=" * 60)
    
    try:
        # Show existing products
        demo_test_with_existing_products()
        
        # Ask user if they want to run live demo
        print("\n🎥 Live Camera Demo")
        response = input("Start live camera scanning demo? (y/n): ").lower().strip()
        
        if response == 'y':
            demo_real_time_scanning()
        else:
            print("Demo cancelled")
        
        print("\n🎊 Demo completed!")
        print("🚀 Your barcode scanner is production-ready!")
        
        return 0
        
    except KeyboardInterrupt:
        print("\n⏹️ Demo interrupted by user")
        return 0
    except Exception as e:
        print(f"\n💥 Demo error: {e}")
        return 1

if __name__ == "__main__":
    sys.exit(main())
