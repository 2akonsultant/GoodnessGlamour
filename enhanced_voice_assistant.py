"""
Enhanced AI Voice Booking Assistant with OpenAI Integration
Advanced conversation handling with natural language processing
"""

import os
import json
import uuid
import logging
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Any
from dataclasses import dataclass, asdict
import asyncio
from flask import Flask, request, Response
from twilio.twiml import VoiceResponse
from twilio.rest import Client
import openai

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Configuration
TWILIO_ACCOUNT_SID = os.getenv('TWILIO_ACCOUNT_SID', 'ACd8941e7d6933a9e031879bc28d7af7e8')
TWILIO_AUTH_TOKEN = os.getenv('TWILIO_AUTH_TOKEN', '815e90983ed99b02e52943cc14602d56')
TWILIO_PHONE_NUMBER = os.getenv('TWILIO_PHONE_NUMBER', '+917019035686')
WEBHOOK_BASE_URL = os.getenv('WEBHOOK_BASE_URL', 'https://your-domain.com')
OPENAI_API_KEY = os.getenv('OPENAI_API_KEY')

# Initialize clients
client = Client(TWILIO_ACCOUNT_SID, TWILIO_AUTH_TOKEN)
openai_client = openai.OpenAI(api_key=OPENAI_API_KEY) if OPENAI_API_KEY else None

# Salon Information
SALON_INFO = {
    "name": "Goodness Glamour Salon",
    "phone": "9036626642",
    "email": "2akonsultant@gmail.com",
    "hours": "Monday - Sunday, 9:00 AM - 8:00 PM",
    "service_type": "Doorstep beauty services"
}

# Services and Pricing
SERVICES = {
    "women": {
        "haircut": {"name": "Women's Haircut & Styling", "price": "₹400-1,200", "duration": "60 minutes"},
        "coloring": {"name": "Hair Coloring & Highlights", "price": "₹1,200-3,500", "duration": "120 minutes"},
        "treatment": {"name": "Hair Treatment & Spa", "price": "₹600-2,000", "duration": "90 minutes"},
        "bridal": {"name": "Bridal & Party Styling", "price": "₹800-2,500", "duration": "90 minutes"},
        "blowdry": {"name": "Professional Blowdry", "price": "₹250-600", "duration": "45 minutes"},
        "hairwash": {"name": "Hair Wash & Styling", "price": "₹200-450", "duration": "30 minutes"},
        "consultation": {"name": "Hair Consultation", "price": "₹150-300", "duration": "30 minutes"}
    },
    "kids": {
        "haircut": {"name": "Kids Haircuts", "price": "₹150-500", "duration": "30 minutes"},
        "party": {"name": "Party Styling", "price": "₹200-600", "duration": "45 minutes"},
        "hairwash": {"name": "Kids Hair Wash", "price": "₹100-300", "duration": "20 minutes"},
        "braiding": {"name": "Creative Braiding", "price": "₹150-400", "duration": "30 minutes"}
    }
}

@dataclass
class BookingData:
    customer_name: str = ""
    phone: str = ""
    service: str = ""
    date: str = ""
    time: str = ""
    address: str = ""
    notes: str = ""

@dataclass
class ConversationState:
    session_id: str
    customer_name: Optional[str] = None
    phone: Optional[str] = None
    current_step: str = "greeting"
    booking_data: BookingData = None
    conversation_history: List[Dict] = None
    
    def __post_init__(self):
        if self.booking_data is None:
            self.booking_data = BookingData()
        if self.conversation_history is None:
            self.conversation_history = []

