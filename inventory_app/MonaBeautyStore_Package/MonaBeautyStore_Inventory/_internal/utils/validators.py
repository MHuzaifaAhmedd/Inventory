"""
Validation Utilities for Inventory Management System
Handles data validation and business rule checks
"""

import re
from datetime import datetime

class Validators:
    """Collection of validation functions"""

    @staticmethod
    def validate_product_name(name):
        """Validate product name"""
        if not name or not name.strip():
            return False, "Product name is required"

        if len(name.strip()) < 2:
            return False, "Product name must be at least 2 characters long"

        if len(name.strip()) > 100:
            return False, "Product name must be less than 100 characters"

        return True, ""

    @staticmethod
    def validate_sku(sku):
        """Validate SKU format"""
        if not sku or not sku.strip():
            return True, ""  # SKU is optional

        # Allow alphanumeric characters, hyphens, and underscores
        if not re.match(r'^[A-Za-z0-9_-]+$', sku.strip()):
            return False, "SKU can only contain letters, numbers, hyphens, and underscores"

        if len(sku.strip()) > 50:
            return False, "SKU must be less than 50 characters"

        return True, ""

    @staticmethod
    def validate_barcode(barcode):
        """Validate barcode format"""
        if not barcode or not barcode.strip():
            return True, ""  # Barcode is optional

        # Allow various barcode formats (numeric, alphanumeric)
        if not re.match(r'^[A-Za-z0-9]+$', barcode.strip()):
            return False, "Barcode can only contain letters and numbers"

        if len(barcode.strip()) < 8 or len(barcode.strip()) > 20:
            return False, "Barcode must be between 8 and 20 characters"

        return True, ""

    @staticmethod
    def validate_cogs(cogs_text):
        """Validate Cost of Goods Sold"""
        if not cogs_text or not cogs_text.strip():
            return True, ""  # COGS is optional

        try:
            cogs = float(cogs_text.strip())
            if cogs < 0:
                return False, "COGS cannot be negative"
            if cogs > 100000:
                return False, "COGS seems unreasonably high"
            return True, ""
        except ValueError:
            return False, "COGS must be a valid number"

    @staticmethod
    def validate_stock_quantity(quantity_text):
        """Validate stock quantity"""
        if not quantity_text or not quantity_text.strip():
            return False, "Stock quantity is required"

        try:
            quantity = int(quantity_text.strip())
            if quantity < 0:
                return False, "Stock quantity cannot be negative"
            if quantity > 100000:
                return False, "Stock quantity seems unreasonably high"
            return True, ""
        except ValueError:
            return False, "Stock quantity must be a whole number"

    @staticmethod
    def validate_selling_price(price_text):
        """Validate selling price"""
        if not price_text or not price_text.strip():
            return False, "Selling price is required"

        try:
            price = float(price_text.strip())
            if price <= 0:
                return False, "Selling price must be greater than zero"
            if price > 100000:
                return False, "Selling price seems unreasonably high"
            return True, ""
        except ValueError:
            return False, "Selling price must be a valid number"

    @staticmethod
    def validate_date(date_text):
        """Validate date format"""
        if not date_text or not date_text.strip():
            return False, "Date is required"

        try:
            datetime.strptime(date_text.strip(), "%Y-%m-%d")
            return True, ""
        except ValueError:
            return False, "Date must be in YYYY-MM-DD format"

    @staticmethod
    def validate_sale_quantity(quantity_text, available_stock):
        """Validate sale quantity against available stock"""
        valid, message = Validators.validate_stock_quantity(quantity_text)
        if not valid:
            return False, message

        try:
            quantity = int(quantity_text.strip())
            if quantity > available_stock:
                return False, f"Insufficient stock. Available: {available_stock}, Requested: {quantity}"
            return True, ""
        except ValueError:
            return False, "Quantity must be a whole number"

    @staticmethod
    def check_duplicate_sku(db_manager, sku, exclude_product_id=None):
        """Check for duplicate SKU"""
        if not sku or not sku.strip():
            return False, ""

        try:
            # This would require a database query to check for duplicates
            # For now, return True (no duplicate)
            return False, ""  # No duplicate found
        except Exception:
            return False, ""

    @staticmethod
    def check_duplicate_barcode(db_manager, barcode, exclude_product_id=None):
        """Check for duplicate barcode"""
        if not barcode or not barcode.strip():
            return False, ""

        try:
            # This would require a database query to check for duplicates
            # For now, return True (no duplicate)
            return False, ""  # No duplicate found
        except Exception:
            return False, ""

