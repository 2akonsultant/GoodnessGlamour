#!/usr/bin/env python3
"""
ngrok Setup Guide for Voice Booking Assistant
Creates a public tunnel to your local server
"""

import os
import subprocess
import time
import requests
from pathlib import Path

def install_ngrok():
    """Install ngrok if not present"""
    print("🔧 Setting up ngrok for public webhook access...")
    
    # Check if ngrok is already installed
    try:
        result = subprocess.run(['ngrok', 'version'], capture_output=True, text=True)
        if result.returncode == 0:
            print("✅ ngrok is already installed")
            return True
    except FileNotFoundError:
        pass
    
    print("📥 ngrok not found. Please install it:")
    print("   1. Go to https://ngrok.com/")
    print("   2. Sign up for a free account")
    print("   3. Download ngrok for Windows")
    print("   4. Extract and add to PATH")
    print("   5. Run: ngrok authtoken YOUR_TOKEN")
    
    return False

def start_ngrok_tunnel(port=7001):
    """Start ngrok tunnel"""
    print(f"🚀 Starting ngrok tunnel on port {port}...")
    
    try:
        # Start ngrok in background
        process = subprocess.Popen(
            ['ngrok', 'http', str(port)],
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE
        )
        
        # Wait for ngrok to start
        time.sleep(3)
        
        # Get the public URL
        try:
            response = requests.get('http://localhost:4040/api/tunnels', timeout=5)
            if response.status_code == 200:
                tunnels = response.json()
                for tunnel in tunnels['tunnels']:
                    if tunnel['proto'] == 'https':
                        public_url = tunnel['public_url']
                        print(f"✅ ngrok tunnel created: {public_url}")
                        return public_url, process
        except Exception as e:
            print(f"⚠️ Could not get ngrok URL: {e}")
        
        print("✅ ngrok tunnel started (check http://localhost:4040 for URL)")
        return "https://your-ngrok-url.ngrok.io", process
        
    except Exception as e:
        print(f"❌ Failed to start ngrok: {e}")
        return None, None

def update_env_with_webhook(webhook_url):
    """Update .env file with webhook URL"""
    env_file = Path('.env')
    
    if not env_file.exists():
        print("❌ .env file not found")
        return False
    
    try:
        # Read current .env
        with open('.env', 'r') as f:
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
        with open('.env', 'w') as f:
            f.writelines(lines)
        
        print(f"✅ Updated .env with webhook URL: {webhook_url}")
        return True
        
    except Exception as e:
        print(f"❌ Failed to update .env: {e}")
        return False

def test_webhook_endpoints(webhook_url):
    """Test webhook endpoints"""
    print(f"🧪 Testing webhook endpoints...")
    
    endpoints = [
        "/health",
        "/verify-twilio",
        "/voice/incoming"
    ]
    
    for endpoint in endpoints:
        try:
            url = f"{webhook_url}{endpoint}"
            response = requests.get(url, timeout=5)
            print(f"✅ {endpoint}: {response.status_code}")
        except Exception as e:
            print(f"❌ {endpoint}: {e}")

def main():
    """Main setup function"""
    print("🌐 ngrok Setup for Voice Booking Assistant")
    print("=" * 50)
    
    # Check ngrok installation
    if not install_ngrok():
        print("\n💡 After installing ngrok, run this script again")
        return
    
    # Start ngrok tunnel
    webhook_url, ngrok_process = start_ngrok_tunnel()
    
    if webhook_url:
        # Update .env file
        update_env_with_webhook(webhook_url)
        
        # Test endpoints
        test_webhook_endpoints(webhook_url)
        
        print("\n🎉 Setup Complete!")
        print(f"📱 Your public webhook URL: {webhook_url}")
        print("\n📋 Next Steps:")
        print("1. Update Twilio webhook URLs in console")
        print("2. Test voice calls with real phone numbers")
        print("3. Generate QR codes for customers")
        
        print(f"\n🛑 To stop ngrok, press Ctrl+C or kill process {ngrok_process.pid}")
        
        # Keep ngrok running
        try:
            ngrok_process.wait()
        except KeyboardInterrupt:
            print("\n🛑 Stopping ngrok...")
            ngrok_process.terminate()
    else:
        print("❌ Failed to setup ngrok tunnel")

if __name__ == '__main__':
    main()
