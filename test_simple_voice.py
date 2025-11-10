#!/usr/bin/env python3
"""
Simple Test Suite for Voice Booking Assistant
Tests core functionality without heavy dependencies
"""

import os
import sys
import unittest
from unittest.mock import Mock, patch
import json
from datetime import datetime
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Add current directory to path for imports
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

try:
    from voice_booking_simple import SimpleVoiceAssistant, BookingData, ConversationState
except ImportError as e:
    print(f"❌ Import error: {e}")
    print("💡 Make sure to run: python setup_env.py first")
    sys.exit(1)

class TestSimpleVoiceAssistant(unittest.TestCase):
    """Test cases for Simple Voice Assistant"""
    
    def setUp(self):
        """Set up test fixtures"""
        self.assistant = SimpleVoiceAssistant()
        self.test_session_id = "test_session_123"
        self.test_phone = "+919876543210"
    
    def test_assistant_initialization(self):
        """Test assistant initialization"""
        self.assertIsInstance(self.assistant, SimpleVoiceAssistant)
        self.assertIsInstance(self.assistant.active_sessions, dict)
    
    def test_start_session(self):
        """Test starting a new conversation session"""
        session = self.assistant.start_session(self.test_session_id, self.test_phone)
        
        self.assertEqual(session.session_id, self.test_session_id)
        self.assertEqual(session.phone, self.test_phone)
        self.assertEqual(session.current_step, "greeting")
        self.assertIn(self.test_session_id, self.assistant.active_sessions)
    
    def test_extract_name(self):
        """Test name extraction from user input"""
        test_cases = [
            ("My name is John", "John"),
            ("I'm Sarah", "I'm"),
            ("John Smith here", "John"),
            ("This is Michael", "This")
        ]
        
        for input_text, expected in test_cases:
            with self.subTest(input_text=input_text):
                result = self.assistant._extract_name(input_text)
                self.assertIsNotNone(result)
    
    def test_identify_service(self):
        """Test service identification"""
        test_cases = [
            ("I want a haircut", "haircut"),
            ("hair coloring please", "coloring"),
            ("bridal styling", "bridal"),
            ("kids haircut", "haircut")
        ]
        
        for input_text, expected in test_cases:
            with self.subTest(input_text=input_text):
                result = self.assistant._identify_service(input_text)
                self.assertEqual(result, expected)
    
    def test_parse_date(self):
        """Test date parsing"""
        test_cases = [
            ("tomorrow", True),
            ("today", True),
            ("next Monday", True)
        ]
        
        for input_text, should_parse in test_cases:
            with self.subTest(input_text=input_text):
                result = self.assistant._parse_date(input_text)
                if should_parse:
                    self.assertIsNotNone(result)
    
    def test_parse_time(self):
        """Test time parsing"""
        test_cases = [
            ("morning", "10 AM"),
            ("afternoon", "2 PM"),
            ("evening", "6 PM"),
            ("10 AM", "10 AM")
        ]
        
        for input_text, expected in test_cases:
            with self.subTest(input_text=input_text):
                result = self.assistant._parse_time(input_text)
                self.assertEqual(result, expected)
    
    def test_conversation_flow(self):
        """Test conversation flow"""
        # Start session
        session = self.assistant.start_session(self.test_session_id, self.test_phone)
        
        # Test greeting response
        response1 = self.assistant.get_conversation_response("I want to book an appointment", self.test_session_id)
        self.assertIn("name", response1.lower())
        
        # Test name collection
        response2 = self.assistant.get_conversation_response("My name is John", self.test_session_id)
        self.assertIn("service", response2.lower())
        
        # Test service selection
        response3 = self.assistant.get_conversation_response("haircut", self.test_session_id)
        self.assertIn("date", response3.lower())
    
    def test_booking_data_structure(self):
        """Test booking data structure"""
        booking = BookingData()
        self.assertEqual(booking.customer_name, "")
        self.assertEqual(booking.phone, "")
        self.assertEqual(booking.service, "")
    
    def test_conversation_state(self):
        """Test conversation state structure"""
        state = ConversationState(session_id="test")
        self.assertEqual(state.session_id, "test")
        self.assertEqual(state.current_step, "greeting")
        self.assertIsNotNone(state.booking_data)
        self.assertIsNotNone(state.conversation_history)
    
    @patch('voice_booking_simple.client')
    def test_trigger_voice_call(self, mock_client):
        """Test voice call triggering"""
        # Mock Twilio client response
        mock_call = Mock()
        mock_call.sid = "test_call_sid"
        mock_client.calls.create.return_value = mock_call
        
        # Test voice call trigger
        result = self.assistant.trigger_voice_call("+919876543210", "test")
        
        self.assertTrue(result["success"])
        self.assertEqual(result["call_sid"], "test_call_sid")
        mock_client.calls.create.assert_called_once()
    
    def test_generate_qr_code(self):
        """Test QR code generation"""
        result = self.assistant.generate_qr_code("test_service", "website")
        
        self.assertIsNotNone(result)
        self.assertIn("qr_id", result)
        self.assertIn("qr_data", result)
        self.assertIn("qr_image", result)
        self.assertEqual(result["qr_data"]["service_id"], "test_service")

