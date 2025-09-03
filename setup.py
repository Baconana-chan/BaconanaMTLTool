#!/usr/bin/env python3
"""
Setup script for Eroge Translation Tool
Handles installation and initial configuration
"""

import os
import sys
import subprocess
import platform
from pathlib import Path


def check_python_version():
    """Check if Python version is compatible"""
    version = sys.version_info
    if version.major < 3 or (version.major == 3 and version.minor < 8):
        print("❌ Error: Python 3.8 or higher is required")
        print(f"Current version: {version.major}.{version.minor}.{version.micro}")
        sys.exit(1)
    print(f"✅ Python version {version.major}.{version.minor}.{version.micro} is compatible")


def install_requirements():
    """Install required packages"""
    print("📦 Installing required packages...")
    
    try:
        # Upgrade pip first
        subprocess.check_call([sys.executable, "-m", "pip", "install", "--upgrade", "pip"])
        
        # Install requirements
        subprocess.check_call([sys.executable, "-m", "pip", "install", "-r", "requirements.txt"])
        
        print("✅ All packages installed successfully")
        return True
        
    except subprocess.CalledProcessError as e:
        print(f"❌ Error installing packages: {e}")
        return False


def create_config_file():
    """Create initial configuration file"""
    config_path = ".env"
    
    if os.path.exists(config_path):
        print(f"✅ Configuration file {config_path} already exists")
        return
    
    print("📝 Creating initial configuration file...")
    
    try:
        with open(config_path, 'w', encoding='utf-8') as f:
            f.write("""#API link, leave blank to use OpenAI API
api=""

#API key - GET YOUR KEY FROM https://platform.openai.com/
key=""

#Organization key, make something up for self hosted or other API
organization=""

#LLM model name
model="gpt-4"

#The language to translate TO
language="English"

#The timeout before disconnect error, 30 to 120 recommended
timeout="120"

#The number of files to translate at the same time
fileThreads="1"

#The number of threads per file
threads="1"

#The wordwrap of dialogue text
width="60"

#The wordwrap of items and help text
listWidth="100"

#The wordwrap of notes text
noteWidth="75"

# Custom input API cost - see https://openai.com/pricing
input_cost=0.002

# Custom output API cost - see https://openai.com/pricing
output_cost=0.002

# Batch size - adjust according to your API's limitations
batchsize="10"

# Frequency penalty - adjust according to your needs
frequency_penalty=0.2
""")
        
        print(f"✅ Configuration file created: {config_path}")
        print("⚠️  Please edit the .env file and add your API key before running the application")
        
    except Exception as e:
        print(f"❌ Error creating configuration file: {e}")


def check_system_requirements():
    """Check system requirements"""
    print("🔍 Checking system requirements...")
    
    # Check OS
    os_name = platform.system()
    print(f"✅ Operating System: {os_name}")
    
    # Check if running on Windows for PyQt5
    if os_name == "Windows":
        print("✅ Windows detected - PyQt5 should work well")
    elif os_name == "Darwin":  # macOS
        print("✅ macOS detected - PyQt5 should work")
    elif os_name == "Linux":
        print("✅ Linux detected - you may need to install additional packages for PyQt5")
        print("   On Ubuntu/Debian: sudo apt-get install python3-pyqt5")
        print("   On CentOS/RHEL: sudo yum install PyQt5")
    
    return True


def create_directories():
    """Create necessary directories"""
    print("📁 Creating directories...")
    
    directories = [
        "output",
        "backups",
        "logs"
    ]
    
    for directory in directories:
        Path(directory).mkdir(exist_ok=True)
        print(f"✅ Created directory: {directory}")


def test_imports():
    """Test if all required modules can be imported"""
    print("🧪 Testing imports...")
    
    required_modules = [
        ("PyQt5.QtWidgets", "PyQt5"),
        ("openai", "OpenAI"),
        ("tiktoken", "tiktoken"),
        ("dotenv", "python-dotenv"),
        ("retry", "retry"),
    ]
    
    failed_imports = []
    
    for module, package in required_modules:
        try:
            __import__(module)
            print(f"✅ {package}")
        except ImportError:
            print(f"❌ {package}")
            failed_imports.append(package)
    
    if failed_imports:
        print(f"\n❌ Failed to import: {', '.join(failed_imports)}")
        print("Please run: pip install -r requirements.txt")
        return False
    
    print("✅ All required modules imported successfully")
    return True


def create_desktop_shortcut():
    """Create desktop shortcut (Windows only)"""
    if platform.system() != "Windows":
        return
    
    try:
        import winshell
        from win32com.client import Dispatch
        
        desktop = winshell.desktop()
        path = os.path.join(desktop, "Eroge Translation Tool.lnk")
        target = os.path.join(os.getcwd(), "main.py")
        wDir = os.getcwd()
        icon = target
        
        shell = Dispatch('WScript.Shell')
        shortcut = shell.CreateShortCut(path)
        shortcut.Targetpath = sys.executable
        shortcut.Arguments = f'"{target}"'
        shortcut.WorkingDirectory = wDir
        shortcut.IconLocation = icon
        shortcut.save()
        
        print(f"✅ Desktop shortcut created: {path}")
        
    except ImportError:
        print("ℹ️  Desktop shortcut creation requires winshell and pywin32")
        print("   Install with: pip install winshell pywin32")
    except Exception as e:
        print(f"⚠️  Could not create desktop shortcut: {e}")


def main():
    """Main setup function"""
    print("🚀 Eroge Translation Tool Setup")
    print("=" * 40)
    
    # Check Python version
    check_python_version()
    
    # Check system requirements
    check_system_requirements()
    
    # Install requirements
    if not install_requirements():
        print("❌ Setup failed due to package installation errors")
        sys.exit(1)
    
    # Test imports
    if not test_imports():
        print("❌ Setup failed due to import errors")
        sys.exit(1)
    
    # Create directories
    create_directories()
    
    # Create config file
    create_config_file()
    
    # Create desktop shortcut (Windows only)
    create_desktop_shortcut()
    
    print("\n🎉 Setup completed successfully!")
    print("\nNext steps:")
    print("1. Edit the .env file and add your OpenAI API key")
    print("2. Run the application with: python main.py")
    print("3. Configure your translation settings in the GUI")
    print("\nFor help, see README.md or visit the documentation")


if __name__ == "__main__":
    main()
