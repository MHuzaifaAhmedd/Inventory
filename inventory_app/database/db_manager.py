"""
Database Manager for Inventory Management System
Handles SQLite database operations
"""

import sqlite3
import os
from datetime import datetime
from pathlib import Path

class DatabaseManager:
    """Manages SQLite database operations"""

    def __init__(self, db_path=None):
        """Initialize database manager"""
        if db_path is None:
            # Default to current directory
            self.db_path = Path(__file__).parent.parent / "inventory.db"
        else:
            self.db_path = Path(db_path)

        self.connection = None
        self.cursor = None

    def connect(self):
        """Connect to database"""
        try:
            self.connection = sqlite3.connect(str(self.db_path))
            self.cursor = self.connection.cursor()
            return True
        except Exception as e:
            print(f"Database connection error: {e}")
            return False

    def disconnect(self):
        """Close database connection"""
        if self.connection:
            self.connection.close()

    def initialize_database(self):
        """Create database tables if they don't exist"""
        if not self.connect():
            return False

        try:
            # Create categories table
            self.cursor.execute('''
                CREATE TABLE IF NOT EXISTS categories (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    name TEXT UNIQUE NOT NULL,
                    description TEXT,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                )
            ''')

            # Create products table
            self.cursor.execute('''
                CREATE TABLE IF NOT EXISTS products (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    name TEXT NOT NULL,
                    sku TEXT UNIQUE,
                    barcode TEXT UNIQUE,
                    category_id INTEGER,
                    cogs REAL NOT NULL DEFAULT 0,
                    initial_stock INTEGER NOT NULL DEFAULT 0,
                    current_stock INTEGER NOT NULL DEFAULT 0,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    FOREIGN KEY (category_id) REFERENCES categories (id)
                )
            ''')

            # Create sales table
            self.cursor.execute('''
                CREATE TABLE IF NOT EXISTS sales (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    product_id INTEGER NOT NULL,
                    quantity INTEGER NOT NULL,
                    selling_price REAL NOT NULL,
                    revenue REAL NOT NULL,
                    profit REAL NOT NULL,
                    sale_date DATE NOT NULL,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    FOREIGN KEY (product_id) REFERENCES products (id)
                )
            ''')

            # Insert default categories
            default_categories = [
                ("Lash o'clock", "Lash products and accessories"),
                ("Nail o'clock", "Nail products and accessories"),
                ("Sponge o'clock", "Sponge products and accessories"),
                ("Set N Forget", "Set and forget beauty products")
            ]

            for category_name, description in default_categories:
                self.cursor.execute('''
                    INSERT OR IGNORE INTO categories (name, description)
                    VALUES (?, ?)
                ''', (category_name, description))

            self.connection.commit()

            # Create indexes for better performance
            self.cursor.execute('CREATE INDEX IF NOT EXISTS idx_products_category ON products(category_id)')
            self.cursor.execute('CREATE INDEX IF NOT EXISTS idx_products_sku ON products(sku)')
            self.cursor.execute('CREATE INDEX IF NOT EXISTS idx_products_barcode ON products(barcode)')
            self.cursor.execute('CREATE INDEX IF NOT EXISTS idx_sales_product ON sales(product_id)')
            self.cursor.execute('CREATE INDEX IF NOT EXISTS idx_sales_date ON sales(sale_date)')

            self.connection.commit()
            return True

        except Exception as e:
            print(f"Database initialization error: {e}")
            return False
        finally:
            self.disconnect()

    # Category operations
    def get_categories(self):
        """Get all categories"""
        if not self.connect():
            return []

        try:
            self.cursor.execute('SELECT id, name, description FROM categories ORDER BY name')
            return self.cursor.fetchall()
        except Exception as e:
            print(f"Error getting categories: {e}")
            return []
        finally:
            self.disconnect()

    def add_category(self, name, description=""):
        """Add new category"""
        if not self.connect():
            return False

        try:
            self.cursor.execute('''
                INSERT INTO categories (name, description)
                VALUES (?, ?)
            ''', (name, description))
            self.connection.commit()
            return True
        except sqlite3.IntegrityError:
            return False  # Category name already exists
        except Exception as e:
            print(f"Error adding category: {e}")
            return False
        finally:
            self.disconnect()

    # Product operations
    def add_product(self, name, sku, barcode, category_id, cogs, initial_stock):
        """Add new product"""
        if not self.connect():
            return False

        try:
            current_time = datetime.now().isoformat()
            self.cursor.execute('''
                INSERT INTO products (name, sku, barcode, category_id, cogs, initial_stock, current_stock, updated_at)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?)
            ''', (name, sku, barcode, category_id, cogs, initial_stock, initial_stock, current_time))
            self.connection.commit()
            return True
        except sqlite3.IntegrityError:
            return False  # SKU or barcode already exists
        except Exception as e:
            print(f"Error adding product: {e}")
            return False
        finally:
            self.disconnect()

    def update_product_barcode(self, product_id, barcode):
        """Update product barcode"""
        if not self.connect():
            return False

        try:
            current_time = datetime.now().isoformat()
            self.cursor.execute('''
                UPDATE products 
                SET barcode = ?, updated_at = ?
                WHERE id = ?
            ''', (barcode, current_time, product_id))
            self.connection.commit()
            return self.cursor.rowcount > 0
        except Exception as e:
            print(f"Error updating product barcode: {e}")
            return False
        finally:
            self.disconnect()

    def update_product(self, product_id, name, sku, barcode, category_id, cogs):
        """Update product information"""
        if not self.connect():
            return False

        try:
            current_time = datetime.now().isoformat()
            self.cursor.execute('''
                UPDATE products
                SET name=?, sku=?, barcode=?, category_id=?, cogs=?, updated_at=?
                WHERE id=?
            ''', (name, sku, barcode, category_id, cogs, current_time, product_id))
            self.connection.commit()
            return True
        except sqlite3.IntegrityError:
            return False  # SKU or barcode already exists
        except Exception as e:
            print(f"Error updating product: {e}")
            return False
        finally:
            self.disconnect()

    def delete_product(self, product_id):
        """Delete product"""
        if not self.connect():
            return False

        try:
            # Check if product has sales records
            self.cursor.execute('SELECT COUNT(*) FROM sales WHERE product_id=?', (product_id,))
            sales_count = self.cursor.fetchone()[0]

            if sales_count > 0:
                return False  # Cannot delete product with sales records

            self.cursor.execute('DELETE FROM products WHERE id=?', (product_id,))
            self.connection.commit()
            return True
        except Exception as e:
            print(f"Error deleting product: {e}")
            return False
        finally:
            self.disconnect()

    def get_products(self, category_id=None):
        """Get all products or products by category"""
        if not self.connect():
            return []

        try:
            if category_id:
                self.cursor.execute('''
                    SELECT p.id, p.name, p.sku, p.barcode, c.name, p.cogs, p.current_stock
                    FROM products p
                    JOIN categories c ON p.category_id = c.id
                    WHERE p.category_id = ?
                    ORDER BY p.name
                ''', (category_id,))
            else:
                self.cursor.execute('''
                    SELECT p.id, p.name, p.sku, p.barcode, c.name, p.cogs, p.current_stock
                    FROM products p
                    JOIN categories c ON p.category_id = c.id
                    ORDER BY p.name
                ''')

            return self.cursor.fetchall()
        except Exception as e:
            print(f"Error getting products: {e}")
            return []
        finally:
            self.disconnect()

    def get_product_by_barcode(self, barcode):
        """Get product by barcode"""
        if not self.connect():
            return None

        try:
            # First try exact barcode match
            self.cursor.execute('''
                SELECT p.id, p.name, p.sku, p.barcode, p.category_id, p.cogs, p.current_stock
                FROM products p
                WHERE p.barcode = ? OR p.sku = ?
            ''', (barcode, barcode))

            result = self.cursor.fetchone()
            
            if result:
                print(f"Found product by barcode: {result}")
                return result
            
            # If not found, try case-insensitive search
            self.cursor.execute('''
                SELECT p.id, p.name, p.sku, p.barcode, p.category_id, p.cogs, p.current_stock
                FROM products p
                WHERE UPPER(p.barcode) = UPPER(?) OR UPPER(p.sku) = UPPER(?)
            ''', (barcode, barcode))

            result = self.cursor.fetchone()
            if result:
                print(f"Found product by case-insensitive search: {result}")
            else:
                print(f"No product found for barcode: {barcode}")
                
            return result
        except Exception as e:
            print(f"Error getting product by barcode: {e}")
            return None
        finally:
            self.disconnect()

    def update_stock(self, product_id, new_stock):
        """Update product stock to new value"""
        if not self.connect():
            return False

        try:
            current_time = datetime.now().isoformat()
            self.cursor.execute('''
                UPDATE products 
                SET current_stock = ?, updated_at = ?
                WHERE id = ?
            ''', (new_stock, current_time, product_id))
            self.connection.commit()
            return self.cursor.rowcount > 0
        except Exception as e:
            print(f"Error updating stock: {e}")
            return False
        finally:
            self.disconnect()

    def update_stock_change(self, product_id, quantity_change, operation="stock_in"):
        """Update product stock (positive for stock_in, negative for stock_out/sale)"""
        if not self.connect():
            return False

        try:
            # Start transaction
            self.connection.execute('BEGIN EXCLUSIVE')

            if operation == "stock_out" and quantity_change > 0:
                quantity_change = -quantity_change

            # Get current stock first
            self.cursor.execute('SELECT current_stock FROM products WHERE id=?', (product_id,))
            result = self.cursor.fetchone()
            if not result:
                print(f"Product with ID {product_id} not found")
                self.connection.rollback()
                return False

            current_stock = result[0]
            new_stock = current_stock + quantity_change

            # Ensure stock doesn't go negative
            if new_stock < 0:
                print(f"Insufficient stock for product {product_id}. Current: {current_stock}, Requested change: {quantity_change}")
                self.connection.rollback()
                return False

            self.cursor.execute('''
                UPDATE products
                SET current_stock = ?, updated_at = ?
                WHERE id = ?
            ''', (new_stock, datetime.now().isoformat(), product_id))

            self.connection.commit()
            return True
        except Exception as e:
            print(f"Error updating stock: {e}")
            try:
                self.connection.rollback()
            except:
                pass
            return False
        finally:
            try:
                self.disconnect()
            except:
                pass

    # Sales operations
    def add_sale(self, product_id, quantity, selling_price, sale_date):
        """Add new sale record"""
        if not self.connect():
            print("Failed to connect to database")
            return False

        try:
            # Start transaction
            self.connection.execute('BEGIN EXCLUSIVE')

            # Get product COGS
            self.cursor.execute('SELECT cogs, current_stock FROM products WHERE id=?', (product_id,))
            result = self.cursor.fetchone()
            if not result:
                print(f"Product with ID {product_id} not found")
                self.connection.rollback()
                return False

            cogs, current_stock = result

            # Check if enough stock is available
            if current_stock < quantity:
                print(f"Insufficient stock. Available: {current_stock}, Requested: {quantity}")
                self.connection.rollback()
                return False

            revenue = quantity * selling_price
            profit = quantity * (selling_price - cogs)

            # Insert sale record
            self.cursor.execute('''
                INSERT INTO sales (product_id, quantity, selling_price, revenue, profit, sale_date)
                VALUES (?, ?, ?, ?, ?, ?)
            ''', (product_id, quantity, selling_price, revenue, profit, sale_date))

            # Update stock
            new_stock = current_stock - quantity
            self.cursor.execute('''
                UPDATE products SET current_stock = ?, updated_at = ?
                WHERE id = ?
            ''', (new_stock, datetime.now().isoformat(), product_id))

            # Commit transaction
            self.connection.commit()
            print(f"Successfully added sale: {quantity} x {selling_price} = ₹{revenue}")
            return True

        except Exception as e:
            print(f"Error adding sale: {e}")
            try:
                self.connection.rollback()
            except:
                pass
            return False
        finally:
            try:
                self.disconnect()
            except:
                pass

    def get_sales(self, start_date=None, end_date=None, category_id=None):
        """Get sales records with optional filters"""
        if not self.connect():
            return []

        try:
            query = '''
                SELECT s.id, p.name, s.quantity, s.selling_price, s.revenue, s.profit, s.sale_date, c.name
                FROM sales s
                JOIN products p ON s.product_id = p.id
                JOIN categories c ON p.category_id = c.id
            '''

            conditions = []
            params = []

            if start_date and end_date:
                conditions.append("s.sale_date BETWEEN ? AND ?")
                params.extend([start_date, end_date])
            elif start_date:
                conditions.append("s.sale_date >= ?")
                params.append(start_date)
            elif end_date:
                conditions.append("s.sale_date <= ?")
                params.append(end_date)

            if category_id:
                conditions.append("p.category_id = ?")
                params.append(category_id)

            if conditions:
                query += " WHERE " + " AND ".join(conditions)

            query += " ORDER BY s.sale_date DESC"

            self.cursor.execute(query, params)
            return self.cursor.fetchall()
        except Exception as e:
            print(f"Error getting sales: {e}")
            return []
        finally:
            self.disconnect()

    def delete_sale(self, sale_id):
        """Delete sale record and restore stock"""
        if not self.connect():
            return False

        try:
            # Get sale details
            self.cursor.execute('SELECT product_id, quantity FROM sales WHERE id=?', (sale_id,))
            result = self.cursor.fetchone()
            if not result:
                return False

            product_id, quantity = result

            # Delete sale
            self.cursor.execute('DELETE FROM sales WHERE id=?', (sale_id,))

            # Restore stock
            self.update_stock(product_id, quantity, "stock_in")

            self.connection.commit()
            return True
        except Exception as e:
            print(f"Error deleting sale: {e}")
            return False
        finally:
            self.disconnect()

    # Analytics functions
    def get_dashboard_stats(self):
        """Get dashboard statistics"""
        if not self.connect():
            return {}

        try:
            stats = {}

            # Total products
            self.cursor.execute('SELECT COUNT(*) FROM products')
            stats['total_products'] = self.cursor.fetchone()[0]

            # Total stock
            self.cursor.execute('SELECT SUM(current_stock) FROM products')
            result = self.cursor.fetchone()[0]
            stats['total_stock'] = result if result else 0

            # Total revenue
            self.cursor.execute('SELECT SUM(revenue) FROM sales')
            result = self.cursor.fetchone()[0]
            stats['total_revenue'] = result if result else 0.0

            # Total profit
            self.cursor.execute('SELECT SUM(profit) FROM sales')
            result = self.cursor.fetchone()[0]
            stats['total_profit'] = result if result else 0.0

            return stats
        except Exception as e:
            print(f"Error getting dashboard stats: {e}")
            return {}
        finally:
            self.disconnect()

    def get_top_selling_products(self, limit=5):
        """Get top selling products"""
        if not self.connect():
            return []

        try:
            self.cursor.execute('''
                SELECT p.name, SUM(s.quantity) as total_quantity, SUM(s.revenue) as total_revenue
                FROM sales s
                JOIN products p ON s.product_id = p.id
                GROUP BY p.id, p.name
                ORDER BY total_quantity DESC
                LIMIT ?
            ''', (limit,))

            return self.cursor.fetchall()
        except Exception as e:
            print(f"Error getting top selling products: {e}")
            return []
        finally:
            self.disconnect()

    def get_profit_trend(self, days=30):
        """Get profit trend data"""
        if not self.connect():
            return []

        try:
            self.cursor.execute('''
                SELECT sale_date, SUM(profit) as daily_profit
                FROM sales
                WHERE sale_date >= date('now', '-{} days')
                GROUP BY sale_date
                ORDER BY sale_date
            '''.format(days))

            return self.cursor.fetchall()
        except Exception as e:
            print(f"Error getting profit trend: {e}")
            return []
        finally:
            self.disconnect()

    def get_category_performance(self):
        """Get performance by category"""
        if not self.connect():
            return []

        try:
            self.cursor.execute('''
                SELECT c.name, SUM(s.revenue) as total_revenue, SUM(s.profit) as total_profit
                FROM sales s
                JOIN products p ON s.product_id = p.id
                JOIN categories c ON p.category_id = c.id
                GROUP BY c.id, c.name
                ORDER BY total_revenue DESC
            ''')

            return self.cursor.fetchall()
        except Exception as e:
            print(f"Error getting category performance: {e}")
            return []
        finally:
            self.disconnect()
