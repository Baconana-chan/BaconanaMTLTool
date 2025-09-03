#!/usr/bin/env python3
"""
Eroge Translation Tool - Main Application
Automatic translation tool for eroge games using AI
Supports RPG Maker MV/MZ games (.json data files)
"""

import sys
import os
from PyQt5.QtWidgets import QApplication
from PyQt5.QtCore import QDir
from gui.main_window import MainWindow

def main():
    """Main application entry point"""
    app = QApplication(sys.argv)
    app.setApplicationName("Eroge Translation Tool")
    app.setApplicationVersion("1.0.0")
    app.setOrganizationName("MTL Tools")
    
    # Set application icon and style
    app.setStyle('Fusion')
    
    # Create main window
    window = MainWindow()
    window.show()
    
    # Start event loop
    sys.exit(app.exec_())

if __name__ == "__main__":
    main()
