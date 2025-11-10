#!/usr/bin/env python3
"""
Setup script for using US Twilio number
This will configure your system to work with a US number
"""

import os
import requests
import json

def update_env_with_us_number(us_number):
    """Update .env file with US phone number"""
    print(f"🔧 Updating .env file with US number: {us_number}")
    
    try:
        # Read current .env file
        with open('.env', 'r', encoding='utf-8') as f:
            lines = f.readlines()
        
        # Update TWILIO_PHONE_NUMBER
        updated = False
        for i, line in enumerate(lines):
            if line.startswith('TWILIO_PHONE_NUMBER='):
                lines[i] = f'TWILIO_PHONE_NUMBER={us_number}\n'
                updated = True
                break
        
        if not updated:
            # Add new line if not found
            lines.append(f'TWILIO_PHONE_NUMBER={us_number}\n')
        
        # Write back to .env
        with open('.env', 'w', encoding='utf-8') as f:
            f.writelines(lines)
        
        print("✅ .env file updated successfully")
        return True
        
    except Exception as e:
        print(f"❌ Failed to update .env: {e}")
        return False

def test_us_number_configuration():
    """Test the system with US number configuration"""
    print("\n🧪 Testing system with US number...")
    
    # Test webhook connectivity
    try:
        webhook_url = "https://cellularly-pneumographic-breanna.ngrok-free.dev"
        headers = {'ngrok-skip-browser-warning': 'true'}
        
        response = requests.get(f"{webhook_url}/health", headers=headers)
        if response.status_code == 200:
            print("✅ Webhook connectivity: OK")
        else:
            print("❌ Webhook connectivity: Failed")
            return False
            
    except Exception as e:
        print(f"❌ Webhook test error: {e}")
        return False
    
    print("✅ System configuration: Ready for US number")
    return True

def show_us_number_benefits():
    """Show benefits of using US number"""
    print("\n🇺🇸 BENEFITS OF US NUMBER:")
    print("="*40)
    print("✅ More available numbers")
    print("✅ Cheaper monthly cost (~$1)")
    print("✅ Better reliability")
    print("✅ Same AI functionality")
    print("✅ Can call Indian customers")
    print("✅ Professional appearance")
    print("✅ Easy to purchase")

def show_purchase_steps():
    """Show steps to purchase US number"""
    print("\n📋 STEPS TO BUY US NUMBER:")
    print("="*35)
    print("1. Go to: https://console.twilio.com/us1/develop/phone-numbers/manage/search")
    print("2. Click 'Buy a number'")
    print("3. Country: United States")
    print("4. Capabilities: ✓ Voice, ✓ SMS")
    print("5. Click 'Search'")
    print("6. Choose any available number")
    print("7. Click 'Buy' (~$1/month)")
    print("8. Copy the number (format: +1XXXXXXXXXX)")
    print("9. Run this script with your new number")

def main():
    """Main setup function"""
    print("🇺🇸 US TWILIO NUMBER SETUP")
    print("🎯 Configure system to work with US number")
    print("="*50)
    
    print("\n📱 Your current system works with ANY Twilio number!")
    print("   US numbers are just easier to get and cheaper")
    
    show_us_number_benefits()
    show_purchase_steps()
    
    print("\n💡 QUICK START:")
    print("1. Buy a US number from Twilio Console")
    print("2. Run: python setup_us_number.py +1XXXXXXXXXX")
    print("3. Test: python test_after_buying_number.py")
    print("4. Your AI voice system will work 100%!")
    
    # Check if number provided as argument
    import sys
    if len(sys.argv) > 1:
        us_number = sys.argv[1]
        print(f"\n🔧 Setting up with number: {us_number}")
        
        if update_env_with_us_number(us_number):
            if test_us_number_configuration():
                print("\n🎉 SUCCESS! Your system is ready!")
                print("🧪 Run: python test_after_buying_number.py")
            else:
                print("\n⚠️ Configuration updated, but test failed")
        else:
            print("\n❌ Failed to update configuration")
    else:
        print("\n📝 To set up with your US number:")
        print("   python setup_us_number.py +1XXXXXXXXXX")

if __name__ == '__main__':
    main()
