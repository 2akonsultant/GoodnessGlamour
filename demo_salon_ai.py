#!/usr/bin/env python3
"""
Demo script for Agentic Salon AI Voice Assistant
Shows the complete system in action with examples
"""

import sys
import os
import time
from datetime import datetime

# Add current directory to path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

def print_banner():
    """Print system banner"""
    print("\n" + "="*80)
    print("🎯 AGENTIC SALON AI VOICE ASSISTANT - COMPLETE SYSTEM DEMO")
    print("="*80)
    print("✨ Multi-Agent AI System for Salon Voice Calls & Bookings")
    print("🤖 Powered by Gemini 2.0 Flash + RAG + Twilio + FastAPI")
    print("="*80)

def demo_ai_conversation():
    """Demo AI conversation capabilities"""
    print("\n🤖 DEMO: AI Conversation System")
    print("-" * 50)
    
    try:
        from voice_agent import AgenticSalonAI
        salon_ai = AgenticSalonAI()
        
        # Demo queries
        demo_queries = [
            "Hello! What services do you offer?",
            "What are your hair coloring prices?",
            "Do you provide doorstep services?",
            "I want to book an appointment for hair spa tomorrow at 3 PM"
        ]
        
        for i, query in enumerate(demo_queries, 1):
            print(f"\n{i}. Customer: {query}")
            response = salon_ai.process_user_input(query)
            print(f"   AI Assistant: {response}")
            time.sleep(1)  # Pause for readability
        
        print("\n✅ AI Conversation Demo Complete!")
        
    except Exception as e:
        print(f"❌ Error in AI demo: {e}")

def demo_rag_system():
    """Demo RAG (Retrieval-Augmented Generation) system"""
    print("\n🔍 DEMO: RAG Knowledge Base System")
    print("-" * 50)
    
    try:
        from voice_agent import AgenticSalonAI
        salon_ai = AgenticSalonAI()
        
        # Demo RAG queries
        rag_queries = [
            "What are your bridal makeup prices?",
            "Do you have kids services?",
            "What time do you open?",
            "How much does keratin treatment cost?"
        ]
        
        for query in rag_queries:
            print(f"\n🔍 Query: {query}")
            context = salon_ai.rag_agent.get_relevant_context(query)
            if context:
                print(f"📚 RAG Context Found:")
                print(f"   {context}")
            else:
                print("   No specific context found - will use general AI knowledge")
        
        print("\n✅ RAG System Demo Complete!")
        
    except Exception as e:
        print(f"❌ Error in RAG demo: {e}")

def demo_booking_flow():
    """Demo complete booking flow"""
    print("\n📅 DEMO: Complete Booking Flow")
    print("-" * 50)
    
    try:
        from voice_agent import AgenticSalonAI
        salon_ai = AgenticSalonAI()
        
        # Simulate complete booking conversation
        booking_steps = [
            "I want to book an appointment",
            "My name is Priya Sharma",
            "My phone number is 9876543210",
            "I want hair coloring service",
            "Tomorrow at 2 PM",
            "123 MG Road, Mumbai",
            "Yes, confirm the booking"
        ]
        
        print("🎭 Simulating Customer Booking Conversation:")
        print("=" * 50)
        
        for i, step in enumerate(booking_steps, 1):
            print(f"\n{i}. Customer: {step}")
            response = salon_ai.process_user_input(step)
            print(f"   AI Assistant: {response}")
            time.sleep(1)
        
        print("\n✅ Booking Flow Demo Complete!")
        print("📊 Booking would be saved to database")
        print("📱 SMS notifications would be sent")
        
    except Exception as e:
        print(f"❌ Error in booking demo: {e}")

def demo_web_interface():
    """Demo web interface capabilities"""
    print("\n🌐 DEMO: Web Interface & API")
    print("-" * 50)
    
    print("📱 Web Interface Features:")
    print("   • QR Code scanning page")
    print("   • Phone number input")
    print("   • One-click voice call trigger")
    print("   • Real-time call status")
    
    print("\n🔗 API Endpoints:")
    print("   • GET  / - QR code interface")
    print("   • POST /trigger-call - Trigger voice call")
    print("   • POST /voice/webhook - Twilio webhook")
    print("   • GET  /health - System health check")
    print("   • GET  /test-ai - Test AI responses")
    print("   • GET  /bookings - View all bookings")
    
    print("\n🚀 To start web server:")
    print("   python run_salon_ai.py --mode web")
    print("   Then visit: http://localhost:8000")
    
    print("\n✅ Web Interface Demo Complete!")