class EnhancedVoiceAssistant:
    """
    Enhanced AI Voice Assistant with OpenAI integration for natural conversations
    """
    
    def __init__(self):
        self.active_sessions: Dict[str, ConversationState] = {}
        
        # Enhanced system prompt for OpenAI
        self.system_prompt = """You are a friendly and professional AI voice assistant for Goodness Glamour Salon, a premium doorstep beauty services company. Your task is to help callers schedule salon appointments by phone.

CRITICAL VOICE CONVERSATION REQUIREMENTS:
- Keep responses SHORT and CLEAR (maximum 15-20 words per response)
- Use a WARM, PROFESSIONAL, and CONVERSATIONAL tone
- Speak naturally like a helpful salon receptionist
- Always CONFIRM details before proceeding
- Be patient and understanding with customers

SALON INFORMATION:
- Name: Goodness Glamour Salon
- Contact: 9036626642
- Service: Doorstep beauty services (we come to your home)
- Hours: Monday - Sunday, 9:00 AM - 8:00 PM

SERVICES AVAILABLE:
Women's Services:
- Haircut & Styling: ₹400-1,200 (60 min)
- Hair Coloring: ₹1,200-3,500 (120 min)
- Hair Treatment: ₹600-2,000 (90 min)
- Bridal Styling: ₹800-2,500 (90 min)
- Blowdry: ₹250-600 (45 min)
- Hair Wash: ₹200-450 (30 min)
- Consultation: ₹150-300 (30 min)

Kids Services:
- Kids Haircut: ₹150-500 (30 min)
- Party Styling: ₹200-600 (45 min)
- Hair Wash: ₹100-300 (20 min)
- Creative Braiding: ₹150-400 (30 min)

CONVERSATION FLOW STEPS:
1. GREETING: Warmly greet caller, introduce yourself as Goodness Glamour's AI assistant
2. NAME: Ask for customer's name and confirm it
3. SERVICE: Ask which service they'd like, provide 2-3 options if they're unsure
4. DATE: Ask for preferred date (mention we're available 9 AM to 8 PM)
5. TIME: Ask for preferred time within our hours
6. ADDRESS: Ask for their address for doorstep service
7. CONFIRM: Repeat all details clearly and ask for confirmation
8. BOOK: Confirm booking and provide booking ID
9. CLOSE: Thank them and mention they'll receive SMS confirmation

RESPONSE STYLE EXAMPLES:
❌ "Hello, thank you for calling Goodness Glamour Salon. I am an AI assistant and I can help you book an appointment. What is your name?"
✅ "Hi! Welcome to Goodness Glamour. I'm your AI assistant. How can I help you today?"

❌ "Which service would you like to book from our comprehensive list of beauty services?"
✅ "What service are you interested in? We do haircuts, coloring, treatments, and bridal styling."

❌ "Could you please provide your complete residential address for our doorstep service delivery?"
✅ "What's your address? We'll come to your home."

Remember: Keep responses SHORT, FRIENDLY, and CONVERSATIONAL. Always confirm details before proceeding. Use natural speech patterns, not robotic responses."""

    def get_ai_response(self, user_input: str, conversation_history: List[Dict], current_step: str) -> str:
        """Get AI response using OpenAI API"""
        if not openai_client:
            return self._get_fallback_response(user_input, current_step)
        
        try:
            # Prepare messages for OpenAI
            messages = [
                {"role": "system", "content": self.system_prompt},
                {"role": "system", "content": f"Current conversation step: {current_step}"}
            ]
            
            # Add conversation history
            messages.extend(conversation_history[-6:])  # Last 6 messages for context
            
            # Add current user input
            messages.append({"role": "user", "content": user_input})
            
            # Get response from OpenAI
            response = openai_client.chat.completions.create(
                model="gpt-3.5-turbo",
                messages=messages,
                max_tokens=100,
                temperature=0.7,
                presence_penalty=0.1,
                frequency_penalty=0.1
            )
            
            return response.choices[0].message.content.strip()
            
        except Exception as e:
            logger.error(f"OpenAI API error: {e}")
            return self._get_fallback_response(user_input, current_step)

    def _get_fallback_response(self, user_input: str, current_step: str) -> str:
        """Fallback responses when OpenAI is not available"""
        user_input_lower = user_input.lower().strip()
        
        if current_step == "greeting":
            if any(word in user_input_lower for word in ["book", "appointment", "schedule", "service"]):
                return "Great! I'd love to help you book an appointment. What's your name?"
            else:
                return "Hello! Welcome to Goodness Glamour Salon. I'm your AI assistant. How can I help you today?"
        
        elif current_step == "get_name":
            return "I didn't catch your name. Could you please tell me your name?"
        
        elif current_step == "get_service":
            return "Which service interests you? We do haircuts, coloring, treatments, and bridal styling."
        
        elif current_step == "get_date":
            return "What date would you like? You can say tomorrow, or a specific date."
        
        elif current_step == "get_time":
            return "What time works for you? We're available 9 AM to 8 PM."
        
        elif current_step == "get_address":
            return "What's your address? We'll come to your home."
        
        elif current_step == "confirm_booking":
            if any(word in user_input_lower for word in ["yes", "confirm", "correct", "book"]):
                return "Perfect! Your booking is confirmed. You'll receive SMS confirmation shortly."
            else:
                return "Please say 'yes' to confirm or 'no' to make changes."
        
        return "I'm here to help! How can I assist you today?"

    def extract_booking_info(self, user_input: str, current_step: str) -> Dict[str, Any]:
        """Extract structured information from user input"""
        user_input_lower = user_input.lower().strip()
        extracted = {}
        
        if current_step == "get_name":
            # Extract name (simple approach)
            words = user_input.split()
            if len(words) >= 1:
                extracted["name"] = words[0].capitalize()
        
        elif current_step == "get_service":
            # Extract service
            service_mapping = {
                "haircut": ["haircut", "cut", "trim"],
                "coloring": ["color", "coloring", "highlight", "dye"],
                "treatment": ["treatment", "spa", "keratin", "therapy"],
                "bridal": ["bridal", "wedding", "party", "styling"],
                "blowdry": ["blowdry", "blow dry", "style"],
                "hairwash": ["wash", "shampoo", "clean"],
                "consultation": ["consultation", "advice", "consult"]
            }
            
            for service, keywords in service_mapping.items():
                if any(keyword in user_input_lower for keyword in keywords):
                    extracted["service"] = service
                    break
        
        elif current_step == "get_date":
            # Extract date
            if "tomorrow" in user_input_lower:
                tomorrow = datetime.now() + timedelta(days=1)
                extracted["date"] = tomorrow.strftime("%A, %B %d")
            elif "today" in user_input_lower:
                extracted["date"] = datetime.now().strftime("%A, %B %d")
            else:
                extracted["date"] = user_input.strip()
        
        elif current_step == "get_time":
            # Extract time
            if any(word in user_input_lower for word in ["morning", "am"]):
                extracted["time"] = "10 AM"
            elif any(word in user_input_lower for word in ["afternoon", "pm"]):
                extracted["time"] = "2 PM"
            elif any(word in user_input_lower for word in ["evening"]):
                extracted["time"] = "6 PM"
            else:
                extracted["time"] = user_input.strip()
        
        elif current_step == "get_address":
            # Extract address
            if len(user_input) > 10:
                extracted["address"] = user_input.strip()
        
        return extracted

    def get_conversation_response(self, user_input: str, session_id: str) -> str:
        """Generate AI response based on conversation state and user input"""
        session = self.active_sessions.get(session_id)
        if not session:
            return "I'm sorry, I'm having trouble with this call. Please try calling again."
        
        # Add user message to history
        session.conversation_history.append({
            "role": "user",
            "content": user_input,
            "timestamp": datetime.now().isoformat()
        })
        
        # Extract structured information
        extracted_info = self.extract_booking_info(user_input, session.current_step)
        
        # Update session based on extracted information
        if extracted_info:
            if "name" in extracted_info:
                session.customer_name = extracted_info["name"]
            if "service" in extracted_info:
                session.booking_data.service = extracted_info["service"]
            if "date" in extracted_info:
                session.booking_data.date = extracted_info["date"]
            if "time" in extracted_info:
                session.booking_data.time = extracted_info["time"]
            if "address" in extracted_info:
                session.booking_data.address = extracted_info["address"]
        
        # Determine next step
        self._update_conversation_step(session, user_input)
        
        # Get AI response
        ai_response = self.get_ai_response(user_input, session.conversation_history, session.current_step)
        
        # Handle special cases
        if session.current_step == "confirm_booking" and not session.booking_data.customer_name:
            ai_response = self._generate_confirmation_message(session)
        elif session.current_step == "booking_complete":
            ai_response = self._complete_booking(session)
        
        # Add AI response to history
        session.conversation_history.append({
            "role": "assistant",
            "content": ai_response,
            "timestamp": datetime.now().isoformat()
        })
        
        return ai_response

    def _update_conversation_step(self, session: ConversationState, user_input: str):
        """Update conversation step based on current state and user input"""
        user_input_lower = user_input.lower().strip()
        
        if session.current_step == "greeting":
            if any(word in user_input_lower for word in ["book", "appointment", "schedule", "service"]):
                session.current_step = "get_name"
        
        elif session.current_step == "get_name" and session.customer_name:
            session.current_step = "get_service"
        
        elif session.current_step == "get_service" and session.booking_data.service:
            session.current_step = "get_date"
        
        elif session.current_step == "get_date" and session.booking_data.date:
            session.current_step = "get_time"
        
        elif session.current_step == "get_time" and session.booking_data.time:
            session.current_step = "get_address"
        
        elif session.current_step == "get_address" and session.booking_data.address:
            session.current_step = "confirm_booking"
        
        elif session.current_step == "confirm_booking":
            if any(word in user_input_lower for word in ["yes", "confirm", "correct", "book"]):
                session.current_step = "booking_complete"
            elif any(word in user_input_lower for word in ["no", "change", "wrong"]):
                session.current_step = "get_name"  # Restart

    def _generate_confirmation_message(self, session: ConversationState) -> str:
        """Generate booking confirmation message"""
        booking = session.booking_data
        return f"""Let me confirm your booking:
Name: {session.customer_name}
Service: {booking.service}
Date: {booking.date}
Time: {booking.time}
Address: {booking.address}
Does this look correct?"""

    def _complete_booking(self, session: ConversationState) -> str:
        """Complete the booking and return confirmation"""
        booking_id = f"BG{datetime.now().strftime('%Y%m%d%H%M%S')}"
        
        # Save booking (integrate with your existing system)
        self._save_booking(session, booking_id)
        
        # Send SMS confirmation
        self._send_sms_confirmation(session, booking_id)
        
        return f"""Perfect! Your booking is confirmed. Booking ID: {booking_id}. 
You'll receive an SMS confirmation shortly. 
Thank you for choosing Goodness Glamour Salon!"""

    def _save_booking(self, session: ConversationState, booking_id: str):
        """Save booking to database/Excel (integrate with existing system)"""
        booking_data = {
            "booking_id": booking_id,
            "customer_name": session.customer_name,
            "phone": session.phone,
            "service": session.booking_data.service,
            "date": session.booking_data.date,
            "time": session.booking_data.time,
            "address": session.booking_data.address,
            "status": "confirmed",
            "created_at": datetime.now().isoformat(),
            "source": "voice_call_ai"
        }
        
        # TODO: Integrate with your existing booking system
        logger.info(f"Booking saved: {booking_data}")

    def _send_sms_confirmation(self, session: ConversationState, booking_id: str):
        """Send SMS confirmation to customer"""
        try:
            message = f"""Goodness Glamour Salon - Booking Confirmed!

Booking ID: {booking_id}
Customer: {session.customer_name}
Service: {session.booking_data.service}
Date: {session.booking_data.date}
Time: {session.booking_data.time}
Address: {session.booking_data.address}

We'll be at your doorstep at the scheduled time. Thank you!"""
            
            client.messages.create(
                body=message,
                from_=TWILIO_PHONE_NUMBER,
                to=session.phone
            )
            logger.info(f"SMS sent to {session.phone}")
        except Exception as e:
            logger.error(f"Failed to send SMS: {e}")

    def start_session(self, call_sid: str, phone_number: str) -> ConversationState:
        """Start a new conversation session"""
        session = ConversationState(
            session_id=call_sid,
            phone=phone_number
        )
        self.active_sessions[call_sid] = session
        return session

    def end_session(self, call_sid: str):
        """End conversation session"""
        if call_sid in self.active_sessions:
            del self.active_sessions[call_sid]

