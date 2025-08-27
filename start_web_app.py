#!/usr/bin/env python3
"""
Startup script for DocumentAgent Web Application
Checks dependencies and starts the Flask server
"""

import os
import sys
import subprocess
import importlib.util

def check_package(package_name):
    """Check if a package is installed."""
    return importlib.util.find_spec(package_name) is not None

def check_ollama_connection():
    """Check if Ollama is running and accessible."""
    try:
        import ollama
        # Try to list models to check connection
        models = ollama.list()
        print(f"✓ Ollama connected - Found {len(models['models'])} models")
        return True
    except Exception as e:
        print(f"✗ Ollama connection failed: {e}")
        print("Make sure Ollama is running and accessible")
        return False

def check_required_packages():
    """Check if all required packages are installed."""
    required_packages = [
        'flask',
        'langchain',
        'langchain_community',
        'langchain_ollama',
        'chromadb',
        'ollama'
    ]
    
    missing_packages = []
    for package in required_packages:
        if not check_package(package):
            missing_packages.append(package)
    
    if missing_packages:
        print(f"✗ Missing packages: {', '.join(missing_packages)}")
        print("Install them with: pip install -r requirements_web.txt")
        return False
    
    print("✓ All required packages are installed")
    return True

def create_directories():
    """Create necessary directories if they don't exist."""
    directories = ['uploads', 'document_vector_db', 'templates']
    
    for directory in directories:
        if not os.path.exists(directory):
            os.makedirs(directory)
            print(f"✓ Created directory: {directory}")
        else:
            print(f"✓ Directory exists: {directory}")

def main():
    """Main startup function."""
    print("DocumentAgent Web Application Startup")
    print("=" * 40)
    
    # Check Python version
    if sys.version_info < (3, 8):
        print("✗ Python 3.8 or higher is required")
        sys.exit(1)
    
    print(f"✓ Python {sys.version.split()[0]} detected")
    
    # Check packages
    if not check_required_packages():
        sys.exit(1)
    
    # Check Ollama
    if not check_ollama_connection():
        print("\nTo start Ollama:")
        print("1. Install Ollama from https://ollama.ai/")
        print("2. Run: ollama serve")
        print("3. Pull a model: ollama pull gemma3:4b")
        print("4. Pull embeddings: ollama pull nomic-embed-text")
        sys.exit(1)
    
    # Create directories
    create_directories()
    
    # Check if web app file exists
    if not os.path.exists('web_app.py'):
        print("✗ web_app.py not found")
        sys.exit(1)
    
    print("\n✓ All checks passed!")
    print("\nStarting web application...")
    print("The application will be available at: http://localhost:5000")
    print("Press Ctrl+C to stop the server")
    print("-" * 40)
    
    # Start the web application
    try:
        from web_app import app
        app.run(debug=True, host='0.0.0.0', port=5000)
    except KeyboardInterrupt:
        print("\n\nServer stopped by user")
    except Exception as e:
        print(f"\n✗ Error starting web application: {e}")
        sys.exit(1)

if __name__ == "__main__":
    main()
