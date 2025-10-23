#!/usr/bin/env python3
"""
Inventory Management System - Mona Beauty Store
Main application entry point
"""

import sys
import os
from pathlib import Path

# Add current directory to path for imports
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from ui.main_window import MainWindow
from database.db_manager import DatabaseManager

def main():
    """Main application entry point"""
    try:
        # If running with PyInstaller splash, close it when UI is ready
        try:
            import pyi_splash  # type: ignore
            pyi_splash.update_text("Loading application...")
        except Exception:
            pyi_splash = None  # noqa: F841

        # Initialize database
        db_manager = DatabaseManager()
        db_manager.initialize_database()

        # Create and run main window
        app = MainWindow()

        try:
            import pyi_splash  # type: ignore
            try:
                pyi_splash.close()
            except Exception:
                pass
        except Exception:
            pass
        app.run()

    except Exception as e:
        print(f"Error starting application: {e}")
        import traceback
        traceback.print_exc()
        input("Press Enter to exit...")

if __name__ == "__main__":
    main()


