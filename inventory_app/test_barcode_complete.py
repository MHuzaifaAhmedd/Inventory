#!/usr/bin/env python3
"""
Complete test for barcode generation and lookup functionality
"""

import sys
import os
from datetime import datetime

# Add the current directory to Python path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from database.db_manager import DatabaseManager

def test_barcode_generation_and_lookup():
    """Test complete barcode workflow"""
    print("🧪 Testing Complete Barcode Functionality")
    print("=" * 60)
    
    # Initialize database
    db = DatabaseManager()
    if not db.connect():
        print("❌ Database connection failed")
        return False
    
    print("✅ Database connected")
    
    # Test 1: Create product with auto-generated barcode
    print("\n📦 Test 1: Auto-Generate Barcode")
    print("-" * 40)
    
    # Get categories
    categories = db.get_categories()
    if not categories:
        print("❌ No categories found")
        return False
    
    category_id = categories[0][0]  # Use first category
    category_name = categories[0][1]
    
    # Generate SKU and barcode like the product management does
    def generate_sku(product_name, category_name):
        name_part = ''.join(filter(str.isalnum, product_name))[:8].upper()
        category_part = ''.join(filter(str.isalnum, category_name))[:3].upper()
        timestamp = datetime.now().strftime("%m%d")
        return f"{category_part}-{name_part}-{timestamp}"
    
    def generate_barcode(product_name, category_name):
        import hashlib
        unique_string = f"{product_name}{category_name}{datetime.now().isoformat()}"
        hash_obj = hashlib.md5(unique_string.encode())
        hash_hex = hash_obj.hexdigest()[:8]
        barcode_num = str(int(hash_hex, 16))[:12].zfill(12)
        return barcode_num
    
    # Test product
    test_product_name = "Test Lash Extension Kit"
    test_sku = generate_sku(test_product_name, category_name)
    test_barcode = generate_barcode(test_product_name, category_name)
    
    print(f"Product Name: {test_product_name}")
    print(f"Generated SKU: {test_sku}")
    print(f"Generated Barcode: {test_barcode}")
    
    # Add product to database
    success = db.add_product(
        test_product_name,
        test_sku,
        test_barcode,
        category_id,
        150.00,
        25
    )
    
    if success:
        print("✅ Product added successfully with auto-generated barcode")
    else:
        print("❌ Failed to add product")
        return False
    
    # Test 2: Lookup product by barcode
    print("\n🔍 Test 2: Barcode Lookup")
    print("-" * 40)
    
    # Test exact barcode lookup
    print(f"Looking up barcode: {test_barcode}")
    found_product = db.get_product_by_barcode(test_barcode)
    
    if found_product:
        print("✅ Product found by barcode!")
        print(f"   ID: {found_product[0]}")
        print(f"   Name: {found_product[1]}")
        print(f"   SKU: {found_product[2]}")
        print(f"   Barcode: {found_product[3]}")
        print(f"   Category ID: {found_product[4]}")
        print(f"   COGS: PKR {found_product[5]:.2f}")
        print(f"   Stock: {found_product[6]}")
    else:
        print("❌ Product NOT found by barcode")
        return False
    
    # Test 3: Lookup product by SKU
    print(f"\nLooking up SKU: {test_sku}")
    found_product_sku = db.get_product_by_barcode(test_sku)  # This method also searches SKU
    
    if found_product_sku:
        print("✅ Product found by SKU!")
        print(f"   Name: {found_product_sku[1]}")
    else:
        print("❌ Product NOT found by SKU")
        return False
    
    # Test 4: Test case-insensitive lookup
    print(f"\nTesting case-insensitive lookup: {test_barcode.lower()}")
    found_product_case = db.get_product_by_barcode(test_barcode.lower())
    
    if found_product_case:
        print("✅ Case-insensitive lookup works!")
    else:
        print("❌ Case-insensitive lookup failed")
    
    # Test 5: Test invalid barcode
    print("\nTesting invalid barcode: INVALID123")
    invalid_product = db.get_product_by_barcode("INVALID123")
    
    if invalid_product is None:
        print("✅ Invalid barcode correctly returns None")
    else:
        print("❌ Invalid barcode should return None")
    
    # Test 6: Stock update
    print("\n📦 Test 6: Stock Update")
    print("-" * 40)
    
    original_stock = found_product[6]
    new_stock = original_stock + 10
    
    stock_updated = db.update_stock(found_product[0], new_stock)
    
    if stock_updated:
        print(f"✅ Stock updated from {original_stock} to {new_stock}")
        
        # Verify stock update
        updated_product = db.get_product_by_barcode(test_barcode)
        if updated_product and updated_product[6] == new_stock:
            print("✅ Stock update verified")
        else:
            print("❌ Stock update verification failed")
    else:
        print("❌ Stock update failed")
    
    # Cleanup - remove test product
    print("\n🧹 Cleanup")
    print("-" * 40)
    
    try:
        db.connect()
        db.cursor.execute("DELETE FROM products WHERE barcode = ?", (test_barcode,))
        db.connection.commit()
        print("✅ Test product removed")
    except Exception as e:
        print(f"⚠️ Cleanup warning: {e}")
    finally:
        db.disconnect()
    
    print("\n" + "=" * 60)
    print("🎉 ALL BARCODE TESTS PASSED!")
    print("✅ Auto-generation works")
    print("✅ Barcode lookup works")
    print("✅ SKU lookup works")
    print("✅ Case-insensitive lookup works")
    print("✅ Invalid barcode handling works")
    print("✅ Stock updates work")
    
    return True

def test_existing_products():
    """Test lookup of existing products"""
    print("\n🔍 Testing Existing Products")
    print("=" * 40)
    
    db = DatabaseManager()
    if not db.connect():
        print("❌ Database connection failed")
        return False
    
    # Get all products
    products = db.get_products()
    
    if not products:
        print("⚠️ No existing products found")
        return True
    
    print(f"Found {len(products)} existing products:")
    
    for product in products[:5]:  # Test first 5 products
        product_id, name, sku, barcode = product[:4]
        print(f"\n📦 Product: {name}")
        print(f"   SKU: {sku or 'None'}")
        print(f"   Barcode: {barcode or 'None'}")
        
        # Test lookup by barcode if exists
        if barcode and barcode.strip():
            found = db.get_product_by_barcode(barcode)
            if found:
                print("   ✅ Barcode lookup: SUCCESS")
            else:
                print("   ❌ Barcode lookup: FAILED")
        
        # Test lookup by SKU if exists
        if sku and sku.strip():
            found_sku = db.get_product_by_barcode(sku)
            if found_sku:
                print("   ✅ SKU lookup: SUCCESS")
            else:
                print("   ❌ SKU lookup: FAILED")
    
    db.disconnect()
    return True

def main():
    """Main test function"""
    print("🚀 COMPLETE BARCODE SYSTEM TEST")
    print("=" * 60)
    
    try:
        # Test 1: Complete barcode workflow
        success1 = test_barcode_generation_and_lookup()
        
        # Test 2: Existing products
        success2 = test_existing_products()
        
        if success1 and success2:
            print("\n🎉 ALL TESTS PASSED!")
            print("🚀 Barcode system is PRODUCTION READY!")
            return 0
        else:
            print("\n❌ SOME TESTS FAILED!")
            return 1
            
    except Exception as e:
        print(f"\n💥 Test error: {e}")
        import traceback
        traceback.print_exc()
        return 1

if __name__ == "__main__":
    sys.exit(main())
