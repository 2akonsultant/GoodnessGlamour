"""
AI Voice Booking Assistant for Goodness Glamour Salon
Optimized system for QR-triggered voice calls with natural conversation flow
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

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Configuration
TWILIO_ACCOUNT_SID = os.getenv('TWILIO_ACCOUNT_SID', 'ACd8941e7d6933a9e031879bc28d7af7e8')
TWILIO_AUTH_TOKEN = os.getenv('TWILIO_AUTH_TOKEN', '815e90983ed99b02e52943cc14602d56')
TWILIO_PHONE_NUMBER = os.getenv('TWILIO_PHONE_NUMBER', '+917019035686')
WEBHOOK_BASE_URL = os.getenv('WEBHOOK_BASE_URL', 'https://your-domain.com')

# Initialize Twilio client
client = Client(TWILIO_ACCOUNT_SID, TWILIO_AUTH_TOKEN)

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

class AIVoiceBookingAssistant:
    """
    Advanced AI Voice Booking Assistant with optimized prompts and conversation flow
    """
    
    def __init__(self):
        self.active_sessions: Dict[str, ConversationState] = {}
        
        # Optimized system prompt for voice conversations
        self.system_prompt = """You are a friendly and professional AI voice assistant for Goodness Glamour Salon, a premium doorstep beauty services company. Your task is to help callers schedule salon appointments by phone.

IMPORTANT VOICE CONVERSATION GUIDELINES:
- Speak in SHORT, CLEAR sentences (maximum 15-20 words per response)
- Use a WARM, PROFESSIONAL tone
- Pause briefly between important information
- Always CONFIRM details before proceeding
- Keep responses conversational, not robotic

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

