#!/usr/bin/env python3
"""
Professional QR Code Scanner - Production-Grade Implementation
Designed for reliable QR code detection and decoding with multiple fallback methods
"""

import cv2
import numpy as np
import time
from typing import Optional, List, Tuple, Dict
import re
import hashlib

class ProfessionalQRScanner:
    """Professional QR code scanner with multiple detection methods"""

    def __init__(self):
        self.last_detection_time = 0
        self.last_qr_code = ""
        self.detection_cooldown = 2.0  # 2 seconds between same QR code

        # Test library availability
        self.opencv_available = self._test_opencv()
        self.pyzbar_available = self._test_pyzbar()

        print(f"🔧 QR Scanner initialized - OpenCV: {self.opencv_available}, pyzbar: {self.pyzbar_available}")

    def _test_opencv(self) -> bool:
        """Test if OpenCV is available and has QR detection"""
        try:
            import cv2
            # Test QR detector creation
            detector = cv2.QRCodeDetector()
            return detector is not None
        except Exception as e:
            print(f"OpenCV QR test failed: {str(e)[:50]}...")
            return False

    def _test_pyzbar(self) -> bool:
        """Test if pyzbar is available"""
        try:
            from pyzbar import pyzbar
            # Test with a simple image
            test_img = np.ones((100, 100), dtype=np.uint8) * 255
            pyzbar.decode(test_img)
            return True
        except Exception as e:
            print(f"pyzbar test failed: {str(e)[:50]}...")
            return False

    def scan_frame(self, frame) -> Optional[str]:
        """Main scanning method - tries all available methods"""
        current_time = time.time()

        try:
            # Method 1: Try OpenCV QR detector (most reliable for QR codes)
            if self.opencv_available:
                qr_data = self._scan_with_opencv_qr(frame)
                if qr_data and self._should_report_qr(qr_data, current_time):
                    print(f"✅ OpenCV QR detected: {qr_data}")
                    return qr_data

            # Method 2: Try pyzbar (works for QR codes too)
            if self.pyzbar_available:
                qr_data = self._scan_with_pyzbar(frame)
                if qr_data and self._should_report_qr(qr_data, current_time):
                    print(f"✅ pyzbar QR detected: {qr_data}")
                    return qr_data

            # Method 3: Try enhanced image processing
            qr_data = self._scan_with_enhanced_processing(frame)
            if qr_data and self._should_report_qr(qr_data, current_time):
                print(f"✅ Enhanced QR detected: {qr_data}")
                return qr_data

            return None

        except Exception as e:
            print(f"❌ QR scan error: {e}")
            return None

    def _scan_with_opencv_qr(self, frame) -> Optional[str]:
        """Scan using OpenCV's built-in QR detector"""
        try:
            detector = cv2.QRCodeDetector()

            # Try original frame
            data, bbox, _ = detector.detectAndDecode(frame)
            if data and self._is_valid_qr_data(data):
                return data

            # Try grayscale conversion
            if len(frame.shape) == 3:
                gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
                data, bbox, _ = detector.detectAndDecode(gray)
                if data and self._is_valid_qr_data(data):
                    return data

            # Try enhanced image
            enhanced = self._enhance_image_for_qr(frame)
            data, bbox, _ = detector.detectAndDecode(enhanced)
            if data and self._is_valid_qr_data(data):
                return data

            return None

        except Exception as e:
            print(f"OpenCV QR scan error: {e}")
            return None

    def _scan_with_pyzbar(self, frame) -> Optional[str]:
        """Scan using pyzbar (supports QR codes)"""
        try:
            from pyzbar import pyzbar

            # Try original frame
            decoded_objects = pyzbar.decode(frame)
            for obj in decoded_objects:
                if obj.type == 'QRCODE':
                    data = obj.data.decode('utf-8')
                    if self._is_valid_qr_data(data):
                        return data

            # Try grayscale
            if len(frame.shape) == 3:
                gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
                decoded_objects = pyzbar.decode(gray)
                for obj in decoded_objects:
                    if obj.type == 'QRCODE':
                        data = obj.data.decode('utf-8')
                        if self._is_valid_qr_data(data):
                            return data

            return None

        except Exception as e:
            print(f"pyzbar QR scan error: {e}")
            return None

    def _scan_with_enhanced_processing(self, frame) -> Optional[str]:
        """Enhanced QR scanning with image preprocessing"""
        try:
            if not self.opencv_available:
                return None

            # Multiple preprocessing techniques
            preprocessing_methods = [
                lambda img: img,  # Original
                lambda img: cv2.convertScaleAbs(img, alpha=1.2, beta=10),  # Contrast enhancement
                lambda img: cv2.GaussianBlur(img, (3, 3), 0),  # Slight blur
                lambda img: self._adaptive_threshold(img),  # Adaptive threshold
                lambda img: self._morphological_operations(img),  # Morphological operations
            ]

            detector = cv2.QRCodeDetector()

            for method in preprocessing_methods:
                try:
                    processed = method(frame.copy() if len(frame.shape) == 3 else frame)
                    data, bbox, _ = detector.detectAndDecode(processed)
                    if data and self._is_valid_qr_data(data):
                        return data
                except:
                    continue

            return None

        except Exception as e:
            print(f"Enhanced processing error: {e}")
            return None

    def _enhance_image_for_qr(self, image):
        """Enhance image for better QR detection"""
        try:
            if len(image.shape) == 2:
                return image

            # Convert to grayscale
            gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)

            # Apply CLAHE (Contrast Limited Adaptive Histogram Equalization)
            clahe = cv2.createCLAHE(clipLimit=2.0, tileGridSize=(8, 8))
            enhanced = clahe.apply(gray)

            # Slight blur to reduce noise
            enhanced = cv2.GaussianBlur(enhanced, (3, 3), 0)

            return enhanced

        except Exception as e:
            print(f"Image enhancement error: {e}")
            return image

    def _adaptive_threshold(self, image):
        """Apply adaptive thresholding"""
        try:
            if len(image.shape) == 3:
                gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
            else:
                gray = image

            # Adaptive threshold
            thresh = cv2.adaptiveThreshold(
                gray, 255, cv2.ADAPTIVE_THRESH_GAUSSIAN_C,
                cv2.THRESH_BINARY, 11, 2
            )

            return thresh

        except Exception as e:
            return image

    def _morphological_operations(self, image):
        """Apply morphological operations to clean the image"""
        try:
            if len(image.shape) == 3:
                gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
            else:
                gray = image

            # Create kernel
            kernel = np.ones((2, 2), np.uint8)

            # Apply morphological operations
            opening = cv2.morphologyEx(gray, cv2.MORPH_OPEN, kernel)
            closing = cv2.morphologyEx(opening, cv2.MORPH_CLOSE, kernel)

            return closing

        except Exception as e:
            return image

    def _is_valid_qr_data(self, data: str) -> bool:
        """Validate if the detected data looks like valid QR code content"""
        try:
            if not data or len(data.strip()) < 2:
                return False

            # Remove common noise patterns
            clean_data = data.strip()

            # Check for minimum content requirements
            if len(clean_data) < 2:
                return False

            # Check for reasonable character distribution
            if len(set(clean_data)) < 2 and len(clean_data) > 10:
                # All same characters is likely noise
                return False

            # Check for URL patterns (common QR content)
            url_pattern = re.compile(r'^(https?://|www\.|ftp://)')
            if url_pattern.match(clean_data.lower()):
                return True

            # Check for email patterns
            email_pattern = re.compile(r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$')
            if email_pattern.match(clean_data):
                return True

            # Check for phone numbers
            phone_pattern = re.compile(r'^\+?[\d\s\-\(\)]{7,}$')
            if phone_pattern.match(clean_data):
                return True

            # Check for product codes (alphanumeric with reasonable length)
            product_pattern = re.compile(r'^[A-Z0-9\-_\.]{3,50}$', re.IGNORECASE)
            if product_pattern.match(clean_data):
                return True

            # Allow text content
            if len(clean_data) >= 3 and len(clean_data) <= 500:
                return True

            return False

        except Exception as e:
            print(f"QR data validation error: {e}")
            return False

    def _should_report_qr(self, qr_data: str, current_time: float) -> bool:
        """Check if QR code should be reported (avoid duplicates)"""
        try:
            # Check cooldown period
            if (qr_data == self.last_qr_code and
                current_time - self.last_detection_time < self.detection_cooldown):
                return False

            # Update tracking
            self.last_qr_code = qr_data
            self.last_detection_time = current_time

            return True

        except Exception as e:
            print(f"Should report QR error: {e}")
            return True

    def scan_image_file(self, image_path: str) -> Optional[str]:
        """Scan QR code from image file"""
        try:
            if not self.opencv_available:
                return None

            # Load image
            frame = cv2.imread(image_path)
            if frame is None:
                return None

            return self.scan_frame(frame)

        except Exception as e:
            print(f"Image file QR scan error: {e}")
            return None

    def get_status(self) -> Dict:
        """Get scanner status"""
        return {
            'opencv_available': self.opencv_available,
            'pyzbar_available': self.pyzbar_available,
            'working': self.opencv_available or self.pyzbar_available,
            'methods': [
                'opencv_qr' if self.opencv_available else None,
                'pyzbar_qr' if self.pyzbar_available else None,
                'enhanced_processing'
            ]
        }

# Test function
def test_professional_qr_scanner():
    """Test the professional QR scanner"""
    print("🧪 Testing Professional QR Code Scanner")
    print("=" * 50)

    scanner = ProfessionalQRScanner()
    status = scanner.get_status()

    print("📊 Scanner Status:")
    for key, value in status.items():
        print(f"   {key}: {value}")

    # Test with camera if available
    if scanner.opencv_available:
        print("\n📷 Testing with camera...")
        try:
            camera = cv2.VideoCapture(0)
            if camera.isOpened():
                print("✅ Camera opened")

                for i in range(10):  # Test 10 frames
                    ret, frame = camera.read()
                    if ret:
                        result = scanner.scan_frame(frame)
                        if result:
                            print(f"🎯 Frame {i}: Detected {result}")
                        else:
                            print(f"🔍 Frame {i}: Scanning...")
                    time.sleep(0.5)

                camera.release()
            else:
                print("❌ Camera not available")
        except Exception as e:
            print(f"❌ Camera test error: {e}")

    return scanner

if __name__ == "__main__":
    test_professional_qr_scanner()

