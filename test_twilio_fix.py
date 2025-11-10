#!/usr/bin/env python3
"""
Test script to check Twilio account status and provide solutions
"""

from twilio.rest import Client
import sys

def check_twilio_account():
    """Check Twilio account status and provide solutions"""
    
    # Your Twilio credentials
    account_sid = "ACd8941e7d6933a9e031879bc28d7af7e8"
    auth_token = "815e90983ed99b02e52943cc14602d56"
    
    try:
        client = Client(account_sid, auth_token)
        
        print("🔍 CHECKING TWILIO ACCOUNT STATUS")
        print("=" * 50)
        
        # Get account info
        account = client.api.accounts(account_sid).fetch()
        print(f"✅ Account Status: {account.status}")
        print(f"📊 Account Type: {account.type}")
        print(f"🏷️  Account Name: {account.friendly_name}")
        
        # Check if it's trial account
        if account.type == "Trial":
            print("\n⚠️  TRIAL ACCOUNT DETECTED!")
            print("This is why you're getting DNO errors.")
            print("\n🔧 SOLUTIONS:")
            print("1. Upgrade to Full Account (Recommended)")
            print("   - Go to: https://console.twilio.com")
            print("   - Add payment method")
            print("   - Upgrade from Trial to Full")
            print("\n2. Use Only Verified Numbers")
            print("   - Go to: Phone Numbers → Verified Caller IDs")
            print("   - Add and verify phone numbers")
            print("   - Only verified numbers can receive calls")
            print("\n3. Purchase Twilio Phone Number")
            print("   - Go to: Phone Numbers → Buy a number")
            print("   - Purchase a business phone number")
            print("   - Update config with new number")
        
        # Check owned phone numbers
        print("\n📞 CHECKING OWNED PHONE NUMBERS")
        print("-" * 30)
        numbers = client.incoming_phone_numbers.list()
        
        if numbers:
            print(f"✅ Found {len(numbers)} owned numbers:")
            for num in numbers:
                print(f"   📱 {num.phone_number} - Status: {num.status}")
        else:
            print("❌ No phone numbers owned")
            print("💡 Solution: Purchase a phone number from Twilio")
        
        # Check verified caller IDs
        print("\n✅ CHECKING VERIFIED CALLER IDs")
        print("-" * 30)
        try:
            verified_numbers = client.outgoing_caller_ids.list()
            if verified_numbers:
                print(f"✅ Found {len(verified_numbers)} verified numbers:")
                for num in verified_numbers:
                    print(f"   📱 {num.phone_number} - Status: {num.status}")
            else:
                print("❌ No verified caller IDs")
                print("💡 Solution: Add and verify phone numbers")
        except Exception as e:
            print(f"⚠️  Could not check verified numbers: {e}")
        
        print("\n🎯 RECOMMENDED ACTION:")
        print("1. Upgrade your Twilio account to Full (remove all restrictions)")
        print("2. Or verify the phone numbers you want to call")
        print("3. Or purchase a Twilio phone number")
        
        return True
        
    except Exception as e:
        print(f"❌ Error checking Twilio account: {e}")
        return False

if __name__ == "__main__":
    check_twilio_account()
