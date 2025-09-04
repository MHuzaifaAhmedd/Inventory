"""
Main Window for Inventory Management System
"""

import tkinter as tk
from tkinter import ttk, messagebox
import sys
import os
from pathlib import Path

# Add parent directory to path for imports
sys.path.insert(0, str(Path(__file__).parent.parent))

from ui.product_management import ProductManagementFrame
from ui.sales_management import SalesManagementFrame
from ui.dashboard import DashboardFrame
from ui.qr_scanner import QRScannerFrame
from database.db_manager import DatabaseManager

class MainWindow:
    """Main application window"""

    def __init__(self):
        """Initialize main window"""
        self.root = tk.Tk()
        self.root.title("Mona Beauty Store - Inventory Management System")
        self.root.geometry("1200x800")
        self.root.minsize(1000, 700)

        # Set application icon (if available)
        try:
            self.root.iconbitmap("assets/icon.ico")
        except:
            pass

        # Initialize database manager
        self.db_manager = DatabaseManager()

        # Configure colors (Mona Beauty Store branding)
        self.primary_color = "#fc68ae"  # Light Pink
        self.background_color = "#fdf7f2"  # Creamy Beige
        self.text_color = "#333333"
        self.secondary_color = "#ffffff"

        # Configure root window
        self.root.configure(bg=self.background_color)

        # Create main container
        self.main_container = tk.Frame(self.root, bg=self.background_color)
        self.main_container.pack(fill=tk.BOTH, expand=True)

        # Create sidebar and content area
        self.create_sidebar()
        self.create_content_area()

        # Initialize frames
        self.frames = {}
        self.create_frames()

        # Show default frame
        self.show_frame("dashboard")

        # Bind keyboard shortcuts
        self.bind_shortcuts()

    def create_sidebar(self):
        """Create sidebar with navigation buttons"""
        self.sidebar = tk.Frame(self.main_container, bg=self.primary_color, width=200)
        self.sidebar.pack(side=tk.LEFT, fill=tk.Y)
        self.sidebar.pack_propagate(False)

        # Title
        title_label = tk.Label(
            self.sidebar,
            text="MONA BEAUTY\nSTORE",
            font=("Arial", 14, "bold"),
            fg=self.secondary_color,
            bg=self.primary_color,
            justify=tk.CENTER
        )
        title_label.pack(pady=(20, 30))

        # Navigation buttons
        self.nav_buttons = {}

        nav_items = [
            ("Dashboard", "dashboard", "📊"),
            ("Products", "products", "📦"),
            ("Sales", "sales", "💰"),
            ("QR Scanner", "barcode", "📱"),
        ]

        for text, frame_name, icon in nav_items:
            btn = tk.Button(
                self.sidebar,
                text=f"{icon} {text}",
                font=("Arial", 11),
                fg=self.primary_color,
                bg=self.secondary_color,
                relief=tk.FLAT,
                bd=0,
                padx=20,
                pady=12,
                anchor=tk.W,
                command=lambda f=frame_name: self.show_frame(f)
            )
            btn.pack(fill=tk.X, padx=10, pady=2)
            self.nav_buttons[frame_name] = btn

            # Hover effects
            btn.bind("<Enter>", lambda e, b=btn: self.on_button_hover(e, b, True))
            btn.bind("<Leave>", lambda e, b=btn: self.on_button_hover(e, b, False))

        # Footer
        footer_label = tk.Label(
            self.sidebar,
            text="© 2024 Mona Beauty Store",
            font=("Arial", 8),
            fg=self.secondary_color,
            bg=self.primary_color
        )
        footer_label.pack(side=tk.BOTTOM, pady=20)

    def create_content_area(self):
        """Create main content area"""
        self.content_area = tk.Frame(self.main_container, bg=self.background_color)
        self.content_area.pack(side=tk.RIGHT, fill=tk.BOTH, expand=True)

    def create_frames(self):
        """Create all frame instances"""
        self.frames = {
            "dashboard": DashboardFrame(self.content_area, self.db_manager, self),
            "products": ProductManagementFrame(self.content_area, self.db_manager, self),
            "sales": SalesManagementFrame(self.content_area, self.db_manager, self),
            "barcode": QRScannerFrame(self.content_area, self.db_manager)
        }

    def show_frame(self, frame_name):
        """Show selected frame"""
        # Update button states
        for name, button in self.nav_buttons.items():
            if name == frame_name:
                button.configure(bg=self.secondary_color, fg=self.primary_color)
            else:
                button.configure(bg=self.primary_color, fg=self.secondary_color)

        # Hide all frames
        for frame in self.frames.values():
            frame.hide()

        # Show selected frame
        if frame_name in self.frames:
            self.frames[frame_name].show()

    def on_button_hover(self, event, button, enter):
        """Handle button hover effects"""
        if enter:
            button.configure(bg=self.secondary_color, fg=self.primary_color)
        else:
            # Reset to active state if button is currently selected
            current_frame = None
            for frame_name, btn in self.nav_buttons.items():
                if btn == button:
                    current_frame = frame_name
                    break

            if current_frame and hasattr(self, 'current_frame') and self.current_frame == current_frame:
                button.configure(bg=self.secondary_color, fg=self.primary_color)
            else:
                button.configure(bg=self.primary_color, fg=self.secondary_color)

    def bind_shortcuts(self):
        """Bind keyboard shortcuts"""
        self.root.bind('<Control-d>', lambda e: self.show_frame("dashboard"))
        self.root.bind('<Control-p>', lambda e: self.show_frame("products"))
        self.root.bind('<Control-s>', lambda e: self.show_frame("sales"))
        self.root.bind('<Control-q>', lambda e: self.show_frame("barcode"))  # QR Scanner
        self.root.bind('<Escape>', lambda e: self.confirm_exit())

    def confirm_exit(self):
        """Confirm application exit"""
        if messagebox.askyesno("Exit", "Are you sure you want to exit?"):
            self.root.quit()

    def run(self):
        """Start the application"""
        # Center window on screen
        self.center_window()

        # Start main loop
        self.root.mainloop()

    def center_window(self):
        """Center window on screen"""
        self.root.update_idletasks()
        width = self.root.winfo_width()
        height = self.root.winfo_height()
        x = (self.root.winfo_screenwidth() // 2) - (width // 2)
        y = (self.root.winfo_screenheight() // 2) - (height // 2)
        self.root.geometry(f'{width}x{height}+{x}+{y}')

