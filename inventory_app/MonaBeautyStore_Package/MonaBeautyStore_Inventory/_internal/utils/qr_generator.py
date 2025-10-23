#!/usr/bin/env python3
"""
Production-Grade QR Code Generation System
Handles QR code creation, validation, and printing for Mona Beauty Store
"""

import os
import sys
from datetime import datetime
from pathlib import Path
import tkinter as tk
from tkinter import messagebox, filedialog
from PIL import Image, ImageDraw, ImageFont

# Import QR code libraries
try:
    import qrcode
    QRCODE_AVAILABLE = True
except ImportError:
    QRCODE_AVAILABLE = False
    print("⚠️ qrcode library not available - QR generation disabled")

try:
    from reportlab.pdfgen import canvas
    from reportlab.lib.pagesizes import letter, A4
    from reportlab.lib.units import inch
    from reportlab.platypus import SimpleDocTemplate, Table, TableStyle, Paragraph, Spacer
    from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
    from reportlab.lib import colors
    PDF_AVAILABLE = True
except ImportError:
    PDF_AVAILABLE = False
    print("⚠️ reportlab not available - PDF generation disabled")

class QRGenerator:
    """Production-grade QR code generation system"""

    def __init__(self, db_manager=None):
        self.db_manager = db_manager
        self.qr_dir = Path("generated_barcodes")  # Use same directory for consistency
        self.qr_dir.mkdir(exist_ok=True)

        # Mona Beauty Store branding colors
        self.brand_colors = {
            'primary': '#fc68ae',  # Light Pink
            'background': '#fdf7f2',  # Creamy Beige
            'text': '#333333',
            'accent': '#e91e63'
        }

    def generate_sku_qr_code(self, product_name, category=""):
        """Generate unique SKU/QR code for new products"""
        try:
            # Create SKU based on product name and category
            name_part = ''.join(filter(str.isalnum, product_name))[:8].upper()
            category_part = ''.join(filter(str.isalnum, category))[:3].upper()

            # Add timestamp for uniqueness
            timestamp = datetime.now().strftime("%m%d")

            # Generate SKU: CATEGORY-NAME-TIMESTAMP
            if category_part:
                sku = f"{category_part}-{name_part}-{timestamp}"
            else:
                sku = f"{name_part}-{timestamp}"

            # Generate QR code data (can be alphanumeric for better readability)
            # Use SKU with additional product info
            qr_data = f"MONA-{sku}-{datetime.now().strftime('%Y%m%d%H%M%S')}"

            return sku, qr_data

        except Exception as e:
            print(f"Error generating SKU/QR code: {e}")
            # Fallback to simple timestamp-based generation
            timestamp = datetime.now().strftime("%Y%m%d%H%M%S")
            return f"PROD-{timestamp}", f"MONA-{timestamp}"

    def validate_qr_format(self, qr_data):
        """Validate QR code data format"""
        try:
            if not qr_data or not qr_data.strip():
                return False, "QR code data cannot be empty"

            qr_data = qr_data.strip()

            # Check length (QR codes can handle up to ~4KB but we limit for practicality)
            if len(qr_data) > 1000:
                return False, "QR code data too long (max 1000 characters)"

            # Check for minimum length
            if len(qr_data) < 2:
                return False, "QR code data too short (min 2 characters)"

            # Check for reasonable character distribution
            if len(set(qr_data)) < 2 and len(qr_data) > 10:
                return False, "QR code data appears to be repetitive"

            return True, ""

        except Exception as e:
            return False, f"Validation error: {str(e)}"

    def generate_qr_image(self, qr_data, include_text=True, size=300, border=4):
        """Generate QR code image with Mona Beauty Store branding"""
        try:
            if not QRCODE_AVAILABLE:
                return None, "QR code library not available"

            # Validate format
            valid, message = self.validate_qr_format(qr_data)
            if not valid:
                return None, message

            # Create QR code object with high error correction
            qr = qrcode.QRCode(
                version=None,  # Auto-size
                error_correction=qrcode.constants.ERROR_CORRECT_M,  # 15% error correction
                box_size=10,
                border=border,
            )

            # Add data
            qr.add_data(qr_data)
            qr.make(fit=True)

            # Create image with custom colors
            img = qr.make_image(fill_color="black", back_color="white")

            # Convert to RGB for branding
            img = img.convert("RGB")

            # Generate filename (use qr_ prefix to distinguish from barcodes)
            safe_qr_data = qr_data[:20].replace('/', '_').replace('\\', '_')
            filename = f"qr_{safe_qr_data}_{datetime.now().strftime('%Y%m%d_%H%M%S')}.png"
            filepath = self.qr_dir / filename

            # Save QR code image
            img.save(filepath)

            # Add branding if requested
            if include_text:
                self.add_branding_to_qr(str(filepath), qr_data)

            return str(filepath), "QR code generated successfully"

        except Exception as e:
            return None, f"Error generating QR code: {str(e)}"

    def add_branding_to_qr(self, image_path, qr_data):
        """Add Mona Beauty Store branding to QR code image"""
        try:
            # Open QR code image
            img = Image.open(image_path)

            # Create new image with extra space for branding
            new_height = img.height + 80
            new_img = Image.new('RGB', (img.width, new_height), color=self.brand_colors['background'])

            # Paste QR code
            new_img.paste(img, (0, 40))

            # Add text
            draw = ImageDraw.Draw(new_img)

            try:
                # Try to use a nice font
                font_large = ImageFont.truetype("arial.ttf", 16)
                font_small = ImageFont.truetype("arial.ttf", 12)
            except:
                # Fallback to default font
                font_large = ImageFont.load_default()
                font_small = ImageFont.load_default()

            # Add store name
            store_text = "MONA BEAUTY STORE"
            text_bbox = draw.textbbox((0, 0), store_text, font=font_large)
            text_width = text_bbox[2] - text_bbox[0]
            x = (new_img.width - text_width) // 2
            draw.text((x, 10), store_text, fill=self.brand_colors['primary'], font=font_large)

            # Add QR code data (truncated if too long)
            display_data = qr_data[:25] + "..." if len(qr_data) > 25 else qr_data
            qr_text = f"Code: {display_data}"
            text_bbox = draw.textbbox((0, 0), qr_text, font=font_small)
            text_width = text_bbox[2] - text_bbox[0]
            x = (new_img.width - text_width) // 2
            draw.text((x, new_height - 25), qr_text, fill=self.brand_colors['text'], font=font_small)

            # Save branded image
            new_img.save(image_path)

        except Exception as e:
            print(f"Error adding branding: {e}")

    def generate_product_qr_codes(self, products=None):
        """Generate QR codes for all products or specific products"""
        try:
            if not products and self.db_manager:
                products = self.db_manager.get_products()

            if not products:
                return [], "No products found"

            generated_qr_codes = []

            for product in products:
                product_id, name, sku, qr_code, category_id, cogs, current_stock = product[:7]

                # Use existing QR code or generate new one
                if not qr_code or qr_code.strip() == "":
                    # Generate new QR code
                    category_name = self.get_category_name(category_id) if self.db_manager else ""
                    new_sku, new_qr_code = self.generate_sku_qr_code(name, category_name)

                    # Update database with new QR code
                    if self.db_manager:
                        self.db_manager.update_product_barcode(product_id, new_qr_code)

                    qr_code = new_qr_code

                # Generate QR code image
                image_path, message = self.generate_qr_image(qr_code)

                if image_path:
                    generated_qr_codes.append({
                        'product_id': product_id,
                        'name': name,
                        'sku': sku,
                        'qr_code': qr_code,
                        'image_path': image_path
                    })

            return generated_qr_codes, f"Generated {len(generated_qr_codes)} QR codes"

        except Exception as e:
            return [], f"Error generating product QR codes: {str(e)}"

    def get_category_name(self, category_id):
        """Get category name by ID"""
        try:
            if self.db_manager:
                categories = self.db_manager.get_categories()
                for cat in categories:
                    if cat[0] == category_id:
                        return cat[1]
            return ""
        except:
            return ""

    def create_qr_print_sheet(self, products=None, sheet_format="A4"):
        """Create printable QR code sheet PDF"""
        try:
            if not PDF_AVAILABLE:
                return None, "PDF generation not available - install reportlab"

            # Generate QR codes first
            qr_data, message = self.generate_product_qr_codes(products)

            if not qr_data:
                return None, message

            # Create PDF
            filename = f"qr_sheet_{datetime.now().strftime('%Y%m%d_%H%M%S')}.pdf"
            filepath = self.qr_dir / filename

            # Set up PDF
            doc = SimpleDocTemplate(str(filepath), pagesize=A4)
            styles = getSampleStyleSheet()
            story = []

            # Title
            title_style = ParagraphStyle(
                'CustomTitle',
                parent=styles['Heading1'],
                fontSize=20,
                spaceAfter=30,
                textColor=colors.HexColor(self.brand_colors['primary']),
                alignment=1  # Center
            )

            title = Paragraph("MONA BEAUTY STORE - PRODUCT QR CODES", title_style)
            story.append(title)
            story.append(Spacer(1, 20))

            # Create table data
            table_data = []
            table_data.append(['Product Name', 'SKU', 'QR Code', 'Category'])

            for item in qr_data:
                # Get category name
                category_name = ""
                if self.db_manager:
                    product = self.db_manager.get_product(item['product_id'])
                    if product:
                        category_name = self.get_category_name(product[4])

                table_data.append([
                    item['name'][:30],  # Truncate long names
                    item['sku'] or 'N/A',
                    item['qr_code'][:25] + "..." if len(item['qr_code']) > 25 else item['qr_code'],
                    category_name
                ])

            # Create table
            table = Table(table_data, colWidths=[3*inch, 1.5*inch, 2*inch, 1.5*inch])
            table.setStyle(TableStyle([
                ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor(self.brand_colors['primary'])),
                ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
                ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
                ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
                ('FONTSIZE', (0, 0), (-1, 0), 12),
                ('BOTTOMPADDING', (0, 0), (-1, 0), 12),
                ('BACKGROUND', (0, 1), (-1, -1), colors.beige),
                ('GRID', (0, 0), (-1, -1), 1, colors.black),
                ('FONTNAME', (0, 1), (-1, -1), 'Helvetica'),
                ('FONTSIZE', (0, 1), (-1, -1), 10),
            ]))

            story.append(table)

            # Add instructions
            story.append(Spacer(1, 30))
            instructions = """
            <b>Instructions for Use:</b><br/>
            1. Print this sheet on standard A4 paper<br/>
            2. Cut out individual QR code labels<br/>
            3. Stick labels on product packaging<br/>
            4. Use QR code scanner to scan products<br/>
            5. For best results, use high-quality printer settings<br/>
            6. QR codes work with any smartphone camera
            """

            instruction_style = ParagraphStyle(
                'Instructions',
                parent=styles['Normal'],
                fontSize=10,
                leftIndent=20
            )

            story.append(Paragraph(instructions, instruction_style))

            # Build PDF
            doc.build(story)

            return str(filepath), f"QR code sheet created with {len(qr_data)} products"

        except Exception as e:
            return None, f"Error creating QR code sheet: {str(e)}"

    def cleanup_old_qr_codes(self, days_old=30):
        """Clean up old QR code files"""
        try:
            import time

            current_time = time.time()
            deleted_count = 0

            for file_path in self.qr_dir.glob("qr_*.png"):
                file_age = current_time - file_path.stat().st_mtime
                if file_age > (days_old * 24 * 60 * 60):  # Convert days to seconds
                    file_path.unlink()
                    deleted_count += 1

            return deleted_count, f"Cleaned up {deleted_count} old QR code files"

        except Exception as e:
            return 0, f"Error cleaning up QR codes: {str(e)}"

# Test function
def test_qr_generator():
    """Test the QR generator"""
    print("🧪 Testing QR Code Generator")
    print("=" * 40)

    generator = QRGenerator()

    # Test SKU generation
    sku, qr_code = generator.generate_sku_qr_code("Lash Extension Kit", "Lash o'clock")
    print(f"Generated SKU: {sku}")
    print(f"Generated QR Code: {qr_code}")

    # Test QR code image generation
    image_path, message = generator.generate_qr_image(qr_code)
    if image_path:
        print(f"✅ QR code image created: {image_path}")
    else:
        print(f"❌ Failed to create QR code: {message}")

    # Test validation
    valid, msg = generator.validate_qr_format("MONA-LASH-001-20241201120000")
    print(f"QR validation: {valid} - {msg}")

if __name__ == "__main__":
    test_qr_generator()
