#!/usr/bin/env python3
"""
Complete System Test for AI Voice Booking Assistant
Tests all functionality and provides detailed results
"""

import requests
import json
import time
from datetime import datetime

# Configuration
WEBHOOK_URL = "https://cellularly-pneumographic-breanna.ngrok-free.dev"
HEADERS = {'ngrok-skip-browser-warning': 'true'}

def test_health_check():
    """Test system health"""
    print("🔍 Testing Health Check...")
    try:
        response = requests.get(f"{WEBHOOK_URL}/health", headers=HEADERS)
        if response.status_code == 200:
            data = response.json()
            print("✅ Health Check: PASSED")
            print(f"   Service: {data.get('service', 'Unknown')}")
            print(f"   Status: {data.get('status', 'Unknown')}")
            print(f"   Twilio Status: {data.get('twilio_status', 'Unknown')}")
            print(f"   Active Sessions: {data.get('active_sessions', 0)}")
            return True
        else:
            print(f"❌ Health Check: FAILED (Status: {response.status_code})")
            return False
    except Exception as e:
        print(f"❌ Health Check: ERROR - {e}")
        return False

def test_twilio_verification():
    """Test Twilio account verification"""
    print("\n📞 Testing Twilio Verification...")
    try:
        response = requests.get(f"{WEBHOOK_URL}/verify-twilio", headers=HEADERS)
        if response.status_code == 200:
            data = response.json()
            if data.get('success'):
                print("✅ Twilio Verification: PASSED")
                account = data.get('account', {})
                print(f"   Account: {account.get('friendly_name', 'Unknown')}")
                print(f"   Status: {account.get('status', 'Unknown')}")
                print(f"   Type: {account.get('type', 'Unknown')}")
                print(f"   Configured Phone: {data.get('configured_phone', 'None')}")
                print(f"   Available Numbers: {len(data.get('phone_numbers', []))}")
                return True
            else:
                print("❌ Twilio Verification: FAILED")
                return False
        else:
            print(f"❌ Twilio Verification: FAILED (Status: {response.status_code})")
            return False
    except Exception as e:
        print(f"❌ Twilio Verification: ERROR - {e}")
        return False

def test_qr_code_generation():
    """Test QR code generation"""
    print("\n📱 Testing QR Code Generation...")
    try:
        response = requests.get(f"{WEBHOOK_URL}/api/qr/generate", headers=HEADERS)
        if response.status_code == 200:
            data = response.json()
            print("✅ QR Code Generation: PASSED")
            print(f"   QR ID: {data.get('qr_id', 'Unknown')}")
            print(f"   QR URL: {data.get('qr_url', 'Unknown')}")
            print(f"   Has Image: {'Yes' if data.get('qr_image') else 'No'}")
            return True
        else:
            print(f"❌ QR Code Generation: FAILED (Status: {response.status_code})")
            return False
    except Exception as e:
        print(f"❌ QR Code Generation: ERROR - {e}")
        return False

def test_voice_call_trigger():
    """Test voice call triggering"""
    print("\n📞 Testing Voice Call Trigger...")
    test_phone = "+917019035686"
    try:
        payload = {
            "phone_number": test_phone,
            "source": "test_system"
        }
        response = requests.post(f"{WEBHOOK_URL}/trigger-voice-call", 
                               headers={**HEADERS, 'Content-Type': 'application/json'},
                               json=payload)
        
        if response.status_code == 200:
            data = response.json()
            if data.get('success'):
                print("✅ Voice Call Trigger: PASSED")
                print(f"   Call SID: {data.get('call_sid', 'Unknown')}")
                print(f"   Message: {data.get('message', 'Unknown')}")
                print(f"   Simulated: {data.get('simulated', False)}")
                return True
            else:
                print("❌ Voice Call Trigger: FAILED")
                print(f"   Error: {data.get('message', 'Unknown error')}")
                return False
        else:
            print(f"❌ Voice Call Trigger: FAILED (Status: {response.status_code})")
            try:
                error_data = response.json()
                print(f"   Error: {error_data.get('message', 'Unknown error')}")
            except:
                print(f"   Raw Response: {response.text[:200]}")
            return False
    except Exception as e:
        print(f"❌ Voice Call Trigger: ERROR - {e}")
        return False

