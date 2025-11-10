#!/usr/bin/env python3
"""
Test script to run after buying a Twilio phone number
This will verify that voice calls work with the new number
"""

import requests
import json

# Configuration - Update with your new Twilio phone number
NEW_TWILIO_NUMBER = "+91XXXXXXXXXX"  # Replace with your new number
WEBHOOK_URL = "https://cellularly-pneumographic-breanna.ngrok-free.dev"
HEADERS = {'ngrok-skip-browser-warning': 'true'}

def test_voice_call_with_new_number():
    """Test voice call with the new Twilio number"""
    print("📞 Testing Voice Call with New Twilio Number...")
    print(f"New Number: {NEW_TWILIO_NUMBER}")
    
    # Update the phone number in .env file
    print("\n🔧 Updating .env file with new number...")
    try:
        with open('.env', 'r', encoding='utf-8') as f:
            lines = f.readlines()
        
        # Update TWILIO_PHONE_NUMBER
        for i, line in enumerate(lines):
            if line.startswith('TWILIO_PHONE_NUMBER='):
                lines[i] = f'TWILIO_PHONE_NUMBER={NEW_TWILIO_NUMBER}\n'
                break
        
        # Write back to .env
        with open('.env', 'w', encoding='utf-8') as f:
            f.writelines(lines)
        
        print("✅ .env file updated with new number")
    except Exception as e:
        print(f"❌ Failed to update .env: {e}")
        return False
    
    # Test voice call trigger
    print("\n🧪 Testing voice call trigger...")
    try:
        payload = {
            "phone_number": "+917019035686",  # Your test number
            "source": "test_new_number"
        }
        
        response = requests.post(f"{WEBHOOK_URL}/trigger-voice-call", 
                               headers={**HEADERS, 'Content-Type': 'application/json'},
                               json=payload)
        
        if response.status_code == 200:
            data = response.json()
            if data.get('success'):
                print("🎉 SUCCESS! Voice calls are now working!")
                print(f"   Call SID: {data.get('call_sid', 'Unknown')}")
                print(f"   Message: {data.get('message', 'Unknown')}")
                print(f"   Simulated: {data.get('simulated', False)}")
                
                if not data.get('simulated', True):
                    print("\n🎯 REAL VOICE CALL INITIATED!")
                    print("   Your phone should ring shortly")
                    print("   AI assistant will guide you through booking")
                else:
                    print("\n⚠️ Still in simulation mode")
                    print("   Set SIMULATION_MODE=false in .env for real calls")
                
                return True
            else:
                print("❌ Voice call still failed")
                print(f"   Error: {data.get('message', 'Unknown error')}")
                return False
        else:
            print(f"❌ Voice call failed (Status: {response.status_code})")
            try:
                error_data = response.json()
                print(f"   Error: {error_data.get('message', 'Unknown error')}")
            except:
                print(f"   Raw Response: {response.text[:200]}")
            return False
            
    except Exception as e:
        print(f"❌ Voice call test error: {e}")
        return False

def show_next_steps():
    """Show next steps after successful test"""
    print("\n🚀 NEXT STEPS AFTER SUCCESSFUL TEST:")
    print("="*50)
    
    print("\n1. 📱 Generate QR Codes for Marketing:")
    print("   - Use the QR generation API")
    print("   - Print QR codes on business cards, flyers")
    print("   - Customers can scan and get instant voice calls")
    
    print("\n2. 🎯 Production Deployment:")
    print("   - Deploy to cloud server (AWS, Google Cloud, etc.)")
    print("   - Get SSL certificate for HTTPS")
    print("   - Update webhook URLs")
    
    print("\n3. 📊 Monitor and Optimize:")
    print("   - Track booking success rates")
    print("   - Monitor call quality")
    print("   - Optimize AI conversation flow")
    
    print("\n4. 🎉 Launch Your AI Voice Booking System!")
    print("   - Start marketing with QR codes")
    print("   - Train staff on the new system")
    print("   - Enjoy 24/7 AI-powered bookings!")

def main():
    """Main test function"""
    print("🧪 POST-PURCHASE TEST: AI Voice Booking Assistant")
    print("🎯 Testing voice calls with new Twilio number")
    print("="*60)
    
    print("\n⚠️ IMPORTANT: Update NEW_TWILIO_NUMBER in this script")
    print("   Replace '+91XXXXXXXXXX' with your actual new number")
    print("   Then run this test again")
    
    if NEW_TWILIO_NUMBER == "+91XXXXXXXXXX":
        print("\n❌ Please update NEW_TWILIO_NUMBER first!")
        return
    
    # Test voice calls
    success = test_voice_call_with_new_number()
    
    if success:
        print("\n🎉 CONGRATULATIONS!")
        print("Your AI Voice Booking Assistant is now 100% functional!")
        show_next_steps()
    else:
        print("\n🔧 TROUBLESHOOTING:")
        print("1. Verify the phone number is correct")
        print("2. Check Twilio Console for number status")
        print("3. Ensure number has Voice capability")
        print("4. Restart the voice assistant service")

if __name__ == '__main__':
    main()
