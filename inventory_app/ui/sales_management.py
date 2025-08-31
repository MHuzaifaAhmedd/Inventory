"""
Sales Management Frame for Inventory Management System
Handles sales entry, profit tracking, and sales reports
"""

import tkinter as tk
from tkinter import ttk, messagebox, simpledialog
from datetime import datetime, date
import re

class SalesManagementFrame:
    """Sales management frame"""

    def __init__(self, parent, db_manager, main_window):
        """Initialize sales management frame"""
        self.parent = parent
        self.db_manager = db_manager
        self.main_window = main_window

        # Colors
        self.primary_color = "#fc68ae"
        self.background_color = "#fdf7f2"
        self.text_color = "#333333"
        self.secondary_color = "#ffffff"

        # Create main frame
        self.frame = tk.Frame(parent, bg=self.background_color)

        # Create components
        self.create_header()
        self.create_sales_form()
        self.create_sales_table()
        self.create_filters()

        # Initialize data
        self.selected_sale = None
        self.products = []
        self.load_products()

    def create_header(self):
        """Create header section"""
        header_frame = tk.Frame(self.frame, bg=self.background_color)
        header_frame.pack(fill=tk.X, padx=20, pady=(20, 10))

        title_label = tk.Label(
            header_frame,
            text="💰 Sales Management",
            font=("Arial", 24, "bold"),
            fg=self.text_color,
            bg=self.background_color
        )
        title_label.pack(side=tk.LEFT)

        # Export button
        export_btn = tk.Button(
            header_frame,
            text="📊 Export Sales",
            font=("Arial", 10),
            fg=self.secondary_color,
            bg=self.primary_color,
            relief=tk.FLAT,
            padx=15,
            pady=5,
            command=self.export_sales
        )
        export_btn.pack(side=tk.RIGHT, padx=(0, 10))

    def create_sales_form(self):
        """Create sales entry form"""
        form_frame = tk.Frame(self.frame, bg=self.secondary_color, relief=tk.RIDGE, bd=2)
        form_frame.pack(fill=tk.X, padx=20, pady=(0, 20))

        # Form title
        form_title = tk.Label(
            form_frame,
            text="New Sale Entry",
            font=("Arial", 14, "bold"),
            fg=self.text_color,
            bg=self.secondary_color,
            pady=10
        )
        form_title.pack()

        # Create form fields
        fields_frame = tk.Frame(form_frame, bg=self.secondary_color)
        fields_frame.pack(fill=tk.X, padx=20, pady=(0, 20))

        # Row 1: Product and Quantity
        row1 = tk.Frame(fields_frame, bg=self.secondary_color)
        row1.pack(fill=tk.X, pady=(0, 10))

        # Product selection
        product_frame = tk.Frame(row1, bg=self.secondary_color)
        product_frame.pack(side=tk.LEFT, fill=tk.X, expand=True, padx=(0, 10))

        tk.Label(product_frame, text="Product:", font=("Arial", 10),
                fg=self.text_color, bg=self.secondary_color, anchor=tk.W).pack(fill=tk.X)
        self.product_combo = ttk.Combobox(product_frame, font=("Arial", 10), state="readonly")
        self.product_combo.pack(fill=tk.X, pady=(2, 0))
        self.product_combo.bind("<<ComboboxSelected>>", self.on_product_select)

        # Quantity
        quantity_frame = tk.Frame(row1, bg=self.secondary_color)
        quantity_frame.pack(side=tk.RIGHT, fill=tk.X, expand=True)

        tk.Label(quantity_frame, text="Quantity:", font=("Arial", 10),
                fg=self.text_color, bg=self.secondary_color, anchor=tk.W).pack(fill=tk.X)
        self.quantity_entry = tk.Entry(quantity_frame, font=("Arial", 10))
        self.quantity_entry.pack(fill=tk.X, pady=(2, 0))

        # Row 2: Selling Price and Date
        row2 = tk.Frame(fields_frame, bg=self.secondary_color)
        row2.pack(fill=tk.X, pady=(0, 10))

        # Selling Price
        price_frame = tk.Frame(row2, bg=self.secondary_color)
        price_frame.pack(side=tk.LEFT, fill=tk.X, expand=True, padx=(0, 10))

        tk.Label(price_frame, text="Selling Price (₹):", font=("Arial", 10),
                fg=self.text_color, bg=self.secondary_color, anchor=tk.W).pack(fill=tk.X)
        self.price_entry = tk.Entry(price_frame, font=("Arial", 10))
        self.price_entry.pack(fill=tk.X, pady=(2, 0))

        # Sale Date
        date_frame = tk.Frame(row2, bg=self.secondary_color)
        date_frame.pack(side=tk.RIGHT, fill=tk.X, expand=True)

        tk.Label(date_frame, text="Sale Date:", font=("Arial", 10),
                fg=self.text_color, bg=self.secondary_color, anchor=tk.W).pack(fill=tk.X)

        date_subframe = tk.Frame(date_frame, bg=self.secondary_color)
        date_subframe.pack(fill=tk.X, pady=(2, 0))

        self.date_entry = tk.Entry(date_subframe, font=("Arial", 10), width=10)
        self.date_entry.pack(side=tk.LEFT)
        self.date_entry.insert(0, datetime.now().strftime("%Y-%m-%d"))

        tk.Button(date_subframe, text="📅", font=("Arial", 8),
                 command=self.pick_date, relief=tk.FLAT, padx=5).pack(side=tk.LEFT, padx=(5, 0))

        # Row 3: Calculated fields (read-only)
        row3 = tk.Frame(fields_frame, bg=self.secondary_color)
        row3.pack(fill=tk.X, pady=(0, 10))

        # Revenue
        revenue_frame = tk.Frame(row3, bg=self.secondary_color)
        revenue_frame.pack(side=tk.LEFT, fill=tk.X, expand=True, padx=(0, 10))

        tk.Label(revenue_frame, text="Revenue (₹):", font=("Arial", 10),
                fg=self.text_color, bg=self.secondary_color, anchor=tk.W).pack(fill=tk.X)
        self.revenue_entry = tk.Entry(revenue_frame, font=("Arial", 10), state="readonly")
        self.revenue_entry.pack(fill=tk.X, pady=(2, 0))

        # Profit
        profit_frame = tk.Frame(row3, bg=self.secondary_color)
        profit_frame.pack(side=tk.RIGHT, fill=tk.X, expand=True)

        tk.Label(profit_frame, text="Profit (₹):", font=("Arial", 10),
                fg=self.text_color, bg=self.secondary_color, anchor=tk.W).pack(fill=tk.X)
        self.profit_entry = tk.Entry(profit_frame, font=("Arial", 10), state="readonly")
        self.profit_entry.pack(fill=tk.X, pady=(2, 0))

        # Bind calculation events
        self.quantity_entry.bind('<KeyRelease>', self.calculate_totals)
        self.price_entry.bind('<KeyRelease>', self.calculate_totals)

        # Form buttons
        buttons_frame = tk.Frame(form_frame, bg=self.secondary_color)
        buttons_frame.pack(fill=tk.X, padx=20, pady=(0, 20))

        self.add_sale_btn = tk.Button(
            buttons_frame,
            text="💰 Add Sale",
            font=("Arial", 10, "bold"),
            fg=self.secondary_color,
            bg=self.primary_color,
            relief=tk.FLAT,
            padx=20,
            pady=8,
            command=self.add_sale
        )
        self.add_sale_btn.pack(side=tk.LEFT, padx=(0, 10))

        self.clear_sale_btn = tk.Button(
            buttons_frame,
            text="🗑️ Clear Form",
            font=("Arial", 10),
            fg=self.text_color,
            bg="#f8f9fa",
            relief=tk.FLAT,
            padx=20,
            pady=8,
            command=self.clear_sale_form
        )
        self.clear_sale_btn.pack(side=tk.LEFT)

    def create_sales_table(self):
        """Create sales table"""
        table_frame = tk.Frame(self.frame, bg=self.secondary_color, relief=tk.RIDGE, bd=2)
        table_frame.pack(fill=tk.BOTH, expand=True, padx=20, pady=(0, 20))

        # Table title
        table_title = tk.Label(
            table_frame,
            text="Sales History",
            font=("Arial", 14, "bold"),
            fg=self.text_color,
            bg=self.secondary_color,
            pady=10
        )
        table_title.pack()

        # Create Treeview
        columns = ("ID", "Product", "Qty", "Sell Price", "Revenue", "Profit", "Date", "Category")
        self.tree = ttk.Treeview(table_frame, columns=columns, show="headings", height=12)

        # Configure columns
        column_widths = [50, 150, 60, 80, 80, 80, 100, 120]
        for col, width in zip(columns, column_widths):
            self.tree.heading(col, text=col, command=lambda c=col: self.sort_column(c))
            self.tree.column(col, width=width, anchor=tk.W)

        # Add scrollbars
        v_scrollbar = ttk.Scrollbar(table_frame, orient=tk.VERTICAL, command=self.tree.yview)
        h_scrollbar = ttk.Scrollbar(table_frame, orient=tk.HORIZONTAL, command=self.tree.xview)
        self.tree.configure(yscrollcommand=v_scrollbar.set, xscrollcommand=h_scrollbar.set)

        # Pack tree and scrollbars
        self.tree.pack(side=tk.LEFT, fill=tk.BOTH, expand=True, padx=(20, 0), pady=(0, 20))
        v_scrollbar.pack(side=tk.RIGHT, fill=tk.Y, pady=(0, 20))
        h_scrollbar.pack(side=tk.BOTTOM, fill=tk.X, padx=(20, 0))

        # Bind selection event
        self.tree.bind('<<TreeviewSelect>>', self.on_sale_select)

    def create_filters(self):
        """Create filter controls"""
        filters_frame = tk.Frame(self.frame, bg=self.background_color)
        filters_frame.pack(fill=tk.X, padx=20, pady=(0, 20))

        # Date range filters
        date_frame = tk.Frame(filters_frame, bg=self.background_color)
        date_frame.pack(side=tk.LEFT)

        tk.Label(date_frame, text="From:", font=("Arial", 9),
                fg=self.text_color, bg=self.background_color).pack(side=tk.LEFT, padx=(0, 5))
        self.from_date_entry = tk.Entry(date_frame, font=("Arial", 9), width=10)
        self.from_date_entry.pack(side=tk.LEFT, padx=(0, 10))

        tk.Label(date_frame, text="To:", font=("Arial", 9),
                fg=self.text_color, bg=self.background_color).pack(side=tk.LEFT, padx=(0, 5))
        self.to_date_entry = tk.Entry(date_frame, font=("Arial", 9), width=10)
        self.to_date_entry.pack(side=tk.LEFT, padx=(0, 10))

        # Category filter
        category_frame = tk.Frame(filters_frame, bg=self.background_color)
        category_frame.pack(side=tk.LEFT, padx=(20, 0))

        tk.Label(category_frame, text="Category:", font=("Arial", 9),
                fg=self.text_color, bg=self.background_color).pack(side=tk.LEFT, padx=(0, 5))
        self.category_filter_combo = ttk.Combobox(category_frame, font=("Arial", 9),
                                                state="readonly", width=15)
        self.category_filter_combo.pack(side=tk.LEFT, padx=(0, 10))
        self.category_filter_combo.set("All Categories")

        # Filter buttons
        buttons_frame = tk.Frame(filters_frame, bg=self.background_color)
        buttons_frame.pack(side=tk.RIGHT)

        self.apply_filter_btn = tk.Button(
            buttons_frame,
            text="🔍 Apply Filter",
            font=("Arial", 9),
            fg=self.secondary_color,
            bg=self.primary_color,
            relief=tk.FLAT,
            padx=10,
            pady=5,
            command=self.apply_filters
        )
        self.apply_filter_btn.pack(side=tk.LEFT, padx=(0, 5))

        self.clear_filter_btn = tk.Button(
            buttons_frame,
            text="🗑️ Clear",
            font=("Arial", 9),
            fg=self.text_color,
            bg="#f8f9fa",
            relief=tk.FLAT,
            padx=10,
            pady=5,
            command=self.clear_filters
        )
        self.clear_filter_btn.pack(side=tk.LEFT)

        # Delete sale button
        self.delete_sale_btn = tk.Button(
            buttons_frame,
            text="🗑️ Delete Sale",
            font=("Arial", 9),
            fg=self.secondary_color,
            bg="#dc3545",
            relief=tk.FLAT,
            padx=10,
            pady=5,
            command=self.delete_selected_sale,
            state=tk.DISABLED
        )
        self.delete_sale_btn.pack(side=tk.LEFT, padx=(10, 0))

    def load_products(self):
        """Load products into combobox"""
        try:
            self.products = self.db_manager.get_products()
            product_names = [f"{p[1]} (Stock: {p[6]})" for p in self.products]
            self.product_combo['values'] = product_names

            # Load categories for filter
            categories = self.db_manager.get_categories()
            category_names = ["All Categories"] + [cat[1] for cat in categories]
            self.category_filter_combo['values'] = category_names

        except Exception as e:
            messagebox.showerror("Error", f"Failed to load products: {e}")

    def load_sales(self):
        """Load sales into table"""
        # Clear existing items
        for item in self.tree.get_children():
            self.tree.delete(item)

        try:
            # Get filter values
            from_date = self.from_date_entry.get().strip()
            to_date = self.to_date_entry.get().strip()
            category_name = self.category_filter_combo.get()

            # Get category ID if specific category selected
            category_id = None
            if category_name != "All Categories":
                categories = self.db_manager.get_categories()
                for cat in categories:
                    if cat[1] == category_name:
                        category_id = cat[0]
                        break

            sales = self.db_manager.get_sales(from_date if from_date else None,
                                            to_date if to_date else None,
                                            category_id)

            for sale in sales:
                # Format values
                sell_price = f"₹{sale[3]:.2f}"
                revenue = f"₹{sale[4]:.2f}"
                profit = f"₹{sale[5]:.2f}"

                self.tree.insert("", tk.END, values=(
                    sale[0],   # ID
                    sale[1],   # Product Name
                    sale[2],   # Quantity
                    sell_price, # Selling Price
                    revenue,   # Revenue
                    profit,    # Profit
                    sale[6],   # Date
                    sale[7]    # Category
                ))

        except Exception as e:
            messagebox.showerror("Error", f"Failed to load sales: {e}")

    def on_product_select(self, event):
        """Handle product selection"""
        selection = self.product_combo.current()
        if selection >= 0 and selection < len(self.products):
            product = self.products[selection]
            # Could auto-fill COGS or other info here if needed
            self.calculate_totals()

    def calculate_totals(self, event=None):
        """Calculate revenue and profit"""
        try:
            quantity_text = self.quantity_entry.get().strip()
            price_text = self.price_entry.get().strip()

            if not quantity_text or not price_text:
                self.revenue_entry.config(state=tk.NORMAL)
                self.revenue_entry.delete(0, tk.END)
                self.revenue_entry.config(state="readonly")

                self.profit_entry.config(state=tk.NORMAL)
                self.profit_entry.delete(0, tk.END)
                self.profit_entry.config(state="readonly")
                return

            quantity = int(quantity_text)
            selling_price = float(price_text)

            # Get selected product COGS
            selection = self.product_combo.current()
            cogs = 0.0
            if selection >= 0 and selection < len(self.products):
                cogs = self.products[selection][5] or 0.0

            # Calculate totals
            revenue = quantity * selling_price
            profit = quantity * (selling_price - cogs)

            # Update display
            self.revenue_entry.config(state=tk.NORMAL)
            self.revenue_entry.delete(0, tk.END)
            self.revenue_entry.insert(0, f"{revenue:.2f}")
            self.revenue_entry.config(state="readonly")

            self.profit_entry.config(state=tk.NORMAL)
            self.profit_entry.delete(0, tk.END)
            self.profit_entry.insert(0, f"{profit:.2f}")
            self.profit_entry.config(state="readonly")

        except ValueError:
            # Invalid input, clear totals
            self.revenue_entry.config(state=tk.NORMAL)
            self.revenue_entry.delete(0, tk.END)
            self.revenue_entry.config(state="readonly")

            self.profit_entry.config(state=tk.NORMAL)
            self.profit_entry.delete(0, tk.END)
            self.profit_entry.config(state="readonly")

    def validate_sale_data(self):
        """Validate sale form data"""
        product_selection = self.product_combo.current()
        quantity_text = self.quantity_entry.get().strip()
        price_text = self.price_entry.get().strip()
        date_text = self.date_entry.get().strip()

        if product_selection < 0:
            messagebox.showwarning("Validation Error", "Please select a product from the dropdown list")
            return False

        if not hasattr(self, 'products') or not self.products:
            messagebox.showwarning("Error", "No products available. Please add products first and restart the application.")
            return False

        if not quantity_text:
            messagebox.showwarning("Validation Error", "Quantity is required")
            return False

        if not price_text:
            messagebox.showwarning("Validation Error", "Selling price is required")
            return False

        # Validate quantity
        try:
            quantity = int(quantity_text)
            if quantity <= 0:
                raise ValueError
        except ValueError:
            messagebox.showwarning("Validation Error", "Quantity must be a positive integer")
            return False

        # Validate price
        try:
            price = float(price_text)
            if price < 0:
                raise ValueError
        except ValueError:
            messagebox.showwarning("Validation Error", "Selling price must be a valid positive number")
            return False

        # Validate date
        try:
            datetime.strptime(date_text, "%Y-%m-%d")
        except ValueError:
            messagebox.showwarning("Validation Error", "Date must be in YYYY-MM-DD format")
            return False

        # Check stock availability
        product = self.products[product_selection]
        available_stock = product[6]
        if quantity > available_stock:
            messagebox.showwarning("Validation Error",
                                 f"Insufficient stock. Available: {available_stock}, Requested: {quantity}")
            return False

        return {
            'product_id': product[0],
            'quantity': quantity,
            'selling_price': price,
            'date': date_text
        }

    def add_sale(self):
        """Add new sale"""
        data = self.validate_sale_data()
        if not data:
            return

        try:
            # Check database connection first
            if not self.db_manager.connect():
                messagebox.showerror("Database Error", "Cannot connect to database. Please restart the application.")
                return

            success = self.db_manager.add_sale(
                data['product_id'],
                data['quantity'],
                data['selling_price'],
                data['date']
            )

            if success:
                messagebox.showinfo("Success", "Sale added successfully!")
                self.clear_sale_form()
                self.load_sales()
                self.load_products()  # Refresh product stock info
            else:
                # Get more specific error information
                try:
                    # Check if product exists and has stock
                    products = self.db_manager.get_products()
                    product = next((p for p in products if p[0] == data['product_id']), None)

                    if not product:
                        messagebox.showerror("Error", "Product not found. Please refresh and try again.")
                    elif product[6] < data['quantity']:  # Current stock
                        messagebox.showerror("Error", f"Insufficient stock. Available: {product[6]}, Requested: {data['quantity']}")
                    else:
                        messagebox.showerror("Error", "Failed to add sale. Please check product data and try again.")
                except Exception:
                    messagebox.showerror("Error", "Database error occurred. Please restart the application.")

        except Exception as e:
            error_msg = str(e)
            if "database is locked" in error_msg.lower():
                messagebox.showerror("Database Error", "Database is locked. Please close other instances of the application and try again.")
            elif "no such table" in error_msg.lower():
                messagebox.showerror("Database Error", "Database schema error. Please run the database fix tool.")
            else:
                messagebox.showerror("Error", f"Failed to add sale: {error_msg}")

    def delete_selected_sale(self):
        """Delete selected sale"""
        if not self.selected_sale:
            return

        # Ask for admin password
        password = simpledialog.askstring("Admin Password", "Enter admin password to delete:", show='*')
        if password != "admin123":  # Default password
            messagebox.showerror("Error", "Invalid admin password")
            return

        if messagebox.askyesno("Confirm Delete",
                              f"Are you sure you want to delete this sale?"):
            try:
                success = self.db_manager.delete_sale(self.selected_sale[0])
                if success:
                    messagebox.showinfo("Success", "Sale deleted successfully!")
                    self.load_sales()
                    self.load_products()  # Refresh product stock info
                else:
                    messagebox.showerror("Error", "Failed to delete sale")

            except Exception as e:
                messagebox.showerror("Error", f"Failed to delete sale: {e}")

    def clear_sale_form(self):
        """Clear sale form"""
        self.product_combo.set("")
        self.quantity_entry.delete(0, tk.END)
        self.price_entry.delete(0, tk.END)
        self.date_entry.delete(0, tk.END)
        self.date_entry.insert(0, datetime.now().strftime("%Y-%m-%d"))
        self.revenue_entry.config(state=tk.NORMAL)
        self.revenue_entry.delete(0, tk.END)
        self.revenue_entry.config(state="readonly")
        self.profit_entry.config(state=tk.NORMAL)
        self.profit_entry.delete(0, tk.END)
        self.profit_entry.config(state="readonly")

    def on_sale_select(self, event):
        """Handle sale selection"""
        selection = self.tree.selection()
        if selection:
            item = self.tree.item(selection[0])
            self.selected_sale = item['values']
            self.delete_sale_btn.config(state=tk.NORMAL)
        else:
            self.selected_sale = None
            self.delete_sale_btn.config(state=tk.DISABLED)

    def apply_filters(self):
        """Apply date and category filters"""
        self.load_sales()

    def clear_filters(self):
        """Clear all filters"""
        self.from_date_entry.delete(0, tk.END)
        self.to_date_entry.delete(0, tk.END)
        self.category_filter_combo.set("All Categories")
        self.load_sales()

    def pick_date(self):
        """Open date picker dialog"""
        # Simple date picker - in a real app you'd use a proper date picker widget
        date_str = simpledialog.askstring("Date", "Enter date (YYYY-MM-DD):",
                                        initialvalue=self.date_entry.get())
        if date_str:
            try:
                datetime.strptime(date_str, "%Y-%m-%d")
                self.date_entry.delete(0, tk.END)
                self.date_entry.insert(0, date_str)
            except ValueError:
                messagebox.showwarning("Invalid Date", "Please enter date in YYYY-MM-DD format")

    def export_sales(self):
        """Export sales data to CSV"""
        try:
            from tkinter import filedialog
            import csv

            filename = filedialog.asksaveasfilename(
                defaultextension=".csv",
                filetypes=[("CSV files", "*.csv"), ("All files", "*.*")]
            )

            if filename:
                # Get all sales data
                sales = self.db_manager.get_sales()

                with open(filename, 'w', newline='', encoding='utf-8') as csvfile:
                    writer = csv.writer(csvfile)
                    writer.writerow(["ID", "Product", "Quantity", "Selling Price",
                                   "Revenue", "Profit", "Date", "Category"])

                    for sale in sales:
                        writer.writerow([
                            sale[0], sale[1], sale[2], sale[3],
                            sale[4], sale[5], sale[6], sale[7]
                        ])

                messagebox.showinfo("Success", f"Sales data exported to {filename}")

        except Exception as e:
            messagebox.showerror("Error", f"Failed to export sales: {e}")

    def sort_column(self, col):
        """Sort table by column"""
        # This is a basic implementation - could be enhanced
        pass

    def show(self):
        """Show the sales management frame"""
        self.frame.pack(fill=tk.BOTH, expand=True)
        self.load_products()
        self.load_sales()
        self.clear_sale_form()

    def hide(self):
        """Hide the sales management frame"""
        self.frame.pack_forget()
