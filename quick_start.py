#!/usr/bin/env python3
"""
Quick Start Script for Agentic Salon AI System
This script helps you get started quickly with the system
"""

import os
import sys
import subprocess
import json
from pathlib import Path

def print_banner():
    """Print welcome banner"""
    print("=" * 60)
    print("🤖 AGENTIC SALON AI SYSTEM - QUICK START")
    print("=" * 60)
    print()

def check_python_version():
    """Check if Python version is compatible"""
    if sys.version_info < (3, 8):
        print("❌ Error: Python 3.8 or higher is required")
        print(f"Current version: {sys.version}")
        sys.exit(1)
    else:
        print(f"✅ Python version: {sys.version.split()[0]}")

def install_dependencies():
    """Install required dependencies"""
    print("\n📦 Installing dependencies...")
    try:
        subprocess.check_call([sys.executable, "-m", "pip", "install", "-r", "requirements.txt"])
        print("✅ Dependencies installed successfully")
    except subprocess.CalledProcessError as e:
        print(f"❌ Error installing dependencies: {e}")
        sys.exit(1)

def create_env_file():
    """Create .env file with template values"""
    env_file = Path(".env")
    if not env_file.exists():
        print("\n🔧 Creating .env file...")
        env_content = """# Gemini AI Configuration
GEMINI_API_KEY=your_gemini_api_key_here

# OpenAI Configuration (for embeddings)
OPENAI_API_KEY=your_openai_api_key_here

# Twilio Configuration
TWILIO_ACCOUNT_SID=your_twilio_account_sid
TWILIO_AUTH_TOKEN=your_twilio_auth_token
TWILIO_PHONE_NUMBER=+1234567890

# Flask Configuration
FLASK_ENV=development
FLASK_DEBUG=True
"""
        env_file.write_text(env_content)
        print("✅ .env file created")
        print("⚠️  Please update .env file with your actual API keys")
    else:
        print("✅ .env file already exists")

def create_config_file():
    """Create config.py from template"""
    config_file = Path("config.py")
    if not config_file.exists():
        print("\n🔧 Creating config.py...")
        subprocess.check_call([sys.executable, "-c", "from config_example import *; import shutil; shutil.copy('config_example.py', 'config.py')"])
        print("✅ config.py created")
    else:
        print("✅ config.py already exists")

def create_directories():
    """Create necessary directories"""
    print("\n📁 Creating directories...")
    directories = ["data", "logs", "chroma_db", "backups"]
    for directory in directories:
        Path(directory).mkdir(exist_ok=True)
        print(f"✅ Created directory: {directory}")

def test_basic_functionality():
    """Test basic functionality"""
    print("\n🧪 Testing basic functionality...")
    try:
        # Test imports
        from voice_agent import AgenticSalonAI, RAGSystem
        print("✅ Voice agent imports successful")
        
        # Test RAG system
        rag_system = RAGSystem()
        print("✅ RAG system initialized")
        
        # Test AI system
        salon_ai = AgenticSalonAI()
        print("✅ AI system initialized")
        
        # Test basic query
        response = salon_ai.process_user_input("Hello, what services do you offer?")
        if response and len(response) > 10:
            print("✅ Basic AI response working")
        else:
            print("⚠️  AI response may not be working properly")
            
    except Exception as e:
        print(f"❌ Error testing functionality: {e}")
        print("⚠️  You may need to set up API keys in .env file")

def show_next_steps():
    """Show next steps to user"""
    print("\n" + "=" * 60)
    print("🚀 NEXT STEPS")
    print("=" * 60)
    print()
    print("1. 📝 Update API Keys:")
    print("   - Edit .env file with your actual API keys")
    print("   - Get Gemini API key from: https://makersuite.google.com/app/apikey")
    print("   - Get OpenAI API key from: https://platform.openai.com/api-keys")
    print("   - Get Twilio credentials from: https://console.twilio.com/")
    print()
    print("2. 🧪 Test the System:")
    print("   python voice_agent.py")
    print()
    print("3. 🎤 Try Voice Mode:")
    print("   - Choose option 2 for voice conversation")
    print("   - Make sure your microphone is working")
    print()
    print("4. 🌐 Start Twilio Server:")
    print("   python twilio_voice_integration.py")
    print()
    print("5. 📱 Test QR Code Integration:")
    print("   - Use ngrok to expose local server")
    print("   - Update Twilio webhook URL")
    print()
    print("📚 For detailed setup instructions, see:")
    print("   AGENTIC_AI_SETUP_GUIDE.md")
    print()

def main():
    """Main setup function"""
    print_banner()
    
    # Check system requirements
    check_python_version()
    
    # Install dependencies
    install_dependencies()
    
    # Create configuration files
    create_env_file()
    create_config_file()
    
    # Create directories
    create_directories()
    
    # Test functionality
    test_basic_functionality()
    
    # Show next steps
    show_next_steps()
    
    print("\n🎉 Setup completed successfully!")
    print("Your Agentic Salon AI System is ready to use!")

if __name__ == "__main__":
    main()
