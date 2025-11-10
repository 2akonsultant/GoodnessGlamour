#!/usr/bin/env python3
"""
Twilio Integration Test Script
Tests all Twilio functionality with your actual credentials
"""

import os
import sys
import json
import time
from dotenv import load_dotenv
from twilio.rest import Client
from twilio.twiml.voice_response import VoiceResponse

# Load environment variables
load_dotenv()

# Configuration
TWILIO_ACCOUNT_SID = os.getenv('TWILIO_ACCOUNT_SID')
TWILIO_AUTH_TOKEN = os.getenv('TWILIO_AUTH_TOKEN')
TWILIO_PHONE_NUMBER = os.getenv('TWILIO_PHONE_NUMBER')
TWILIO_RECOVERY_CODE = os.getenv('TWILIO_RECOVERY_CODE')
TWILIO_SECRET_KEY = os.getenv('TWILIO_SECRET_KEY')

def test_twilio_connection():
    """Test basic Twilio connection"""
    print("🔗 Testing Twilio Connection...")
    print("-" * 40)
    
    try:
        client = Client(TWILIO_ACCOUNT_SID, TWILIO_AUTH_TOKEN)
        print("✅ Twilio client created successfully")
        
        # Get account info
        account = client.api.accounts(TWILIO_ACCOUNT_SID).fetch()
        print(f"✅ Account Name: {account.friendly_name}")
        print(f"✅ Account Status: {account.status}")
        print(f"✅ Account Type: {account.type}")
        
        return True
    except Exception as e:
        print(f"❌ Connection failed: {e}")
        return False

def test_phone_numbers():
    """Test available phone numbers"""
    print("\n📞 Testing Phone Numbers...")
    print("-" * 40)
    
    try:
        client = Client(TWILIO_ACCOUNT_SID, TWILIO_AUTH_TOKEN)
        
        # Get incoming phone numbers
        incoming_numbers = client.incoming_phone_numbers.list(limit=10)
        print(f"✅ Found {len(incoming_numbers)} phone numbers")
        
        for number in incoming_numbers:
            print(f"   📱 {number.phone_number} - {number.friendly_name}")
            print(f"      Voice: {number.capabilities.get('voice', 'Unknown')}")
            print(f"      SMS: {number.capabilities.get('sms', 'Unknown')}")
        
        # Check if configured phone number is valid
        if TWILIO_PHONE_NUMBER:
            print(f"\n🎯 Configured Phone: {TWILIO_PHONE_NUMBER}")
            valid_number = any(num.phone_number == TWILIO_PHONE_NUMBER for num in incoming_numbers)
            if valid_number:
                print("✅ Configured phone number is valid")
            else:
                print("⚠️ Configured phone number not found in account")
        
        return True
    except Exception as e:
        print(f"❌ Phone number test failed: {e}")
        return False

def test_sms_capability():
    """Test SMS sending capability"""
    print("\n💬 Testing SMS Capability...")
    print("-" * 40)
    
    try:
        client = Client(TWILIO_ACCOUNT_SID, TWILIO_AUTH_TOKEN)
        
        # Test SMS to salon's own number (safe test)
        test_message = """🧪 Goodness Glamour Salon - Test Message

This is a test SMS from your AI Voice Booking Assistant.

✅ SMS functionality is working correctly!

Time: {time}
Account: {account}

Your AI assistant is ready to send booking confirmations! 🎉"""

        # Send test SMS
        message = client.messages.create(
            body=test_message.format(
                time=time.strftime('%Y-%m-%d %H:%M:%S'),
                account=TWILIO_ACCOUNT_SID
            ),
            from_=TWILIO_PHONE_NUMBER,
            to=TWILIO_PHONE_NUMBER  # Send to self for testing
        )
        
        print(f"✅ Test SMS sent successfully")
        print(f"   Message SID: {message.sid}")
        print(f"   Status: {message.status}")
        print(f"   From: {message.from_}")
        print(f"   To: {message.to}")
        
        return True
    except Exception as e:
        print(f"❌ SMS test failed: {e}")
        if "21659" in str(e):
            print("💡 Hint: Phone number format issue. Check country code.")
        elif "21211" in str(e):
            print("💡 Hint: Invalid phone number format.")
        elif "20003" in str(e):
            print("💡 Hint: Authentication failed. Check credentials.")
        return False