def demo_voice_integration():
    """Demo voice call integration"""
    print("\n📞 DEMO: Voice Call Integration")
    print("-" * 50)
    
    print("🎯 Voice Call Flow:")
    print("   1. Customer scans QR code")
    print("   2. Enters phone number on web interface")
    print("   3. System triggers Twilio voice call")
    print("   4. Customer receives AI voice call")
    print("   5. Natural conversation with AI")
    print("   6. Booking collection via voice")
    print("   7. SMS confirmation sent")
    
    print("\n🔧 Twilio Integration:")
    print("   • Voice calls with AI responses")
    print("   • Speech-to-text conversion")
    print("   • Text-to-speech synthesis")
    print("   • SMS notifications")
    print("   • Webhook handling")
    
    print("\n📋 Prerequisites:")
    print("   • Twilio account with phone number")
    print("   • Webhook URL configured")
    print("   • HTTPS domain for production")
    
    print("\n✅ Voice Integration Demo Complete!")

def demo_database_system():
    """Demo database and storage"""
    print("\n🗄️ DEMO: Database & Storage System")
    print("-" * 50)
    
    print("📊 Database Features:")
    print("   • SQLite database for bookings")
    print("   • Customer information storage")
    print("   • Excel file fallback")
    print("   • Automatic data backup")
    
    print("\n📋 Data Stored:")
    print("   • Booking details (ID, customer, service, date, time)")
    print("   • Customer information (name, phone, address)")
    print("   • Service history and preferences")
    print("   • Timestamps and status tracking")
    
    print("\n🔍 Database Schema:")
    print("   • bookings table - All appointment data")
    print("   • customers table - Customer profiles")
    print("   • Automatic indexing and relationships")
    
    print("\n✅ Database System Demo Complete!")

def demo_deployment():
    """Demo deployment options"""
    print("\n🚀 DEMO: Deployment Options")
    print("-" * 50)
    
    print("🏠 Local Development:")
    print("   python run_salon_ai.py --mode web")
    print("   Access: http://localhost:8000")
    
    print("\n☁️ Cloud Deployment Options:")
    print("   • Railway: Connect GitHub, set env vars, deploy")
    print("   • Heroku: Add Procfile, set config, deploy")
    print("   • DigitalOcean: App Platform with auto-scaling")
    print("   • AWS: EC2 with load balancing")
    print("   • Google Cloud: App Engine or Cloud Run")
    
    print("\n🔧 Production Requirements:")
    print("   • HTTPS domain for webhooks")
    print("   • Twilio account with phone number")
    print("   • Gemini API key")
    print("   • Database backup strategy")
    print("   • Monitoring and logging")
    
    print("\n✅ Deployment Demo Complete!")

def main():
    """Main demo function"""
    print_banner()
    
    print("\n🎯 SYSTEM COMPONENTS DEMO")
    print("Choose a demo to run:")
    print("1. AI Conversation System")
    print("2. RAG Knowledge Base")
    print("3. Complete Booking Flow")
    print("4. Web Interface & API")
    print("5. Voice Call Integration")
    print("6. Database & Storage")
    print("7. Deployment Options")
    print("8. Run All Demos")
    print("9. Exit")
    
    while True:
        try:
            choice = input("\nEnter your choice (1-9): ").strip()
            
            if choice == "1":
                demo_ai_conversation()
            elif choice == "2":
                demo_rag_system()
            elif choice == "3":
                demo_booking_flow()
            elif choice == "4":
                demo_web_interface()
            elif choice == "5":
                demo_voice_integration()
            elif choice == "6":
                demo_database_system()
            elif choice == "7":
                demo_deployment()
            elif choice == "8":
                print("\n🎬 RUNNING ALL DEMOS...")
                demo_ai_conversation()
                demo_rag_system()
                demo_booking_flow()
                demo_web_interface()
                demo_voice_integration()
                demo_database_system()
                demo_deployment()
                print("\n🎉 ALL DEMOS COMPLETE!")
            elif choice == "9":
                print("\n👋 Goodbye!")
                break
            else:
                print("❌ Invalid choice. Please enter 1-9.")
                continue
            
            print("\n" + "="*80)
            print("Demo completed! Choose another option or exit.")
            
        except KeyboardInterrupt:
            print("\n\n👋 Demo interrupted. Goodbye!")
            break
        except Exception as e:
            print(f"\n❌ Error: {e}")
            print("Please try again.")

if __name__ == "__main__":
    main()
