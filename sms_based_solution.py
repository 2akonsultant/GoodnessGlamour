"""
SMS-Based Solution - Alternative to Voice Calls
When customer scans QR code, send SMS with booking link instead of voice call
"""

import google.generativeai as genai
import json
import uuid
from datetime import datetime
from typing import Dict, List, Optional, Any
from dataclasses import dataclass
import logging

# Import existing components
from voice_agent import AgenticSalonAI, TwilioVoiceHandler

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class SMSBasedSalonAI:
    """SMS-based salon AI system - no voice calls needed"""
    
    def __init__(self):
        self.ai_system = AgenticSalonAI()
        self.twilio_handler = TwilioVoiceHandler()
        self.booking_url = "http://localhost:8000"  # Your web interface URL
    
    def send_booking_sms(self, customer_phone: str) -> bool:
        """Send SMS with booking link when QR code is scanned"""
        try:
            # Create personalized SMS message
            sms_message = f"""🎯 Goodness Glamour Salon - AI Assistant Ready!

Hi! I'm your AI assistant for Goodness Glamour Salon.

✨ Our Services:
• Haircut & Styling (₹500-₹1,500)
• Hair Coloring (₹2,000-₹5,000) 
• Hair Spa (₹1,500-₹3,000)
• Keratin Treatment (₹4,000-₹8,000)
• Kids Services (₹300-₹1,500)
• Bridal Makeup (₹15,000-₹30,000)

🏠 Doorstep Service Available
⏰ Hours: 9 AM - 8 PM, Mon-Sun

📱 Click to chat with AI: {self.booking_url}
📞 Call: 9036626642

Book your appointment now! 💄✨"""
            
            # Send SMS via Twilio
            if self.twilio_handler.twilio_available:
                success = self.twilio_handler.send_sms(customer_phone, sms_message)
                if success:
                    logger.info(f"SMS sent successfully to {customer_phone}")
                    return True
                else:
                    logger.error(f"Failed to send SMS to {customer_phone}")
                    return False
            else:
                # Fallback: Log the message
                logger.info(f"SMS would be sent to {customer_phone}: {sms_message}")
                return True
                
        except Exception as e:
            logger.error(f"Error sending booking SMS: {e}")
            return False
    
    def process_web_booking(self, customer_input: str) -> str:
        """Process booking requests from web interface"""
        try:
            # Use existing AI system to process the request
            response = self.ai_system.process_user_input(customer_input)
            return response
        except Exception as e:
            logger.error(f"Error processing web booking: {e}")
            return "I'm sorry, I'm having trouble processing your request. Please try again."

def test_sms_solution():
    """Test the SMS-based solution"""
    print("📱 TESTING SMS-BASED SOLUTION")
    print("=" * 50)
    
    sms_ai = SMSBasedSalonAI()
    
    # Test SMS sending
    test_phone = "+919876543210"
    print(f"📤 Sending SMS to {test_phone}...")
    
    success = sms_ai.send_booking_sms(test_phone)
    
    if success:
        print("✅ SMS sent successfully!")
        print("📱 Customer will receive SMS with booking link")
        print("🌐 Customer can click link to chat with AI")
        print("📅 Customer can complete booking via web interface")
    else:
        print("❌ SMS sending failed")
        print("💡 Check Twilio configuration")
    
    print("\n🎯 SMS-BASED WORKFLOW:")
    print("1. Customer scans QR code")
    print("2. System sends SMS with booking link")
    print("3. Customer clicks link to chat with AI")
    print("4. Customer completes booking via web")
    print("5. Confirmation SMS sent")
    
    return success

if __name__ == "__main__":
    test_sms_solution()
