"""
Dashboard Frame for Inventory Management System
Shows analytics, charts, and real-time statistics
"""

import tkinter as tk
from tkinter import ttk, messagebox
import matplotlib.pyplot as plt
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
import seaborn as sns
import pandas as pd
from datetime import datetime, timedelta
import threading
import time

class DashboardFrame:
    """Dashboard frame with analytics and visualizations"""

    def __init__(self, parent, db_manager, main_window):
        """Initialize dashboard frame"""
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

        # Create dashboard components
        self.create_header()
        self.create_stats_cards()
        self.create_charts_area()
        self.create_filter_section()

        # Initialize charts
        self.charts = {}

        # Auto-refresh timer
        self.auto_refresh = True
        self.refresh_interval = 30000  # 30 seconds

    def create_header(self):
        """Create dashboard header"""
        header_frame = tk.Frame(self.frame, bg=self.background_color)
        header_frame.pack(fill=tk.X, padx=20, pady=(20, 10))

        title_label = tk.Label(
            header_frame,
            text="📊 Dashboard",
            font=("Arial", 24, "bold"),
            fg=self.text_color,
            bg=self.background_color
        )
        title_label.pack(side=tk.LEFT)

        # Refresh button
        refresh_btn = tk.Button(
            header_frame,
            text="🔄 Refresh",
            font=("Arial", 10),
            fg=self.secondary_color,
            bg=self.primary_color,
            relief=tk.FLAT,
            padx=15,
            pady=5,
            command=self.refresh_dashboard
        )
        refresh_btn.pack(side=tk.RIGHT)

        # Last updated label
        self.last_updated_label = tk.Label(
            header_frame,
            text="",
            font=("Arial", 9),
            fg=self.text_color,
            bg=self.background_color
        )
        self.last_updated_label.pack(side=tk.RIGHT, padx=(0, 20))

    def create_stats_cards(self):
        """Create statistics cards"""
        stats_frame = tk.Frame(self.frame, bg=self.background_color)
        stats_frame.pack(fill=tk.X, padx=20, pady=(0, 20))

        # Stats cards data
        self.stats_cards = {}

        card_configs = [
            ("Total Products", "📦", "total_products"),
            ("Total Stock", "📊", "total_stock"),
            ("Total Revenue", "💰", "total_revenue"),
            ("Total Profit", "📈", "total_profit")
        ]

        for i, (title, icon, key) in enumerate(card_configs):
            card = self.create_stats_card(stats_frame, title, icon, key)
            card.pack(side=tk.LEFT, fill=tk.BOTH, expand=True, padx=(0, 10) if i < 3 else (0, 0))
            self.stats_cards[key] = card

    def create_stats_card(self, parent, title, icon, key):
        """Create individual stats card"""
        card = tk.Frame(parent, bg=self.secondary_color, relief=tk.RAISED, bd=2)

        # Icon and title
        header_frame = tk.Frame(card, bg=self.secondary_color)
        header_frame.pack(fill=tk.X, padx=15, pady=(15, 5))

        icon_label = tk.Label(
            header_frame,
            text=icon,
            font=("Arial", 20),
            fg=self.primary_color,
            bg=self.secondary_color
        )
        icon_label.pack(side=tk.LEFT)

        title_label = tk.Label(
            header_frame,
            text=title,
            font=("Arial", 10),
            fg=self.text_color,
            bg=self.secondary_color
        )
        title_label.pack(side=tk.RIGHT)

        # Value
        value_label = tk.Label(
            card,
            text="0",
            font=("Arial", 24, "bold"),
            fg=self.primary_color,
            bg=self.secondary_color
        )
        value_label.pack(pady=(0, 15))

        # Store reference
        card.value_label = value_label
        return card

    def create_charts_area(self):
        """Create charts area"""
        charts_frame = tk.Frame(self.frame, bg=self.background_color)
        charts_frame.pack(fill=tk.BOTH, expand=True, padx=20, pady=(0, 20))

        # Left chart (Top selling products)
        left_frame = tk.Frame(charts_frame, bg=self.secondary_color, relief=tk.RIDGE, bd=2)
        left_frame.pack(side=tk.LEFT, fill=tk.BOTH, expand=True, padx=(0, 10))

        left_title = tk.Label(
            left_frame,
            text="Top 5 Best-Selling Products",
            font=("Arial", 12, "bold"),
            fg=self.text_color,
            bg=self.secondary_color,
            pady=10
        )
        left_title.pack()

        self.top_products_frame = tk.Frame(left_frame, bg=self.secondary_color)
        self.top_products_frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=(0, 10))

        # Right chart area
        right_frame = tk.Frame(charts_frame, bg=self.background_color)
        right_frame.pack(side=tk.RIGHT, fill=tk.BOTH, expand=True)

        # Profit trend chart
        profit_frame = tk.Frame(right_frame, bg=self.secondary_color, relief=tk.RIDGE, bd=2)
        profit_frame.pack(fill=tk.BOTH, expand=True, pady=(0, 10))

        profit_title = tk.Label(
            profit_frame,
            text="Profit Trend (Last 30 Days)",
            font=("Arial", 12, "bold"),
            fg=self.text_color,
            bg=self.secondary_color,
            pady=10
        )
        profit_title.pack()

        self.profit_chart_frame = tk.Frame(profit_frame, bg=self.secondary_color)
        self.profit_chart_frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=(0, 10))

        # Category performance chart
        category_frame = tk.Frame(right_frame, bg=self.secondary_color, relief=tk.RIDGE, bd=2)
        category_frame.pack(fill=tk.BOTH, expand=True)

        category_title = tk.Label(
            category_frame,
            text="Category Performance",
            font=("Arial", 12, "bold"),
            fg=self.text_color,
            bg=self.secondary_color,
            pady=10
        )
        category_title.pack()

        self.category_chart_frame = tk.Frame(category_frame, bg=self.secondary_color)
        self.category_chart_frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=(0, 10))

    def create_filter_section(self):
        """Create filter section for category selection"""
        filter_frame = tk.Frame(self.frame, bg=self.background_color)
        filter_frame.pack(fill=tk.X, padx=20, pady=(0, 20))

        filter_label = tk.Label(
            filter_frame,
            text="Filter by Category:",
            font=("Arial", 10),
            fg=self.text_color,
            bg=self.background_color
        )
        filter_label.pack(side=tk.LEFT)

        # Category filter combobox
        self.category_filter = ttk.Combobox(
            filter_frame,
            state="readonly",
            font=("Arial", 10),
            width=20
        )
        self.category_filter.pack(side=tk.LEFT, padx=(10, 0))
        self.category_filter.bind("<<ComboboxSelected>>", self.on_category_filter_change)

        # Populate categories
        self.populate_category_filter()

    def populate_category_filter(self):
        """Populate category filter dropdown"""
        categories = self.db_manager.get_categories()
        category_names = ["All Categories"] + [cat[1] for cat in categories]
        self.category_filter['values'] = category_names
        self.category_filter.set("All Categories")

    def on_category_filter_change(self, event):
        """Handle category filter change"""
        self.refresh_dashboard()

    def refresh_dashboard(self):
        """Refresh all dashboard data and charts"""
        try:
            # Update last updated time
            current_time = datetime.now().strftime("%H:%M:%S")
            self.last_updated_label.config(text=f"Last updated: {current_time}")

            # Get selected category
            selected_category = self.category_filter.get()
            category_id = None
            if selected_category != "All Categories":
                categories = self.db_manager.get_categories()
                for cat in categories:
                    if cat[1] == selected_category:
                        category_id = cat[0]
                        break

            # Update stats cards
            self.update_stats_cards(category_id)

            # Update charts
            self.update_top_products_chart(category_id)
            self.update_profit_trend_chart(category_id)
            self.update_category_performance_chart()

        except Exception as e:
            messagebox.showerror("Error", f"Failed to refresh dashboard: {e}")

    def update_stats_cards(self, category_id=None):
        """Update statistics cards"""
        try:
            stats = self.db_manager.get_dashboard_stats(category_id)

            # Format values
            total_products = stats.get('total_products', 0)
            total_stock = stats.get('total_stock', 0)
            total_revenue = stats.get('total_revenue', 0.0)
            total_profit = stats.get('total_profit', 0.0)

            # Update card values
            self.stats_cards['total_products'].value_label.config(text=str(total_products))
            self.stats_cards['total_stock'].value_label.config(text=str(total_stock))
            self.stats_cards['total_revenue'].value_label.config(text=f"PKR {total_revenue:,.2f}")
            self.stats_cards['total_profit'].value_label.config(text=f"PKR {total_profit:,.2f}")

        except Exception as e:
            print(f"Error updating stats cards: {e}")

    def update_top_products_chart(self, category_id=None):
        """Update top products chart"""
        try:
            # Clear existing chart
            for widget in self.top_products_frame.winfo_children():
                widget.destroy()

            # Get top products data
            top_products = self.db_manager.get_top_selling_products(5, category_id)

            if not top_products:
                no_data_label = tk.Label(
                    self.top_products_frame,
                    text="No sales data available",
                    font=("Arial", 10),
                    fg=self.text_color,
                    bg=self.secondary_color
                )
                no_data_label.pack(expand=True)
                return

            # Create matplotlib figure
            fig, ax = plt.subplots(figsize=(4, 3), dpi=80)
            fig.patch.set_facecolor(self.secondary_color)

            # Prepare data
            products = [p[0] for p in top_products]
            quantities = [p[1] for p in top_products]

            # Create horizontal bar chart
            bars = ax.barh(products, quantities, color=self.primary_color, alpha=0.7)
            ax.set_xlabel('Quantity Sold')
            ax.set_title('Top 5 Best-Selling Products', fontsize=10, pad=10)
            ax.set_facecolor(self.secondary_color)

            # Add value labels on bars
            for bar, qty in zip(bars, quantities):
                ax.text(bar.get_width() + 0.1, bar.get_y() + bar.get_height()/2,
                       f'{qty}', ha='left', va='center', fontsize=8)

            plt.tight_layout()

            # Embed in tkinter
            canvas = FigureCanvasTkAgg(fig, self.top_products_frame)
            canvas.draw()
            canvas.get_tk_widget().pack(fill=tk.BOTH, expand=True)

            # Store reference to prevent garbage collection
            self.charts['top_products'] = canvas

        except Exception as e:
            print(f"Error updating top products chart: {e}")

    def update_profit_trend_chart(self, category_id=None):
        """Update profit trend chart"""
        try:
            # Clear existing chart
            for widget in self.profit_chart_frame.winfo_children():
                widget.destroy()

            # Get profit trend data
            profit_data = self.db_manager.get_profit_trend(30, category_id)

            if not profit_data:
                no_data_label = tk.Label(
                    self.profit_chart_frame,
                    text="No profit data available",
                    font=("Arial", 10),
                    fg=self.text_color,
                    bg=self.secondary_color
                )
                no_data_label.pack(expand=True)
                return

            # Create matplotlib figure
            fig, ax = plt.subplots(figsize=(4, 3), dpi=80)
            fig.patch.set_facecolor(self.secondary_color)

            # Prepare data
            dates = [p[0] for p in profit_data]
            profits = [p[1] for p in profit_data]

            # Create line chart
            ax.plot(dates, profits, marker='o', color=self.primary_color,
                   linewidth=2, markersize=4)
            ax.set_xlabel('Date')
            ax.set_ylabel('Profit (PKR)')
            ax.set_title('Profit Trend (Last 30 Days)', fontsize=10, pad=10)
            ax.set_facecolor(self.secondary_color)
            ax.tick_params(axis='x', rotation=45, labelsize=8)
            ax.grid(True, alpha=0.3)

            plt.tight_layout()

            # Embed in tkinter
            canvas = FigureCanvasTkAgg(fig, self.profit_chart_frame)
            canvas.draw()
            canvas.get_tk_widget().pack(fill=tk.BOTH, expand=True)

            # Store reference to prevent garbage collection
            self.charts['profit_trend'] = canvas

        except Exception as e:
            print(f"Error updating profit trend chart: {e}")

    def update_category_performance_chart(self):
        """Update category performance chart"""
        try:
            # Clear existing chart
            for widget in self.category_chart_frame.winfo_children():
                widget.destroy()

            # Get category performance data
            category_data = self.db_manager.get_category_performance()

            if not category_data:
                no_data_label = tk.Label(
                    self.category_chart_frame,
                    text="No category data available",
                    font=("Arial", 10),
                    fg=self.text_color,
                    bg=self.secondary_color
                )
                no_data_label.pack(expand=True)
                return

            # Create matplotlib figure
            fig, ax = plt.subplots(figsize=(4, 3), dpi=80)
            fig.patch.set_facecolor(self.secondary_color)

            # Prepare data
            categories = [c[0] for c in category_data]
            revenues = [c[1] for c in category_data]

            # Create pie chart
            colors = [self.primary_color, '#ff8bb8', '#ffb3d1', '#ffcce6']
            wedges, texts, autotexts = ax.pie(revenues, labels=categories, autopct='%1.1f%%',
                                            colors=colors[:len(categories)], startangle=90)
            ax.set_title('Revenue by Category', fontsize=10, pad=10)

            plt.tight_layout()

            # Embed in tkinter
            canvas = FigureCanvasTkAgg(fig, self.category_chart_frame)
            canvas.draw()
            canvas.get_tk_widget().pack(fill=tk.BOTH, expand=True)

            # Store reference to prevent garbage collection
            self.charts['category_performance'] = canvas

        except Exception as e:
            print(f"Error updating category performance chart: {e}")

    def show(self):
        """Show the dashboard frame"""
        self.frame.pack(fill=tk.BOTH, expand=True)
        self.refresh_dashboard()

        # Start auto-refresh
        if self.auto_refresh:
            self.start_auto_refresh()

    def hide(self):
        """Hide the dashboard frame"""
        self.frame.pack_forget()
        self.stop_auto_refresh()

    def start_auto_refresh(self):
        """Start auto-refresh timer"""
        if hasattr(self, 'refresh_timer'):
            self.frame.after_cancel(self.refresh_timer)

        self.refresh_timer = self.frame.after(self.refresh_interval, self.auto_refresh_callback)

    def stop_auto_refresh(self):
        """Stop auto-refresh timer"""
        if hasattr(self, 'refresh_timer'):
            self.frame.after_cancel(self.refresh_timer)

    def auto_refresh_callback(self):
        """Auto-refresh callback"""
        if self.auto_refresh and self.frame.winfo_ismapped():
            self.refresh_dashboard()
            self.start_auto_refresh()