CONVERSATION FLOW:
1. GREETING: Warmly greet caller, introduce yourself as Goodness Glamour's AI assistant
2. NAME: Ask for customer's name and confirm it
3. SERVICE: Ask which service they'd like, provide 2-3 options if they're unsure
4. DATE: Ask for preferred date (mention we're available 9 AM to 8 PM)
5. TIME: Ask for preferred time within our hours
6. ADDRESS: Ask for their address for doorstep service
7. CONFIRM: Repeat all details clearly and ask for confirmation
8. BOOK: Confirm booking and provide booking ID
9. CLOSE: Thank them and mention they'll receive SMS confirmation

RESPONSE EXAMPLES:
❌ "Hello, thank you for calling Goodness Glamour Salon. I am an AI assistant and I can help you book an appointment. What is your name?"
✅ "Hi! Welcome to Goodness Glamour. I'm your AI assistant. How can I help you today?"

❌ "Which service would you like to book from our comprehensive list of beauty services?"
✅ "What service are you interested in? We do haircuts, coloring, treatments, and bridal styling."

Remember: Keep responses SHORT, FRIENDLY, and CONVERSATIONAL. Always confirm details before proceeding."""

    def get_conversation_response(self, user_input: str, session_id: str) -> str:
        """Generate AI response based on conversation state and user input"""
        session = self.active_sessions.get(session_id)
        if not session:
            return "I'm sorry, I'm having trouble with this call. Please try calling again."
        
        # Simple rule-based responses for voice calls (can be enhanced with OpenAI/Gemini)
        current_step = session.current_step
        user_input_lower = user_input.lower().strip()
        
        if current_step == "greeting":
            if any(word in user_input_lower for word in ["book", "appointment", "schedule", "service"]):
                session.current_step = "get_name"
                return "Great! I'd love to help you book an appointment. What's your name?"
            else:
                return "Hello! Welcome to Goodness Glamour Salon. I'm your AI assistant. How can I help you today?"
        
        elif current_step == "get_name":
            # Extract name from input
            name = self._extract_name(user_input)
            if name:
                session.customer_name = name
                session.current_step = "get_service"
                return f"Nice to meet you, {name}! Which service would you like? We do haircuts, coloring, treatments, and bridal styling."
            else:
                return "I didn't catch your name. Could you please tell me your name?"
        
        elif current_step == "get_service":
            service = self._identify_service(user_input)
            if service:
                session.booking_data.service = service
                session.current_step = "get_date"
                service_info = self._get_service_info(service)
                return f"Perfect! {service_info['name']} is {service_info['price']}. What date works for you?"
            else:
                return "Which service interests you? We do haircuts, coloring, treatments, and bridal styling."
        
        elif current_step == "get_date":
            date = self._parse_date(user_input)
            if date:
                session.booking_data.date = date
                session.current_step = "get_time"
                return f"Great! For {date}, what time would work? We're available 9 AM to 8 PM."
            else:
                return "What date would you like? You can say tomorrow, or a specific date."
        
        elif current_step == "get_time":
            time = self._parse_time(user_input)
            if time:
                session.booking_data.time = time
                session.current_step = "get_address"
                return "Perfect! What's your address for our doorstep service?"
            else:
                return "What time works for you? We're available 9 AM to 8 PM."
        
        elif current_step == "get_address":
            address = user_input.strip()
            if len(address) > 10:  # Basic validation
                session.booking_data.address = address
                session.current_step = "confirm_booking"
                return self._generate_confirmation_message(session)
            else:
                return "Could you please provide your complete address for our doorstep service?"
        
        elif current_step == "confirm_booking":
            if any(word in user_input_lower for word in ["yes", "confirm", "correct", "book"]):
                session.current_step = "booking_complete"
                return self._complete_booking(session)
            elif any(word in user_input_lower for word in ["no", "change", "wrong"]):
                session.current_step = "get_name"  # Restart
                return "No problem! Let's start over. What's your name?"
            else:
                return "Please say 'yes' to confirm or 'no' to make changes."
        
        elif current_step == "booking_complete":
            return "Thank you for choosing Goodness Glamour! Have a wonderful day!"
        
        return "I'm not sure how to help with that. Could you please repeat?"

    def _extract_name(self, text: str) -> Optional[str]:
        """Extract name from user input"""
        # Simple name extraction - can be enhanced with NLP
        words = text.split()
        if len(words) >= 1:
            return words[0].capitalize()
        return None

    def _identify_service(self, text: str) -> Optional[str]:
        """Identify service from user input"""
        text_lower = text.lower()
        
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
            if any(keyword in text_lower for keyword in keywords):
                return service
        
        return None

    def _get_service_info(self, service: str) -> Dict:
        """Get service information"""
        for category in SERVICES.values():
            if service in category:
                return category[service]
        return {"name": "Service", "price": "Contact us", "duration": "Varies"}

    def _parse_date(self, text: str) -> Optional[str]:
        """Parse date from user input"""
        text_lower = text.lower()
        
        if "tomorrow" in text_lower:
            tomorrow = datetime.now() + timedelta(days=1)
            return tomorrow.strftime("%A, %B %d")
        elif "today" in text_lower:
            return datetime.now().strftime("%A, %B %d")
        else:
            # For now, return as-is for specific dates
            return text.strip()

    def _parse_time(self, text: str) -> Optional[str]:
        """Parse time from user input"""
        text_lower = text.lower()
        
        # Simple time parsing
        if any(word in text_lower for word in ["morning", "am"]):
            return "10 AM"
        elif any(word in text_lower for word in ["afternoon", "pm"]):
            return "2 PM"
        elif any(word in text_lower for word in ["evening"]):
            return "6 PM"
        else:
            # Return as-is for specific times
            return text.strip()

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
            "source": "voice_call"
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

# Initialize the assistant
voice_assistant = AIVoiceBookingAssistant()

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
        session = voice_assistant.start_session(call_sid, from_number)
        
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
        ai_response = voice_assistant.get_conversation_response(speech_result, call_sid)
        
        # Create TwiML response
        response = VoiceResponse()
        response.say(ai_response, voice='Polly.Joanna', language='en-US')
        
        # Check if conversation is complete
        session = voice_assistant.active_sessions.get(call_sid)
        if session and session.current_step == "booking_complete":
            response.hangup()
            voice_assistant.end_session(call_sid)
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
        voice_assistant.end_session(call_sid)
    
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
            'active_sessions': len(voice_assistant.active_sessions),
            'timestamp': datetime.now().isoformat()
        }),
        status=200,
        mimetype='application/json'
    )

if __name__ == '__main__':
    port = int(os.environ.get('PORT', 7001))
    logger.info(f"Starting AI Voice Booking Assistant on port {port}")
    app.run(host='0.0.0.0', port=port, debug=True)