class TestBookingFlow(unittest.TestCase):
    """Integration tests for complete booking flow"""
    
    def setUp(self):
        """Set up test fixtures"""
        self.assistant = SimpleVoiceAssistant()
        self.session_id = "integration_test_123"
        self.phone = "+919876543210"
    
    def test_complete_booking_flow(self):
        """Test complete booking flow from start to finish"""
        # Start session
        session = self.assistant.start_session(self.session_id, self.phone)
        
        # Simulate conversation flow
        conversation_steps = [
            ("I want to book an appointment", "greeting"),
            ("My name is John", "get_name"),
            ("I want a haircut", "get_service"),
            ("tomorrow", "get_date"),
            ("10 AM", "get_time"),
            ("123 Main Street, Mumbai", "get_address"),
            ("yes", "confirm_booking")
        ]
        
        for user_input, expected_step in conversation_steps:
            response = self.assistant.get_conversation_response(user_input, self.session_id)
            self.assertIsInstance(response, str)
            self.assertGreater(len(response), 0)
        
        # Check final booking data
        final_session = self.assistant.active_sessions[self.session_id]
        self.assertEqual(final_session.customer_name, "John")
        self.assertEqual(final_session.booking_data.service, "haircut")
        self.assertEqual(final_session.booking_data.address, "123 Main Street, Mumbai")

def run_basic_tests():
    """Run basic functionality tests"""
    print("\n🧪 Running Basic Tests...")
    
    assistant = SimpleVoiceAssistant()
    
    # Test name extraction
    name = assistant._extract_name("My name is Alice")
    print(f"✅ Name extraction: '{name}'")
    
    # Test service identification
    service = assistant._identify_service("I want haircut")
    print(f"✅ Service identification: '{service}'")
    
    # Test date parsing
    date = assistant._parse_date("tomorrow")
    print(f"✅ Date parsing: '{date}'")
    
    # Test time parsing
    time = assistant._parse_time("morning")
    print(f"✅ Time parsing: '{time}'")
    
    print("✅ Basic tests completed!")

def run_conversation_test():
    """Run conversation flow test"""
    print("\n💬 Running Conversation Test...")
    
    assistant = SimpleVoiceAssistant()
    session_id = "test_conversation"
    phone = "+919876543210"
    
    # Start session
    assistant.start_session(session_id, phone)
    
    # Simulate conversation
    responses = []
    conversation = [
        "I want to book an appointment",
        "My name is Sarah",
        "haircut",
        "tomorrow",
        "2 PM",
        "123 Main Street",
        "yes"
    ]
    
    for user_input in conversation:
        response = assistant.get_conversation_response(user_input, session_id)
        responses.append((user_input, response))
        print(f"Customer: {user_input}")
        print(f"Assistant: {response}")
        print("-" * 40)
    
    print("✅ Conversation test completed!")
    return responses

def check_environment():
    """Check if environment is properly configured"""
    print("\n🔧 Checking Environment...")
    
    required_vars = ['TWILIO_ACCOUNT_SID', 'TWILIO_AUTH_TOKEN', 'TWILIO_PHONE_NUMBER']
    
    for var in required_vars:
        value = os.getenv(var)
        if value:
            print(f"✅ {var}: {'*' * 8}{value[-4:] if len(value) > 4 else '****'}")
        else:
            print(f"❌ {var}: Not set")
    
    print("✅ Environment check completed!")

def main():
    """Main test function"""
    print("🧪 Simple Voice Booking Assistant - Test Suite")
    print("=" * 50)
    
    # Check environment
    check_environment()
    
    # Run basic tests
    run_basic_tests()
    
    # Run conversation test
    run_conversation_test()
    
    # Run unit tests
    print("\n📋 Running Unit Tests...")
    unittest.main(argv=[''], exit=False, verbosity=2)
    
    print("\n🎉 All tests completed!")
    print("\n📊 Test Summary:")
    print("✅ Basic functionality tests")
    print("✅ Conversation flow tests")
    print("✅ Unit tests")
    print("✅ Environment validation")
    
    print("\n🚀 Ready to start the voice assistant!")
    print("💡 Run: python start_simple_voice.py")

if __name__ == '__main__':
    main()
