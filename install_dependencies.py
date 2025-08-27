#!/usr/bin/env python3
"""
DocumentAgent Dependency Installer
Installs all required packages for the DocumentAgent project
"""

import subprocess
import sys
import os

def run_command(command, description):
    """Run a command and handle errors."""
    print(f"🔄 {description}...")
    try:
        result = subprocess.run(command, shell=True, check=True, capture_output=True, text=True)
        print(f"✅ {description} completed successfully")
        return True
    except subprocess.CalledProcessError as e:
        print(f"❌ {description} failed:")
        print(f"   Error: {e.stderr}")
        return False

def check_python_version():
    """Check if Python version is compatible."""
    version = sys.version_info
    if version.major < 3 or (version.major == 3 and version.minor < 8):
        print("❌ Python 3.8 or higher is required")
        print(f"   Current version: {version.major}.{version.minor}.{version.micro}")
        return False
    print(f"✅ Python {version.major}.{version.minor}.{version.micro} detected")
    return True

def install_dependencies():
    """Install all required dependencies."""
    print("🚀 Installing DocumentAgent dependencies...")
    print("=" * 50)
    
    # Check Python version
    if not check_python_version():
        return False
    
    # Install core dependencies
    if not run_command("pip install --upgrade pip", "Upgrading pip"):
        return False
    
    # Install requirements
    if os.path.exists("requirements.txt"):
        if not run_command("pip install -r requirements.txt", "Installing requirements from requirements.txt"):
            return False
    else:
        print("⚠️  requirements.txt not found, installing core packages...")
        core_packages = [
            "langchain>=0.3.0",
            "langchain-ollama>=0.1.0",
            "Flask>=2.3.3",
            "chromadb>=1.0.0",
            "ollama>=0.5.0",
            "PyMuPDF>=1.23.0"
        ]
        for package in core_packages:
            if not run_command(f"pip install {package}", f"Installing {package}"):
                return False
    
    print("=" * 50)
    print("🎉 All dependencies installed successfully!")
    print("\n📋 Next steps:")
    print("1. Make sure Ollama is running")
    print("2. Pull required models: ollama pull gemma3:4b nomic-embed-text")
    print("3. Run the web app: python web_app.py")
    print("4. Open http://localhost:5000 in your browser")
    
    return True

if __name__ == "__main__":
    success = install_dependencies()
    sys.exit(0 if success else 1)
