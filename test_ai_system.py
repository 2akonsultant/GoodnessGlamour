#!/usr/bin/env python3
"""
Simple test script for the Agentic Salon AI Voice Assistant
Tests all major components without interactive input
"""

import sys
import os
from datetime import datetime

# Add current directory to path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

def test_ai_conversation():
    """Test AI conversation capabilities"""
    print("🤖 Testing AI Conversation System...")
    print("-" * 50)
    
    try:
        from voice_agent import AgenticSalonAI
        salon_ai = AgenticSalonAI()
        
        # Test queries
        test_queries = [
            "Hello! What services do you offer?",
            "What are your hair coloring prices?",
            "Do you provide doorstep services?",
            "What time do you open?"
        ]
        
        for i, query in enumerate(test_queries, 1):
            print(f"\n{i}. Customer: {query}")
            response = salon_ai.process_user_input(query)
            print(f"   AI Assistant: {response}")
        
        print("\n✅ AI Conversation Test Complete!")
        return True
        
    except Exception as e:
        print(f"❌ Error in AI conversation test: {e}")
        return False

def test_rag_system():
    """Test RAG (Retrieval-Augmented Generation) system"""
    print("\n🔍 Testing RAG Knowledge Base System...")
    print("-" * 50)
    
    try:
        from voice_agent import AgenticSalonAI
        salon_ai = AgenticSalonAI()
        
        # Test RAG queries
        rag_queries = [
            "What are your bridal makeup prices?",
            "Do you have kids services?",
            "How much does keratin treatment cost?"
        ]
        
        for query in rag_queries:
            print(f"\n🔍 Query: {query}")
            context = salon_ai.rag_agent.get_relevant_context(query)
            if context:
                print(f"📚 RAG Context Found: {context[:100]}...")
            else:
                print("   No specific context found - will use general AI knowledge")
        
        print("\n✅ RAG System Test Complete!")
        return True
        
    except Exception as e:
        print(f"❌ Error in RAG test: {e}")
        return False

def test_booking_flow():
    """Test complete booking flow"""
    print("\n📅 Testing Complete Booking Flow...")
    print("-" * 50)
    
    try:
        from voice_agent import AgenticSalonAI
        salon_ai = AgenticSalonAI()
        
        # Simulate booking conversation
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
        
        print("\n✅ Booking Flow Test Complete!")
        print("📊 Booking would be saved to database")
        print("📱 SMS notifications would be sent")
        return True
        
    except Exception as e:
        print(f"❌ Error in booking test: {e}")
        return False

def test_database():
    """Test database functionality"""
    print("\n🗄️ Testing Database System...")
    print("-" * 50)
    
    try:
        from voice_agent import DatabaseHandler
        db = DatabaseHandler()
        
        # Test booking data
        test_booking = {
            "booking_id": "TEST001",
            "customer_name": "Test Customer",
            "phone": "9876543210",
            "service": "Hair Coloring",
            "date": "Tomorrow",
            "time": "2 PM",
            "address": "123 Test Street",
            "status": "confirmed",
            "created_at": datetime.now().isoformat()
        }
        
        # Save test booking
        success = db.save_booking(test_booking)
        if success:
            print("✅ Test booking saved to database")
        else:
            print("❌ Failed to save test booking")
        
        # Test customer history
        history = db.get_customer_history("9876543210")
        print(f"📋 Customer history entries: {len(history)}")
        
        print("\n✅ Database Test Complete!")
        return True
        
    except Exception as e:
        print(f"❌ Error in database test: {e}")
        return False

def test_configuration():
    """Test configuration validation"""
    print("\n⚙️ Testing Configuration...")
    print("-" * 50)
    
    try:
        from config import config
        
        print(f"🔑 Gemini API Key: {'✅ Set' if config.GEMINI_API_KEY and not config.GEMINI_API_KEY.startswith('your_') else '❌ Not configured'}")
        print(f"📞 Twilio Account SID: {'✅ Set' if config.TWILIO_ACCOUNT_SID and not config.TWILIO_ACCOUNT_SID.startswith('your_') else '❌ Not configured'}")
        print(f"🔐 Twilio Auth Token: {'✅ Set' if config.TWILIO_AUTH_TOKEN and not config.TWILIO_AUTH_TOKEN.startswith('your_') else '❌ Not configured'}")
        print(f"📱 Twilio Phone: {'✅ Set' if config.TWILIO_PHONE_NUMBER and not config.TWILIO_PHONE_NUMBER.startswith('your_') else '❌ Not configured'}")
        print(f"🌐 Webhook URL: {'✅ Set' if config.WEBHOOK_URL and config.WEBHOOK_URL != 'https://your-domain.com' else '❌ Not configured'}")
        
        # Validate configuration
        is_valid = config.validate_config()
        print(f"\n📋 Configuration Status: {'✅ Valid' if is_valid else '❌ Invalid'}")
        
        return is_valid
        
    except Exception as e:
        print(f"❌ Error in configuration test: {e}")
        return False

def main():
    """Run all tests"""
    print("\n" + "="*80)
    print("🎯 AGENTIC SALON AI VOICE ASSISTANT - SYSTEM TESTS")
    print("="*80)
    print("🧪 Testing all major components...")
    print("="*80)
    
    tests = [
        ("Configuration", test_configuration),
        ("AI Conversation", test_ai_conversation),
        ("RAG System", test_rag_system),
        ("Database", test_database),
        ("Booking Flow", test_booking_flow)
    ]
    
    results = []
    
    for test_name, test_func in tests:
        print(f"\n🧪 Running {test_name} Test...")
        try:
            result = test_func()
            results.append((test_name, result))
        except Exception as e:
            print(f"❌ {test_name} test failed with error: {e}")
            results.append((test_name, False))
    
    # Summary
    print("\n" + "="*80)
    print("📊 TEST RESULTS SUMMARY")
    print("="*80)
    
    passed = 0
    for test_name, result in results:
        status = "✅ PASSED" if result else "❌ FAILED"
        print(f"{test_name}: {status}")
        if result:
            passed += 1
    
    print(f"\n🎯 Overall: {passed}/{len(results)} tests passed")
    
    if passed == len(results):
        print("🎉 All tests passed! System is ready for use.")
    else:
        print("⚠️  Some tests failed. Check configuration and dependencies.")
    
    print("\n" + "="*80)

if __name__ == "__main__":
    main()
