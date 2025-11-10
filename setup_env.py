#!/usr/bin/env python3
"""
Environment Setup Script for Voice Booking Assistant
Creates .env file with Twilio credentials
"""

import os
from pathlib import Path

def create_env_file():
    """Create .env file with Twilio credentials"""
    
    env_content = """# AI Voice Booking Assistant - Environment Variables
# Twilio Configuration (Your Actual Credentials)
TWILIO_ACCOUNT_SID=ACd8941e7d6933a9e031879bc28d7af7e8
TWILIO_AUTH_TOKEN=815e90983ed99b02e52943cc14602d56
TWILIO_PHONE_NUMBER=+917019035686
TWILIO_RECOVERY_CODE=J4VXS81L35XTR3ZK54V8TX7A
TWILIO_SECRET_KEY=dUytv2kejZ0E3jPTgUyNCXV92zzfulJw

# Server Configuration
WEBHOOK_BASE_URL=https://your-domain.com
PORT=7001

# Simulation Mode (for testing without actual phone calls)
SIMULATION_MODE=true

# Optional: OpenAI Configuration (for enhanced conversations)
# OPENAI_API_KEY=your_openai_api_key_here

# Optional: Existing SalonBooker API
# SALONBOOKER_API_URL=http://localhost:5000
"""
    
    env_file = Path('.env')
    
    if env_file.exists():
        print("✅ .env file already exists")
        return True
    
    try:
        with open('.env', 'w') as f:
            f.write(env_content)
        print("✅ .env file created successfully")
        print("📝 Edit .env file to update WEBHOOK_BASE_URL with your actual domain")
        return True
    except Exception as e:
        print(f"❌ Error creating .env file: {e}")
        return False

def check_env_variables():
    """Check if environment variables are properly set"""
    from dotenv import load_dotenv
    load_dotenv()
    
    required_vars = ['TWILIO_ACCOUNT_SID', 'TWILIO_AUTH_TOKEN', 'TWILIO_PHONE_NUMBER']
    
    print("\n🔧 Checking environment variables:")
    print("-" * 40)
    
    all_set = True
    for var in required_vars:
        value = os.getenv(var)
        if value:
            print(f"✅ {var}: {'*' * 8}{value[-4:] if len(value) > 4 else '****'}")
        else:
            print(f"❌ {var}: Not set")
            all_set = False
    
    optional_vars = ['WEBHOOK_BASE_URL', 'PORT', 'OPENAI_API_KEY']
    for var in optional_vars:
        value = os.getenv(var)
        if value:
            print(f"✅ {var}: {value}")
        else:
            print(f"⚠️ {var}: Not set (optional)")
    
    print("-" * 40)
    return all_set

def main():
    """Main setup function"""
    print("🔧 Setting up Voice Booking Assistant Environment")
    print("=" * 50)
    
    # Create .env file
    if create_env_file():
        print("\n📋 Next steps:")
        print("1. Edit .env file to set your actual webhook URL")
        print("2. Run: python test_simple_voice.py")
        print("3. Run: python start_simple_voice.py")
        
        # Check environment variables
        check_env_variables()
        
        print("\n🎉 Setup complete!")
    else:
        print("\n❌ Setup failed. Please create .env file manually.")

if __name__ == '__main__':
    main()