# Initialize the enhanced assistant
enhanced_assistant = EnhancedVoiceAssistant()

# Flask app for webhooks
app = Flask(__name__)

@app.route('/voice/incoming', methods=['POST'])
def handle_incoming_call():
    """Handle incoming voice call from QR code scan"""
    try:
        call_sid = request.form.get('CallSid')
        from_number = request.form.get('From')
        
        logger.info(f"Incoming call from {from_number}, SID: {call_sid}")
        
        # Start new session
        session = enhanced_assistant.start_session(call_sid, from_number)
        
        # Create TwiML response
        response = VoiceResponse()
        
        # Welcome message
        response.say(
            "Hello! Welcome to Goodness Glamour Salon. I'm your AI assistant. How can I help you today?",
            voice='Polly.Joanna',
            language='en-US'
        )
        
        # Gather user input
        gather = response.gather(
            input='speech',
            action=f'{WEBHOOK_BASE_URL}/voice/process_speech/{call_sid}',
            speech_timeout='auto',
            language='en-US',
            enhanced=True
        )
        
        # Fallback
        response.say("I didn't hear anything. Please speak after the tone.")
        response.redirect(f'{WEBHOOK_BASE_URL}/voice/process_speech/{call_sid}')
        
        return str(response)
        
    except Exception as e:
        logger.error(f"Error handling incoming call: {e}")
        response = VoiceResponse()
        response.say("I'm sorry, there was a technical issue. Please try again later.")
        response.hangup()
        return str(response)

