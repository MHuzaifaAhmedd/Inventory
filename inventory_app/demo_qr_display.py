#!/usr/bin/env python3
"""
Demo script to show QR code display functionality
"""

import tkinter as tk
from tkinter import ttk
import sys
import os

# Add current directory to path
sys.path.insert(0, '.')

def demo_qr_display():
    """Demonstrate QR code display functionality"""
    print("🧪 Demonstrating QR Code Display Functionality")
    print("=" * 60)

    try:
        # Create a simple demo window
        root = tk.Tk()
        root.title("QR Code Display Demo")
        root.geometry("800x600")

        # Create main frame
        main_frame = tk.Frame(root)
        main_frame.pack(fill=tk.BOTH, expand=True, padx=20, pady=20)

        # Title
        title_label = tk.Label(main_frame, text="📱 QR Code Display Demo",
                              font=("Arial", 16, "bold"))
        title_label.pack(pady=10)

        # Instructions
        instructions = tk.Label(main_frame,
            text="""This demo shows how QR codes are displayed in the scanner interface:

1. Text results appear on the LEFT side
2. QR code images appear on the RIGHT side
3. Images are automatically resized to fit the display area
4. Both new and existing QR codes can be viewed

Click the buttons below to test the functionality!""",
            font=("Arial", 10),
            justify=tk.LEFT,
            wraplength=700
        )
        instructions.pack(pady=10)

        # Results display area (similar to QR scanner)
        results_frame = ttk.LabelFrame(main_frame, text="QR Scan Results Demo", padding=10)
        results_frame.pack(fill=tk.BOTH, expand=True, pady=10)

        # Results display area with QR image display
        results_container = tk.Frame(results_frame)
        results_container.pack(fill=tk.BOTH, expand=True)

        # Text results on left
        text_frame = tk.Frame(results_container)
        text_frame.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)

        results_text = tk.Text(text_frame, height=10, width=40)
        results_text.pack(fill=tk.BOTH, expand=True)

        # QR image display on right
        image_frame = tk.Frame(results_container)
        image_frame.pack(side=tk.RIGHT, fill=tk.BOTH, expand=False, padx=(10, 0))

        qr_display_label = ttk.Label(image_frame, text="No QR Code Generated\n\nClick buttons below to test!")
        qr_display_label.pack(pady=10)

        def add_demo_result(result):
            """Add result to text area"""
            import time
            timestamp = time.strftime("%H:%M:%S")
            results_text.insert(tk.END, f"[{timestamp}] {result}\n")
            results_text.see(tk.END)

        def display_qr_image_demo(image_path):
            """Display QR code image in the demo"""
            try:
                from PIL import Image, ImageTk

                if not os.path.exists(image_path):
                    qr_display_label.config(text=f"QR Code file not found:\n{image_path}")
                    return

                # Load and resize image for display
                img = Image.open(image_path)
                # Resize to fit display area (max 200x200)
                img.thumbnail((200, 200), Image.Resampling.LANCZOS)

                # Convert to Tkinter format
                photo = ImageTk.PhotoImage(img)

                # Update display label
                qr_display_label.config(image=photo, text="")
                qr_display_label.image = photo  # Keep reference

                add_demo_result(f"✅ QR code displayed: {os.path.basename(image_path)}")

            except Exception as e:
                qr_display_label.config(text=f"Error displaying QR code:\n{str(e)[:50]}")
                add_demo_result(f"❌ Error displaying QR code: {e}")

        def generate_demo_qr():
            """Generate a demo QR code"""
            try:
                import qrcode
                from PIL import Image

                # Create demo QR code
                qr = qrcode.QRCode(
                    version=1,
                    error_correction=qrcode.constants.ERROR_CORRECT_L,
                    box_size=10,
                    border=4,
                )
                qr.add_data('DEMO-QR-CODE-FOR-INVENTORY')
                qr.make(fit=True)

                img = qr.make_image(fill_color="black", back_color="white")

                # Save to generated_barcodes directory
                os.makedirs('generated_barcodes', exist_ok=True)
                filepath = 'generated_barcodes/demo_qr_code.png'
                img.save(filepath)

                # Display the QR code
                display_qr_image_demo(filepath)

                add_demo_result("✅ Demo QR code generated!")
                add_demo_result("   📱 You can scan this with your phone")
                add_demo_result("   📷 QR code displayed on the right!")

            except Exception as e:
                add_demo_result(f"❌ Error generating demo QR code: {e}")

        def show_existing_qr_demo():
            """Show existing QR codes"""
            try:
                import glob

                qr_dir = "generated_barcodes"
                if not os.path.exists(qr_dir):
                    add_demo_result("❌ No QR codes directory found")
                    return

                # Find QR code files
                qr_patterns = [
                    os.path.join(qr_dir, "qr_*.png"),
                    os.path.join(qr_dir, "barcode_*.png")
                ]

                qr_files = []
                for pattern in qr_patterns:
                    qr_files.extend(glob.glob(pattern))

                if not qr_files:
                    add_demo_result("❌ No QR code files found")
                    add_demo_result("💡 Generate QR codes first")
                    return

                # Sort by modification time (newest first)
                qr_files.sort(key=lambda x: os.path.getmtime(x), reverse=True)

                add_demo_result(f"📷 Found {len(qr_files)} QR code files:")
                for i, qr_file in enumerate(qr_files[:3], 1):  # Show first 3
                    filename = os.path.basename(qr_file)
                    add_demo_result(f"   {i}. {filename}")

                # Display the most recent QR code
                if qr_files:
                    display_qr_image_demo(qr_files[0])
                    add_demo_result(f"📸 Displaying most recent: {os.path.basename(qr_files[0])}")

            except Exception as e:
                add_demo_result(f"❌ Error showing QR codes: {e}")

        # Buttons frame
        buttons_frame = tk.Frame(main_frame)
        buttons_frame.pack(fill=tk.X, pady=10)

        # Generate Demo QR button
        generate_btn = tk.Button(
            buttons_frame,
            text="🔲 Generate Demo QR Code",
            font=("Arial", 10, "bold"),
            bg="#fc68ae",
            fg="white",
            padx=15,
            pady=8,
            command=generate_demo_qr
        )
        generate_btn.pack(side=tk.LEFT, padx=5)

        # Show Existing QR button
        show_btn = tk.Button(
            buttons_frame,
            text="📷 Show Existing QR Codes",
            font=("Arial", 10, "bold"),
            bg="#17a2b8",
            fg="white",
            padx=15,
            pady=8,
            command=show_existing_qr_demo
        )
        show_btn.pack(side=tk.LEFT, padx=5)

        # Clear button
        clear_btn = tk.Button(
            buttons_frame,
            text="🗑️ Clear Results",
            font=("Arial", 10),
            bg="#f8f9fa",
            padx=15,
            pady=8,
            command=lambda: results_text.delete(1.0, tk.END)
        )
        clear_btn.pack(side=tk.RIGHT, padx=5)

        # Initial demo message
        add_demo_result("🎯 Welcome to QR Code Display Demo!")
        add_demo_result("📱 This shows how QR codes appear in the scanner interface")
        add_demo_result("🔲 Click 'Generate Demo QR Code' to create and display a QR code")
        add_demo_result("📷 Click 'Show Existing QR Codes' to view saved QR codes")

        # Start the demo
        root.mainloop()

    except Exception as e:
        print(f"❌ Demo failed: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    print("🚀 Starting QR Code Display Demo...")
    print("📱 This will open a demo window showing QR code display functionality")
    print("Press Ctrl+C in terminal to exit")
    print()

    demo_qr_display()

