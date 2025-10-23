"""
Product Management Frame for Inventory Management System
Handles adding, editing, and deleting products
"""

import tkinter as tk
from tkinter import ttk, messagebox, simpledialog
import re
import os

class ProductManagementFrame:
    """Product management frame"""

    def __init__(self, parent, db_manager, main_window):
        """Initialize product management frame"""
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
        self.create_product_form()
        self.create_products_table()
        self.create_action_buttons()

        # Initialize data
        self.selected_product = None
        self.categories = []
        self.load_categories()
        # Map of product_id -> full product tuple from DB (raw values)
        self.products_by_id = {}

    def create_header(self):
        """Create header section"""
        header_frame = tk.Frame(self.frame, bg=self.background_color)
        header_frame.pack(fill=tk.X, padx=20, pady=(20, 10))

        title_label = tk.Label(
            header_frame,
            text="📦 Product Management",
            font=("Arial", 24, "bold"),
            fg=self.text_color,
            bg=self.background_color
        )
        title_label.pack(side=tk.LEFT)

        # Search section
        search_frame = tk.Frame(header_frame, bg=self.background_color)
        search_frame.pack(side=tk.RIGHT)

        search_label = tk.Label(
            search_frame,
            text="Search:",
            font=("Arial", 10),
            fg=self.text_color,
            bg=self.background_color
        )
        search_label.pack(side=tk.LEFT, padx=(0, 5))

        self.search_var = tk.StringVar()
        self.search_entry = tk.Entry(
            search_frame,
            textvariable=self.search_var,
            font=("Arial", 10),
            width=20
        )
        self.search_entry.pack(side=tk.LEFT)
        self.search_entry.bind('<KeyRelease>', self.on_search)

    def create_product_form(self):
        """Create product form for adding/editing"""
        form_frame = tk.Frame(self.frame, bg=self.secondary_color, relief=tk.RIDGE, bd=2)
        form_frame.pack(fill=tk.X, padx=20, pady=(0, 20))

        # Form title
        form_title = tk.Label(
            form_frame,
            text="Product Details",
            font=("Arial", 14, "bold"),
            fg=self.text_color,
            bg=self.secondary_color,
            pady=10
        )
        form_title.pack()

        # Create form fields
        fields_frame = tk.Frame(form_frame, bg=self.secondary_color)
        fields_frame.pack(fill=tk.X, padx=20, pady=(0, 20))

        # Row 1: Product Name and SKU
        row1 = tk.Frame(fields_frame, bg=self.secondary_color)
        row1.pack(fill=tk.X, pady=(0, 10))

        # Product Name
        name_frame = tk.Frame(row1, bg=self.secondary_color)
        name_frame.pack(side=tk.LEFT, fill=tk.X, expand=True, padx=(0, 10))

        tk.Label(name_frame, text="Product Name:", font=("Arial", 10),
                fg=self.text_color, bg=self.secondary_color, anchor=tk.W).pack(fill=tk.X)
        self.name_entry = tk.Entry(name_frame, font=("Arial", 10))
        self.name_entry.pack(fill=tk.X, pady=(2, 0))

        # SKU
        sku_frame = tk.Frame(row1, bg=self.secondary_color)
        sku_frame.pack(side=tk.RIGHT, fill=tk.X, expand=True)

        tk.Label(sku_frame, text="SKU/QR Code:", font=("Arial", 10),
                fg=self.text_color, bg=self.secondary_color, anchor=tk.W).pack(fill=tk.X)
        self.sku_entry = tk.Entry(sku_frame, font=("Arial", 10))
        self.sku_entry.pack(fill=tk.X, pady=(2, 0))

        # Row 2: Category and COGS
        row2 = tk.Frame(fields_frame, bg=self.secondary_color)
        row2.pack(fill=tk.X, pady=(0, 10))

        # Category
        category_frame = tk.Frame(row2, bg=self.secondary_color)
        category_frame.pack(side=tk.LEFT, fill=tk.X, expand=True, padx=(0, 10))

        tk.Label(category_frame, text="Category:", font=("Arial", 10),
                fg=self.text_color, bg=self.secondary_color, anchor=tk.W).pack(fill=tk.X)
        self.category_combo = ttk.Combobox(category_frame, font=("Arial", 10), state="readonly")
        self.category_combo.pack(fill=tk.X, pady=(2, 0))

        # COGS
        cogs_frame = tk.Frame(row2, bg=self.secondary_color)
        cogs_frame.pack(side=tk.RIGHT, fill=tk.X, expand=True)

        tk.Label(cogs_frame, text="COGS (PKR):", font=("Arial", 10),
                fg=self.text_color, bg=self.secondary_color, anchor=tk.W).pack(fill=tk.X)
        self.cogs_entry = tk.Entry(cogs_frame, font=("Arial", 10))
        self.cogs_entry.pack(fill=tk.X, pady=(2, 0))

        # Row 3: Initial Stock
        row3 = tk.Frame(fields_frame, bg=self.secondary_color)
        row3.pack(fill=tk.X, pady=(0, 10))

        # Initial Stock
        stock_frame = tk.Frame(row3, bg=self.secondary_color)
        stock_frame.pack(side=tk.LEFT, fill=tk.X, expand=True)

        tk.Label(stock_frame, text="Initial Stock:", font=("Arial", 10),
                fg=self.text_color, bg=self.secondary_color, anchor=tk.W).pack(fill=tk.X)
        self.stock_entry = tk.Entry(stock_frame, font=("Arial", 10))
        self.stock_entry.pack(fill=tk.X, pady=(2, 0))

        # Form buttons
        buttons_frame = tk.Frame(form_frame, bg=self.secondary_color)
        buttons_frame.pack(fill=tk.X, padx=20, pady=(0, 20))

        self.add_btn = tk.Button(
            buttons_frame,
            text="➕ Add Product",
            font=("Arial", 10, "bold"),
            fg=self.secondary_color,
            bg=self.primary_color,
            relief=tk.FLAT,
            padx=20,
            pady=8,
            command=self.add_product
        )
        self.add_btn.pack(side=tk.LEFT, padx=(0, 10))

        self.update_btn = tk.Button(
            buttons_frame,
            text="✏️ Update Product",
            font=("Arial", 10, "bold"),
            fg=self.secondary_color,
            bg="#28a745",
            relief=tk.FLAT,
            padx=20,
            pady=8,
            command=self.update_product,
            state=tk.DISABLED
        )
        self.update_btn.pack(side=tk.LEFT, padx=(0, 10))

        self.clear_btn = tk.Button(
            buttons_frame,
            text="🗑️ Clear Form",
            font=("Arial", 10),
            fg=self.text_color,
            bg="#f8f9fa",
            relief=tk.FLAT,
            padx=20,
            pady=8,
            command=self.clear_form
        )
        self.clear_btn.pack(side=tk.LEFT)

    def create_products_table(self):
        """Create products table"""
        table_frame = tk.Frame(self.frame, bg=self.secondary_color, relief=tk.RIDGE, bd=2)
        table_frame.pack(fill=tk.BOTH, expand=True, padx=20, pady=(0, 20))

        # Table title with instructions
        title_frame = tk.Frame(table_frame, bg=self.secondary_color)
        title_frame.pack(fill=tk.X, padx=20)

        table_title = tk.Label(
            title_frame,
            text="📦 Products List",
            font=("Arial", 14, "bold"),
            fg=self.text_color,
            bg=self.secondary_color
        )
        table_title.pack(side=tk.LEFT)

        select_hint = tk.Label(
            title_frame,
            text="👆 Click on any row to select a product",
            font=("Arial", 9),
            fg=self.primary_color,
            bg=self.secondary_color
        )
        select_hint.pack(side=tk.RIGHT, padx=(20, 0))

        # Create Treeview
        columns = ("ID", "Name", "SKU", "QR Code", "Category", "COGS", "Stock")
        self.tree = ttk.Treeview(table_frame, columns=columns, show="headings", height=15)

        # Configure columns
        column_widths = [50, 200, 100, 150, 120, 80, 80]
        for col, width in zip(columns, column_widths):
            self.tree.heading(col, text=col, command=lambda c=col: self.sort_column(c))
            self.tree.column(col, width=width, anchor=tk.CENTER)

        # Add scrollbars
        v_scrollbar = ttk.Scrollbar(table_frame, orient=tk.VERTICAL, command=self.tree.yview)
        h_scrollbar = ttk.Scrollbar(table_frame, orient=tk.HORIZONTAL, command=self.tree.xview)
        self.tree.configure(yscrollcommand=v_scrollbar.set, xscrollcommand=h_scrollbar.set)

        # Pack tree and scrollbars
        self.tree.pack(side=tk.LEFT, fill=tk.BOTH, expand=True, padx=(20, 0), pady=(0, 20))
        v_scrollbar.pack(side=tk.RIGHT, fill=tk.Y, pady=(0, 20))
        h_scrollbar.pack(side=tk.BOTTOM, fill=tk.X, padx=(20, 0))

        # Bind selection event
        self.tree.bind('<<TreeviewSelect>>', self.on_product_select)

        # Bind double-click for quick edit
        self.tree.bind('<Double-1>', self.quick_edit_product)

        # Allow deselection by clicking on empty space and via ESC key
        self.tree.bind('<Button-1>', self.on_tree_click, add='+')
        self.tree.bind('<Escape>', self.on_escape_clear_selection)

    def create_action_buttons(self):
        """Create action buttons for selected product"""
        actions_frame = tk.Frame(self.frame, bg=self.background_color)
        actions_frame.pack(fill=tk.X, padx=20, pady=(0, 20))

        # Instructions label
        self.instructions_label = tk.Label(
            actions_frame,
            text="💡 Select a product from the table below to enable Edit/Delete buttons",
            font=("Arial", 9),
            fg=self.text_color,
            bg=self.background_color
        )
        self.instructions_label.pack(side=tk.TOP, fill=tk.X, pady=(0, 10))

        # Left side buttons
        left_frame = tk.Frame(actions_frame, bg=self.background_color)
        left_frame.pack(side=tk.LEFT)

        self.edit_btn = tk.Button(
            left_frame,
            text="✏️ Edit Selected",
            font=("Arial", 10, "bold"),
            fg=self.secondary_color,
            bg="#17a2b8",
            relief=tk.FLAT,
            padx=15,
            pady=8,
            command=self.edit_selected_product,
            state=tk.DISABLED
        )
        self.edit_btn.pack(side=tk.LEFT, padx=(0, 10))

        self.delete_btn = tk.Button(
            left_frame,
            text="🗑️ Delete Selected",
            font=("Arial", 10, "bold"),
            fg=self.secondary_color,
            bg="#dc3545",
            relief=tk.FLAT,
            padx=15,
            pady=8,
            command=self.delete_selected_product,
            state=tk.DISABLED
        )
        self.delete_btn.pack(side=tk.LEFT, padx=(0, 10))

        # Right side buttons
        right_frame = tk.Frame(actions_frame, bg=self.background_color)
        right_frame.pack(side=tk.RIGHT)

        self.refresh_btn = tk.Button(
            right_frame,
            text="🔄 Refresh",
            font=("Arial", 10),
            fg=self.secondary_color,
            bg=self.primary_color,
            relief=tk.FLAT,
            padx=15,
            pady=8,
            command=self.load_products
        )
        self.refresh_btn.pack(side=tk.LEFT, padx=(0, 10))

        self.generate_qr_btn = tk.Button(
            right_frame,
            text="🔲 Generate QR Codes",
            font=("Arial", 9),
            fg=self.secondary_color,
            bg="#17a2b8",
            relief=tk.FLAT,
            padx=10,
            pady=8,
            command=self.generate_all_qr_codes
        )
        self.generate_qr_btn.pack(side=tk.LEFT, padx=(0, 10))

        # Database reset button (for development/testing)
        self.reset_btn = tk.Button(
            right_frame,
            text="🔥 Reset DB",
            font=("Arial", 9),
            fg="white",
            bg="#ff6b6b",
            relief=tk.FLAT,
            padx=10,
            pady=6,
            command=self.reset_database
        )
        self.reset_btn.pack(side=tk.LEFT)

    def load_categories(self):
        """Load categories into combobox"""
        self.categories = self.db_manager.get_categories()
        category_names = [cat[1] for cat in self.categories]
        self.category_combo['values'] = category_names
        if category_names:
            self.category_combo.set(category_names[0])

    def load_products(self):
        """Load products into table"""
        # Clear existing items
        for item in self.tree.get_children():
            self.tree.delete(item)

        try:
            products = self.db_manager.get_products()
            # refresh raw products map
            self.products_by_id = {}

            for product in products:
                # Format COGS
                cogs_formatted = f"PKR {product[5]:.2f}" if product[5] else "PKR 0.00"
                # store raw tuple for later use when editing
                self.products_by_id[product[0]] = product

                self.tree.insert("", tk.END, values=(
                    product[0],  # ID
                    product[1],  # Name
                    product[2] or "",  # SKU
                    product[3] or "",  # QR Code
                    product[4],  # Category
                    cogs_formatted,  # COGS
                    product[6]   # Stock
                ))

        except Exception as e:
            messagebox.showerror("Error", f"Failed to load products: {e}")

    def validate_product_data(self):
        """Validate product form data"""
        name = self.name_entry.get().strip()
        sku = self.sku_entry.get().strip()
        qr_code = self.sku_entry.get().strip()  # Using SKU field for QR code
        category = self.category_combo.get()
        cogs_text = self.cogs_entry.get().strip()
        stock_text = self.stock_entry.get().strip()

        if not name:
            messagebox.showwarning("Validation Error", "Product name is required")
            return False

        if not category:
            messagebox.showwarning("Validation Error", "Category is required")
            return False

        # Validate COGS
        try:
            cogs = float(cogs_text) if cogs_text else 0.0
            if cogs < 0:
                raise ValueError
        except ValueError:
            messagebox.showwarning("Validation Error", "COGS must be a valid positive number")
            return False

        # Validate stock
        try:
            stock = int(stock_text) if stock_text else 0
            if stock < 0:
                raise ValueError
        except ValueError:
            messagebox.showwarning("Validation Error", "Stock must be a valid positive integer")
            return False

        return {
            'name': name,
            'sku': sku,
            'qr_code': qr_code,
            'category': category,
            'cogs': cogs,
            'stock': stock
        }

    def add_product(self):
        """Add new product"""
        data = self.validate_product_data()
        if not data:
            return

        # Get category ID
        category_id = None
        category_name = ""
        for cat in self.categories:
            if cat[1] == data['category']:
                category_id = cat[0]
                category_name = cat[1]
                break

        if not category_id:
            messagebox.showerror("Error", "Invalid category selected")
            return

        try:
            # Auto-generate SKU/QR Code if not provided
            sku = data['sku']
            qr_code = data['qr_code']

            if not sku or sku.strip() == "":
                # Auto-generate SKU
                sku = self.generate_sku(data['name'], category_name)
                print(f"Auto-generated SKU: {sku}")

            if not qr_code or qr_code.strip() == "":
                # Auto-generate QR code
                qr_code = self.generate_qr_code(data['name'], category_name)
                print(f"Auto-generated QR Code: {qr_code}")

            success = self.db_manager.add_product(
                data['name'],
                sku,
                qr_code,
                category_id,
                data['cogs'],
                data['stock']
            )

            if success:
                messagebox.showinfo("Success",
                    f"Product added successfully!\n\n"
                    f"Product: {data['name']}\n"
                    f"SKU: {sku}\n"
                    f"QR Code: {qr_code}\n"
                    f"Category: {category_name}")
                self.clear_form()
                self.load_products()
            else:
                messagebox.showerror("Error", "Failed to add product. SKU/QR Code may already exist.")

        except Exception as e:
            messagebox.showerror("Error", f"Failed to add product: {e}")
    
    def generate_sku(self, product_name, category_name):
        """Generate unique SKU for product"""
        try:
            from datetime import datetime
            
            # Clean product name (take first 8 alphanumeric chars)
            name_part = ''.join(filter(str.isalnum, product_name))[:8].upper()
            
            # Clean category name (take first 3 alphanumeric chars)
            category_part = ''.join(filter(str.isalnum, category_name))[:3].upper()
            
            # Add timestamp for uniqueness
            timestamp = datetime.now().strftime("%m%d")
            
            # Generate SKU: CATEGORY-NAME-TIMESTAMP
            if category_part:
                sku = f"{category_part}-{name_part}-{timestamp}"
            else:
                sku = f"{name_part}-{timestamp}"
            
            return sku
            
        except Exception as e:
            print(f"Error generating SKU: {e}")
            # Fallback to simple timestamp-based generation
            from datetime import datetime
            timestamp = datetime.now().strftime("%Y%m%d%H%M%S")
            return f"PROD-{timestamp}"
    
    def generate_qr_code(self, product_name, category_name):
        """Generate unique QR code for product"""
        try:
            from utils.qr_generator import QRGenerator

            qr_generator = QRGenerator(self.db_manager)
            sku, qr_code = qr_generator.generate_sku_qr_code(product_name, category_name)

            return qr_code

        except Exception as e:
            print(f"Error generating QR code: {e}")
            # Fallback to timestamp-based generation
            from datetime import datetime
            timestamp = datetime.now().strftime("%Y%m%d%H%M%S")
            return f"MONA-{timestamp}"

    def update_product(self):
        """Update selected product"""
        if not self.selected_product:
            return

        data = self.validate_product_data()
        if not data:
            return

        # Get category ID
        category_id = None
        for cat in self.categories:
            if cat[1] == data['category']:
                category_id = cat[0]
                break

        if not category_id:
            messagebox.showerror("Error", "Invalid category selected")
            return

        try:
            # Update core product fields
            success = self.db_manager.update_product(
                self.selected_product[0],  # Product ID
                data['name'],
                data['sku'],
                data['qr_code'],  # Using QR code
                category_id,
                data['cogs']
            )

            # Update initial_stock if changed
            initial_update_success = True
            stock_delta_applied = True
            stock_delta_message = ""
            try:
                # Fetch current initial_stock
                product_full = self.db_manager.get_product_by_id(self.selected_product[0])
                current_initial = product_full[6] if product_full and len(product_full) > 6 else None
                current_remaining = product_full[7] if product_full and len(product_full) > 7 else None
                if current_initial is not None and data['stock'] != current_initial:
                    initial_update_success = self.db_manager.update_product_initial_stock(
                        self.selected_product[0], data['stock']
                    )

                    # Adjust remaining stock by the same delta so list reflects change
                    if initial_update_success and current_remaining is not None:
                        delta = data['stock'] - current_initial
                        if delta != 0:
                            # Use stock_in/stock_out helper which guards against negatives
                            op = "stock_in" if delta > 0 else "stock_out"
                            qty = abs(delta)
                            stock_delta_applied = self.db_manager.update_stock_change(
                                self.selected_product[0], qty, op
                            )
                            if not stock_delta_applied:
                                stock_delta_message = "Remaining stock could not be adjusted (would go negative)."
            except Exception:
                # Don't block overall update if initial stock fetch fails
                initial_update_success = False
                stock_delta_applied = False

            if success and initial_update_success and stock_delta_applied:
                messagebox.showinfo("Success", "Product updated successfully!")
                self.clear_form()
                self.load_products()
            elif success:
                # Build a precise partial message
                partials = []
                if not initial_update_success:
                    partials.append("initial stock could not be saved")
                if initial_update_success and not stock_delta_applied:
                    partials.append(stock_delta_message or "remaining stock could not be adjusted")
                msg = "Product updated, but " + ", and ".join(partials) + "."
                messagebox.showwarning("Partial Success", msg)
                self.clear_form()
                self.load_products()
            else:
                messagebox.showerror("Error", "Failed to update product. SKU/QR Code may already exist.")

        except Exception as e:
            messagebox.showerror("Error", f"Failed to update product: {e}")

    def delete_selected_product(self):
        """Delete selected product"""
        if not self.selected_product:
            return

        # Ask for admin password
        password = simpledialog.askstring("Admin Password", "Enter admin password to delete:", show='*')
        if password != "admin123":  # Default password
            messagebox.showerror("Error", "Invalid admin password")
            return

        if messagebox.askyesno("Confirm Delete",
                              f"Are you sure you want to delete '{self.selected_product[1]}'?"):
            try:
                success = self.db_manager.delete_product(self.selected_product[0])
                if success:
                    messagebox.showinfo("Success", "Product deleted successfully!")
                    self.clear_form()
                    self.load_products()
                else:
                    messagebox.showerror("Error", "Cannot delete product with existing sales records.")

            except Exception as e:
                messagebox.showerror("Error", f"Failed to delete product: {e}")

    def edit_selected_product(self):
        """Edit selected product"""
        if not self.selected_product:
            return

        # Populate form with selected product data
        self.name_entry.delete(0, tk.END)
        self.name_entry.insert(0, self.selected_product[1])

        self.sku_entry.delete(0, tk.END)
        self.sku_entry.insert(0, self.selected_product[2] or "")

        self.category_combo.set(self.selected_product[4])

        self.cogs_entry.delete(0, tk.END)
        self.cogs_entry.insert(0, str(self.selected_product[5]) if self.selected_product[5] else "")

        # Populate initial stock
        try:
            # When products are loaded via get_products(), tuple shape is:
            # (id, name, sku, barcode, category_name, cogs, current_stock)
            # We need initial_stock, so fetch full record by id
            product_full = self.db_manager.get_product_by_id(self.selected_product[0])
            if product_full:
                # product_full: (id, name, sku, barcode, category_id, cogs, initial_stock, current_stock)
                initial_stock_val = product_full[6] if len(product_full) > 6 else 0
            else:
                # Fallback to current_stock shown in table if full record failed
                initial_stock_val = self.selected_product[6] if len(self.selected_product) > 6 else 0

            self.stock_entry.delete(0, tk.END)
            self.stock_entry.insert(0, str(initial_stock_val))
        except Exception:
            # Safe fallback
            self.stock_entry.delete(0, tk.END)

        # Enable update button
        self.update_btn.config(state=tk.NORMAL)
        self.add_btn.config(state=tk.DISABLED)

    def clear_form(self):
        """Clear product form"""
        self.name_entry.delete(0, tk.END)
        self.sku_entry.delete(0, tk.END)
        self.cogs_entry.delete(0, tk.END)
        self.stock_entry.delete(0, tk.END)

        if self.categories:
            self.category_combo.set(self.categories[0][1])

        self.selected_product = None
        self.update_btn.config(state=tk.DISABLED)
        self.add_btn.config(state=tk.NORMAL)

    def on_product_select(self, event):
        """Handle product selection"""
        selection = self.tree.selection()
        if selection:
            item = self.tree.item(selection[0])
            values = item['values']
            # values[0] is product ID from the table
            try:
                product_id = values[0]
            except Exception:
                product_id = None

            # Prefer raw data from DB to avoid formatted strings (e.g., "PKR 100.00")
            self.selected_product = self.products_by_id.get(product_id)

            # Fallback: attempt to sanitize from table values if mapping missing
            if not self.selected_product and values:
                try:
                    # Expected order: (ID, Name, SKU, QR, Category, COGS_FMT, Stock)
                    cogs_text = str(values[5]) if len(values) > 5 else "0"
                    import re as _re
                    match = _re.search(r"([-+]?[0-9]*\.?[0-9]+)", cogs_text)
                    cogs_val = float(match.group(1)) if match else 0.0
                    stock_val = int(values[6]) if len(values) > 6 else 0
                    self.selected_product = (
                        values[0],            # id
                        values[1],            # name
                        values[2] or "",     # sku
                        values[3] or "",     # qr_code
                        values[4],            # category
                        cogs_val,             # cogs (numeric)
                        stock_val             # stock
                    )
                except Exception:
                    self.selected_product = None

            # Enable action buttons with visual feedback
            self.edit_btn.config(state=tk.NORMAL, bg="#28a745")
            self.delete_btn.config(state=tk.NORMAL, bg="#dc3545")

            # Update instructions
            self.instructions_label.config(
                text=f"✅ Selected: {self.selected_product[1]} - Click Edit or Delete buttons above",
                fg="#28a745"
            )
        else:
            self.selected_product = None
            self.edit_btn.config(state=tk.DISABLED, bg="#17a2b8")
            self.delete_btn.config(state=tk.DISABLED, bg="#dc3545")

            # Reset instructions
            self.instructions_label.config(
                text="💡 Select a product from the table below to enable Edit/Delete buttons",
                fg=self.text_color
            )

    def quick_edit_product(self, event):
        """Handle double-click for quick edit"""
        try:
            row_id = self.tree.identify_row(event.y)
            if row_id:
                # Double-clicked a row: proceed to edit
                self.edit_selected_product()
            else:
                # Double-clicked empty area: exit edit mode and reset to Add Product state
                self.tree.selection_remove(self.tree.selection())
                self.selected_product = None
                self.clear_form()
                self.edit_btn.config(state=tk.DISABLED, bg="#17a2b8")
                self.delete_btn.config(state=tk.DISABLED, bg="#dc3545")
                self.instructions_label.config(
                    text="💡 Select a product from the table below to enable Edit/Delete buttons",
                    fg=self.text_color
                )
                return "break"
        except Exception:
            # Fallback to original behavior
            self.edit_selected_product()

    def on_tree_click(self, event):
        """Clear selection when clicking empty area in the treeview"""
        try:
            row_id = self.tree.identify_row(event.y)
            if not row_id:
                # Clicked outside any row; clear selection and reset UI state
                self.tree.selection_remove(self.tree.selection())
                self.selected_product = None
                self.edit_btn.config(state=tk.DISABLED, bg="#17a2b8")
                self.delete_btn.config(state=tk.DISABLED, bg="#dc3545")
                self.instructions_label.config(
                    text="💡 Select a product from the table below to enable Edit/Delete buttons",
                    fg=self.text_color
                )
                return "break"
        except Exception:
            pass
        # Let default behavior proceed for normal clicks
        return None

    def on_escape_clear_selection(self, event):
        """Allow clearing selection with the Escape key"""
        try:
            self.tree.selection_remove(self.tree.selection())
            self.selected_product = None
            self.edit_btn.config(state=tk.DISABLED, bg="#17a2b8")
            self.delete_btn.config(state=tk.DISABLED, bg="#dc3545")
            self.instructions_label.config(
                text="💡 Select a product from the table below to enable Edit/Delete buttons",
                fg=self.text_color
            )
            return "break"
        except Exception:
            return None

    def on_search(self, event):
        """Handle search functionality"""
        search_term = self.search_var.get().lower()

        # Clear current items
        for item in self.tree.get_children():
            self.tree.delete(item)

        try:
            products = self.db_manager.get_products()
            # refresh raw products map
            self.products_by_id = {}

            for product in products:
                # Check if search term matches any field
                if (search_term in str(product[1]).lower() or  # Name
                    search_term in str(product[2] or "").lower() or  # SKU
                    search_term in str(product[3] or "").lower() or  # QR Code
                    search_term in str(product[4]).lower()):  # Category

                    # Format COGS
                    cogs_formatted = f"PKR {product[5]:.2f}" if product[5] else "PKR 0.00"
                    # store raw tuple for later use when editing
                    self.products_by_id[product[0]] = product

                    self.tree.insert("", tk.END, values=(
                        product[0], product[1], product[2] or "", product[3] or "",
                        product[4], cogs_formatted, product[6]
                    ))

        except Exception as e:
            print(f"Search error: {e}")

    def reset_database(self):
        """Reset database and start fresh"""
        if messagebox.askyesno("Reset Database",
                              "⚠️ This will DELETE ALL products, sales, and categories!\n\n"
                              "Are you sure you want to reset the database?\n\n"
                              "This action cannot be undone."):
            try:
                # Ask for admin password
                password = simpledialog.askstring("Admin Password",
                                                "Enter admin password to reset database:", show='*')
                if password != "admin123":
                    messagebox.showerror("Error", "Invalid admin password")
                    return

                # Reset database file
                if os.path.exists("inventory.db"):
                    os.remove("inventory.db")

                # Reinitialize database schema
                if self.db_manager.initialize_database():
                    messagebox.showinfo("Success",
                                      "✅ Database reset successfully!\n\n"
                                      "The application will restart with a clean database.\n\n"
                                      "You can now add your own products.")

                    # Recreate UI frames so they bind to the reinitialized database
                    try:
                        self.main_window.recreate_frames()
                    except Exception:
                        # Fallback: reload product list in current frame
                        self.load_products()
                else:
                    messagebox.showerror("Error", "Failed to reset database")

            except Exception as e:
                messagebox.showerror("Error", f"Database reset failed: {e}")

    def generate_all_qr_codes(self):
        """Generate QR codes for all products that don't have them"""
        try:
            from utils.qr_generator import QRGenerator

            qr_generator = QRGenerator(self.db_manager)
            products = self.db_manager.get_products()

            updated_count = 0
            for product in products:
                product_id, name, sku, qr_code, category_id, cogs, current_stock = product[:7]

                # Skip if QR code already exists
                if qr_code and qr_code.strip():
                    continue

                # Get category name
                category_name = ""
                for cat in self.categories:
                    if cat[0] == category_id:
                        category_name = cat[1]
                        break

                # Generate new QR code
                new_sku, new_qr_code = qr_generator.generate_sku_qr_code(name, category_name)

                # Update database
                success = self.db_manager.update_product_barcode(product_id, new_qr_code)
                if success:
                    updated_count += 1
                    print(f"Generated QR code for {name}: {new_qr_code}")

            if updated_count > 0:
                messagebox.showinfo("Success",
                    f"✅ Generated QR codes for {updated_count} products!\n\n"
                    "All products now have QR codes that can be scanned.\n\n"
                    "📷 Check the 'QR Scanner' tab to see the generated QR codes!")
                self.load_products()  # Refresh the table
            else:
                messagebox.showinfo("Info", "All products already have QR codes!")

        except ImportError:
            messagebox.showerror("Error", "QR Generator not available")
        except Exception as e:
            messagebox.showerror("Error", f"Failed to generate QR codes: {e}")

    def sort_column(self, col):
        """Sort table by column"""
        # This is a basic implementation - could be enhanced
        pass

    def show(self):
        """Show the product management frame"""
        self.frame.pack(fill=tk.BOTH, expand=True)
        self.load_categories()
        self.load_products()
        self.clear_form()

    def hide(self):
        """Hide the product management frame"""
        self.frame.pack_forget()