class BusinessRules:
    """Business rule validation"""

    @staticmethod
    def validate_product_creation(db_manager, product_data):
        """Validate complete product data for creation"""
        errors = []

        # Validate individual fields
        valid, message = Validators.validate_product_name(product_data.get('name', ''))
        if not valid:
            errors.append(message)

        valid, message = Validators.validate_sku(product_data.get('sku', ''))
        if not valid:
            errors.append(message)

        valid, message = Validators.validate_barcode(product_data.get('barcode', ''))
        if not valid:
            errors.append(message)

        valid, message = Validators.validate_cogs(product_data.get('cogs', ''))
        if not valid:
            errors.append(message)

        valid, message = Validators.validate_stock_quantity(str(product_data.get('stock', 0)))
        if not valid:
            errors.append(message)

        # Check for duplicates
        if product_data.get('sku'):
            duplicate, message = Validators.check_duplicate_sku(db_manager, product_data['sku'])
            if duplicate:
                errors.append(f"SKU already exists: {message}")

        if product_data.get('barcode'):
            duplicate, message = Validators.check_duplicate_barcode(db_manager, product_data['barcode'])
            if duplicate:
                errors.append(f"Barcode already exists: {message}")

        return len(errors) == 0, errors

    @staticmethod
    def validate_sale_creation(db_manager, sale_data):
        """Validate complete sale data for creation"""
        errors = []

        # Validate quantity
        valid, message = Validators.validate_stock_quantity(str(sale_data.get('quantity', 0)))
        if not valid:
            errors.append(message)

        # Validate price
        valid, message = Validators.validate_selling_price(str(sale_data.get('price', 0)))
        if not valid:
            errors.append(message)

        # Validate date
        valid, message = Validators.validate_date(sale_data.get('date', ''))
        if not valid:
            errors.append(message)

        # Check stock availability
        if sale_data.get('product_id'):
            try:
                # Get current stock - this would need to be implemented
                available_stock = 100  # Placeholder
                valid, message = Validators.validate_sale_quantity(
                    str(sale_data.get('quantity', 0)), available_stock)
                if not valid:
                    errors.append(message)
            except Exception as e:
                errors.append(f"Error checking stock: {e}")

        return len(errors) == 0, errors

class Alerts:
    """Alert and notification system"""

    @staticmethod
    def check_low_stock_products(db_manager, threshold=10):
        """Check for products with low stock"""
        try:
            products = db_manager.get_products()
            low_stock_products = []

            for product in products:
                current_stock = product[6]  # Current stock
                if current_stock <= threshold:
                    low_stock_products.append({
                        'id': product[0],
                        'name': product[1],
                        'stock': current_stock,
                        'threshold': threshold
                    })

            return low_stock_products
        except Exception:
            return []

    @staticmethod
    def check_out_of_stock_products(db_manager):
        """Check for products that are out of stock"""
        try:
            products = db_manager.get_products()
            out_of_stock = []

            for product in products:
                current_stock = product[6]  # Current stock
                if current_stock == 0:
                    out_of_stock.append({
                        'id': product[0],
                        'name': product[1],
                        'category': product[4]
                    })

            return out_of_stock
        except Exception:
            return []

    @staticmethod
    def generate_inventory_alerts(db_manager):
        """Generate comprehensive inventory alerts"""
        alerts = []

        # Low stock alerts
        low_stock = Alerts.check_low_stock_products(db_manager)
        for product in low_stock:
            alerts.append({
                'type': 'warning',
                'category': 'Low Stock',
                'message': f"'{product['name']}' has only {product['stock']} units remaining",
                'product_id': product['id']
            })

        # Out of stock alerts
        out_of_stock = Alerts.check_out_of_stock_products(db_manager)
        for product in out_of_stock:
            alerts.append({
                'type': 'error',
                'category': 'Out of Stock',
                'message': f"'{product['name']}' is out of stock",
                'product_id': product['id']
            })

        return alerts


