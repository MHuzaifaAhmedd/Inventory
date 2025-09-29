#!/usr/bin/env python3
"""
Test script to verify sales functionality
"""

from database.db_manager import DatabaseManager

def test_database():
    """Test database connection and product loading"""
    print("🔧 Testing Database Connection...")

    db = DatabaseManager()

    if not db.connect():
        print("❌ Failed to connect to database")
        return False

    # Test product loading
    try:
        products = db.get_products()
        print(f"✅ Found {len(products)} products in database:")

        for i, product in enumerate(products, 1):
            print(f"  {i}. {product[1]} (ID: {product[0]}, Stock: {product[6]}, COGS: PKR {product[5]})")

        if len(products) == 0:
            print("❌ No products found! This is the issue.")
            return False
        else:
            print("✅ Products loaded successfully")
            return True

    except Exception as e:
        print(f"❌ Error loading products: {e}")
        return False
    finally:
        db.disconnect()

def test_sale_simulation():
    """Test a sale simulation"""
    print("\n💰 Testing Sale Simulation...")

    db = DatabaseManager()
    if not db.connect():
        print("❌ Cannot connect to database")
        return

    try:
        # Get first product
        products = db.get_products()
        if not products:
            print("❌ No products available for sale")
            return

        product = products[0]  # Use first product
        print(f"📦 Testing sale of: {product[1]}")
        print(f"   Stock before: {product[6]}")
        print(f"   COGS: PKR {product[5]}")

        # Simulate a sale
        quantity = 1
        selling_price = product[5] * 1.5  # 50% markup

        success = db.add_sale(product[0], quantity, selling_price, "2024-12-19")

        if success:
            print("✅ Sale added successfully!")
            print(f"   Revenue: PKR {selling_price:.2f}")
            print(f"   Profit: PKR {selling_price - product[5]:.2f}")

            # Check updated stock
            updated_products = db.get_products()
            updated_product = next(p for p in updated_products if p[0] == product[0])
            print(f"   Stock after: {updated_product[6]}")
        else:
            print("❌ Sale failed!")

    except Exception as e:
        print(f"❌ Sale simulation error: {e}")
    finally:
        db.disconnect()

def main():
    """Main test function"""
    print("=" * 50)
    print("MONA BEAUTY STORE - SALES TEST")
    print("=" * 50)

    # Test database
    if test_database():
        test_sale_simulation()
    else:
        print("\n🔧 Please run: python fix_database.py")

    print("\n" + "=" * 50)

if __name__ == "__main__":
    main()


