#!/usr/bin/env python3
"""
Sample Data Generator for Inventory Management System
Creates sample products, categories, and sales data for testing
"""

from database.db_manager import DatabaseManager
from datetime import datetime, timedelta
import random

class SampleDataGenerator:
    """Generates sample data for testing"""

    def __init__(self):
        """Initialize sample data generator"""
        self.db_manager = DatabaseManager()

    def generate_sample_data(self):
        """Generate comprehensive sample data"""
        print("Generating sample data...")

        # Generate sample products
        self.generate_sample_products()

        # Generate sample sales
        self.generate_sample_sales()

        print("Sample data generation completed!")

    def generate_sample_products(self):
        """Generate sample products for each category"""

        # Lash o'clock products
        lash_products = [
            ("Lash Extension Kit Basic", "LEK-BASIC", "LEK001", 150.00, 25),
            ("Lash Extension Kit Premium", "LEK-PREMIUM", "LEK002", 250.00, 15),
            ("Lash Adhesive 5ml", "LASH-ADH-5ML", "LA001", 45.00, 50),
            ("Lash Primer 10ml", "LASH-PRIMER", "LP001", 35.00, 40),
            ("Lash Remover 100ml", "LASH-REMOVER", "LR001", 65.00, 30),
            ("Lash Brush Set", "LASH-BRUSH", "LB001", 25.00, 60),
            ("Lash Tweezers Set", "LASH-TWEEZERS", "LT001", 55.00, 35),
            ("Lash Mascara 8ml", "LASH-MASCARA", "LM001", 85.00, 45),
        ]

        # Nail o'clock products
        nail_products = [
            ("Nail Polish Set 12 Colors", "NP-SET-12", "NP001", 120.00, 20),
            ("Nail Art Kit Professional", "NAK-PRO", "NAK001", 180.00, 12),
            ("Nail Extension Kit Acrylic", "NEK-ACRYLIC", "NE001", 200.00, 18),
            ("Nail Gel Set 8 Colors", "NG-SET-8", "NG001", 95.00, 28),
            ("Nail Cutter Professional", "NC-PRO", "NC001", 75.00, 25),
            ("Nail File Set 5pcs", "NF-SET-5", "NF001", 30.00, 80),
            ("Nail Buffer Block", "NB-BLOCK", "NB001", 20.00, 90),
            ("Nail Primer 15ml", "NP-PRIMER", "NP002", 40.00, 55),
        ]

        # Sponge o'clock products
        sponge_products = [
            ("Beauty Sponge Set 6pcs", "BS-SET-6", "BS001", 45.00, 40),
            ("Blending Sponge Premium", "BLEND-PREM", "BP001", 25.00, 70),
            ("Sponge Blender Duo", "SB-DUO", "SB001", 35.00, 50),
            ("Foundation Sponge 4pcs", "FS-4PCS", "FS001", 55.00, 35),
            ("Sponge Puff Set", "SP-PUFF", "SP001", 30.00, 65),
            ("Makeup Sponge Variety", "MS-VAR", "MS001", 40.00, 45),
        ]

        # Set N Forget products
        set_n_forget_products = [
            ("Setting Powder 15g", "SP-15G", "SP002", 65.00, 35),
            ("Setting Spray 100ml", "SS-100ML", "SS001", 75.00, 40),
            ("Fixing Mist 120ml", "FM-120ML", "FM001", 85.00, 30),
            ("Makeup Setting Kit", "MS-KIT", "MS002", 150.00, 20),
            ("Powder Puff Set", "PP-SET", "PP001", 45.00, 50),
            ("Setting Brush", "SB-BRUSH", "SB002", 35.00, 60),
        ]

        # Get category IDs
        categories = self.db_manager.get_categories()
        category_map = {cat[1]: cat[0] for cat in categories}

        # Add products for each category
        product_lists = [
            (lash_products, "Lash o'clock"),
            (nail_products, "Nail o'clock"),
            (sponge_products, "Sponge o'clock"),
            (set_n_forget_products, "Set N Forget")
        ]

        for products, category_name in product_lists:
            category_id = category_map.get(category_name)
            if category_id:
                for product in products:
                    name, sku, barcode, cogs, stock = product
                    self.db_manager.add_product(name, sku, barcode, category_id, cogs, stock)

        print(f"Added {len(lash_products) + len(nail_products) + len(sponge_products) + len(set_n_forget_products)} sample products")

    def generate_sample_sales(self):
        """Generate sample sales data"""

        # Get all products
        products = self.db_manager.get_products()

        if not products:
            print("No products found. Please generate products first.")
            return

        # Generate sales for the last 90 days
        end_date = datetime.now()
        start_date = end_date - timedelta(days=90)

        total_sales = 0

        for i in range(90):  # 90 days
            current_date = start_date + timedelta(days=i)

            # Generate 3-8 sales per day (weekends have fewer sales)
            is_weekend = current_date.weekday() >= 5
            sales_per_day = random.randint(2, 5) if is_weekend else random.randint(4, 8)

            for _ in range(sales_per_day):
                # Select random product
                product = random.choice(products)

                # Generate realistic sales data
                max_quantity = min(product[6], 10)  # Don't sell more than available or 10 units
                if max_quantity > 0:
                    quantity = random.randint(1, max_quantity)

                    # Add some markup to COGS for selling price (20-50% profit margin)
                    profit_margin = random.uniform(0.2, 0.5)
                    selling_price = product[5] * (1 + profit_margin)

                    # Occasionally give discounts
                    if random.random() < 0.1:  # 10% chance
                        discount = random.uniform(0.05, 0.15)
                        selling_price *= (1 - discount)

                    # Round to nearest rupee
                    selling_price = round(selling_price)

                    try:
                        self.db_manager.add_sale(
                            product[0],  # Product ID
                            quantity,
                            selling_price,
                            current_date.strftime("%Y-%m-%d")
                        )
                        total_sales += 1
                    except Exception as e:
                        print(f"Error adding sale: {e}")

        print(f"Added {total_sales} sample sales transactions")

def main():
    """Main function to generate sample data"""
    print("Mona Beauty Store - Sample Data Generator")
    print("=" * 50)

    generator = SampleDataGenerator()

    # Initialize database
    generator.db_manager.initialize_database()

    # Generate sample data
    generator.generate_sample_data()

    print("\nSample data generation completed successfully!")
    print("You can now run the application to see the data.")

if __name__ == "__main__":
    main()


