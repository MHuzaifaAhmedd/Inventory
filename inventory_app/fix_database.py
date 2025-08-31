#!/usr/bin/env python3
"""
Database Fix Script for Inventory Management System
Fixes database locking issues and reinitializes if needed
"""

import os
import sqlite3
from pathlib import Path

def fix_database():
    """Fix database issues and reinitialize if needed"""
    db_path = Path("inventory.db")
    journal_path = Path("inventory.db-journal")

    print("🔧 Fixing database issues...")

    # Remove journal file if it exists
    if journal_path.exists():
        print("📄 Removing journal file...")
        journal_path.unlink()
        print("✅ Journal file removed")

    # Check if database exists and is accessible
    if db_path.exists():
        try:
            conn = sqlite3.connect(str(db_path))
            cursor = conn.cursor()

            # Test basic query
            cursor.execute("SELECT name FROM sqlite_master WHERE type='table'")
            tables = cursor.fetchall()
            print(f"📊 Database has {len(tables)} tables: {[t[0] for t in tables]}")

            conn.close()
            print("✅ Database is accessible")

        except sqlite3.Error as e:
            print(f"❌ Database error: {e}")
            print("🔄 Reinitializing database...")

            # Remove corrupted database
            db_path.unlink()

            # Create new database
            create_new_database()
    else:
        print("📄 Database doesn't exist, creating new one...")
        create_new_database()

def create_new_database():
    """Create a new database with proper schema"""
    from database.db_manager import DatabaseManager

    print("🏗️ Creating new database...")

    db_manager = DatabaseManager()

    if db_manager.initialize_database():
        print("✅ Database created successfully")

        # Add some sample categories and products
        print("📦 Adding sample data...")

        # Add categories
        categories = [
            ("Lash o'clock", "Lash products and accessories"),
            ("Nail o'clock", "Nail products and accessories"),
            ("Sponge o'clock", "Sponge products and accessories"),
            ("Set N Forget", "Set and forget beauty products")
        ]

        for name, desc in categories:
            if db_manager.add_category(name, desc):
                print(f"✅ Added category: {name}")

        # Add sample products
        sample_products = [
            ("Lash Extension Kit Basic", "LEK-BASIC", "LEK001", 1, 150.00, 25),
            ("Nail Polish Set 12 Colors", "NP-SET-12", "NP001", 2, 120.00, 20),
            ("Beauty Sponge Set 6pcs", "BS-SET-6", "BS001", 3, 45.00, 40),
            ("Setting Powder 15g", "SP-15G", "SP002", 4, 65.00, 35),
        ]

        for name, sku, barcode, cat_id, cogs, stock in sample_products:
            if db_manager.add_product(name, sku, barcode, cat_id, cogs, stock):
                print(f"✅ Added product: {name}")

        print("🎉 Sample data added successfully!")

    else:
        print("❌ Failed to create database")

def main():
    """Main function"""
    print("=" * 50)
    print("MONA BEAUTY STORE - DATABASE FIX TOOL")
    print("=" * 50)

    try:
        fix_database()
        print("\n✅ Database fix completed!")
        print("You can now run the application normally.")
        print("Use: python run.py")

    except Exception as e:
        print(f"❌ Error fixing database: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    main()


