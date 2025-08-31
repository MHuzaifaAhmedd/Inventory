#!/usr/bin/env python3
"""
Manual test for barcode scanning interface
"""

import sys
import os

# Add the current directory to Python path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from database.db_manager import DatabaseManager

def test_manual_barcode_lookup():
    """Test manual barcode lookup like the scanner interface"""
    print("🔍 Manual Barcode Lookup Test")
    print("=" * 40)
    
    db = DatabaseManager()
    
    # Get all products to show available barcodes
    products = db.get_products()
    
    if not products:
        print("⚠️ No products found in database")
        return
    
    print("📦 Available products with barcodes:")
    valid_barcodes = []
    
    for product in products:
        product_id, name, sku, barcode = product[:4]
        if barcode and barcode.strip():
            print(f"   • {name}: {barcode}")
            valid_barcodes.append(barcode)
        elif sku and sku.strip():
            print(f"   • {name}: {sku} (SKU)")
            valid_barcodes.append(sku)
    
    if not valid_barcodes:
        print("⚠️ No products have barcodes or SKUs")
        return
    
    # Test lookup with first available barcode
    test_barcode = valid_barcodes[0]
    print(f"\n🧪 Testing lookup with: {test_barcode}")
    
    # This simulates what happens in the barcode scanner
    found_product = db.get_product_by_barcode(test_barcode)
    
    if found_product:
        product_id, name, sku, barcode, category_id, cogs, current_stock = found_product[:7]
        
        # Get category name
        categories = db.get_categories()
        category_name = "Unknown"
        for cat in categories:
            if cat[0] == category_id:
                category_name = cat[1]
                break
        
        print("✅ Product found!")
        print(f"   Name: {name}")
        print(f"   SKU: {sku or 'N/A'}")
        print(f"   Barcode: {barcode or 'N/A'}")
        print(f"   Category: {category_name}")
        print(f"   COGS: ₹{cogs:.2f}")
        print(f"   Stock: {current_stock} units")
        
        print("\n🎯 This is exactly what the barcode scanner will show!")
        
    else:
        print("❌ Product not found - this indicates a problem")

def main():
    """Main test"""
    try:
        test_manual_barcode_lookup()
        print("\n✅ Manual test completed")
    except Exception as e:
        print(f"❌ Test error: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    main()
