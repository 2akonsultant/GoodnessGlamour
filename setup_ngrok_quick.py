#!/usr/bin/env python3
"""
Quick ngrok Setup Script
Automates the webhook URL setup process
"""

import os
import subprocess
import time
import requests
import json
from pathlib import Path

def check_ngrok_installed():
    """Check if ngrok is installed"""
    try:
        result = subprocess.run(['ngrok', 'version'], capture_output=True, text=True)
        if result.returncode == 0:
            print("✅ ngrok is installed")
            return True
    except FileNotFoundError:
        pass
    
    print("❌ ngrok not found")
    return False

def install_ngrok_instructions():
    """Show ngrok installation instructions"""
    print("\n📥 INSTALL NGROK:")
    print("=" * 40)
    print("1. Go to: https://ngrok.com/")
    print("2. Click 'Sign up for free'")
    print("3. Create account with your email")
    print("4. Download ngrok for Windows")
    print("5. Extract ngrok.exe to a folder")
    print("6. Add folder to PATH or use full path")
    print("\n💡 Quick install:")
    print("   - Download: https://bin.equinox.io/c/bNyj1mQVY4c/ngrok-v3-stable-windows-amd64.zip")
    print("   - Extract to C:\\ngrok\\")
    print("   - Add C:\\ngrok\\ to your PATH")

def get_ngrok_url():
    """Get the ngrok public URL"""
    try:
        response = requests.get('http://localhost:4040/api/tunnels', timeout=5)
        if response.status_code == 200:
            tunnels = response.json()
            for tunnel in tunnels['tunnels']:
                if tunnel['proto'] == 'https':
                    return tunnel['public_url']
    except Exception as e:
        print(f"⚠️ Could not get ngrok URL: {e}")
    return None

def update_env_file(webhook_url):
    """Update .env file with webhook URL"""
    env_file = Path('.env')
    
    if not env_file.exists():
        print("❌ .env file not found. Creating one...")
        create_env_file()
    
    try:
        # Read current .env
        with open('.env', 'r', encoding='utf-8') as f:
            lines = f.readlines()
        
        # Update or add WEBHOOK_BASE_URL
        updated = False
        for i, line in enumerate(lines):
            if line.startswith('WEBHOOK_BASE_URL='):
                lines[i] = f'WEBHOOK_BASE_URL={webhook_url}\n'
                updated = True
                break
        
        if not updated:
            lines.append(f'WEBHOOK_BASE_URL={webhook_url}\n')
        
        # Write back to .env
        with open('.env', 'w', encoding='utf-8') as f:
            f.writelines(lines)
        
        print(f"✅ Updated .env with webhook URL: {webhook_url}")
        return True
        
    except Exception as e:
        print(f"❌ Failed to update .env: {e}")
        return False

def create_env_file():
    """Create a basic .env file"""
    env_content = """TWILIO_ACCOUNT_SID=ACd8941e7d6933a9e031879bc28d7af7e8
TWILIO_AUTH_TOKEN=815e90983ed99b02e52943cc14602d56
TWILIO_PHONE_NUMBER=+917019035686
WEBHOOK_BASE_URL=https://your-domain.com
SIMULATION_MODE=true
PORT=7001
"""
    try:
        with open('.env', 'w', encoding='utf-8') as f:
            f.write(env_content)
        print("✅ Created .env file")
    except Exception as e:
        print(f"❌ Failed to create .env file: {e}")

def test_webhook_url(webhook_url):
    """Test if webhook URL is working"""
    print(f"\n🧪 Testing webhook URL: {webhook_url}")
    
    endpoints = [
        "/health",
        "/verify-twilio"
    ]
    
    for endpoint in endpoints:
        try:
            url = f"{webhook_url}{endpoint}"
            response = requests.get(url, timeout=5)
            if response.status_code == 200:
                print(f"✅ {endpoint}: Working")
            else:
                print(f"⚠️ {endpoint}: Status {response.status_code}")
        except Exception as e:
            print(f"❌ {endpoint}: {e}")

def start_ngrok_tunnel(port=7001):
    """Start ngrok tunnel"""
    print(f"\n🚀 Starting ngrok tunnel on port {port}...")
    
    try:
        # Start ngrok in background
        process = subprocess.Popen(
            ['ngrok', 'http', str(port)],
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE
        )
        
        print("⏳ Waiting for ngrok to start...")
        time.sleep(3)
        
        # Get the public URL
        webhook_url = get_ngrok_url()
        
        if webhook_url:
            print(f"✅ ngrok tunnel created: {webhook_url}")
            return webhook_url, process
        else:
            print("⚠️ Could not get ngrok URL automatically")
            print("💡 Check http://localhost:4040 for the ngrok dashboard")
            return None, process
        
    except Exception as e:
        print(f"❌ Failed to start ngrok: {e}")
        return None, None

def show_next_steps(webhook_url):
    """Show next steps after webhook setup"""
    print(f"\n🎉 WEBHOOK URL SETUP COMPLETE!")
    print("=" * 50)
    print(f"📱 Your webhook URL: {webhook_url}")
    
    print(f"\n📋 NEXT STEPS:")
    print("1. ✅ Webhook URL is configured")
    print("2. 🔄 Start your voice assistant:")
    print("   python voice_booking_simple.py")
    print("3. 🧪 Test the system:")
    print(f"   curl {webhook_url}/health")
    print("4. 📞 Buy a Twilio phone number for real calls")
    print("5. 🎯 Test voice calls with real numbers")
    
    print(f"\n🌐 NGROK DASHBOARD:")
    print("   http://localhost:4040")
    print("   (Shows all requests and tunnel status)")
    
    print(f"\n🛑 TO STOP NGROK:")
    print("   Press Ctrl+C in the ngrok window")

def main():
    """Main setup function"""
    print("🌐 WEBHOOK URL SETUP FOR AI VOICE BOOKING ASSISTANT")
    print("=" * 60)
    
    # Check if ngrok is installed
    if not check_ngrok_installed():
        install_ngrok_instructions()
        print("\n💡 After installing ngrok, run this script again")
        return
    
    # Start ngrok tunnel
    webhook_url, ngrok_process = start_ngrok_tunnel()
    
    if webhook_url:
        # Update .env file
        if update_env_file(webhook_url):
            # Test the webhook
            test_webhook_url(webhook_url)
            
            # Show next steps
            show_next_steps(webhook_url)
            
            # Keep ngrok running
            print(f"\n🔄 Keeping ngrok running...")
            print(f"💡 Your webhook URL is: {webhook_url}")
            print(f"🛑 Press Ctrl+C to stop")
            
            try:
                ngrok_process.wait()
            except KeyboardInterrupt:
                print(f"\n🛑 Stopping ngrok...")
                ngrok_process.terminate()
        else:
            print("❌ Failed to update .env file")
    else:
        print("❌ Failed to create ngrok tunnel")
        print("💡 Make sure ngrok is installed and try again")

if __name__ == '__main__':
    main()
