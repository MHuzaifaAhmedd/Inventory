#!/usr/bin/env python3
"""
Test Manual Barcode Lookup
"""

from database.db_manager import DatabaseManager

def test_manual_barcode():
    """Test manual barcode lookup functionality"""
    print("🔍 Testing Manual Barcode Lookup")
    print("=" * 40)

    db = DatabaseManager()
    if not db.connect():
        print("❌ Database connection failed")
        return

    # Test with some sample barcodes
    test_barcodes = ["TEST001", "SAMPLE123", "PROD456"]

    for barcode in test_barcodes:
        print(f"\n🔎 Looking up barcode: {barcode}")
        product = db.get_product_by_barcode(barcode)

        if product:
            print(f"✅ Found: {product[1]} (ID: {product[0]}, Stock: {product[6]})")
        else:
            print(f"❌ Not found: {barcode}")

    # Test with SKU lookup (since barcodes might be empty)
    print("\n📦 Testing SKU lookup:")
    products = db.get_products()
    if products:
        for product in products[:3]:  # Test first 3 products
            sku = product[2] or f"SKU{product[0]}"  # Use SKU or generate one
            print(f"🔎 Looking up SKU: {sku}")
            # In real app, this would be done by SKU field
            found_product = next((p for p in products if p[2] == sku), None)
            if found_product:
                print(f"✅ Found: {found_product[1]} (ID: {found_product[0]})")
            else:
                print(f"❌ Not found: {sku}")

    db.disconnect()

    print("\n🎉 Manual barcode lookup test completed!")
    print("💡 In the app, you can:")
    print("   • Type any barcode/SKU in the manual entry field")
    print("   • Click 'Lookup' to find the product")
    print("   • Add stock adjustments for found products")

if __name__ == "__main__":
    test_manual_barcode()
