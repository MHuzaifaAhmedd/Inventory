# Inventory Management System

A comprehensive Python-based inventory management system with barcode scanning capabilities, built using Tkinter for the GUI and SQLite for data storage.

## Features

- 📱 **Barcode Scanner**: Camera-based barcode scanning using OpenCV and pyzbar
- 🗄️ **Product Management**: Add, edit, and manage products with categories
- 📊 **Stock Management**: Track inventory levels with stock in/out operations
- 💰 **Sales Management**: Record sales and track revenue/profit
- 🔲 **Barcode Generation**: Generate barcodes for products
- 📈 **Dashboard**: Visual overview of inventory status
- 🖨️ **Print Support**: Generate printable barcode sheets

## Screenshots

*Screenshots will be added here*

## Installation

### Prerequisites

- Python 3.7 or higher
- Webcam (for barcode scanning)
- Git

### Setup

1. **Clone the repository**
   ```bash
   git clone https://github.com/MHuzaifaAhmedd/Inventory.git
   cd Inventory
   ```

2. **Create virtual environment**
   ```bash
   python -m venv venv
   ```

3. **Activate virtual environment**
   - Windows:
     ```bash
     venv\Scripts\activate
     ```
   - macOS/Linux:
     ```bash
     source venv/bin/activate
     ```

4. **Install dependencies**
   ```bash
   pip install -r requirements.txt
   ```

5. **Run the application**
   ```bash
   python run.py
   ```

## Usage

### Starting the Application
- Run `python run.py` from the project directory
- The main window will open with navigation tabs

### Barcode Scanning
- **Camera Scanner**: Click "Start Camera" and point at barcodes
- **Manual Entry**: Type SKU/barcode manually
- **Image Upload**: Upload barcode images for scanning
- **External Scanner**: Connect USB barcode scanner

### Product Management
- Add new products with categories and pricing
- Generate unique SKUs and barcodes
- Track stock levels and costs

### Sales Management
- Record sales transactions
- Track revenue and profit margins
- Monitor inventory depletion

## Project Structure

```
inventory_app/
├── ui/                    # User interface components
│   ├── main_window.py    # Main application window
│   ├── dashboard.py      # Dashboard view
│   ├── barcode_scanner.py # Barcode scanning interface
│   ├── product_management.py # Product CRUD operations
│   └── sales_management.py   # Sales tracking
├── database/             # Database management
│   └── db_manager.py     # SQLite database operations
├── utils/                # Utility functions
│   ├── barcode_generator.py # Barcode generation
│   ├── production_barcode_scanner.py # Production scanner
│   └── professional_barcode_scanner.py # Professional scanner
├── assets/               # Static assets
├── main.py               # Application entry point
└── run.py                # Main runner script
```

## Dependencies

- **GUI**: tkinter (built-in)
- **Image Processing**: OpenCV (opencv-python)
- **Barcode Scanning**: pyzbar
- **Barcode Generation**: python-barcode
- **Database**: SQLite3 (built-in)
- **Image Handling**: Pillow (PIL)
- **Data Processing**: NumPy

## Configuration

### Database
- SQLite database file: `inventory.db`
- Automatically created on first run
- Sample data can be loaded using `sample_data.py`

### Barcode Scanning
- Supports multiple barcode formats (UPC, EAN, QR, etc.)
- Camera settings can be adjusted in `barcode_scanner.py`
- Fallback scanning methods available

## Troubleshooting

### Common Issues

1. **Camera not working**
   - Ensure webcam is connected and not in use by other applications
   - Check OpenCV installation: `pip install opencv-python`

2. **Barcode scanning issues**
   - Install pyzbar: `pip install pyzbar`
   - On Windows, may need Visual C++ Redistributables
   - Try alternative scanning methods

3. **Database errors**
   - Delete `inventory.db` and restart (will recreate database)
   - Check file permissions

### DLL Issues (Windows)
If you encounter DLL errors with pyzbar:
1. Use alternative scanner (built-in)
2. Install Visual C++ Redistributables
3. Use manual entry or external scanner

## Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Test thoroughly
5. Submit a pull request

## License

This project is open source and available under the [MIT License](LICENSE).

## Support

For issues and questions:
- Create an issue on GitHub
- Check the troubleshooting section above
- Review the documentation in the `docs/` folder

## Roadmap

- [ ] Multi-user support
- [ ] Cloud synchronization
- [ ] Advanced reporting
- [ ] Mobile app companion
- [ ] API endpoints
- [ ] Multi-language support

---

**Built with ❤️ using Python and Tkinter**
