#!/usr/bin/env python3
"""
Fresh Setup Script for Mona Beauty Store Inventory
Resets database and provides quick start guide
"""

import os
from database.db_manager import DatabaseManager

def setup_fresh_database():
    """Set up a fresh database for the user"""
    print("🎨 MONA BEAUTY STORE - FRESH SETUP")
    print("=" * 50)

    # Reset database
    print("🔄 Resetting database...")
    if os.path.exists("inventory.db"):
        os.remove("inventory.db")
        print("✅ Old database removed")

    # Initialize fresh database
    db = DatabaseManager()
    if db.initialize_database():
        print("✅ Fresh database created")

        # Add sample categories
        categories = [
            ("Lash o'clock", "Lash products and accessories"),
            ("Nail o'clock", "Nail products and accessories"),
            ("Sponge o'clock", "Sponge products and accessories"),
            ("Set N Forget", "Setting powders and fixing products")
        ]

        print("📂 Adding categories...")
        for name, desc in categories:
            if db.add_category(name, desc):
                print(f"  ✅ {name}")
            else:
                print(f"  ❌ Failed: {name}")

        db.disconnect()
        print("\n🎉 Setup complete!")
        print("\n🚀 Next steps:")
        print("1. Run: python run.py")
        print("2. Go to 'Products' tab")
        print("3. Click '🔥 Reset DB' button (password: admin123)")
        print("4. Or start adding your own products!")
        print("\n💡 Pro tips:")
        print("• Use the 'Reset DB' button in Products tab to start fresh")
        print("• Add your products one by one")
        print("• Test sales after adding products")
        print("• Check the dashboard for analytics")

    else:
        print("❌ Failed to initialize database")

if __name__ == "__main__":
    setup_fresh_database()


