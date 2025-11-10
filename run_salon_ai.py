#!/usr/bin/env python3
"""
Main entry point for the Agentic Salon AI Voice Assistant
Handles both standalone AI testing and web server modes
"""

import sys
import os
import argparse
import logging
from typing import Optional

# Add current directory to path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

# Import our modules
try:
    from voice_agent import AgenticSalonAI, config
    from api_server import app
    import uvicorn
except ImportError as e:
    print(f"❌ Import error: {e}")
    print("Please install dependencies: pip install -r requirements_ai.txt")
    sys.exit(1)

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('logs/salon_ai.log'),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)

def create_directories():
    """Create necessary directories"""
    directories = ['logs', 'data', 'chroma_db']
    for directory in directories:
        os.makedirs(directory, exist_ok=True)
        logger.info(f"Created directory: {directory}")

def validate_environment():
    """Validate environment and configuration"""
    logger.info("🔍 Validating environment...")
    
    # Check Python version
    if sys.version_info < (3, 8):
        logger.error("❌ Python 3.8+ required")
        return False
    
    # Check configuration
    if not config.validate_config():
        logger.error("❌ Configuration validation failed")
        logger.info("Please update config.py with your API keys")
        return False
    
    # Check required files
    required_files = ['voice_agent.py', 'api_server.py', 'config.py']
    for file in required_files:
        if not os.path.exists(file):
            logger.error(f"❌ Required file missing: {file}")
            return False
    
    logger.info("✅ Environment validation passed")
    return True

def run_ai_test():
    """Run AI system in test mode"""
    logger.info("🤖 Starting AI test mode...")
    
    try:
        salon_ai = AgenticSalonAI()
        
        print("\n" + "="*60)
        print("🎯 AGENTIC SALON AI VOICE ASSISTANT")
        print("="*60)
        print("\nChoose test mode:")
        print("1. Text conversation")
        print("2. Voice conversation (requires microphone)")
        print("3. Test RAG system")
        print("4. Test booking flow")
        print("5. Test Twilio integration")
        
        choice = input("\nEnter your choice (1-5): ").strip()
        
        if choice == "1":
            print("\n💬 TEXT CONVERSATION MODE")
            print("Type 'exit' to quit")
            while True:
                user_input = input("\nYou: ").strip()
                if user_input.lower() == "exit":
                    break
                response = salon_ai.process_user_input(user_input)
                print(f"Assistant: {response}")
        
        elif choice == "2":
            print("\n🎤 VOICE CONVERSATION MODE")
            salon_ai.start_voice_conversation()
        
        elif choice == "3":
            print("\n🔍 TESTING RAG SYSTEM")
            test_queries = [
                "What are your hair coloring prices?",
                "Do you provide doorstep services?",
                "What time do you open?",
                "How much does bridal makeup cost?"
            ]
            
            for query in test_queries:
                print(f"\nQuery: {query}")
                context = salon_ai.rag_agent.get_relevant_context(query)
                if context:
                    print(f"RAG Context: {context}")
                else:
                    print("No relevant context found")
        
        elif choice == "4":
            print("\n📅 TESTING BOOKING FLOW")
            test_booking = [
                "I want to book an appointment",
                "My name is Sarah",
                "My phone is 9876543210",
                "I want hair coloring",
                "Tomorrow",
                "2 PM",
                "123 Main Street, Mumbai"
            ]
            
            for step in test_booking:
                print(f"\nCustomer: {step}")
                response = salon_ai.process_user_input(step)
                print(f"Assistant: {response}")
        
        elif choice == "5":
            print("\n📞 TESTING TWILIO INTEGRATION")
            if salon_ai.twilio_handler.twilio_available:
                phone = input("Enter test phone number (with country code): ").strip()
                webhook_url = f"{config.WEBHOOK_URL}/voice/webhook"
                success = salon_ai.trigger_voice_call(phone, webhook_url)
                if success:
                    print("✅ Voice call initiated successfully!")
                else:
                    print("❌ Failed to initiate voice call")
            else:
                print("❌ Twilio not available. Please check configuration.")
        
        else:
            print("❌ Invalid choice")
    
    except Exception as e:
        logger.error(f"Error in AI test mode: {e}")
        print(f"❌ Error: {e}")

def run_web_server(host: str = "0.0.0.0", port: int = 8000, debug: bool = False):
    """Run the web server"""
    logger.info(f"🌐 Starting web server on {host}:{port}")
    
    try:
        uvicorn.run(
            "api_server:app",
            host=host,
            port=port,
            reload=debug,
            log_level="info" if not debug else "debug"
        )
    except Exception as e:
        logger.error(f"Error starting web server: {e}")
        print(f"❌ Server error: {e}")

def main():
    """Main entry point"""
    parser = argparse.ArgumentParser(description="Agentic Salon AI Voice Assistant")
    parser.add_argument("--mode", choices=["ai", "web", "test"], default="web",
                       help="Run mode: ai (standalone AI), web (web server), test (AI testing)")
    parser.add_argument("--host", default="0.0.0.0", help="Host for web server")
    parser.add_argument("--port", type=int, default=8000, help="Port for web server")
    parser.add_argument("--debug", action="store_true", help="Enable debug mode")
    
    args = parser.parse_args()
    
    # Create necessary directories
    create_directories()
    
    # Validate environment
    if not validate_environment():
        print("\n❌ Setup incomplete. Please check the setup guide.")
        sys.exit(1)
    
    print("\n🎉 Agentic Salon AI Voice Assistant")
    print("="*50)
    
    if args.mode == "ai":
        run_ai_test()
    elif args.mode == "web":
        print(f"🌐 Starting web server at http://{args.host}:{args.port}")
        print("📱 QR Code interface available")
        print("📞 Voice calls will be triggered via web interface")
        run_web_server(args.host, args.port, args.debug)
    elif args.mode == "test":
        print("🧪 Running system tests...")
        run_ai_test()
    
    print("\n✅ System ready!")

if __name__ == "__main__":
    main()
