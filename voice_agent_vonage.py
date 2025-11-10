"""
Alternative Voice Agent using Vonage (Nexmo) instead of Twilio
"""

import google.generativeai as genai
import json
import uuid
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Any
from dataclasses import dataclass
import asyncio
import logging

# Optional imports with fallbacks
try:
    import speech_recognition as sr
    SPEECH_RECOGNITION_AVAILABLE = True
except ImportError:
    SPEECH_RECOGNITION_AVAILABLE = False
    sr = None

try:
    import pyttsx3
    TTS_AVAILABLE = True
except ImportError:
    TTS_AVAILABLE = False
    pyttsx3 = None

try:
    import chromadb
    from chromadb.config import Settings
    CHROMADB_AVAILABLE = True
except ImportError:
    CHROMADB_AVAILABLE = False
    chromadb = None
    Settings = None

# Vonage (Nexmo) imports
try:
    import vonage
    VONAGE_AVAILABLE = True
except ImportError:
    VONAGE_AVAILABLE = False
    vonage = None

try:
    import sqlite3
    import pandas as pd
    DATABASE_AVAILABLE = True
except ImportError:
    DATABASE_AVAILABLE = False
    sqlite3 = None
    pd = None

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Import configuration
try:
    from config import config
    GEMINI_API_KEY = config.GEMINI_API_KEY
    VONAGE_API_KEY = getattr(config, 'VONAGE_API_KEY', 'your_vonage_api_key')
    VONAGE_API_SECRET = getattr(config, 'VONAGE_API_SECRET', 'your_vonage_api_secret')
    VONAGE_PHONE_NUMBER = getattr(config, 'VONAGE_PHONE_NUMBER', 'your_vonage_phone_number')
    WEBHOOK_URL = config.WEBHOOK_URL
except ImportError:
    # Fallback configuration
    GEMINI_API_KEY = "AIzaSyDEw4nW0xV_FQKf1SUX9fFJwnEY5n8_Jwc"
    VONAGE_API_KEY = "your_vonage_api_key"
    VONAGE_API_SECRET = "your_vonage_api_secret"
    VONAGE_PHONE_NUMBER = "your_vonage_phone_number"
    WEBHOOK_URL = "https://your-domain.com"

# Configure Gemini AI
genai.configure(api_key=GEMINI_API_KEY)

# Salon context for the AI
SALON_CONTEXT = """
You are an AI assistant for Goodness Glamour Salon, a premium ladies and kids salon offering doorstep beauty services.

SALON INFORMATION:
- Name: Goodness Glamour Salon
- Contact: 9036626642
- Email: 2akonsultant@gmail.com
- Service Hours: Monday - Sunday, 9:00 AM - 8:00 PM
- Service Type: We provide doorstep services across the city

SERVICES & PRICES:

Women's Hair Services:
- Haircut & Styling: ₹500 - ₹1,500
- Hair Coloring: ₹2,000 - ₹5,000
- Hair Spa Treatment: ₹1,500 - ₹3,000
- Keratin Treatment: ₹4,000 - ₹8,000

Kids Hair Services:
- Kids Haircut: ₹300 - ₹700
- Party Hairstyle: ₹800 - ₹1,500
- Creative Braiding: ₹500 - ₹1,200

Bridal & Party Services:
- Bridal Hair & Makeup: ₹15,000 - ₹30,000
- Party Makeup: ₹3,000 - ₹8,000

KEY FEATURES:
- Doorstep service (we come to your home)
- Professional stylists with 5+ years experience
- Premium products used
- Flexible timing (9 AM - 8 PM)

Be friendly, professional, and encourage customers to book appointments through our website.
"""

class VonageVoiceHandler:
    """Handles Vonage voice calls and SMS"""
    
    def __init__(self):
        # Try to import and initialize Vonage directly
        try:
            import vonage
            self.client = vonage.Client(
                key=VONAGE_API_KEY,
                secret=VONAGE_API_SECRET
            )
            self.vonage_available = True
            logger.info("Vonage client initialized successfully")
        except ImportError as e:
            logger.error(f"Vonage import failed: {e}")
            self.vonage_available = False
            self.client = None
        except Exception as e:
            logger.error(f"Vonage initialization failed: {e}")
            self.vonage_available = False
            self.client = None
    
    def make_voice_call(self, customer_phone: str, webhook_url: str) -> bool:
        """Make a voice call to customer using Vonage"""
        if not self.vonage_available:
            logger.warning("Vonage not available. Cannot make voice call.")
            return False
        
        try:
            # Vonage voice call
            response = self.client.voice.create_call({
                'to': [{'type': 'phone', 'number': customer_phone}],
                'from': {'type': 'phone', 'number': VONAGE_PHONE_NUMBER},
                'ncco': [
                    {
                        'action': 'talk',
                        'text': 'Hello! Welcome to Goodness Glamour Salon. How can I help you today?'
                    },
                    {
                        'action': 'input',
                        'type': ['speech'],
                        'speech': {
                            'endOnSilence': 3,
                            'language': 'en-IN'
                        },
                        'eventUrl': [f'{webhook_url}/voice/process']
                    }
                ]
            })
            
            logger.info(f"Vonage voice call initiated to {customer_phone}. Call ID: {response.get('uuid')}")
            return True
        except Exception as e:
            logger.error(f"Failed to make Vonage voice call: {e}")
            return False
    
    def send_sms(self, to_phone: str, message: str) -> bool:
        """Send SMS via Vonage"""
        if not self.vonage_available:
            logger.warning("Vonage not available. Cannot send SMS.")
            return False
        
        try:
            response = self.client.sms.send_message({
                'from': VONAGE_PHONE_NUMBER,
                'to': to_phone,
                'text': message
            })
            
            logger.info(f"Vonage SMS sent to {to_phone}. Message ID: {response.get('messages', [{}])[0].get('message-id')}")
            return True
        except Exception as e:
            logger.error(f"Failed to send Vonage SMS: {e}")
            return False

# Test the Vonage integration
def test_vonage_integration():
    """Test Vonage integration"""
    print("🔍 TESTING VONAGE INTEGRATION")
    print("=" * 50)
    
    vonage_handler = VonageVoiceHandler()
    print(f"✅ Vonage Available: {vonage_handler.vonage_available}")
    
    if vonage_handler.vonage_available:
        print("✅ Vonage client initialized successfully")
        print("📞 Ready to make voice calls")
        print("📱 Ready to send SMS")
    else:
        print("❌ Vonage not available")
        print("💡 Install: pip install vonage")
        print("💡 Configure API keys in config.py")
    
    return vonage_handler.vonage_available

if __name__ == "__main__":
    test_vonage_integration()
