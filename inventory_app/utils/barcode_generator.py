#!/usr/bin/env python3
"""
Production-Grade Barcode Generation System
Handles barcode creation, validation, and printing for Mona Beauty Store
"""

import os
import sys
from datetime import datetime
from pathlib import Path
import tkinter as tk
from tkinter import messagebox, filedialog
from PIL import Image, ImageDraw, ImageFont

# Import barcode libraries
try:
    import barcode
    from barcode.writer import ImageWriter
    from barcode import Code128, EAN13, Code39, UPCA
    BARCODE_AVAILABLE = True
except ImportError:
    BARCODE_AVAILABLE = False
    print("⚠️ python-barcode not available - barcode generation disabled")

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

class BarcodeGenerator:
    """Production-grade barcode generation system"""
    
    def __init__(self, db_manager=None):
        self.db_manager = db_manager
        self.barcode_dir = Path("generated_barcodes")
        self.barcode_dir.mkdir(exist_ok=True)
        
        # Mona Beauty Store branding colors
        self.brand_colors = {
            'primary': '#fc68ae',  # Light Pink
            'background': '#fdf7f2',  # Creamy Beige
            'text': '#333333',
            'accent': '#e91e63'
        }
    
    def generate_sku_barcode(self, product_name, category=""):
        """Generate unique SKU/Barcode for new products"""
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
            
            # Generate barcode (numeric for better scanner compatibility)
            # Use timestamp + hash for unique numeric barcode
            import hashlib
            hash_obj = hashlib.md5(sku.encode())
            hash_hex = hash_obj.hexdigest()[:8]
            barcode_num = str(int(hash_hex, 16))[:12].zfill(12)
            
            return sku, barcode_num
            
        except Exception as e:
            print(f"Error generating SKU/Barcode: {e}")
            # Fallback to simple timestamp-based generation
            timestamp = datetime.now().strftime("%Y%m%d%H%M%S")
            return f"PROD-{timestamp}", timestamp
    
    def validate_barcode_format(self, barcode, barcode_type="CODE128"):
        """Validate barcode format based on type"""
        try:
            if not barcode or not barcode.strip():
                return False, "Barcode cannot be empty"
            
            barcode = barcode.strip()
            
            if barcode_type == "EAN13":
                if not barcode.isdigit() or len(barcode) != 13:
                    return False, "EAN13 must be exactly 13 digits"
            elif barcode_type == "UPCA":
                if not barcode.isdigit() or len(barcode) != 12:
                    return False, "UPC-A must be exactly 12 digits"
            elif barcode_type == "CODE39":
                if not all(c.isalnum() or c in "-.$/+% " for c in barcode):
                    return False, "Code39 contains invalid characters"
            elif barcode_type == "CODE128":
                # Most flexible format
                if len(barcode) > 80:
                    return False, "Code128 barcode too long (max 80 characters)"
            
            return True, ""
            
        except Exception as e:
            return False, f"Validation error: {str(e)}"
    
    def generate_barcode_image(self, barcode_data, barcode_type="code128", 
                             include_text=True, width=300, height=100):
        """Generate barcode image with Mona Beauty Store branding"""
        try:
            if not BARCODE_AVAILABLE:
                return None, "Barcode library not available"
            
            # Select barcode class
            barcode_classes = {
                'code128': Code128,
                'code39': Code39,
                'ean13': EAN13,
                'upca': UPCA
            }
            
            barcode_class = barcode_classes.get(barcode_type.lower(), Code128)
            
            # Validate format
            valid, message = self.validate_barcode_format(barcode_data, barcode_type.upper())
            if not valid:
                return None, message
            
            # Generate barcode
            writer = ImageWriter()
            writer.format = 'PNG'
            
            # Create barcode object
            barcode_obj = barcode_class(barcode_data, writer=writer)
            
            # Generate image
            filename = f"barcode_{barcode_data}_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
            filepath = self.barcode_dir / filename
            
            # Save barcode image
            barcode_obj.save(filepath)
            
            # Add branding if requested
            if include_text:
                self.add_branding_to_barcode(f"{filepath}.png", barcode_data)
            
            return f"{filepath}.png", "Barcode generated successfully"
            
        except Exception as e:
            return None, f"Error generating barcode: {str(e)}"
    
    def add_branding_to_barcode(self, image_path, barcode_data):
        """Add Mona Beauty Store branding to barcode image"""
        try:
            # Open barcode image
            img = Image.open(image_path)
            
            # Create new image with extra space for branding
            new_height = img.height + 80
            new_img = Image.new('RGB', (img.width, new_height), color=self.brand_colors['background'])
            
            # Paste barcode
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
            text_width = draw.textbbox((0, 0), store_text, font=font_large)[2]
            x = (new_img.width - text_width) // 2
            draw.text((x, 10), store_text, fill=self.brand_colors['primary'], font=font_large)
            
            # Add barcode number
            barcode_text = f"Code: {barcode_data}"
            text_width = draw.textbbox((0, 0), barcode_text, font=font_small)[2]
            x = (new_img.width - text_width) // 2
            draw.text((x, new_height - 25), barcode_text, fill=self.brand_colors['text'], font=font_small)
            
            # Save branded image
            new_img.save(image_path)
            
        except Exception as e:
            print(f"Error adding branding: {e}")
    
    def generate_product_barcodes(self, products=None):
        """Generate barcodes for all products or specific products"""
        try:
            if not products and self.db_manager:
                products = self.db_manager.get_products()
            
            if not products:
                return [], "No products found"
            
            generated_barcodes = []
            
            for product in products:
                product_id, name, sku, barcode, category_id, cogs, current_stock = product[:7]
                
                # Use existing barcode or generate new one
                if not barcode or barcode.strip() == "":
                    # Generate new barcode
                    category_name = self.get_category_name(category_id) if self.db_manager else ""
                    new_sku, new_barcode = self.generate_sku_barcode(name, category_name)
                    
                    # Update database with new barcode
                    if self.db_manager:
                        self.db_manager.update_product_barcode(product_id, new_barcode)
                    
                    barcode = new_barcode
                
                # Generate barcode image
                image_path, message = self.generate_barcode_image(barcode)
                
                if image_path:
                    generated_barcodes.append({
                        'product_id': product_id,
                        'name': name,
                        'sku': sku,
                        'barcode': barcode,
                        'image_path': image_path
                    })
            
            return generated_barcodes, f"Generated {len(generated_barcodes)} barcodes"
            
        except Exception as e:
            return [], f"Error generating product barcodes: {str(e)}"
    
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
    
    def create_barcode_print_sheet(self, products=None, sheet_format="A4"):
        """Create printable barcode sheet PDF"""
        try:
            if not PDF_AVAILABLE:
                return None, "PDF generation not available - install reportlab"
            
            # Generate barcodes first
            barcode_data, message = self.generate_product_barcodes(products)
            
            if not barcode_data:
                return None, message
            
            # Create PDF
            filename = f"barcode_sheet_{datetime.now().strftime('%Y%m%d_%H%M%S')}.pdf"
            filepath = self.barcode_dir / filename
            
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
            
            title = Paragraph("MONA BEAUTY STORE - PRODUCT BARCODES", title_style)
            story.append(title)
            story.append(Spacer(1, 20))
            
            # Create table data
            table_data = []
            table_data.append(['Product Name', 'SKU', 'Barcode', 'Category'])
            
            for item in barcode_data:
                # Get category name
                category_name = ""
                if self.db_manager:
                    product = self.db_manager.get_product(item['product_id'])
                    if product:
                        category_name = self.get_category_name(product[4])
                
                table_data.append([
                    item['name'][:30],  # Truncate long names
                    item['sku'] or 'N/A',
                    item['barcode'],
                    category_name
                ])
            
            # Create table
            table = Table(table_data, colWidths=[3*inch, 1.5*inch, 1.5*inch, 1.5*inch])
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
            2. Cut out individual barcode labels<br/>
            3. Stick labels on product packaging<br/>
            4. Use barcode scanner to scan products<br/>
            5. For best results, use high-quality printer settings
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
            
            return str(filepath), f"Barcode sheet created with {len(barcode_data)} products"
            
        except Exception as e:
            return None, f"Error creating barcode sheet: {str(e)}"
    
    def cleanup_old_barcodes(self, days_old=30):
        """Clean up old barcode files"""
        try:
            import time
            
            current_time = time.time()
            deleted_count = 0
            
            for file_path in self.barcode_dir.glob("barcode_*.png"):
                file_age = current_time - file_path.stat().st_mtime
                if file_age > (days_old * 24 * 60 * 60):  # Convert days to seconds
                    file_path.unlink()
                    deleted_count += 1
            
            return deleted_count, f"Cleaned up {deleted_count} old barcode files"
            
        except Exception as e:
            return 0, f"Error cleaning up barcodes: {str(e)}"

# Test function
def test_barcode_generator():
    """Test the barcode generator"""
    print("🧪 Testing Barcode Generator")
    print("=" * 40)
    
    generator = BarcodeGenerator()
    
    # Test SKU generation
    sku, barcode = generator.generate_sku_barcode("Lash Extension Kit", "Lash o'clock")
    print(f"Generated SKU: {sku}")
    print(f"Generated Barcode: {barcode}")
    
    # Test barcode image generation
    image_path, message = generator.generate_barcode_image(barcode)
    if image_path:
        print(f"✅ Barcode image created: {image_path}")
    else:
        print(f"❌ Failed to create barcode: {message}")
    
    # Test validation
    valid, msg = generator.validate_barcode_format("123456789012", "UPCA")
    print(f"UPC-A validation: {valid} - {msg}")

if __name__ == "__main__":
    test_barcode_generator()
