#!/usr/bin/env python3
"""
AI Voice Booking System - Master Startup Script
Starts all voice booking services with proper configuration
"""

import os
import sys
import time
import signal
import subprocess
import threading
from datetime import datetime
import logging

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('logs/voice_system.log'),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)

class VoiceSystemManager:
    """Manages all voice booking services"""
    
    def __init__(self):
        self.processes = {}
        self.running = False
        self.services = {
            'voice-assistant': {
                'script': 'ai_voice_booking_assistant.py',
                'port': 7001,
                'required': True,
                'description': 'Basic AI Voice Assistant'
            },
            'enhanced-assistant': {
                'script': 'enhanced_voice_assistant.py',
                'port': 7002,
                'required': False,
                'description': 'Enhanced AI Assistant (OpenAI)'
            },
            'qr-trigger': {
                'script': 'qr_voice_trigger_system.py',
                'port': 7003,
                'required': True,
                'description': 'QR Code Trigger System'
            },
            'booking-integration': {
                'script': 'voice_booking_integration.py',
                'port': 7004,
                'required': True,
                'description': 'Booking Integration Service'
            }
        }
    
    def check_dependencies(self):
        """Check if all required dependencies are installed"""
        logger.info("🔍 Checking dependencies...")
        
        required_packages = [
            'flask', 'twilio', 'qrcode', 'pandas', 'requests'
        ]
        
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
            logger.info("💡 Install with: pip install -r requirements_voice.txt")
            return False
        
        logger.info("✅ All dependencies are installed")
        return True
    
    def check_environment(self):
        """Check environment variables and configuration"""
        logger.info("🔧 Checking environment configuration...")
        
        required_env_vars = [
            'TWILIO_ACCOUNT_SID',
            'TWILIO_AUTH_TOKEN',
            'TWILIO_PHONE_NUMBER'
        ]
        
        missing_vars = []
        for var in required_env_vars:
            if not os.getenv(var):
                missing_vars.append(var)
                logger.error(f"❌ {var} - Not set")
            else:
                logger.info(f"✅ {var} - OK")
        
        optional_vars = ['OPENAI_API_KEY', 'WEBHOOK_BASE_URL']
        for var in optional_vars:
            if os.getenv(var):
                logger.info(f"✅ {var} - OK")
            else:
                logger.warning(f"⚠️ {var} - Not set (optional)")
        
        if missing_vars:
            logger.error(f"❌ Missing required environment variables: {missing_vars}")
            logger.info("💡 Create a .env file with your Twilio credentials")
            return False
        
        logger.info("✅ Environment configuration is valid")
        return True
    
    def create_directories(self):
        """Create necessary directories"""
        logger.info("📁 Creating directories...")
        
        directories = ['data', 'logs', 'backups']
        for directory in directories:
            os.makedirs(directory, exist_ok=True)
            logger.info(f"✅ Created directory: {directory}")
    
    def start_service(self, service_name, service_config):
        """Start a single service"""
        script = service_config['script']
        port = service_config['port']
        description = service_config['description']
        
        logger.info(f"🚀 Starting {description} on port {port}...")
        
        try:
            # Set environment variables for the service
            env = os.environ.copy()
            env['PORT'] = str(port)
            
            # Start the service
            process = subprocess.Popen(
                [sys.executable, script],
                env=env,
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                text=True
            )
            
            self.processes[service_name] = process
            logger.info(f"✅ {description} started (PID: {process.pid})")
            
            # Wait a moment to check if service started successfully
            time.sleep(2)
            if process.poll() is not None:
                stdout, stderr = process.communicate()
                logger.error(f"❌ {description} failed to start")
                logger.error(f"Error: {stderr}")
                return False
            
            return True
            
        except Exception as e:
            logger.error(f"❌ Failed to start {description}: {e}")
            return False
    
    def stop_service(self, service_name):
        """Stop a single service"""
        if service_name in self.processes:
            process = self.processes[service_name]
            logger.info(f"🛑 Stopping {service_name}...")
            
            try:
                process.terminate()
                process.wait(timeout=10)
                logger.info(f"✅ {service_name} stopped")
            except subprocess.TimeoutExpired:
                logger.warning(f"⚠️ Force killing {service_name}")
                process.kill()
                process.wait()
            except Exception as e:
                logger.error(f"❌ Error stopping {service_name}: {e}")
            
            del self.processes[service_name]
    
    def start_all_services(self):
        """Start all voice booking services"""
        logger.info("🚀 Starting AI Voice Booking System...")
        logger.info("=" * 60)
        
        # Check prerequisites
        if not self.check_dependencies():
            return False
        
        if not self.check_environment():
            return False
        
        self.create_directories()
        
        # Start services
        failed_services = []
        
        for service_name, service_config in self.services.items():
            if service_config['required'] or os.getenv('START_ALL_SERVICES', '').lower() == 'true':
                success = self.start_service(service_name, service_config)
                if not success and service_config['required']:
                    failed_services.append(service_name)
        
        if failed_services:
            logger.error(f"❌ Failed to start required services: {failed_services}")
            self.stop_all_services()
            return False
        
        self.running = True
        logger.info("✅ AI Voice Booking System is running!")
        logger.info("=" * 60)
        self.print_status()
        
        return True
    
    def stop_all_services(self):
        """Stop all services"""
        logger.info("🛑 Stopping AI Voice Booking System...")
        
        for service_name in list(self.processes.keys()):
            self.stop_service(service_name)
        
        self.running = False
        logger.info("✅ All services stopped")
    
    def print_status(self):
        """Print system status"""
        logger.info("📊 System Status:")
        logger.info("-" * 40)
        
        for service_name, service_config in self.services.items():
            status = "🟢 Running" if service_name in self.processes else "🔴 Stopped"
            port = service_config['port']
            description = service_config['description']
            logger.info(f"{description:<30} | Port {port:<5} | {status}")
        
        logger.info("-" * 40)
        logger.info("🌐 Service URLs:")
        logger.info(f"Voice Assistant:     http://localhost:7001/health")
        logger.info(f"Enhanced Assistant:  http://localhost:7002/health")
        logger.info(f"QR Trigger System:   http://localhost:7003/health")
        logger.info(f"Booking Integration: http://localhost:7004/health")
        logger.info("=" * 60)
    
    def monitor_services(self):
        """Monitor running services"""
        while self.running:
            try:
                time.sleep(30)  # Check every 30 seconds
                
                for service_name, process in list(self.processes.items()):
                    if process.poll() is not None:
                        logger.error(f"❌ {service_name} has stopped unexpectedly")
                        self.stop_service(service_name)
                        
                        # Restart if it's a required service
                        if self.services[service_name]['required']:
                            logger.info(f"🔄 Restarting {service_name}...")
                            self.start_service(service_name, self.services[service_name])
                
            except KeyboardInterrupt:
                break
            except Exception as e:
                logger.error(f"❌ Error in service monitoring: {e}")
    
    def signal_handler(self, signum, frame):
        """Handle shutdown signals"""
        logger.info(f"\n🛑 Received signal {signum}, shutting down...")
        self.stop_all_services()
        sys.exit(0)

def main():
    """Main function"""
    print("🎤 AI Voice Booking Assistant for Goodness Glamour Salon")
    print("=" * 60)
    
    manager = VoiceSystemManager()
    
    # Set up signal handlers
    signal.signal(signal.SIGINT, manager.signal_handler)
    signal.signal(signal.SIGTERM, manager.signal_handler)
    
    # Start services
    if not manager.start_all_services():
        logger.error("❌ Failed to start voice booking system")
        sys.exit(1)
    
    try:
        # Start monitoring in a separate thread
        monitor_thread = threading.Thread(target=manager.monitor_services)
        monitor_thread.daemon = True
        monitor_thread.start()
        
        logger.info("🎉 System is ready! Press Ctrl+C to stop.")
        logger.info("📱 Test QR code: http://localhost:7003/qr/voice-booking")
        
        # Keep main thread alive
        while manager.running:
            time.sleep(1)
            
    except KeyboardInterrupt:
        logger.info("\n🛑 Shutting down...")
        manager.stop_all_services()
    except Exception as e:
        logger.error(f"❌ Unexpected error: {e}")
        manager.stop_all_services()
        sys.exit(1)

if __name__ == '__main__':
    main()
