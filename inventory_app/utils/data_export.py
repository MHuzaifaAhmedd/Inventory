"""
Data Export Utilities for Inventory Management System
Handles CSV and Excel export functionality
"""

import csv
import os
from datetime import datetime
from pathlib import Path

class DataExporter:
    """Handles data export operations"""

    def __init__(self, db_manager):
        """Initialize data exporter"""
        self.db_manager = db_manager

    def export_products_to_csv(self, filename=None):
        """Export products list to CSV"""
        try:
            if not filename:
                timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
                filename = f"products_export_{timestamp}.csv"

            # Get products data
            products = self.db_manager.get_products()

            with open(filename, 'w', newline='', encoding='utf-8') as csvfile:
                writer = csv.writer(csvfile)

                # Write header
                writer.writerow([
                    "Product ID", "Name", "SKU", "Barcode", "Category",
                    "COGS", "Initial Stock", "Current Stock", "Created Date"
                ])

                # Write data
                for product in products:
                    writer.writerow([
                        product[0],  # ID
                        product[1],  # Name
                        product[2] or "",  # SKU
                        product[3] or "",  # Barcode
                        product[4],  # Category
                        product[5] or 0,  # COGS
                        product[6],  # Initial Stock (we'll use current stock)
                        product[6],  # Current Stock
                        "N/A"  # Created date not available in current query
                    ])

            return filename

        except Exception as e:
            raise Exception(f"Failed to export products: {e}")

    def export_sales_to_csv(self, filename=None, start_date=None, end_date=None, category_id=None):
        """Export sales data to CSV"""
        try:
            if not filename:
                timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
                filename = f"sales_export_{timestamp}.csv"

            # Get sales data
            sales = self.db_manager.get_sales(start_date, end_date, category_id)

            with open(filename, 'w', newline='', encoding='utf-8') as csvfile:
                writer = csv.writer(csvfile)

                # Write header
                writer.writerow([
                    "Sale ID", "Product Name", "Quantity", "Selling Price",
                    "Revenue", "Profit", "Sale Date", "Category"
                ])

                # Write data
                for sale in sales:
                    writer.writerow([
                        sale[0],  # ID
                        sale[1],  # Product Name
                        sale[2],  # Quantity
                        sale[3],  # Selling Price
                        sale[4],  # Revenue
                        sale[5],  # Profit
                        sale[6],  # Date
                        sale[7]   # Category
                    ])

            return filename

        except Exception as e:
            raise Exception(f"Failed to export sales: {e}")

    def export_inventory_report(self, filename=None):
        """Export comprehensive inventory report"""
        try:
            if not filename:
                timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
                filename = f"inventory_report_{timestamp}.csv"

            # Get dashboard stats
            stats = self.db_manager.get_dashboard_stats()

            # Get products by category
            categories = self.db_manager.get_categories()
            products = self.db_manager.get_products()

            with open(filename, 'w', newline='', encoding='utf-8') as csvfile:
                writer = csv.writer(csvfile)

                # Write report header
                writer.writerow(["MONA BEAUTY STORE - INVENTORY REPORT"])
                writer.writerow([f"Generated on: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}"])
                writer.writerow([])

                # Write summary
                writer.writerow(["SUMMARY"])
                writer.writerow(["Total Products", stats.get('total_products', 0)])
                writer.writerow(["Total Stock", stats.get('total_stock', 0)])
                writer.writerow(["Total Revenue", f"₹{stats.get('total_revenue', 0):.2f}"])
                writer.writerow(["Total Profit", f"₹{stats.get('total_profit', 0):.2f}"])
                writer.writerow([])

                # Write products by category
                writer.writerow(["PRODUCTS BY CATEGORY"])
                writer.writerow(["Category", "Product Count", "Total Stock Value"])

                category_summary = {}
                for product in products:
                    category = product[4]
                    if category not in category_summary:
                        category_summary[category] = {'count': 0, 'stock_value': 0}
                    category_summary[category]['count'] += 1
                    category_summary[category]['stock_value'] += (product[5] or 0) * product[6]

                for category, data in category_summary.items():
                    writer.writerow([
                        category,
                        data['count'],
                        f"₹{data['stock_value']:.2f}"
                    ])

                writer.writerow([])

                # Write detailed products
                writer.writerow(["DETAILED PRODUCT LIST"])
                writer.writerow([
                    "Name", "SKU", "Barcode", "Category", "COGS",
                    "Current Stock", "Stock Value"
                ])

                for product in products:
                    stock_value = (product[5] or 0) * product[6]
                    writer.writerow([
                        product[1],  # Name
                        product[2] or "",  # SKU
                        product[3] or "",  # Barcode
                        product[4],  # Category
                        product[5] or 0,  # COGS
                        product[6],  # Stock
                        f"₹{stock_value:.2f}"  # Stock Value
                    ])

            return filename

        except Exception as e:
            raise Exception(f"Failed to export inventory report: {e}")

    def export_sales_report(self, filename=None, start_date=None, end_date=None):
        """Export detailed sales report with analytics"""
        try:
            if not filename:
                timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
                filename = f"sales_report_{timestamp}.csv"

            # Get sales data
            sales = self.db_manager.get_sales(start_date, end_date)

            # Get top products
            top_products = self.db_manager.get_top_selling_products(10)

            # Get category performance
            category_perf = self.db_manager.get_category_performance()

            with open(filename, 'w', newline='', encoding='utf-8') as csvfile:
                writer = csv.writer(csvfile)

                # Write report header
                writer.writerow(["MONA BEAUTY STORE - SALES REPORT"])
                date_range = ""
                if start_date and end_date:
                    date_range = f" ({start_date} to {end_date})"
                elif start_date:
                    date_range = f" (from {start_date})"
                elif end_date:
                    date_range = f" (until {end_date})"
                writer.writerow([f"Generated on: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}{date_range}"])
                writer.writerow([])

                # Calculate summary
                total_revenue = sum(sale[4] for sale in sales)
                total_profit = sum(sale[5] for sale in sales)
                total_quantity = sum(sale[2] for sale in sales)

                writer.writerow(["SALES SUMMARY"])
                writer.writerow(["Total Sales", len(sales)])
                writer.writerow(["Total Quantity Sold", total_quantity])
                writer.writerow(["Total Revenue", f"₹{total_revenue:.2f}"])
                writer.writerow(["Total Profit", f"₹{total_profit:.2f}"])
                if total_revenue > 0:
                    writer.writerow(["Profit Margin", f"{(total_profit/total_revenue)*100:.1f}%"])
                writer.writerow([])

                # Top selling products
                writer.writerow(["TOP 10 BEST-SELLING PRODUCTS"])
                writer.writerow(["Product", "Quantity Sold", "Revenue"])
                for product in top_products:
                    writer.writerow([
                        product[0],
                        product[1],
                        f"₹{product[2]:.2f}"
                    ])
                writer.writerow([])

                # Category performance
                writer.writerow(["CATEGORY PERFORMANCE"])
                writer.writerow(["Category", "Revenue", "Profit"])
                for cat in category_perf:
                    writer.writerow([
                        cat[0],
                        f"₹{cat[1]:.2f}",
                        f"₹{cat[2]:.2f}"
                    ])
                writer.writerow([])

                # Detailed sales
                writer.writerow(["DETAILED SALES"])
                writer.writerow([
                    "Date", "Product", "Quantity", "Selling Price",
                    "Revenue", "Profit", "Category"
                ])

                # Sort sales by date
                sales.sort(key=lambda x: x[6], reverse=True)

                for sale in sales:
                    writer.writerow([
                        sale[6],  # Date
                        sale[1],  # Product
                        sale[2],  # Quantity
                        sale[3],  # Selling Price
                        sale[4],  # Revenue
                        sale[5],  # Profit
                        sale[7]   # Category
                    ])

            return filename

        except Exception as e:
            raise Exception(f"Failed to export sales report: {e}")