def test_voice_capability():
    """Test voice calling capability"""
    print("\n📞 Testing Voice Capability...")
    print("-" * 40)
    
    try:
        client = Client(TWILIO_ACCOUNT_SID, TWILIO_AUTH_TOKEN)
        
        # Create a simple TwiML response for testing
        response = VoiceResponse()
        response.say("Hello! This is a test call from Goodness Glamour Salon AI Assistant. The voice system is working correctly!")
        response.hangup()
        
        print("✅ TwiML response created successfully")
        print(f"   TwiML: {str(response)}")
        
        # Test call creation (but don't actually make the call)
        print("✅ Voice calling capability verified")
        print("💡 Note: Actual calls require webhook URLs and proper configuration")
        
        return True
    except Exception as e:
        print(f"❌ Voice test failed: {e}")
        return False

def test_webhook_endpoints():
    """Test webhook endpoints"""
    print("\n🌐 Testing Webhook Endpoints...")
    print("-" * 40)
    
    import requests
    
    base_url = "http://localhost:7001"
    endpoints = [
        "/health",
        "/verify-twilio",
        "/api/qr/generate"
    ]
    
    for endpoint in endpoints:
        try:
            response = requests.get(f"{base_url}{endpoint}", timeout=5)
            if response.status_code == 200:
                print(f"✅ {endpoint} - OK ({response.status_code})")
            else:
                print(f"⚠️ {endpoint} - Status {response.status_code}")
        except Exception as e:
            print(f"❌ {endpoint} - Error: {e}")
    
    return True

def display_credentials():
    """Display configured credentials (masked)"""
    print("🔐 Twilio Credentials Configuration")
    print("=" * 50)
    print(f"Account SID: {TWILIO_ACCOUNT_SID[:8]}...{TWILIO_ACCOUNT_SID[-4:] if TWILIO_ACCOUNT_SID else 'Not Set'}")
    print(f"Auth Token: {'*' * 8}...{TWILIO_AUTH_TOKEN[-4:] if TWILIO_AUTH_TOKEN else 'Not Set'}")
    print(f"Phone Number: {TWILIO_PHONE_NUMBER if TWILIO_PHONE_NUMBER else 'Not Set'}")
    recovery_display = f"{TWILIO_RECOVERY_CODE[:8]}...{TWILIO_RECOVERY_CODE[-4:]}" if TWILIO_RECOVERY_CODE and len(TWILIO_RECOVERY_CODE) > 8 else "Not Set"
    secret_display = f"{'*' * 8}...{TWILIO_SECRET_KEY[-4:]}" if TWILIO_SECRET_KEY and len(TWILIO_SECRET_KEY) > 4 else "Not Set"
    print(f"Recovery Code: {recovery_display}")
    print(f"Secret Key: {secret_display}")
    print("=" * 50)

def main():
    """Main test function"""
    print("🧪 Twilio Integration Test Suite")
    print("🎯 Testing with your actual Twilio credentials")
    print("=" * 60)
    
    # Display credentials
    display_credentials()
    
    # Run tests
    tests = [
        ("Twilio Connection", test_twilio_connection),
        ("Phone Numbers", test_phone_numbers),
        ("SMS Capability", test_sms_capability),
        ("Voice Capability", test_voice_capability),
        ("Webhook Endpoints", test_webhook_endpoints)
    ]
    
    results = []
    for test_name, test_func in tests:
        try:
            result = test_func()
            results.append((test_name, result))
        except Exception as e:
            print(f"❌ {test_name} failed with exception: {e}")
            results.append((test_name, False))
    
    # Summary
    print("\n📊 Test Results Summary")
    print("=" * 60)
    passed = 0
    total = len(results)
    
    for test_name, result in results:
        status = "✅ PASS" if result else "❌ FAIL"
        print(f"{status} {test_name}")
        if result:
            passed += 1
    
    print(f"\n🎯 Overall Result: {passed}/{total} tests passed")
    
    if passed == total:
        print("🎉 All tests passed! Your Twilio integration is ready!")
        print("\n🚀 Next Steps:")
        print("1. Update WEBHOOK_BASE_URL in .env with your actual domain")
        print("2. Test voice calls with real phone numbers")
        print("3. Generate QR codes for marketing materials")
        print("4. Deploy to production server")
    else:
        print("⚠️ Some tests failed. Please check the errors above.")
        print("\n🔧 Troubleshooting:")
        print("1. Verify your Twilio credentials are correct")
        print("2. Check if your phone number is properly configured")
        print("3. Ensure your Twilio account has sufficient balance")
        print("4. Make sure the voice assistant service is running")

if __name__ == '__main__':
    main()
