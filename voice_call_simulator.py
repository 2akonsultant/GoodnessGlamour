#!/usr/bin/env python3
"""
Voice Call Simulator for Testing
Simulates voice calls without requiring actual Twilio phone numbers
"""

import os
import json
import time
import logging
from datetime import datetime
from typing import Dict, List, Optional
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class VoiceCallSimulator:
    """Simulates voice calls for testing purposes"""
    
    def __init__(self):
        self.active_calls: Dict[str, Dict] = {}
        self.call_history: List[Dict] = []
    
    def simulate_voice_call(self, phone_number: str, source: str = "test") -> Dict:
        """Simulate a voice call"""
        call_id = f"sim_{int(time.time())}"
        
        # Create simulated call data
        call_data = {
            "call_sid": call_id,
            "phone_number": phone_number,
            "source": source,
            "status": "initiated",
            "created_at": datetime.now().isoformat(),
            "simulated": True
        }
        
        # Add to active calls
        self.active_calls[call_id] = call_data
        
        # Log the simulation
        logger.info(f"🎭 SIMULATED voice call to {phone_number}")
        logger.info(f"   Call ID: {call_id}")
        logger.info(f"   Source: {source}")
        
        # Simulate call progression
        self._simulate_call_progression(call_id)
        
        return {
            "success": True,
            "call_sid": call_id,
            "message": "Simulated voice call initiated",
            "phone_number": phone_number,
            "source": source,
            "simulated": True
        }
    
    def _simulate_call_progression(self, call_id: str):
        """Simulate call status progression"""
        call_data = self.active_calls.get(call_id)
        if not call_data:
            return
        
        # Simulate call status changes
        statuses = ["initiated", "ringing", "answered", "in-progress"]
        
        for status in statuses:
            time.sleep(1)  # Simulate time passing
            call_data["status"] = status
            logger.info(f"   📞 Call {call_id}: {status}")
            
            if status == "answered":
                # Simulate conversation
                self._simulate_conversation(call_id)
        
        # Complete the call
        call_data["status"] = "completed"
        call_data["completed_at"] = datetime.now().isoformat()
        
        # Move to history
        self.call_history.append(call_data.copy())
        del self.active_calls[call_id]
        
        logger.info(f"   ✅ Call {call_id}: completed")
    
    def _simulate_conversation(self, call_id: str):
        """Simulate AI conversation"""
        call_data = self.active_calls.get(call_id)
        if not call_data:
            return
        
        logger.info(f"   🤖 AI: Hello! Welcome to Goodness Glamour Salon. I'm your AI assistant.")
        time.sleep(2)
        
        logger.info(f"   👤 Customer: Hi, I want to book an appointment")
        time.sleep(2)
        
        logger.info(f"   🤖 AI: Great! What's your name?")
        time.sleep(2)
        
        logger.info(f"   👤 Customer: My name is Sarah")
        time.sleep(2)
        
        logger.info(f"   🤖 AI: Nice to meet you, Sarah! Which service would you like?")
        time.sleep(2)
        
        logger.info(f"   👤 Customer: I want a haircut")
        time.sleep(2)
        
        logger.info(f"   🤖 AI: Perfect! What date works for you?")
        time.sleep(2)
        
        logger.info(f"   👤 Customer: Tomorrow")
        time.sleep(2)
        
        logger.info(f"   🤖 AI: Great! What time would work? We're available 9 AM to 8 PM.")
        time.sleep(2)
        
        logger.info(f"   👤 Customer: 2 PM")
        time.sleep(2)
        
        logger.info(f"   🤖 AI: Perfect! What's your address for our doorstep service?")
        time.sleep(2)
        
        logger.info(f"   👤 Customer: 123 Main Street, Mumbai")
        time.sleep(2)
        
        logger.info(f"   🤖 AI: Let me confirm your booking...")
        time.sleep(2)
        
        logger.info(f"   🤖 AI: Booking confirmed! Booking ID: BG{int(time.time())}")
        time.sleep(2)
        
        logger.info(f"   🤖 AI: Thank you for choosing Goodness Glamour!")
        
        # Add booking to call data
        call_data["booking_created"] = {
            "customer_name": "Sarah",
            "service": "haircut",
            "date": "tomorrow",
            "time": "2 PM",
            "address": "123 Main Street, Mumbai",
            "booking_id": f"BG{int(time.time())}"
        }
    
    def get_call_status(self, call_id: str) -> Optional[Dict]:
        """Get status of a simulated call"""
        if call_id in self.active_calls:
            return self.active_calls[call_id]
        
        # Check history
        for call in self.call_history:
            if call["call_sid"] == call_id:
                return call
        
        return None
    
    def get_all_calls(self) -> List[Dict]:
        """Get all calls (active and history)"""
        all_calls = list(self.active_calls.values()) + self.call_history
        return sorted(all_calls, key=lambda x: x["created_at"], reverse=True)

def main():
    """Test the voice call simulator"""
    print("🎭 Voice Call Simulator - Testing Mode")
    print("=" * 50)
    
    simulator = VoiceCallSimulator()
    
    # Test phone numbers
    test_numbers = [
        "+917019035686",  # Your number
        "+919876543210",  # Test number
        "+919876543211"   # Another test number
    ]
    
    for phone_number in test_numbers:
        print(f"\n📞 Testing call to {phone_number}")
        print("-" * 30)
        
        result = simulator.simulate_voice_call(phone_number, "test_simulator")
        
        if result["success"]:
            print(f"✅ Simulated call initiated: {result['call_sid']}")
        else:
            print(f"❌ Failed to simulate call")
    
    print(f"\n📊 Call History:")
    print("-" * 30)
    
    all_calls = simulator.get_all_calls()
    for call in all_calls[:5]:  # Show last 5 calls
        print(f"📞 {call['phone_number']} - {call['status']} - {call['created_at']}")
        if "booking_created" in call:
            booking = call["booking_created"]
            print(f"   📋 Booking: {booking['customer_name']} - {booking['service']}")

if __name__ == '__main__':
    main()
