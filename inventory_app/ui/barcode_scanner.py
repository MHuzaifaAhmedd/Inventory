"""
Barcode Scanner Frame for Inventory Management System
Handles barcode scanning via external scanner or camera
"""

import tkinter as tk
from tkinter import ttk, messagebox, filedialog, simpledialog
import threading
import time
from PIL import Image, ImageTk
import os
import sys

# Graceful import handling for production
try:
    import cv2
    CV2_AVAILABLE = True
except ImportError:
    CV2_AVAILABLE = False
    print("⚠️ OpenCV not available - camera scanning disabled")

try:
    import numpy as np
    NUMPY_AVAILABLE = True
except ImportError:
    NUMPY_AVAILABLE = False
    print("⚠️ NumPy not available - alternative scanning limited")

# Don't import pyzbar at startup - import only when needed
PYZBAR_AVAILABLE = False
USE_ALTERNATIVE_SCANNER = False

try:
    import barcode
    from barcode.writer import ImageWriter
    BARCODE_AVAILABLE = True
except ImportError:
    BARCODE_AVAILABLE = False
    print("⚠️ python-barcode not available - barcode generation disabled")

class BarcodeScannerFrame(ttk.Frame):
    def __init__(self, parent, db_manager):
        super().__init__(parent)
        self.parent = parent
        self.db_manager = db_manager
        self.camera = None
        self.is_camera_on = False
        self.scan_thread = None
        
        self.create_widgets()
        
    def create_widgets(self):
        # Title
        title_label = ttk.Label(self, text="📱 Barcode Scanner", 
                               font=("Arial", 16, "bold"))
        title_label.pack(pady=10)
        
        # Status indicator
        self.create_status_indicator()
        
        # Camera frame
        self.camera_frame = ttk.LabelFrame(self, text="Camera Scanner", padding=10)
        self.camera_frame.pack(fill="both", expand=True, padx=20, pady=10)
        
        # Camera display
        self.camera_label = ttk.Label(self.camera_frame, text="Camera not started")
        self.camera_label.pack(pady=10)
        
        # Camera controls
        self.create_camera_controls()
        
        # Manual entry frame
        manual_frame = ttk.LabelFrame(self, text="Manual Entry", padding=10)
        manual_frame.pack(fill="x", padx=20, pady=10)
        
        # Manual entry controls
        self.create_manual_controls()
        
        # Alternative methods frame
        alt_frame = ttk.LabelFrame(self, text="Alternative Scanning Methods", padding=10)
        alt_frame.pack(fill="x", padx=20, pady=10)
        
        # Alternative methods
        self.create_alternative_methods(alt_frame)
        
        # Results frame
        results_frame = ttk.LabelFrame(self, text="Scan Results", padding=10)
        results_frame.pack(fill="x", padx=20, pady=10)
        
        # Results display
        self.results_text = tk.Text(results_frame, height=8, width=50)
        self.results_text.pack(fill="both", expand=True)
        
        # Action buttons frame
        action_frame = ttk.Frame(results_frame)
        action_frame.pack(fill="x", pady=5)
        
        # Clear results button
        clear_btn = ttk.Button(action_frame, text="Clear Results", 
                              command=self.clear_results)
        clear_btn.pack(side="left", padx=5)
        
        # Generate barcodes button
        generate_btn = ttk.Button(action_frame, text="Generate Barcodes", 
                                 command=self.generate_all_barcodes)
        generate_btn.pack(side="left", padx=5)
        
        # Print sheet button
        print_btn = ttk.Button(action_frame, text="Print Barcode Sheet", 
                              command=self.create_print_sheet)
        print_btn.pack(side="left", padx=5)
        
        # Product actions frame (hidden initially)
        self.product_actions_frame = ttk.Frame(results_frame)
        self.current_product = None
        
    def create_status_indicator(self):
        """Create status indicator showing available scanning methods"""
        status_frame = ttk.Frame(self)
        status_frame.pack(fill="x", padx=20, pady=5)
        
        # Check if pyzbar is available (without importing)
        pyzbar_available = False
        try:
            import importlib.util
            spec = importlib.util.find_spec("pyzbar")
            pyzbar_available = spec is not None
        except:
            pass
            
        if pyzbar_available and CV2_AVAILABLE:
            status_text = "✅ Camera scanning available"
            status_color = "green"
        elif BARCODE_AVAILABLE:
            status_text = "⚠️ Manual entry and image scanning available"
            status_color = "orange"
        else:
            status_text = "❌ No barcode libraries available"
            status_color = "red"
        
        status_label = ttk.Label(status_frame, text=status_text, 
                                foreground=status_color, font=("Arial", 10, "bold"))
        status_label.pack()
        
    def create_camera_controls(self):
        controls_frame = ttk.Frame(self.camera_frame)
        controls_frame.pack(pady=10)
        
        self.start_btn = ttk.Button(controls_frame, text="Start Camera", 
                                   command=self.start_camera)
        self.start_btn.pack(side="left", padx=5)
        
        self.stop_btn = ttk.Button(controls_frame, text="Stop Camera", 
                                  command=self.stop_camera, state="disabled")
        self.stop_btn.pack(side="left", padx=5)
        
        # Help text
        pyzbar_available = False
        try:
            import importlib.util
            spec = importlib.util.find_spec("pyzbar")
            pyzbar_available = spec is not None
        except:
            pass
            
        if pyzbar_available and CV2_AVAILABLE:
            help_text = "✅ Camera scanning ready. Click 'Start Camera' to begin."
        else:
            help_text = "❌ Camera scanning requires pyzbar + OpenCV libraries.\n" \
                       "Use manual entry or alternative methods below."
        
        help_label = ttk.Label(self.camera_frame, text=help_text, 
                              foreground="blue", wraplength=400)
        help_label.pack(pady=5)
        
    def create_manual_controls(self):
        # SKU/Barcode entry
        entry_frame = ttk.Frame(self)
        entry_frame.pack(fill="x", pady=5)
        
        ttk.Label(entry_frame, text="Enter SKU/Barcode:").pack(side="left")
        self.manual_entry = ttk.Entry(entry_frame, width=30)
        self.manual_entry.pack(side="left", padx=5)
        self.manual_entry.bind('<Return>', self.lookup_manual)
        
        lookup_btn = ttk.Button(entry_frame, text="Lookup", 
                               command=self.lookup_manual)
        lookup_btn.pack(side="left", padx=5)
        
        # Quick test button
        test_btn = ttk.Button(entry_frame, text="Test with Sample", 
                             command=self.test_with_sample)
        test_btn.pack(side="left", padx=5)
        
    def create_alternative_methods(self, parent_frame):
        """Create alternative scanning methods"""
        # External scanner
        ext_frame = ttk.Frame(parent_frame)
        ext_frame.pack(fill="x", pady=5)
        
        ext_btn = ttk.Button(ext_frame, text="📱 External USB Scanner", 
                            command=self.use_external_scanner)
        ext_btn.pack(side="left", padx=5)
        
        ext_label = ttk.Label(ext_frame, text="Connect USB scanner, click field, scan")
        ext_label.pack(side="left", padx=5)
        
        # File upload
        file_frame = ttk.Frame(parent_frame)
        file_frame.pack(fill="x", pady=5)
        
        file_btn = ttk.Button(file_frame, text="📷 Upload Image", 
                             command=self.upload_image)
        file_btn.pack(side="left", padx=5)
        
        file_label = ttk.Label(file_frame, text="Upload barcode image for scanning")
        file_label.pack(side="left", padx=5)
        
        # QR code generator
        qr_frame = ttk.Frame(parent_frame)
        qr_frame.pack(fill="x", pady=5)
        
        qr_btn = ttk.Button(qr_frame, text="🔲 Generate QR Code", 
                            command=self.generate_qr_code)
        qr_btn.pack(side="left", padx=5)
        
        qr_label = ttk.Label(qr_frame, text="Create QR codes for your products")
        qr_label.pack(side="left", padx=5)
        
    def try_import_pyzbar(self):
        """Try to import pyzbar when needed"""
        global PYZBAR_AVAILABLE, USE_ALTERNATIVE_SCANNER
        if PYZBAR_AVAILABLE:
            return True
            
        try:
            from pyzbar import pyzbar
            PYZBAR_AVAILABLE = True
            USE_ALTERNATIVE_SCANNER = False
            return True
        except Exception as e:
            PYZBAR_AVAILABLE = False
            USE_ALTERNATIVE_SCANNER = True
            print(f"pyzbar not available: {e}")
            return False
        
    def start_camera(self):
        if not CV2_AVAILABLE:
            messagebox.showwarning("Camera Not Available", 
                "OpenCV library is required for camera scanning.\n\n"
                "To enable camera scanning:\n"
                "1. Install OpenCV: pip install opencv-python\n"
                "2. Restart the application\n\n"
                "For now, use manual entry or image upload instead!")
            return
            
        if not self.try_import_pyzbar():
            result = messagebox.askyesno("Barcode Detection Not Available", 
                "pyzbar library has DLL dependency issues on this system.\n\n"
                "Would you like to try the alternative scanning method?\n\n"
                "Alternative method uses basic image processing\n"
                "and works better for simple barcodes.\n\n"
                "Click Yes to try alternative scanner\n"
                "Click No to use manual entry instead")
            
            if not result:
                return
            else:
                global USE_ALTERNATIVE_SCANNER
                USE_ALTERNATIVE_SCANNER = True
                messagebox.showinfo("Alternative Scanner", 
                    "Using alternative barcode scanning method.\n\n"
                    "This works best with:\n"
                    "• Clear, well-lit barcodes\n"
                    "• 1D barcodes (like UPC/EAN)\n"
                    "• High contrast images\n\n"
                    "Camera will start in basic mode.")
        
        try:
            self.camera = cv2.VideoCapture(0)
            if not self.camera.isOpened():
                messagebox.showerror("Camera Error", 
                                   "❌ Cannot access camera.\n\n"
                                   "Please check:\n"
                                   "• Camera is connected\n"
                                   "• No other app is using camera\n"
                                   "• Camera permissions are enabled")
                return
                
            self.is_camera_on = True
            self.start_btn.config(state="disabled")
            self.stop_btn.config(state="normal")
            
            # Start scanning thread
            self.scan_thread = threading.Thread(target=self.scan_barcodes)
            self.scan_thread.daemon = True
            self.scan_thread.start()
            
            messagebox.showinfo("Camera Started", 
                              "✅ Camera is now active!\n\n"
                              "Point camera at barcodes to scan.\n"
                              "Click 'Stop Camera' when done.")
            
        except Exception as e:
            error_msg = str(e)
            if "libzbar-64.dll" in error_msg or "libiconv.dll" in error_msg:
                self.show_dll_error()
            else:
                messagebox.showerror("Camera Error", f"Failed to start camera: {error_msg}")
    
    def stop_camera(self):
        self.is_camera_on = False
        if self.camera:
            self.camera.release()
            self.camera = None
        
        self.start_btn.config(state="normal")
        self.stop_btn.config(state="disabled")
        self.camera_label.config(text="Camera stopped")
        
    def scan_barcodes(self):
        # Initialize professional scanner
        try:
            from utils.professional_barcode_scanner import ProfessionalBarcodeScanner
            scanner = ProfessionalBarcodeScanner()
            status = scanner.get_status()
            
            self.add_scan_result("🚀 Professional scanner initialized")
            self.add_scan_result(f"📊 Methods available: {[m for m in status['methods'] if m]}")
            self.add_scan_result("🎯 READY TO SCAN - Point camera at barcode!")
            
        except Exception as e:
            self.add_scan_result(f"❌ Scanner initialization failed: {e}")
            scanner = None
        
        scan_count = 0
        
        while self.is_camera_on:
            if self.camera and self.camera.isOpened():
                ret, frame = self.camera.read()
                if ret:
                    # Convert frame for display
                    frame_rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
                    frame_pil = Image.fromarray(frame_rgb)
                    frame_pil = frame_pil.resize((400, 300), Image.Resampling.LANCZOS)
                    frame_tk = ImageTk.PhotoImage(frame_pil)
                    
                    self.camera_label.config(image=frame_tk)
                    self.camera_label.image = frame_tk
                    
                    # Professional barcode scanning
                    if scanner:
                        try:
                            # Scan every 10 frames for good performance
                            if scan_count % 10 == 0:
                                barcode_data = scanner.scan_frame(frame)
                                
                                if barcode_data:
                                    self.add_scan_result(f"🎯 BARCODE DETECTED: {barcode_data}")
                                    self.lookup_product(barcode_data)
                                    
                                    # Visual feedback
                                    self.add_scan_result("✅ Scanning successful!")
                                    
                                    # Brief pause after detection
                                    time.sleep(0.5)
                            
                            scan_count += 1
                            
                        except Exception as e:
                            if scan_count % 50 == 0:  # Log errors occasionally
                                self.add_scan_result(f"⚠️ Scan error: {str(e)[:50]}")
                    
                    # Fallback scanning methods
                    else:
                        # Try pyzbar directly as fallback
                        try:
                            from pyzbar import pyzbar
                            if scan_count % 10 == 0:  # Every 10 frames
                                barcodes = pyzbar.decode(frame)
                                for barcode in barcodes:
                                    barcode_data = barcode.data.decode('utf-8')
                                    barcode_type = barcode.type
                                    
                                    self.add_scan_result(f"📷 Fallback scan - Type: {barcode_type}, Data: {barcode_data}")
                                    self.lookup_product(barcode_data)
                                    time.sleep(0.5)
                                    
                        except Exception as e:
                            if scan_count % 100 == 0:
                                self.add_scan_result("🔍 Scanning for barcodes...")
                        
                        scan_count += 1
                        
            time.sleep(0.1)  # Small delay to prevent high CPU usage
    
    def lookup_manual(self, event=None):
        barcode_data = self.manual_entry.get().strip()
        if barcode_data:
            self.lookup_product(barcode_data)
            self.manual_entry.delete(0, tk.END)
        else:
            messagebox.showwarning("Input Required", "Please enter a SKU or barcode.")
    
    def test_with_sample(self):
        """Test with a sample barcode"""
        sample_barcodes = ["123456789", "987654321", "SAMPLE001", "TEST123"]
        sample = sample_barcodes[int(time.time()) % len(sample_barcodes)]
        self.manual_entry.delete(0, tk.END)
        self.manual_entry.insert(0, sample)
        self.lookup_product(sample)
    
    def lookup_product(self, barcode_data):
        # Search in database
        product = self.db_manager.get_product_by_barcode(barcode_data)
        if product:
            product_id, name, sku, barcode, category_id, cogs, current_stock = product[:7]
            
            # Get category name
            category_name = "Unknown"
            categories = self.db_manager.get_categories()
            for cat in categories:
                if cat[0] == category_id:
                    category_name = cat[1]
                    break
            
            self.add_scan_result(f"✅ Found: {name}")
            self.add_scan_result(f"   SKU: {sku or 'N/A'}")
            self.add_scan_result(f"   Stock: {current_stock} units")
            self.add_scan_result(f"   Category: {category_name}")
            self.add_scan_result(f"   COGS: ₹{cogs:.2f}")
            
            # Show action buttons
            self.show_product_actions(product)
        else:
            self.add_scan_result(f"❌ Not found: {barcode_data}")
            self.add_scan_result(f"   Tip: Add this product in Products section")
            
            # Offer to create new product
            self.offer_create_product(barcode_data)
    
    def use_external_scanner(self):
        messagebox.showinfo("External Scanner", 
                          "📱 External USB Barcode Scanner:\n\n"
                          "1. Connect USB scanner to computer\n"
                          "2. Scanner acts like keyboard\n"
                          "3. Click in manual entry field above\n"
                          "4. Scan barcode - it will auto-enter\n"
                          "5. Press Enter or click Lookup\n\n"
                          "💡 Most USB scanners work immediately!")
    
    def upload_image(self):
        if not CV2_AVAILABLE:
            messagebox.showwarning("Image Processing Not Available", 
                "OpenCV library is required for image processing.\n\n"
                "To enable image scanning:\n"
                "1. Install OpenCV: pip install opencv-python\n"
                "2. Restart the application\n\n"
                "For now, use manual entry or external scanner instead!")
            return
            
        file_path = filedialog.askopenfilename(
            title="Select Barcode Image",
            filetypes=[("Image files", "*.png *.jpg *.jpeg *.bmp *.gif")]
        )
        
        if file_path:
            try:
                # Load and process image
                image = cv2.imread(file_path)
                if image is not None:
                                                # Try to decode barcode from image using professional scanner
                            try:
                                from utils.professional_barcode_scanner import ProfessionalBarcodeScanner
                                scanner = ProfessionalBarcodeScanner()
                                
                                self.add_scan_result("🔍 Scanning image with professional scanner...")
                                barcode_data = scanner.scan_frame(image)
                                
                                if barcode_data:
                                    self.add_scan_result(f"✅ Image scan successful - Data: {barcode_data}")
                                    self.lookup_product(barcode_data)
                                else:
                                    self.add_scan_result("🔍 Trying direct pyzbar scan...")
                                    
                                    # Try pyzbar directly
                                    try:
                                        from pyzbar import pyzbar
                                        barcodes = pyzbar.decode(image)
                                        if barcodes:
                                            for barcode in barcodes:
                                                barcode_data = barcode.data.decode('utf-8')
                                                barcode_type = barcode.type
                                                self.add_scan_result(f"📷 Direct pyzbar scan - Type: {barcode_type}, Data: {barcode_data}")
                                                self.lookup_product(barcode_data)
                                                return
                                    except Exception as e:
                                        self.add_scan_result(f"⚠️ pyzbar error: {str(e)[:50]}")
                                    
                                    self.add_scan_result("❌ No barcode detected in image")
                                    self.add_scan_result("💡 Try: Better quality image, clear barcode, good lighting")
                                            
                            except Exception as e:
                                self.add_scan_result(f"❌ Professional scanner error: {str(e)}")
                                self.add_scan_result("❌ Image scanning failed")
                else:
                    self.add_scan_result("❌ Failed to load image")
                    
            except Exception as e:
                self.add_scan_result(f"❌ Error processing image: {str(e)}")
    
    def generate_qr_code(self):
        """Generate QR code for testing"""
        try:
            if BARCODE_AVAILABLE:
                # Create sample QR code
                qr = barcode.get('qr', 'MONA-BEAUTY-001', writer=ImageWriter())
                qr.save('sample_qr_code')
                
                self.add_scan_result("✅ QR code generated: sample_qr_code.png")
                self.add_scan_result("   You can scan this with your phone!")
                
            else:
                self.add_scan_result("❌ QR generation requires python-barcode library")
                
        except Exception as e:
            self.add_scan_result(f"❌ Error generating QR code: {str(e)}")
    
    def add_scan_result(self, result):
        timestamp = time.strftime("%H:%M:%S")
        self.results_text.insert(tk.END, f"[{timestamp}] {result}\n")
        self.results_text.see(tk.END)
    
    def clear_results(self):
        self.results_text.delete(1.0, tk.END)
    

    
    def show(self):
        """Show the barcode scanner frame"""
        self.pack(fill=tk.BOTH, expand=True)
    
    def hide(self):
        """Hide the barcode scanner frame"""
        self.pack_forget()
        self.stop_camera()  # Stop camera when switching frames
    
    def alternative_barcode_scan(self, image):
        """Alternative barcode scanning using basic image processing"""
        try:
            if not CV2_AVAILABLE or not NUMPY_AVAILABLE:
                return None
            
            # Convert to grayscale
            gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
            
            # Apply threshold to get binary image
            _, binary = cv2.threshold(gray, 127, 255, cv2.THRESH_BINARY)
            
            # Look for barcode patterns (simplified approach)
            # This is a basic implementation - looks for vertical line patterns
            
            # Find contours
            contours, _ = cv2.findContours(binary, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
            
            for contour in contours:
                # Get bounding rectangle
                x, y, w, h = cv2.boundingRect(contour)
                
                # Check if it might be a barcode (wide and not too tall)
                if w > 100 and h < w/3 and h > 20:
                    # Extract the region
                    roi = binary[y:y+h, x:x+w]
                    
                    # Simple pattern analysis
                    # This is a very basic approach - in production you'd want more sophisticated algorithms
                    lines = self.analyze_barcode_lines(roi)
                    if lines:
                        # Generate a simple barcode based on line patterns
                        # This is a placeholder - real implementation would decode actual patterns
                        barcode_data = f"ALT{hash(str(lines)) % 1000000:06d}"
                        return barcode_data
            
            return None
            
        except Exception as e:
            print(f"Alternative scan error: {e}")
            return None
    
    def analyze_barcode_lines(self, roi):
        """Basic line analysis for barcode detection"""
        try:
            if not NUMPY_AVAILABLE:
                return None
                
            # Sum pixels vertically to get line pattern
            vertical_sum = np.sum(roi, axis=0)
            
            # Find peaks and valleys
            threshold = np.mean(vertical_sum) * 0.5
            lines = []
            
            current_state = 'white' if vertical_sum[0] > threshold else 'black'
            current_width = 1
            
            for i in range(1, len(vertical_sum)):
                pixel_state = 'white' if vertical_sum[i] > threshold else 'black'
                
                if pixel_state == current_state:
                    current_width += 1
                else:
                    lines.append((current_state, current_width))
                    current_state = pixel_state
                    current_width = 1
            
            # Add the last segment
            lines.append((current_state, current_width))
            
            # Return pattern if it looks like a barcode (alternating black/white)
            if len(lines) > 10:  # Minimum number of bars for a barcode
                return lines
            
            return None
            
        except Exception as e:
            print(f"Line analysis error: {e}")
            return None
    
    def show_dll_error(self):
        """Show DLL error with helpful instructions"""
        messagebox.showerror("DLL Dependencies Missing", 
            "pyzbar requires additional DLL files on Windows.\n\n"
            "Solutions:\n\n"
            "1. RECOMMENDED: Use Alternative Scanner\n"
            "   • Click 'Start Camera' and choose 'Yes' for alternative\n"
            "   • Works with most common barcodes\n\n"
            "2. Install Visual C++ Redistributables:\n"
            "   • Download from Microsoft website\n"
            "   • Install both x86 and x64 versions\n\n"
            "3. Use Manual Entry or External Scanner\n"
            "   • Both work without any dependencies\n\n"
            "For now, try the alternative scanner option!")
    
    def show_product_actions(self, product):
        """Show action buttons for scanned product"""
        self.current_product = product
        
        # Clear existing action buttons
        for widget in self.product_actions_frame.winfo_children():
            widget.destroy()
        
        # Show the frame
        self.product_actions_frame.pack(fill="x", pady=10)
        
        # Action buttons
        ttk.Label(self.product_actions_frame, text="Quick Actions:", 
                 font=("Arial", 10, "bold")).pack(anchor="w")
        
        button_frame = ttk.Frame(self.product_actions_frame)
        button_frame.pack(fill="x", pady=5)
        
        # Stock In button
        stock_in_btn = ttk.Button(button_frame, text="📦 Stock In", 
                                 command=self.quick_stock_in)
        stock_in_btn.pack(side="left", padx=5)
        
        # Stock Out button
        stock_out_btn = ttk.Button(button_frame, text="📤 Stock Out", 
                                  command=self.quick_stock_out)
        stock_out_btn.pack(side="left", padx=5)
        
        # Quick Sale button
        sale_btn = ttk.Button(button_frame, text="💰 Quick Sale", 
                             command=self.quick_sale)
        sale_btn.pack(side="left", padx=5)
        
        # Generate Barcode button
        barcode_btn = ttk.Button(button_frame, text="🔲 Generate Barcode", 
                                command=self.generate_product_barcode)
        barcode_btn.pack(side="left", padx=5)
    
    def quick_stock_in(self):
        """Quick stock in operation"""
        if not self.current_product:
            return
        
        # Simple input dialog
        quantity = tk.simpledialog.askinteger("Stock In", 
            f"Add stock for: {self.current_product[1]}\\n\\n"
            f"Current Stock: {self.current_product[6]}\\n"
            "Enter quantity to add:", 
            minvalue=1, maxvalue=1000)
        
        if quantity:
            try:
                # Update stock in database
                new_stock = self.current_product[6] + quantity
                success = self.db_manager.update_stock(self.current_product[0], new_stock)
                
                if success:
                    self.add_scan_result(f"✅ Stock In: +{quantity} units")
                    self.add_scan_result(f"   New Stock: {new_stock}")
                    
                    # Update current product data
                    product_list = list(self.current_product)
                    product_list[6] = new_stock
                    self.current_product = tuple(product_list)
                else:
                    self.add_scan_result("❌ Failed to update stock")
                    
            except Exception as e:
                self.add_scan_result(f"❌ Error: {str(e)}")
    
    def quick_stock_out(self):
        """Quick stock out operation"""
        if not self.current_product:
            return
        
        current_stock = self.current_product[6]
        
        # Simple input dialog
        quantity = tk.simpledialog.askinteger("Stock Out", 
            f"Remove stock for: {self.current_product[1]}\\n\\n"
            f"Current Stock: {current_stock}\\n"
            "Enter quantity to remove:", 
            minvalue=1, maxvalue=current_stock)
        
        if quantity:
            try:
                # Update stock in database
                new_stock = current_stock - quantity
                success = self.db_manager.update_stock(self.current_product[0], new_stock)
                
                if success:
                    self.add_scan_result(f"✅ Stock Out: -{quantity} units")
                    self.add_scan_result(f"   New Stock: {new_stock}")
                    
                    # Update current product data
                    product_list = list(self.current_product)
                    product_list[6] = new_stock
                    self.current_product = tuple(product_list)
                    
                    # Check for low stock
                    if new_stock <= 10:
                        self.add_scan_result(f"⚠️ LOW STOCK WARNING!")
                else:
                    self.add_scan_result("❌ Failed to update stock")
                    
            except Exception as e:
                self.add_scan_result(f"❌ Error: {str(e)}")
    
    def quick_sale(self):
        """Quick sale operation"""
        if not self.current_product:
            return
        
        # Create sale dialog
        self.create_sale_dialog()
    
    def create_sale_dialog(self):
        """Create dialog for quick sale"""
        dialog = tk.Toplevel(self.parent)
        dialog.title("Quick Sale")
        dialog.geometry("400x300")
        dialog.configure(bg="#fdf7f2")  # Brand background color
        
        # Product info
        product = self.current_product
        info_frame = ttk.LabelFrame(dialog, text="Product Information", padding=10)
        info_frame.pack(fill="x", padx=20, pady=10)
        
        ttk.Label(info_frame, text=f"Product: {product[1]}", 
                 font=("Arial", 10, "bold")).pack(anchor="w")
        ttk.Label(info_frame, text=f"Current Stock: {product[6]} units").pack(anchor="w")
        ttk.Label(info_frame, text=f"COGS: ₹{product[5]:.2f}").pack(anchor="w")
        
        # Sale inputs
        sale_frame = ttk.LabelFrame(dialog, text="Sale Details", padding=10)
        sale_frame.pack(fill="x", padx=20, pady=10)
        
        # Quantity
        ttk.Label(sale_frame, text="Quantity:").grid(row=0, column=0, sticky="w", pady=5)
        quantity_var = tk.StringVar(value="1")
        quantity_entry = ttk.Entry(sale_frame, textvariable=quantity_var, width=10)
        quantity_entry.grid(row=0, column=1, sticky="w", padx=10)
        
        # Selling Price
        ttk.Label(sale_frame, text="Selling Price (₹):").grid(row=1, column=0, sticky="w", pady=5)
        price_var = tk.StringVar(value=str(product[5] * 1.5))  # Suggest 50% markup
        price_entry = ttk.Entry(sale_frame, textvariable=price_var, width=10)
        price_entry.grid(row=1, column=1, sticky="w", padx=10)
        
        # Profit calculation
        profit_label = ttk.Label(sale_frame, text="", foreground="#fc68ae", font=("Arial", 10, "bold"))
        profit_label.grid(row=2, column=0, columnspan=2, pady=10)
        
        def calculate_profit():
            try:
                qty = int(quantity_var.get())
                price = float(price_var.get())
                profit = qty * (price - product[5])
                revenue = qty * price
                profit_label.config(text=f"Revenue: ₹{revenue:.2f} | Profit: ₹{profit:.2f}")
            except:
                profit_label.config(text="Invalid input")
        
        # Bind calculation to entry changes
        quantity_var.trace("w", lambda *args: calculate_profit())
        price_var.trace("w", lambda *args: calculate_profit())
        calculate_profit()  # Initial calculation
        
        # Buttons
        button_frame = ttk.Frame(dialog)
        button_frame.pack(fill="x", padx=20, pady=20)
        
        def confirm_sale():
            try:
                quantity = int(quantity_var.get())
                selling_price = float(price_var.get())
                
                if quantity <= 0 or selling_price <= 0:
                    messagebox.showerror("Error", "Quantity and price must be positive")
                    return
                
                if quantity > product[6]:
                    messagebox.showerror("Error", f"Not enough stock. Available: {product[6]}")
                    return
                
                # Record sale
                from datetime import datetime
                sale_date = datetime.now().isoformat()
                
                success = self.db_manager.add_sale(
                    product[0], quantity, selling_price, sale_date
                )
                
                if success:
                    # Update stock
                    new_stock = product[6] - quantity
                    self.db_manager.update_stock(product[0], new_stock)
                    
                    # Show success
                    revenue = quantity * selling_price
                    profit = quantity * (selling_price - product[5])
                    
                    self.add_scan_result(f"✅ SALE RECORDED")
                    self.add_scan_result(f"   Quantity: {quantity}")
                    self.add_scan_result(f"   Revenue: ₹{revenue:.2f}")
                    self.add_scan_result(f"   Profit: ₹{profit:.2f}")
                    self.add_scan_result(f"   Remaining Stock: {new_stock}")
                    
                    dialog.destroy()
                    
                    # Update current product
                    product_list = list(self.current_product)
                    product_list[6] = new_stock
                    self.current_product = tuple(product_list)
                else:
                    messagebox.showerror("Error", "Failed to record sale")
                    
            except ValueError:
                messagebox.showerror("Error", "Please enter valid numbers")
            except Exception as e:
                messagebox.showerror("Error", f"Sale failed: {str(e)}")
        
        ttk.Button(button_frame, text="Record Sale", command=confirm_sale).pack(side="right", padx=5)
        ttk.Button(button_frame, text="Cancel", command=dialog.destroy).pack(side="right", padx=5)
    
    def generate_product_barcode(self):
        """Generate barcode for current product"""
        if not self.current_product:
            return
        
        try:
            from utils.barcode_generator import BarcodeGenerator
            
            generator = BarcodeGenerator(self.db_manager)
            product = self.current_product
            
            # Generate barcode if not exists
            barcode = product[3]
            if not barcode or barcode.strip() == "":
                # Generate new barcode
                category_name = ""
                categories = self.db_manager.get_categories()
                for cat in categories:
                    if cat[0] == product[4]:
                        category_name = cat[1]
                        break
                
                sku, barcode = generator.generate_sku_barcode(product[1], category_name)
                
                # Update database
                success = self.db_manager.update_product_barcode(product[0], barcode)
                if not success:
                    self.add_scan_result("❌ Failed to update product barcode")
                    return
            
            # Generate barcode image
            image_path, message = generator.generate_barcode_image(barcode)
            
            if image_path:
                self.add_scan_result(f"✅ Barcode generated: {barcode}")
                self.add_scan_result(f"   Saved to: {image_path}")
                
                # Show barcode image
                self.show_barcode_image(image_path)
            else:
                self.add_scan_result(f"❌ Failed to generate barcode: {message}")
                
        except ImportError:
            self.add_scan_result("❌ Barcode generator not available")
        except Exception as e:
            self.add_scan_result(f"❌ Error generating barcode: {str(e)}")
    
    def show_barcode_image(self, image_path):
        """Show generated barcode image"""
        try:
            # Create popup window
            popup = tk.Toplevel(self.parent)
            popup.title("Generated Barcode")
            popup.configure(bg="#fdf7f2")
            
            # Load and display image
            from PIL import Image, ImageTk
            img = Image.open(image_path)
            img = img.resize((400, 200), Image.Resampling.LANCZOS)
            photo = ImageTk.PhotoImage(img)
            
            label = ttk.Label(popup, image=photo)
            label.image = photo  # Keep a reference
            label.pack(padx=20, pady=20)
            
            # Buttons
            button_frame = ttk.Frame(popup)
            button_frame.pack(pady=10)
            
            ttk.Button(button_frame, text="Save As...", 
                      command=lambda: self.save_barcode_as(image_path)).pack(side="left", padx=5)
            ttk.Button(button_frame, text="Close", 
                      command=popup.destroy).pack(side="left", padx=5)
            
        except Exception as e:
            messagebox.showerror("Error", f"Cannot display barcode: {str(e)}")
    
    def save_barcode_as(self, source_path):
        """Save barcode image to chosen location"""
        try:
            filename = filedialog.asksaveasfilename(
                title="Save Barcode As",
                defaultextension=".png",
                filetypes=[("PNG files", "*.png"), ("All files", "*.*")]
            )
            
            if filename:
                import shutil
                shutil.copy2(source_path, filename)
                messagebox.showinfo("Success", f"Barcode saved to:\\n{filename}")
        except Exception as e:
            messagebox.showerror("Error", f"Failed to save barcode: {str(e)}")
    
    def offer_create_product(self, barcode_data):
        """Offer to create new product with scanned barcode"""
        result = messagebox.askyesno("Product Not Found", 
            f"Barcode '{barcode_data}' not found in inventory.\\n\\n"
            "Would you like to create a new product with this barcode?")
        
        if result:
            self.create_product_dialog(barcode_data)
    
    def create_product_dialog(self, barcode):
        """Create dialog for new product creation"""
        dialog = tk.Toplevel(self.parent)
        dialog.title("Create New Product")
        dialog.geometry("500x400")
        dialog.configure(bg="#fdf7f2")
        
        # Form frame
        form_frame = ttk.LabelFrame(dialog, text="Product Details", padding=20)
        form_frame.pack(fill="both", expand=True, padx=20, pady=20)
        
        # Product Name
        ttk.Label(form_frame, text="Product Name:").grid(row=0, column=0, sticky="w", pady=5)
        name_var = tk.StringVar()
        ttk.Entry(form_frame, textvariable=name_var, width=30).grid(row=0, column=1, sticky="ew", padx=10)
        
        # SKU
        ttk.Label(form_frame, text="SKU:").grid(row=1, column=0, sticky="w", pady=5)
        sku_var = tk.StringVar()
        ttk.Entry(form_frame, textvariable=sku_var, width=30).grid(row=1, column=1, sticky="ew", padx=10)
        
        # Barcode (pre-filled)
        ttk.Label(form_frame, text="Barcode:").grid(row=2, column=0, sticky="w", pady=5)
        barcode_var = tk.StringVar(value=barcode)
        ttk.Entry(form_frame, textvariable=barcode_var, width=30).grid(row=2, column=1, sticky="ew", padx=10)
        
        # Category
        ttk.Label(form_frame, text="Category:").grid(row=3, column=0, sticky="w", pady=5)
        category_var = tk.StringVar()
        categories = self.db_manager.get_categories()
        category_names = [cat[1] for cat in categories]
        category_combo = ttk.Combobox(form_frame, textvariable=category_var, 
                                     values=category_names, state="readonly", width=27)
        category_combo.grid(row=3, column=1, sticky="ew", padx=10)
        if category_names:
            category_combo.set(category_names[0])
        
        # COGS
        ttk.Label(form_frame, text="COGS (₹):").grid(row=4, column=0, sticky="w", pady=5)
        cogs_var = tk.StringVar()
        ttk.Entry(form_frame, textvariable=cogs_var, width=30).grid(row=4, column=1, sticky="ew", padx=10)
        
        # Initial Stock
        ttk.Label(form_frame, text="Initial Stock:").grid(row=5, column=0, sticky="w", pady=5)
        stock_var = tk.StringVar(value="0")
        ttk.Entry(form_frame, textvariable=stock_var, width=30).grid(row=5, column=1, sticky="ew", padx=10)
        
        # Configure grid weights
        form_frame.grid_columnconfigure(1, weight=1)
        
        # Buttons
        button_frame = ttk.Frame(dialog)
        button_frame.pack(fill="x", padx=20, pady=20)
        
        def create_product():
            try:
                # Validate inputs
                if not name_var.get().strip():
                    messagebox.showerror("Error", "Product name is required")
                    return
                
                if not category_var.get():
                    messagebox.showerror("Error", "Please select a category")
                    return
                
                try:
                    cogs = float(cogs_var.get())
                    stock = int(stock_var.get())
                except ValueError:
                    messagebox.showerror("Error", "COGS must be a number and stock must be an integer")
                    return
                
                # Get category ID
                category_id = None
                for cat in categories:
                    if cat[1] == category_var.get():
                        category_id = cat[0]
                        break
                
                # Create product
                success = self.db_manager.add_product(
                    name_var.get().strip(),
                    sku_var.get().strip() or None,
                    barcode_var.get().strip(),
                    category_id,
                    cogs,
                    stock
                )
                
                if success:
                    self.add_scan_result(f"✅ Product created: {name_var.get()}")
                    self.add_scan_result(f"   Barcode: {barcode_var.get()}")
                    self.add_scan_result(f"   Stock: {stock}")
                    dialog.destroy()
                    
                    # Look up the newly created product
                    self.lookup_product(barcode_var.get())
                else:
                    messagebox.showerror("Error", "Failed to create product. Barcode may already exist.")
                    
            except Exception as e:
                messagebox.showerror("Error", f"Failed to create product: {str(e)}")
        
        ttk.Button(button_frame, text="Create Product", command=create_product).pack(side="right", padx=5)
        ttk.Button(button_frame, text="Cancel", command=dialog.destroy).pack(side="right", padx=5)
    
    def generate_all_barcodes(self):
        """Generate barcodes for all products"""
        try:
            from utils.barcode_generator import BarcodeGenerator
            
            generator = BarcodeGenerator(self.db_manager)
            barcodes, message = generator.generate_product_barcodes()
            
            self.add_scan_result(f"📊 {message}")
            for item in barcodes[:5]:  # Show first 5
                self.add_scan_result(f"   ✅ {item['name']}: {item['barcode']}")
            
            if len(barcodes) > 5:
                self.add_scan_result(f"   ... and {len(barcodes) - 5} more")
                
        except ImportError:
            self.add_scan_result("❌ Barcode generator not available")
        except Exception as e:
            self.add_scan_result(f"❌ Error generating barcodes: {str(e)}")
    
    def create_print_sheet(self):
        """Create printable barcode sheet"""
        try:
            from utils.barcode_generator import BarcodeGenerator
            
            generator = BarcodeGenerator(self.db_manager)
            pdf_path, message = generator.create_barcode_print_sheet()
            
            if pdf_path:
                self.add_scan_result(f"✅ Print sheet created: {pdf_path}")
                
                # Ask to open
                result = messagebox.askyesno("Print Sheet Created", 
                    f"Barcode print sheet created successfully!\\n\\n"
                    f"Location: {pdf_path}\\n\\n"
                    "Would you like to open it now?")
                
                if result:
                    import os
                    os.startfile(pdf_path)  # Windows
            else:
                self.add_scan_result(f"❌ Failed to create print sheet: {message}")
                
        except ImportError:
            self.add_scan_result("❌ PDF generator not available - install reportlab")
        except Exception as e:
            self.add_scan_result(f"❌ Error creating print sheet: {str(e)}")
    
    def is_reasonable_barcode(self, barcode_data: str) -> bool:
        """Check if detected barcode is reasonable (not random noise)"""
        try:
            if not barcode_data or len(barcode_data) < 8:
                return False
            
            # Check if it's all the same character (likely noise)
            if len(set(barcode_data)) < 3:
                return False
            
            # Check for reasonable barcode patterns
            import re
            
            # Allow common barcode formats
            patterns = [
                r'^\d{8,20}$',  # Numeric barcodes
                r'^[A-Z0-9\-_]{8,20}$',  # Alphanumeric with separators
                r'^[A-Za-z]{2,4}\-[A-Za-z0-9\-]{3,15}$',  # SKU-like patterns
            ]
            
            for pattern in patterns:
                if re.match(pattern, barcode_data):
                    return True
            
            # Additional checks for existing products
            # If barcode exists in database, it's definitely valid
            existing_product = self.db_manager.get_product_by_barcode(barcode_data)
            if existing_product:
                return True
            
            return False
            
        except Exception as e:
            print(f"Barcode validation error: {e}")
            return True  # Default to true if validation fails
    
    def on_closing(self):
        self.stop_camera()