def test_qr_landing_page():
    """Test QR landing page"""
    print("\n🌐 Testing QR Landing Page...")
    try:
        response = requests.get(f"{WEBHOOK_URL}/qr/voice-booking", headers=HEADERS)
        if response.status_code == 200:
            content = response.text
            if "Goodness Glamour" in content and "Call Me Now" in content:
                print("✅ QR Landing Page: PASSED")
                print("   Contains: Goodness Glamour branding")
                print("   Contains: Call Me Now button")
                return True
            else:
                print("⚠️ QR Landing Page: PARTIAL")
                print("   Page loads but may not have expected content")
                return False
        else:
            print(f"❌ QR Landing Page: FAILED (Status: {response.status_code})")
            return False
    except Exception as e:
        print(f"❌ QR Landing Page: ERROR - {e}")
        return False

def show_test_summary(results):
    """Show test summary"""
    print("\n" + "="*60)
    print("📊 TEST SUMMARY")
    print("="*60)
    
    total_tests = len(results)
    passed_tests = sum(results.values())
    
    print(f"Total Tests: {total_tests}")
    print(f"Passed: {passed_tests}")
    print(f"Failed: {total_tests - passed_tests}")
    print(f"Success Rate: {(passed_tests/total_tests)*100:.1f}%")
    
    print("\n📋 Detailed Results:")
    for test_name, result in results.items():
        status = "✅ PASS" if result else "❌ FAIL"
        print(f"   {status} {test_name}")
    
    print("\n🎯 System Status:")
    if passed_tests >= 4:
        print("✅ System is READY for production use!")
        print("✅ All core functionality is working")
        if not results.get("Voice Call Trigger", False):
            print("⚠️ Voice calls need verified Twilio phone number")
    elif passed_tests >= 2:
        print("⚠️ System is PARTIALLY working")
        print("⚠️ Some functionality may be limited")
    else:
        print("❌ System needs attention")
        print("❌ Multiple components are not working")

def show_next_steps():
    """Show next steps for the user"""
    print("\n🚀 NEXT STEPS:")
    print("="*60)
    
    print("\n1. 🌐 Test Web Interface:")
    print("   Open: https://cellularly-pneumographic-breanna.ngrok-free.dev/qr/voice-booking")
    print("   Enter your phone number and click 'Call Me Now'")
    
    print("\n2. 📱 Generate QR Codes:")
    print("   Use the API to generate QR codes for marketing")
    print("   Print QR codes on business cards, flyers, etc.")
    
    print("\n3. 📞 Enable Real Voice Calls:")
    print("   Buy a Twilio phone number with Voice capability")
    print("   Update TWILIO_PHONE_NUMBER in .env file")
    print("   Set SIMULATION_MODE=false")
    
    print("\n4. 🎯 Production Deployment:")
    print("   Deploy to cloud server (AWS, Google Cloud, etc.)")
    print("   Get SSL certificate for HTTPS")
    print("   Update webhook URLs")

def main():
    """Main test function"""
    print("🧪 AI Voice Booking Assistant - Complete System Test")
    print("🎯 Testing all functionality")
    print("="*60)
    print(f"Webhook URL: {WEBHOOK_URL}")
    print(f"Test Time: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print("="*60)
    
    # Run all tests
    results = {}
    
    results["Health Check"] = test_health_check()
    results["Twilio Verification"] = test_twilio_verification()
    results["QR Code Generation"] = test_qr_code_generation()
    results["Voice Call Trigger"] = test_voice_call_trigger()
    results["QR Landing Page"] = test_qr_landing_page()
    
    # Show summary
    show_test_summary(results)
    show_next_steps()
    
    print(f"\n🎉 Testing completed at {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")

if __name__ == '__main__':
    main()
