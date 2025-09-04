"""
QR Code Scanner Frame for Inventory Management System
Handles QR code scanning via camera with production-grade detection
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

# Don't import qrcode at startup - import only when needed
QRCODE_AVAILABLE = False

try:
    import qrcode
    QRCODE_AVAILABLE = True
    print("✅ qrcode library loaded successfully")
except ImportError as e:
    QRCODE_AVAILABLE = False
    print(f"⚠️ qrcode library not available - QR code generation disabled: {e}")
    # Try to install qrcode library
    try:
        import subprocess
        import sys
        subprocess.check_call([sys.executable, "-m", "pip", "install", "qrcode[pil]"])
        print("✅ qrcode library installed, please restart the application")
    except:
        print("❌ Could not install qrcode library automatically")
except Exception as e:
    QRCODE_AVAILABLE = False
    print(f"⚠️ qrcode library error - QR code generation disabled: {e}")

class QRScannerFrame(ttk.Frame):
    def __init__(self, parent, db_manager):
        super().__init__(parent)
        self.parent = parent
        self.db_manager = db_manager
        self.camera = None
        self.is_camera_on = False
        self.scan_thread = None
        self.current_product = None
        self.operation_mode = "stock_out"  # Default to stock-out for inventory management

        self.create_widgets()

    def create_operation_mode_controls(self):
        """Create operation mode selection controls"""
        mode_frame = ttk.LabelFrame(self, text="Operation Mode", padding=10)
        mode_frame.pack(fill="x", padx=20, pady=5)
        
        # Operation mode selection
        self.operation_var = tk.StringVar(value="stock_out")
        
        stock_out_radio = ttk.Radiobutton(mode_frame, text="📤 Stock Out (Deduct from inventory)", 
                                         variable=self.operation_var, value="stock_out",
                                         command=self.on_operation_mode_change)
        stock_out_radio.pack(side="left", padx=10)
        
        stock_in_radio = ttk.Radiobutton(mode_frame, text="📥 Stock In (Add to inventory)", 
                                        variable=self.operation_var, value="stock_in",
                                        command=self.on_operation_mode_change)
        stock_in_radio.pack(side="left", padx=10)
        
        # Quantity input for stock operations
        qty_frame = ttk.Frame(mode_frame)
        qty_frame.pack(side="right", padx=10)
        
        ttk.Label(qty_frame, text="Quantity:").pack(side="left")
        self.quantity_var = tk.StringVar(value="1")
        self.quantity_entry = ttk.Entry(qty_frame, textvariable=self.quantity_var, width=8)
        self.quantity_entry.pack(side="left", padx=5)
        
        # Auto-process checkbox
        self.auto_process_var = tk.BooleanVar(value=True)
        auto_check = ttk.Checkbutton(mode_frame, text="Auto-process on scan", 
                                   variable=self.auto_process_var)
        auto_check.pack(side="right", padx=10)

    def on_operation_mode_change(self):
        """Handle operation mode change"""
        self.operation_mode = self.operation_var.get()
        mode_text = "📤 Stock Out" if self.operation_mode == "stock_out" else "📥 Stock In"
        self.add_scan_result(f"🔄 Operation mode changed to: {mode_text}")

    def create_widgets(self):
        # Title
        title_label = ttk.Label(self, text="📱 QR Code Scanner",
                               font=("Arial", 16, "bold"))
        title_label.pack(pady=10)
        
        # Operation mode selection
        self.create_operation_mode_controls()
        
        # Status indicator
        self.create_status_indicator()
        

        # Main content area with better layout
        main_content = tk.Frame(self)
        main_content.pack(fill="both", expand=True, padx=20, pady=10)
        
        # Left side - Camera and controls
        left_side = tk.Frame(main_content)
        left_side.pack(side=tk.LEFT, fill="both", expand=True, padx=(0, 10))
        
        # Camera frame
        self.camera_frame = ttk.LabelFrame(left_side, text="QR Camera Scanner", padding=10)
        self.camera_frame.pack(fill="both", expand=True)

        # Camera display
        self.camera_label = ttk.Label(self.camera_frame, text="Camera not started")
        self.camera_label.pack(pady=10)
        
        # Camera controls
        self.create_camera_controls()
        
        # Manual entry frame
        manual_frame = ttk.LabelFrame(left_side, text="Manual QR Entry", padding=10)
        manual_frame.pack(fill="x", pady=(10, 0))

        # Manual entry controls
        self.create_manual_controls()

        # Alternative methods frame
        alt_frame = ttk.LabelFrame(left_side, text="Alternative Scanning Methods", padding=10)
        alt_frame.pack(fill="x", pady=(10, 0))

        # Alternative methods
        self.create_alternative_methods(alt_frame)
        
        # Right side - QR Code Display (Dedicated space)
        right_side = tk.Frame(main_content)
        right_side.pack(side=tk.RIGHT, fill="y", expand=False, padx=(10, 0))
        
        # QR Code Display Frame (Fixed size to prevent cutoff)
        qr_display_frame = ttk.LabelFrame(right_side, text="🔲 Generated QR Code", padding=15)
        qr_display_frame.pack(fill="y", expand=False)
        qr_display_frame.configure(width=350, height=500)  # Fixed size to prevent cutoff
        
        # Status indicator for QR display
        self.display_status_label = ttk.Label(qr_display_frame, text="🔲 Generated QR Code (Ready for Scanning)",
                                             font=("Arial", 10, "bold"), foreground="blue")
        self.display_status_label.pack(pady=(0, 10))

        # QR code display label (Larger for better visibility)
        self.qr_display_label = ttk.Label(qr_display_frame, 
                                         text="No QR Code Generated\n\n💡 Enter a QR code and press Lookup\nto generate and display it here\n\n📱 The QR code will appear here\nfor easy scanning",
                                         font=("Arial", 9),
                                         justify="center",
                                         wraplength=320)
        self.qr_display_label.pack(pady=10, expand=True, fill="both")

        # Camera status indicator
        self.camera_status_label = ttk.Label(qr_display_frame, text="", font=("Arial", 8), foreground="green")
        self.camera_status_label.pack(pady=(5, 0))
        
        # Results frame (Text results at bottom)
        results_frame = ttk.LabelFrame(self, text="📋 Scan Results & Log", padding=10)
        results_frame.pack(fill="x", padx=20, pady=(10, 0))

        self.results_text = tk.Text(results_frame, height=6, width=80, font=("Consolas", 9))
        self.results_text.pack(fill="x")
        
        # Action buttons frame
        action_frame = ttk.Frame(results_frame)
        action_frame.pack(fill="x", pady=5)
        
        # Clear results button
        clear_btn = ttk.Button(action_frame, text="Clear Results", 
                              command=self.clear_results)
        clear_btn.pack(side="left", padx=5)
        
        # Generate QR codes button
        generate_btn = ttk.Button(action_frame, text="Generate QR Codes",
                                 command=self.generate_all_qr_codes)
        generate_btn.pack(side="left", padx=5)

        # Print sheet button
        print_btn = ttk.Button(action_frame, text="Print QR Code Sheet",
                              command=self.create_print_sheet)
        print_btn.pack(side="left", padx=5)

        # Show QR codes button
        show_qr_btn = ttk.Button(action_frame, text="📷 Show QR Codes",
                                command=self.show_existing_qr_codes)
        show_qr_btn.pack(side="left", padx=5)
        
        # Product actions frame (hidden initially)
        self.product_actions_frame = ttk.Frame(results_frame)
        self.current_product = None
        
    def create_status_indicator(self):
        """Create status indicator showing available scanning methods"""
        status_frame = ttk.Frame(self)
        status_frame.pack(fill="x", padx=20, pady=5)

        # Check QR code scanning availability
        qr_scanning_available = CV2_AVAILABLE and (QRCODE_AVAILABLE or self._check_pyzbar_available())

        if qr_scanning_available:
            status_text = "✅ QR code scanning available"
            status_color = "green"
        elif QRCODE_AVAILABLE:
            status_text = "⚠️ Manual entry and QR generation available"
            status_color = "orange"
        else:
            status_text = "❌ No QR code libraries available"
            status_color = "red"

        status_label = ttk.Label(status_frame, text=status_text,
                                foreground=status_color, font=("Arial", 10, "bold"))
        status_label.pack()

    def _check_pyzbar_available(self) -> bool:
        """Check if pyzbar is available for QR code scanning"""
        try:
            import importlib.util
            spec = importlib.util.find_spec("pyzbar")
            return spec is not None
        except:
            return False
        
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
        qr_scanning_available = CV2_AVAILABLE and (QRCODE_AVAILABLE or self._check_pyzbar_available())

        if qr_scanning_available:
            help_text = "✅ QR scanning ready. Click 'Start Camera' to begin."
        else:
            help_text = "❌ QR scanning requires OpenCV + QR libraries.\n" \
                       "Use manual entry or alternative methods below."

        help_label = ttk.Label(self.camera_frame, text=help_text,
                              foreground="blue", wraplength=400)
        help_label.pack(pady=5)
        
    def create_manual_controls(self):
        # SKU/QR entry
        entry_frame = ttk.Frame(self)
        entry_frame.pack(fill="x", pady=5)

        ttk.Label(entry_frame, text="Enter SKU/QR Code:").pack(side="left")
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

        # Check if QR scanning is available
        qr_available = QRCODE_AVAILABLE or self._check_pyzbar_available()
        if not qr_available:
            messagebox.showwarning("QR Detection Not Available",
                "QR code detection libraries are not available.\n\n"
                "Install required libraries:\n"
                "1. pip install qrcode[pil]\n"
                "2. pip install pyzbar (optional)\n"
                "3. Restart the application\n\n"
                "For now, use manual entry or image upload instead!")
            return

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

            # Update status indicators
            self.camera_status_label.config(text="📷 Camera: ACTIVE", foreground="green")
            self.display_status_label.config(text="📹 Camera Live Feed", foreground="green")

            # Start scanning thread
            self.scan_thread = threading.Thread(target=self.scan_qr_codes)
            self.scan_thread.daemon = True
            self.scan_thread.start()

            messagebox.showinfo("Camera Started",
                              "✅ Camera is now active!\n\n"
                              "Point camera at QR codes to scan.\n"
                              "You can also enter QR codes manually while camera is on.\n"
                              "Click 'Stop Camera' when done.")

        except Exception as e:
            messagebox.showerror("Camera Error", f"Failed to start camera: {str(e)}")
    
    def stop_camera(self):
        self.is_camera_on = False
        if self.camera:
            self.camera.release()
            self.camera = None
        
        self.start_btn.config(state="normal")
        self.stop_btn.config(state="disabled")
        self.camera_label.config(text="Camera stopped")

        # Update status indicators
        self.camera_status_label.config(text="📷 Camera: STOPPED", foreground="red")
        self.display_status_label.config(text="📱 QR Code Display Area", foreground="blue")
        
    def scan_qr_codes(self):
        # Initialize professional QR scanner
        try:
            from utils.professional_qr_scanner import ProfessionalQRScanner
            scanner = ProfessionalQRScanner()
            status = scanner.get_status()

            self.add_scan_result("🚀 Professional QR scanner initialized")
            self.add_scan_result(f"📊 Methods available: {[m for m in status['methods'] if m]}")
            self.add_scan_result("🎯 READY TO SCAN - Point camera at QR code!")

        except Exception as e:
            self.add_scan_result(f"❌ QR scanner initialization failed: {e}")
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

                    # Professional QR scanning
                    if scanner:
                        try:
                            # Scan every 5 frames for better responsiveness
                            if scan_count % 5 == 0:
                                qr_data = scanner.scan_frame(frame)

                                if qr_data:
                                    self.add_scan_result(f"🎯 QR CODE DETECTED: {qr_data}")
                                    self.lookup_product(qr_data, is_camera_scan=True)

                                    # Visual feedback
                                    self.add_scan_result("✅ QR scanning successful!")

                                    # Brief pause after detection
                                    time.sleep(0.5)

                            scan_count += 1

                        except Exception as e:
                            if scan_count % 50 == 0:  # Log errors occasionally
                                self.add_scan_result(f"⚠️ QR scan error: {str(e)[:50]}")

                    # Fallback scanning methods
                    else:
                        # Try pyzbar directly as fallback for QR codes
                        try:
                            from pyzbar import pyzbar
                            if scan_count % 5 == 0:  # Every 5 frames
                                decoded_objects = pyzbar.decode(frame)
                                for obj in decoded_objects:
                                    if obj.type == 'QRCODE':
                                        qr_data = obj.data.decode('utf-8')

                                        self.add_scan_result(f"📷 Fallback QR scan - Data: {qr_data}")
                                        self.lookup_product(qr_data, is_camera_scan=True)
                                        time.sleep(0.5)

                        except Exception as e:
                            if scan_count % 100 == 0:
                                self.add_scan_result("🔍 Scanning for QR codes...")

                        scan_count += 1

            time.sleep(0.1)  # Small delay to prevent high CPU usage
    
    def lookup_manual(self, event=None):
        qr_data = self.manual_entry.get().strip()
        if qr_data:
            self.lookup_product(qr_data)
            self.manual_entry.delete(0, tk.END)
        else:
            messagebox.showwarning("Input Required", "Please enter a SKU or QR code.")
    
    def test_with_sample(self):
        """Test with a sample QR code"""
        sample_qr_codes = ["123456789", "987654321", "SAMPLE001", "TEST123", "QR-DEMO-001"]
        sample = sample_qr_codes[int(time.time()) % len(sample_qr_codes)]
        self.manual_entry.delete(0, tk.END)
        self.manual_entry.insert(0, sample)
        self.lookup_product(sample)
    
    def lookup_product(self, qr_data, is_camera_scan=False):
        # Search in database
        product = self.db_manager.get_product_by_barcode(qr_data)
        if product:
            product_id, name, sku, qr_code, category_id, cogs, current_stock = product[:7]

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

            # Store current product for operations
            self.current_product = product

            # Generate and display QR code image for this product
            self.generate_and_display_product_qr(product, qr_data)

            # Only process stock operations if this is a camera scan
            if is_camera_scan:
                # Auto-process stock operation for camera scans
                if self.auto_process_var.get():
                    self.process_stock_operation(product)
                else:
                    # Show action buttons for manual processing
                    self.show_product_actions(product)
            else:
                # For manual lookup, only show info and QR code, no stock operations
                self.add_scan_result(f"📱 QR code generated and displayed for manual lookup")
                self.add_scan_result(f"💡 To process stock operations, scan this QR code with the camera")
                self.show_quick_actions()
        else:
            self.add_scan_result(f"❌ Not found: {qr_data}")
            self.add_scan_result(f"   Tip: Add this product in Products section")

            # Generate and display QR code for the entered data (even if not in database)
            self.generate_and_display_manual_qr(qr_data)

            # Offer to create new product
            self.offer_create_product(qr_data)

    def process_stock_operation(self, product):
        """Process stock operation automatically when QR is scanned"""
        try:
            product_id, name, sku, qr_code, category_id, cogs, current_stock = product[:7]
            
            # Get quantity from input
            try:
                quantity = int(self.quantity_var.get())
                if quantity <= 0:
                    self.add_scan_result("❌ Quantity must be greater than 0")
                    return
            except ValueError:
                self.add_scan_result("❌ Invalid quantity. Using default: 1")
                quantity = 1
                self.quantity_var.set("1")
            
            # Process based on operation mode
            if self.operation_mode == "stock_out":
                # Check if sufficient stock available
                if current_stock < quantity:
                    self.add_scan_result(f"❌ Insufficient stock! Available: {current_stock}, Required: {quantity}")
                    return
                
                # Process stock out
                success = self.db_manager.update_stock_change(product_id, quantity, "stock_out")
                if success:
                    new_stock = current_stock - quantity
                    self.add_scan_result(f"✅ Stock Out: -{quantity} units")
                    self.add_scan_result(f"   Previous Stock: {current_stock}")
                    self.add_scan_result(f"   New Stock: {new_stock}")
                    
                    # Update current product data
                    product_list = list(self.current_product)
                    product_list[6] = new_stock
                    self.current_product = tuple(product_list)
                else:
                    self.add_scan_result("❌ Failed to process stock out")
                    
            elif self.operation_mode == "stock_in":
                # Process stock in
                success = self.db_manager.update_stock_change(product_id, quantity, "stock_in")
                if success:
                    new_stock = current_stock + quantity
                    self.add_scan_result(f"✅ Stock In: +{quantity} units")
                    self.add_scan_result(f"   Previous Stock: {current_stock}")
                    self.add_scan_result(f"   New Stock: {new_stock}")
                    
                    # Update current product data
                    product_list = list(self.current_product)
                    product_list[6] = new_stock
                    self.current_product = tuple(product_list)
                else:
                    self.add_scan_result("❌ Failed to process stock in")
            
            # Show additional action buttons
            self.show_quick_actions()
            
        except Exception as e:
            self.add_scan_result(f"❌ Error processing stock operation: {str(e)}")

    def show_quick_actions(self):
        """Show quick action buttons after stock operation"""
        action_frame = ttk.Frame(self)
        action_frame.pack(fill="x", padx=20, pady=5)
        
        # Quick sale button
        sale_btn = ttk.Button(action_frame, text="💰 Quick Sale",
                             command=self.quick_sale)
        sale_btn.pack(side="left", padx=5)
        
        # Generate QR Code button
        qr_btn = ttk.Button(action_frame, text="🔲 Generate QR Code",
                            command=self.generate_product_qr_code)
        qr_btn.pack(side="left", padx=5)
        
        # Manual operation button
        manual_btn = ttk.Button(action_frame, text="⚙️ Manual Operations",
                               command=self.show_manual_operations)
        manual_btn.pack(side="left", padx=5)

    def show_manual_operations(self):
        """Show manual operation dialog"""
        if not self.current_product:
            self.add_scan_result("❌ No product selected")
            return
        
        # Create manual operations dialog
        dialog = tk.Toplevel(self)
        dialog.title("Manual Operations")
        dialog.geometry("400x300")
        dialog.transient(self)
        dialog.grab_set()
        
        # Center the dialog
        dialog.geometry("+%d+%d" % (self.winfo_rootx() + 50, self.winfo_rooty() + 50))
        
        # Product info
        product_id, name, sku, qr_code, category_id, cogs, current_stock = self.current_product[:7]
        
        info_frame = ttk.LabelFrame(dialog, text="Product Information", padding=10)
        info_frame.pack(fill="x", padx=10, pady=5)
        
        ttk.Label(info_frame, text=f"Product: {name}").pack(anchor="w")
        ttk.Label(info_frame, text=f"SKU: {sku}").pack(anchor="w")
        ttk.Label(info_frame, text=f"Current Stock: {current_stock}").pack(anchor="w")
        
        # Operation controls
        op_frame = ttk.LabelFrame(dialog, text="Operations", padding=10)
        op_frame.pack(fill="both", expand=True, padx=10, pady=5)
        
        # Stock In
        stock_in_frame = ttk.Frame(op_frame)
        stock_in_frame.pack(fill="x", pady=5)
        
        ttk.Label(stock_in_frame, text="Stock In:").pack(side="left")
        stock_in_qty = ttk.Entry(stock_in_frame, width=10)
        stock_in_qty.pack(side="left", padx=5)
        stock_in_qty.insert(0, "1")
        
        def do_stock_in():
            try:
                qty = int(stock_in_qty.get())
                if qty > 0:
                    success = self.db_manager.update_stock_change(product_id, qty, "stock_in")
                    if success:
                        self.add_scan_result(f"✅ Manual Stock In: +{qty} units")
                        dialog.destroy()
                    else:
                        messagebox.showerror("Error", "Failed to update stock")
                else:
                    messagebox.showerror("Error", "Quantity must be positive")
            except ValueError:
                messagebox.showerror("Error", "Invalid quantity")
        
        ttk.Button(stock_in_frame, text="Add Stock", command=do_stock_in).pack(side="left", padx=5)
        
        # Stock Out
        stock_out_frame = ttk.Frame(op_frame)
        stock_out_frame.pack(fill="x", pady=5)
        
        ttk.Label(stock_out_frame, text="Stock Out:").pack(side="left")
        stock_out_qty = ttk.Entry(stock_out_frame, width=10)
        stock_out_qty.pack(side="left", padx=5)
        stock_out_qty.insert(0, "1")
        
        def do_stock_out():
            try:
                qty = int(stock_out_qty.get())
                if qty > 0:
                    if current_stock >= qty:
                        success = self.db_manager.update_stock_change(product_id, qty, "stock_out")
                        if success:
                            self.add_scan_result(f"✅ Manual Stock Out: -{qty} units")
                            dialog.destroy()
                        else:
                            messagebox.showerror("Error", "Failed to update stock")
                    else:
                        messagebox.showerror("Error", f"Insufficient stock. Available: {current_stock}")
                else:
                    messagebox.showerror("Error", "Quantity must be positive")
            except ValueError:
                messagebox.showerror("Error", "Invalid quantity")
        
        ttk.Button(stock_out_frame, text="Remove Stock", command=do_stock_out).pack(side="left", padx=5)
        
        # Close button
        ttk.Button(dialog, text="Close", command=dialog.destroy).pack(pady=10)

    def quick_sale(self):
        """Quick sale operation"""
        if not self.current_product:
            self.add_scan_result("❌ No product selected")
            return
        
        product_id, name, sku, qr_code, category_id, cogs, current_stock = self.current_product[:7]
        
        # Simple sale dialog
        dialog = tk.Toplevel(self)
        dialog.title("Quick Sale")
        dialog.geometry("350x200")
        dialog.transient(self)
        dialog.grab_set()
        
        # Center the dialog
        dialog.geometry("+%d+%d" % (self.winfo_rootx() + 50, self.winfo_rooty() + 50))
        
        # Product info
        info_frame = ttk.LabelFrame(dialog, text="Product", padding=10)
        info_frame.pack(fill="x", padx=10, pady=5)
        
        ttk.Label(info_frame, text=f"Product: {name}").pack(anchor="w")
        ttk.Label(info_frame, text=f"Available Stock: {current_stock}").pack(anchor="w")
        ttk.Label(info_frame, text=f"COGS: ₹{cogs:.2f}").pack(anchor="w")
        
        # Sale controls
        sale_frame = ttk.LabelFrame(dialog, text="Sale Details", padding=10)
        sale_frame.pack(fill="both", expand=True, padx=10, pady=5)
        
        # Quantity
        qty_frame = ttk.Frame(sale_frame)
        qty_frame.pack(fill="x", pady=5)
        ttk.Label(qty_frame, text="Quantity:").pack(side="left")
        qty_entry = ttk.Entry(qty_frame, width=10)
        qty_entry.pack(side="left", padx=5)
        qty_entry.insert(0, "1")
        
        # Selling price
        price_frame = ttk.Frame(sale_frame)
        price_frame.pack(fill="x", pady=5)
        ttk.Label(price_frame, text="Selling Price:").pack(side="left")
        price_entry = ttk.Entry(price_frame, width=10)
        price_entry.pack(side="left", padx=5)
        price_entry.insert(0, f"{cogs * 1.5:.2f}")  # Default 50% markup
        
        def process_sale():
            try:
                quantity = int(qty_entry.get())
                selling_price = float(price_entry.get())
                
                if quantity <= 0:
                    messagebox.showerror("Error", "Quantity must be positive")
                    return
                
                if selling_price <= 0:
                    messagebox.showerror("Error", "Price must be positive")
                    return
                
                if current_stock < quantity:
                    messagebox.showerror("Error", f"Insufficient stock. Available: {current_stock}")
                    return
                
                # Process sale
                from datetime import datetime
                success = self.db_manager.add_sale(product_id, quantity, selling_price, datetime.now().isoformat())
                
                if success:
                    self.add_scan_result(f"✅ Sale recorded: {quantity} units @ ₹{selling_price:.2f}")
                    dialog.destroy()
                else:
                    messagebox.showerror("Error", "Failed to record sale")
                    
            except ValueError:
                messagebox.showerror("Error", "Invalid input values")
        
        ttk.Button(sale_frame, text="Process Sale", command=process_sale).pack(pady=10)
        ttk.Button(dialog, text="Cancel", command=dialog.destroy).pack(pady=5)
    
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
                                    self.lookup_product(barcode_data, is_camera_scan=True)
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
                                                self.lookup_product(barcode_data, is_camera_scan=True)
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
        """Generate QR code for testing and display it"""
        try:
            # Ensure QR library is available
            if not self.ensure_qr_library():
                return

            import qrcode
            from PIL import Image, ImageTk

            # Create sample QR code
            qr = qrcode.QRCode(
                version=1,
                error_correction=qrcode.constants.ERROR_CORRECT_L,
                box_size=10,
                border=4,
            )
            qr.add_data('MONA-BEAUTY-001')
            qr.make(fit=True)

            img = qr.make_image(fill_color="black", back_color="white")

            # Save to generated_barcodes directory
            import os
            os.makedirs('generated_barcodes', exist_ok=True)
            filepath = 'generated_barcodes/sample_qr_code.png'
            img.save(filepath)

            # Display the QR code in the UI
            self.display_qr_image(filepath)

            self.add_scan_result("✅ QR code generated: sample_qr_code.png")
            self.add_scan_result("   You can scan this with your phone!")
            self.add_scan_result("   📷 QR code displayed on the right!")

        except Exception as e:
            self.add_scan_result(f"❌ Error generating QR code: {str(e)}")
    
    def ensure_qr_library(self):
        """Ensure QR code library is available"""
        global QRCODE_AVAILABLE
        if not QRCODE_AVAILABLE:
            try:
                import qrcode
                QRCODE_AVAILABLE = True
                print("✅ qrcode library loaded successfully")
                return True
            except ImportError:
                # Try to install automatically
                try:
                    import subprocess
                    import sys
                    print("🔄 Installing qrcode library...")
                    subprocess.check_call([sys.executable, "-m", "pip", "install", "qrcode[pil]", "--quiet"])
                    import qrcode
                    QRCODE_AVAILABLE = True
                    self.add_scan_result("✅ QR code library installed successfully!")
                    return True
                except Exception as install_error:
                    self.add_scan_result("❌ Could not install qrcode library automatically")
                    self.add_scan_result("💡 Please run: pip install qrcode[pil]")
                    return False
        return True

    def generate_and_display_product_qr(self, product, qr_data):
        """Generate and display QR code for an existing product"""
        try:
            # Ensure QR library is available
            if not self.ensure_qr_library():
                return

            product_id, name, sku, qr_code, category_id, cogs, current_stock = product[:7]

            # Add visual feedback that QR generation is happening
            self.add_scan_result(f"🎨 Generating QR code for: {name}")

            # Check if QR image already exists
            import os
            import glob

            qr_dir = 'generated_barcodes'
            os.makedirs(qr_dir, exist_ok=True)

            # Look for existing QR code image
            existing_files = glob.glob(os.path.join(qr_dir, f"qr_*{qr_data[:20].replace('/', '_')}*.png"))

            if existing_files:
                # Use existing QR code image
                self.display_qr_image(existing_files[0])
                self.add_scan_result("📸 QR code displayed from existing file")
            else:
                # Generate new QR code image
                self.add_scan_result("🔄 Creating QR code image...")

                from utils.qr_generator import QRGenerator
                qr_generator = QRGenerator(self.db_manager)
                image_path, message = qr_generator.generate_qr_image(qr_data)

                if image_path and os.path.exists(image_path):
                    self.display_qr_image(image_path)
                    self.add_scan_result(f"✅ QR code ready for: {name}")
                else:
                    self.add_scan_result(f"❌ Failed to generate QR code: {message}")

        except Exception as e:
            self.add_scan_result(f"❌ Error generating product QR code: {str(e)}")
            import traceback
            print(f"QR generation error details: {traceback.format_exc()}")

    def generate_and_display_manual_qr(self, qr_data):
        """Generate and display QR code for manually entered data"""
        try:
            # Ensure QR library is available
            if not self.ensure_qr_library():
                return

            # Add clear feedback about what we're doing
            self.add_scan_result(f"🎨 Creating QR code for: {qr_data}")
            if self.is_camera_on:
                self.add_scan_result("📷 Camera is active - QR code will appear in display area")

            from utils.qr_generator import QRGenerator
            qr_generator = QRGenerator(self.db_manager)
            image_path, message = qr_generator.generate_qr_image(qr_data)

            if image_path and os.path.exists(image_path):
                self.display_qr_image(image_path)
                self.add_scan_result("✅ QR code generated and displayed!")
                self.add_scan_result("📋 You can now scan this QR code or use it for inventory")

                # Additional helpful info
                if self.is_camera_on:
                    self.add_scan_result("💡 Tip: Point camera at the QR code to scan it")
                else:
                    self.add_scan_result("💡 Tip: Click 'Start Camera' to scan QR codes")
            else:
                self.add_scan_result(f"❌ Failed to generate QR code: {message}")

        except Exception as e:
            self.add_scan_result(f"❌ Error generating manual QR code: {str(e)}")
            import traceback
            print(f"Manual QR generation error details: {traceback.format_exc()}")

    def display_qr_image(self, image_path):
        """Display QR code image in the UI"""
        try:
            from PIL import Image, ImageTk
            import os

            if not os.path.exists(image_path):
                # Use after() to schedule UI update in main thread
                self.after(0, lambda: self.qr_display_label.config(text=f"QR Code file not found:\n{image_path}"))
                return

            # Load and resize image for display
            img = Image.open(image_path)
            # Resize to fit display area (larger size for better visibility)
            img.thumbnail((320, 320), Image.Resampling.LANCZOS)

            # Convert to Tkinter format
            photo = ImageTk.PhotoImage(img)

            # Update display label in main thread
            self.after(0, lambda: self.update_qr_display(photo, image_path))

            print(f"✅ QR code displayed: {image_path}")

        except Exception as e:
            # Use after() to schedule UI update in main thread
            self.after(0, lambda: self.qr_display_label.config(text=f"Error displaying QR code:\n{str(e)[:50]}"))
            print(f"❌ Error displaying QR code: {e}")

    def update_qr_display(self, photo, image_path):
        """Update QR display in main thread"""
        try:
            self.qr_display_label.config(image=photo, text="")
            self.qr_display_label.image = photo  # Keep reference

            # Update status indicator with more prominent text
            if self.is_camera_on:
                self.display_status_label.config(text="🔲 QR Code Ready for Scanning (Camera Active)", 
                                               foreground="green", font=("Arial", 10, "bold"))
            else:
                self.display_status_label.config(text="🔲 QR Code Ready for Scanning", 
                                               foreground="green", font=("Arial", 10, "bold"))

            # Add prominent success message
            self.add_scan_result(f"✅ QR code displayed: {os.path.basename(image_path)}")
            self.add_scan_result(f"📱 QR code is now visible and ready for scanning!")
            
        except Exception as e:
            print(f"❌ Error updating QR display: {e}")

    def show_existing_qr_codes(self):
        """Show existing QR codes from generated_barcodes directory"""
        try:
            import os
            import glob

            qr_dir = "generated_barcodes"
            if not os.path.exists(qr_dir):
                self.add_scan_result("❌ No QR codes directory found")
                return

            # Find QR code files (both qr_ and barcode_ prefixed)
            qr_patterns = [
                os.path.join(qr_dir, "qr_*.png"),
                os.path.join(qr_dir, "barcode_*.png")
            ]

            qr_files = []
            for pattern in qr_patterns:
                qr_files.extend(glob.glob(pattern))

            if not qr_files:
                self.add_scan_result("❌ No QR code files found")
                self.add_scan_result("💡 Generate QR codes first using 'Generate QR Codes' button")
                return

            # Sort by modification time (newest first)
            qr_files.sort(key=lambda x: os.path.getmtime(x), reverse=True)

            self.add_scan_result(f"📷 Found {len(qr_files)} QR code files:")
            for i, qr_file in enumerate(qr_files[:5], 1):  # Show first 5
                filename = os.path.basename(qr_file)
                self.add_scan_result(f"   {i}. {filename}")

            # Display the most recent QR code
            if qr_files:
                self.display_qr_image(qr_files[0])
                self.add_scan_result(f"📸 Displaying most recent: {os.path.basename(qr_files[0])}")

        except Exception as e:
            self.add_scan_result(f"❌ Error showing QR codes: {str(e)}")

    def generate_all_qr_codes(self):
        """Generate QR codes for all products"""
        try:
            # Ensure QR library is available
            if not self.ensure_qr_library():
                return

            from utils.qr_generator import QRGenerator

            qr_generator = QRGenerator(self.db_manager)
            qr_codes, message = qr_generator.generate_product_qr_codes()

            self.add_scan_result(f"📊 {message}")
            for item in qr_codes[:5]:  # Show first 5
                self.add_scan_result(f"   ✅ {item['name']}: {item['qr_code']}")

            if len(qr_codes) > 5:
                self.add_scan_result(f"   ... and {len(qr_codes) - 5} more")

            # Show the first generated QR code
            if qr_codes:
                import os
                image_path = qr_codes[0]['image_path']
                if os.path.exists(image_path):
                    self.display_qr_image(image_path)
                    self.add_scan_result(f"📸 Displaying: {qr_codes[0]['name']}")

        except ImportError:
            self.add_scan_result("❌ QR generator not available")
        except Exception as e:
            self.add_scan_result(f"❌ Error generating QR codes: {str(e)}")
    
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
        
        # Generate QR Code button
        qr_btn = ttk.Button(button_frame, text="🔲 Generate QR Code",
                                command=self.generate_product_qr_code)
        qr_btn.pack(side="left", padx=5)
    
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
    
    def generate_product_qr_code(self):
        """Generate QR code for current product"""
        if not self.current_product:
            return

        try:
            from utils.qr_generator import QRGenerator

            generator = QRGenerator(self.db_manager)
            product = self.current_product

            # Generate QR code if not exists
            qr_code = product[3]
            if not qr_code or qr_code.strip() == "":
                # Generate new QR code
                category_name = ""
                categories = self.db_manager.get_categories()
                for cat in categories:
                    if cat[0] == product[4]:
                        category_name = cat[1]
                        break

                sku, qr_code = generator.generate_sku_qr_code(product[1], category_name)

                # Update database
                success = self.db_manager.update_product_barcode(product[0], qr_code)
                if not success:
                    self.add_scan_result("❌ Failed to update product QR code")
                    return

            # Generate QR code image
            image_path, message = generator.generate_qr_image(qr_code)

            if image_path:
                self.add_scan_result(f"✅ QR code generated: {qr_code}")
                self.add_scan_result(f"   Saved to: {image_path}")

                # Show QR code image
                self.show_qr_image(image_path)
            else:
                self.add_scan_result(f"❌ Failed to generate QR code: {message}")

        except ImportError:
            self.add_scan_result("❌ QR generator not available")
        except Exception as e:
            self.add_scan_result(f"❌ Error generating QR code: {str(e)}")
    
    def show_qr_image(self, image_path):
        """Show generated QR code image"""
        try:
            # Create popup window
            popup = tk.Toplevel(self.parent)
            popup.title("Generated QR Code")
            popup.configure(bg="#fdf7f2")

            # Load and display image
            from PIL import Image, ImageTk
            img = Image.open(image_path)
            img = img.resize((400, 400), Image.Resampling.LANCZOS)  # QR codes need square display
            photo = ImageTk.PhotoImage(img)

            label = ttk.Label(popup, image=photo)
            label.image = photo  # Keep a reference
            label.pack(padx=20, pady=20)

            # Buttons
            button_frame = ttk.Frame(popup)
            button_frame.pack(pady=10)

            ttk.Button(button_frame, text="Save As...",
                      command=lambda: self.save_qr_as(image_path)).pack(side="left", padx=5)
            ttk.Button(button_frame, text="Close",
                      command=popup.destroy).pack(side="left", padx=5)

        except Exception as e:
            messagebox.showerror("Error", f"Cannot display QR code: {str(e)}")

    def save_qr_as(self, source_path):
        """Save QR code image to chosen location"""
        try:
            filename = filedialog.asksaveasfilename(
                title="Save QR Code As",
                defaultextension=".png",
                filetypes=[("PNG files", "*.png"), ("All files", "*.*")]
            )

            if filename:
                import shutil
                shutil.copy2(source_path, filename)
                messagebox.showinfo("Success", f"QR code saved to:\\n{filename}")
        except Exception as e:
            messagebox.showerror("Error", f"Failed to save QR code: {str(e)}")
    
    def offer_create_product(self, qr_data):
        """Offer to create new product with scanned QR code"""
        result = messagebox.askyesno("Product Not Found",
            f"QR code '{qr_data}' not found in inventory.\\n\\n"
            "Would you like to create a new product with this QR code?")

        if result:
            self.create_product_dialog(qr_data)
    
    def create_product_dialog(self, qr_code):
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

        # QR Code (pre-filled)
        ttk.Label(form_frame, text="QR Code:").grid(row=2, column=0, sticky="w", pady=5)
        qr_code_var = tk.StringVar(value=qr_code)
        ttk.Entry(form_frame, textvariable=qr_code_var, width=30).grid(row=2, column=1, sticky="ew", padx=10)
        
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
                    qr_code_var.get().strip(),
                    category_id,
                    cogs,
                    stock
                )

                if success:
                    self.add_scan_result(f"✅ Product created: {name_var.get()}")
                    self.add_scan_result(f"   QR Code: {qr_code_var.get()}")
                    self.add_scan_result(f"   Stock: {stock}")
                    dialog.destroy()

                    # Look up the newly created product
                    self.lookup_product(qr_code_var.get())
                else:
                    messagebox.showerror("Error", "Failed to create product. QR code may already exist.")
                    
            except Exception as e:
                messagebox.showerror("Error", f"Failed to create product: {str(e)}")
        
        ttk.Button(button_frame, text="Create Product", command=create_product).pack(side="right", padx=5)
        ttk.Button(button_frame, text="Cancel", command=dialog.destroy).pack(side="right", padx=5)
    
    def generate_all_qr_codes(self):
        """Generate QR codes for all products"""
        try:
            from utils.qr_generator import QRGenerator

            generator = QRGenerator(self.db_manager)
            qr_codes, message = generator.generate_product_qr_codes()

            self.add_scan_result(f"📊 {message}")
            for item in qr_codes[:5]:  # Show first 5
                self.add_scan_result(f"   ✅ {item['name']}: {item['qr_code']}")

            if len(qr_codes) > 5:
                self.add_scan_result(f"   ... and {len(qr_codes) - 5} more")

        except ImportError:
            self.add_scan_result("❌ QR generator not available")
        except Exception as e:
            self.add_scan_result(f"❌ Error generating QR codes: {str(e)}")
    
    def create_print_sheet(self):
        """Create printable QR code sheet"""
        try:
            from utils.qr_generator import QRGenerator

            generator = QRGenerator(self.db_manager)
            pdf_path, message = generator.create_qr_print_sheet()

            if pdf_path:
                self.add_scan_result(f"✅ QR print sheet created: {pdf_path}")

                # Ask to open
                result = messagebox.askyesno("Print Sheet Created",
                    f"QR code print sheet created successfully!\\n\\n"
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
    
    def is_reasonable_qr_code(self, qr_data: str) -> bool:
        """Check if detected QR code is reasonable (not random noise)"""
        try:
            if not qr_data or len(qr_data.strip()) < 2:
                return False

            clean_data = qr_data.strip()

            # Check for minimum content requirements
            if len(clean_data) < 2:
                return False

            # Check for reasonable character distribution
            if len(set(clean_data)) < 2 and len(clean_data) > 10:
                # All same characters is likely noise
                return False

            # Check for URL patterns (common QR content)
            import re
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

            # Additional checks for existing products
            # If QR code exists in database, it's definitely valid
            existing_product = self.db_manager.get_product_by_barcode(clean_data)
            if existing_product:
                return True

            return False

        except Exception as e:
            print(f"QR code validation error: {e}")
            return True  # Default to true if validation fails
    
    def on_closing(self):
        self.stop_camera()