@app.route('/voice/process_speech/<call_sid>', methods=['POST'])
def process_speech(call_sid):
    """Process speech input from Twilio"""
    try:
        speech_result = request.form.get('SpeechResult', '')
        
        if not speech_result:
            response = VoiceResponse()
            response.say("I didn't hear anything. Please speak clearly.")
            response.redirect(f'{WEBHOOK_BASE_URL}/voice/process_speech/{call_sid}')
            return str(response)
        
        logger.info(f"Processing speech for call {call_sid}: {speech_result}")
        
        # Get AI response
        ai_response = enhanced_assistant.get_conversation_response(speech_result, call_sid)
        
        # Create TwiML response
        response = VoiceResponse()
        response.say(ai_response, voice='Polly.Joanna', language='en-US')
        
        # Check if conversation is complete
        session = enhanced_assistant.active_sessions.get(call_sid)
        if session and session.current_step == "booking_complete":
            response.hangup()
            enhanced_assistant.end_session(call_sid)
        else:
            # Continue conversation
            gather = response.gather(
                input='speech',
                action=f'{WEBHOOK_BASE_URL}/voice/process_speech/{call_sid}',
                speech_timeout='auto',
                language='en-US',
                enhanced=True
            )
            
            response.say("I'm listening.")
            response.redirect(f'{WEBHOOK_BASE_URL}/voice/process_speech/{call_sid}')
        
        return str(response)
        
    except Exception as e:
        logger.error(f"Error processing speech: {e}")
        response = VoiceResponse()
        response.say("I'm sorry, I'm having trouble understanding. Please try again.")
        response.redirect(f'{WEBHOOK_BASE_URL}/voice/process_speech/{call_sid}')
        return str(response)

