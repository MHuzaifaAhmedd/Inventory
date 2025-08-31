#!/usr/bin/env python3
"""
Run script for Mona Beauty Store Inventory Management System
Provides easy way to start the application with options
"""

import sys
import os
from pathlib import Path
import argparse

# Add current directory to path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

def main():
    """Main run function"""
    parser = argparse.ArgumentParser(description='Mona Beauty Store Inventory System')
    parser.add_argument('--sample-data', action='store_true',
                       help='Generate sample data for testing')
    parser.add_argument('--reset-db', action='store_true',
                       help='Reset database (WARNING: Deletes all data)')

    args = parser.parse_args()

    # Import after argument parsing to avoid import errors
    from database.db_manager import DatabaseManager

    # Handle database reset
    if args.reset_db:
        print("WARNING: This will delete all existing data!")
        response = input("Are you sure? (yes/no): ")
        if response.lower() == 'yes':
            db_path = Path(__file__).parent / "inventory.db"
            if db_path.exists():
                os.remove(db_path)
                print("Database reset complete.")
        else:
            print("Database reset cancelled.")
            return

    # Initialize database
    db_manager = DatabaseManager()
    db_manager.initialize_database()

    # Generate sample data if requested
    if args.sample_data:
        print("Generating sample data...")
        from sample_data import SampleDataGenerator
        generator = SampleDataGenerator()
        generator.generate_sample_data()

    # Start the application
    print("Starting Mona Beauty Store Inventory System...")
    from ui.main_window import MainWindow
    app = MainWindow()
    app.run()

if __name__ == "__main__":
    main()


