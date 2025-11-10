#!/usr/bin/env python3
"""
Simple Voice Booking System - Easy Startup Script
No complex dependencies, just the essentials
"""

import os
import sys
import time
import signal
import subprocess
import logging
from datetime import datetime
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

def check_dependencies():
    """Check if basic dependencies are installed"""
    logger.info("🔍 Checking dependencies...")
    
    required_packages = ['flask', 'twilio', 'qrcode', 'openpyxl']
    missing_packages = []
    
    for package in required_packages:
        try:
            __import__(package)
            logger.info(f"✅ {package} - OK")
        except ImportError:
            missing_packages.append(package)
            logger.error(f"❌ {package} - Missing")
    
    if missing_packages:
        logger.error(f"❌ Missing packages: {missing_packages}")
        logger.info("💡 Install with: pip install -r requirements_voice_simple.txt")
        return False
    
    logger.info("✅ All dependencies are installed")
    return True

def check_environment():
    """Check environment variables"""
    logger.info("🔧 Checking environment configuration...")
    
    required_vars = ['TWILIO_ACCOUNT_SID', 'TWILIO_AUTH_TOKEN', 'TWILIO_PHONE_NUMBER']
    missing_vars = []
    
    for var in required_vars:
        if not os.getenv(var):
            missing_vars.append(var)
            logger.error(f"❌ {var} - Not set")
        else:
            logger.info(f"✅ {var} - OK")
    
    if missing_vars:
        logger.error(f"❌ Missing required environment variables: {missing_vars}")
        logger.info("💡 Create a .env file with your Twilio credentials")
        return False
    
    logger.info("✅ Environment configuration is valid")
    return True

def create_directories():
    """Create necessary directories"""
    logger.info("📁 Creating directories...")
    
    directories = ['data', 'logs']
    for directory in directories:
        os.makedirs(directory, exist_ok=True)
        logger.info(f"✅ Created directory: {directory}")

def start_voice_assistant():
    """Start the simple voice assistant"""
    logger.info("🚀 Starting Simple AI Voice Booking Assistant...")
    
    try:
        # Set default port
        env = os.environ.copy()
        if 'PORT' not in env:
            env['PORT'] = '7001'
        
        # Start the service
        process = subprocess.Popen(
            [sys.executable, 'voice_booking_simple.py'],
            env=env
        )
        
        logger.info(f"✅ Voice Assistant started (PID: {process.pid})")
        logger.info(f"🌐 Service URL: http://localhost:{env['PORT']}")
        logger.info(f"📱 QR Landing Page: http://localhost:{env['PORT']}/qr/voice-booking")
        logger.info(f"🔍 Health Check: http://localhost:{env['PORT']}/health")
        
        return process
        
    except Exception as e:
        logger.error(f"❌ Failed to start voice assistant: {e}")
        return None

def signal_handler(signum, frame):
    """Handle shutdown signals"""
    logger.info(f"\n🛑 Received signal {signum}, shutting down...")
    sys.exit(0)

def main():
    """Main function"""
    print("🎤 Simple AI Voice Booking Assistant for Goodness Glamour Salon")
    print("=" * 60)
    
    # Set up signal handlers
    signal.signal(signal.SIGINT, signal_handler)
    signal.signal(signal.SIGTERM, signal_handler)
    
    # Check prerequisites
    if not check_dependencies():
        logger.error("❌ Dependencies check failed")
        sys.exit(1)
    
    if not check_environment():
        logger.error("❌ Environment check failed")
        sys.exit(1)
    
    create_directories()
    
    # Start voice assistant
    process = start_voice_assistant()
    if not process:
        logger.error("❌ Failed to start voice assistant")
        sys.exit(1)
    
    logger.info("=" * 60)
    logger.info("🎉 Simple Voice Booking System is ready!")
    logger.info("📞 Test by visiting: http://localhost:7001/qr/voice-booking")
    logger.info("🛑 Press Ctrl+C to stop")
    logger.info("=" * 60)
    
    try:
        # Keep the process running
        process.wait()
    except KeyboardInterrupt:
        logger.info("\n🛑 Shutting down...")
        process.terminate()
        process.wait()
    except Exception as e:
        logger.error(f"❌ Unexpected error: {e}")
        process.terminate()
        sys.exit(1)

if __name__ == '__main__':
    main()