@app.route('/voice/status/<call_sid>', methods=['POST'])
def call_status(call_sid):
    """Handle call status updates"""
    call_status = request.form.get('CallStatus')
    logger.info(f"Call {call_sid} status: {call_status}")
    
    # Clean up if call ended
    if call_status in ['completed', 'busy', 'no-answer', 'failed', 'canceled']:
        enhanced_assistant.end_session(call_sid)
    
    return Response(status=200)

@app.route('/qr/trigger_call', methods=['POST'])
def trigger_voice_call():
    """Trigger voice call when QR code is scanned"""
    try:
        data = request.get_json()
        customer_phone = data.get('phone_number')
        
        if not customer_phone:
            return Response("Phone number required", status=400)
        
        # Make outbound call to customer
        call = client.calls.create(
            url=f'{WEBHOOK_BASE_URL}/voice/incoming',
            to=customer_phone,
            from_=TWILIO_PHONE_NUMBER,
            method='POST',
            status_callback=f'{WEBHOOK_BASE_URL}/voice/status',
            status_callback_method='POST'
        )
        
        logger.info(f"Outbound call initiated to {customer_phone}, SID: {call.sid}")
        
        return Response(
            json.dumps({
                'success': True,
                'call_sid': call.sid,
                'message': 'Voice call initiated'
            }),
            status=200,
            mimetype='application/json'
        )
        
    except Exception as e:
        logger.error(f"Error triggering voice call: {e}")
        return Response(
            json.dumps({
                'success': False,
                'error': str(e)
            }),
            status=500,
            mimetype='application/json'
        )

@app.route('/health', methods=['GET'])
def health_check():
    """Health check endpoint"""
    return Response(
        json.dumps({
            'status': 'healthy',
            'active_sessions': len(enhanced_assistant.active_sessions),
            'openai_available': openai_client is not None,
            'timestamp': datetime.now().isoformat()
        }),
        status=200,
        mimetype='application/json'
    )

if __name__ == '__main__':
    port = int(os.environ.get('PORT', 7002))
    logger.info(f"Starting Enhanced AI Voice Booking Assistant on port {port}")
    logger.info(f"OpenAI available: {openai_client is not None}")
    app.run(host='0.0.0.0', port=port, debug=True)
