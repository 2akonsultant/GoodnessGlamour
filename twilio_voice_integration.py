"""
Twilio Voice Integration for QR Code Triggered AI Voice Calls
This module handles incoming voice calls from customers who scan QR codes
"""

from flask import Flask, request, Response
from twilio.twiml import VoiceResponse
from twilio.rest import Client
import os
import logging
from voice_agent import AgenticSalonAI
import json
import uuid
from datetime import datetime
from config import config

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Twilio configuration (use centralized config)
TWILIO_ACCOUNT_SID = config.TWILIO_ACCOUNT_SID
TWILIO_AUTH_TOKEN = config.TWILIO_AUTH_TOKEN
TWILIO_PHONE_NUMBER = config.TWILIO_PHONE_NUMBER
WEBHOOK_BASE_URL = config.WEBHOOK_URL.rstrip('/')

# Initialize Twilio client
client = Client(TWILIO_ACCOUNT_SID, TWILIO_AUTH_TOKEN)

# Initialize Flask app
app = Flask(__name__)

# Global AI system instance
salon_ai = None

class TwilioVoiceAgent:
    """Handles Twilio voice call interactions"""
    
    def __init__(self):
        self.salon_ai = AgenticSalonAI()
        self.active_calls = {}  # Track active call sessions
    
    def handle_incoming_call(self, call_sid: str, from_number: str):
        """Handle incoming voice call from QR code scan"""
        try:
            # Create conversation context for this call
            session_id = str(uuid.uuid4())
            self.salon_ai.conversation_context.session_id = session_id
            
            # Store call information
            self.active_calls[call_sid] = {
                'session_id': session_id,
                'from_number': from_number,
                'start_time': datetime.now(),
                'conversation_step': 'greeting'
            }
            
            logger.info(f"New call from {from_number}, Session: {session_id}")
            
            # Create TwiML response for greeting
            response = VoiceResponse()
            
            # Welcome message
            response.say(
                "Hello! Welcome to Goodness Glamour Salon. "
                "I'm your AI assistant. How can I help you today?",
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
            
            # Fallback if no speech detected
            response.say(
                "I didn't hear anything. Please speak after the tone.",
                voice='Polly.Joanna'
            )
            response.redirect(f'{WEBHOOK_BASE_URL}/voice/process_speech/{call_sid}')
            
            return str(response)
            
        except Exception as e:
            logger.error(f"Error handling incoming call: {e}")
            response = VoiceResponse()
            response.say(
                "I'm sorry, there was a technical issue. Please try again later.",
                voice='Polly.Joanna'
            )
            response.hangup()
            return str(response)
    
    def process_speech_input(self, call_sid: str, speech_result: str):
        """Process speech input from the call"""
        try:
            if call_sid not in self.active_calls:
                logger.error(f"Call {call_sid} not found in active calls")
                return self._create_error_response()
            
            call_info = self.active_calls[call_sid]
            
            if not speech_result:
                return self._create_no_speech_response(call_sid)
            
            logger.info(f"Processing speech for call {call_sid}: {speech_result}")
            
            # Process the speech through our AI system
            ai_response = self.salon_ai.process_user_input(
                speech_result, 
                use_voice=False  # We'll handle TTS via Twilio
            )
            
            # Check if booking was completed
            if "booking_data" in ai_response.lower():
                # Handle booking completion
                response = self._handle_booking_completion(call_sid, ai_response)
            else:
                # Continue conversation
                response = self._continue_conversation(call_sid, ai_response)
            
            return str(response)
            
        except Exception as e:
            logger.error(f"Error processing speech: {e}")
            return self._create_error_response()
    
    def _continue_conversation(self, call_sid: str, ai_response: str):
        """Continue the conversation flow"""
        response = VoiceResponse()
        
        # Speak the AI response
        response.say(
            ai_response,
            voice='Polly.Joanna',
            language='en-US'
        )
        
        # Check if this is the end of conversation
        if any(word in ai_response.lower() for word in ["thank you", "goodbye", "confirmed"]):
            response.say(
                "Thank you for calling Goodness Glamour Salon. Have a wonderful day!",
                voice='Polly.Joanna'
            )
            response.hangup()
            # Clean up call session
            if call_sid in self.active_calls:
                del self.active_calls[call_sid]
        else:
            # Gather next input
            gather = response.gather(
                input='speech',
                action=f'{WEBHOOK_BASE_URL}/voice/process_speech/{call_sid}',
                speech_timeout='auto',
                language='en-US',
                enhanced=True
            )
            
            # Fallback
            response.say("I'm listening.", voice='Polly.Joanna')
            response.redirect(f'{WEBHOOK_BASE_URL}/voice/process_speech/{call_sid}')
        
        return response
    
    def _handle_booking_completion(self, call_sid: str, ai_response: str):
        """Handle booking completion flow"""
        response = VoiceResponse()
        
        # Speak confirmation
        response.say(
            ai_response,
            voice='Polly.Joanna',
            language='en-US'
        )
        
        # Send SMS confirmation (optional)
        call_info = self.active_calls.get(call_sid, {})
        if call_info.get('from_number'):
            self._send_sms_confirmation(call_info['from_number'])
        
        # End call
        response.say(
            "You will receive a confirmation message shortly. Thank you for choosing Goodness Glamour Salon!",
            voice='Polly.Joanna'
        )
        response.hangup()
        
        # Clean up
        if call_sid in self.active_calls:
            del self.active_calls[call_sid]
        
        return response
    
    def _create_no_speech_response(self, call_sid: str):
        """Handle when no speech is detected"""
        response = VoiceResponse()
        response.say(
            "I didn't hear anything. Please speak clearly after the tone.",
            voice='Polly.Joanna'
        )
        response.redirect(f'{WEBHOOK_BASE_URL}/voice/process_speech/{call_sid}')
        return str(response)
    
    def _create_error_response(self):
        """Create error response"""
        response = VoiceResponse()
        response.say(
            "I'm sorry, there was a technical issue. Please try calling again later.",
            voice='Polly.Joanna'
        )
        response.hangup()
        return str(response)
    
    def _send_sms_confirmation(self, phone_number: str):
        """Send SMS confirmation to customer"""
        try:
            message = client.messages.create(
                body="Thank you for booking with Goodness Glamour Salon! Your appointment has been confirmed. We'll be in touch soon.",
                from_=TWILIO_PHONE_NUMBER,
                to=phone_number
            )
            logger.info(f"SMS sent to {phone_number}: {message.sid}")
        except Exception as e:
            logger.error(f"Error sending SMS: {e}")

# Initialize Twilio voice agent
twilio_agent = TwilioVoiceAgent()

# Flask routes
@app.route('/voice/incoming', methods=['POST'])
def handle_incoming_call():
    """Handle incoming Twilio voice call"""
    call_sid = request.form.get('CallSid')
    from_number = request.form.get('From')
    
    logger.info(f"Incoming call from {from_number}, SID: {call_sid}")
    
    return twilio_agent.handle_incoming_call(call_sid, from_number)

@app.route('/voice/process_speech/<call_sid>', methods=['POST'])
def process_speech(call_sid):
    """Process speech input from Twilio"""
    speech_result = request.form.get('SpeechResult', '')
    
    logger.info(f"Processing speech for call {call_sid}: {speech_result}")
    
    return twilio_agent.process_speech_input(call_sid, speech_result)

@app.route('/voice/status/<call_sid>', methods=['POST'])
def call_status(call_sid):
    """Handle call status updates"""
    call_status = request.form.get('CallStatus')
    logger.info(f"Call {call_sid} status: {call_status}")
    
    # Clean up if call ended
    if call_status in ['completed', 'busy', 'no-answer', 'failed', 'canceled']:
        if call_sid in twilio_agent.active_calls:
            del twilio_agent.active_calls[call_sid]
            logger.info(f"Cleaned up call session: {call_sid}")
    
    return Response(status=200)

# Generic status callback (Twilio posts CallSid in form payload)
@app.route('/voice/status', methods=['POST'])
def call_status_generic():
    call_sid = request.form.get('CallSid')
    call_status = request.form.get('CallStatus')
    logger.info(f"Call {call_sid} status: {call_status}")
    if call_status in ['completed', 'busy', 'no-answer', 'failed', 'canceled']:
        if call_sid in twilio_agent.active_calls:
            del twilio_agent.active_calls[call_sid]
            logger.info(f"Cleaned up call session: {call_sid}")
    return Response(status=200)

# QR Code webhook endpoint
@app.route('/qr/trigger_call', methods=['POST'])
def trigger_voice_call():
    """Trigger voice call when QR code is scanned"""
    try:
        data = request.get_json()
        customer_phone = data.get('phone_number')
        qr_code_id = data.get('qr_code_id', 'salon_qr')
        
        if not customer_phone:
            return Response("Phone number required", status=400)
        
        # Make outbound call to customer
        call = client.calls.create(
            url=f'{WEBHOOK_BASE_URL}/voice/incoming',
            to=customer_phone,
            from_=TWILIO_PHONE_NUMBER,
            method='POST',
            status_callback=f'{WEBHOOK_BASE_URL}/voice/status',
            status_callback_method='POST',
            status_callback_event=['initiated','ringing','answered','completed']
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

# Health check endpoint
@app.route('/health', methods=['GET'])
def health_check():
    """Health check endpoint"""
    return Response(
        json.dumps({
            'status': 'healthy',
            'active_calls': len(twilio_agent.active_calls),
            'timestamp': datetime.now().isoformat()
        }),
        status=200,
        mimetype='application/json'
    )

# Webhook to handle web-based QR code scans
@app.route('/web/qr_scan', methods=['POST'])
def web_qr_scan():
    """Handle QR code scan from web interface"""
    try:
        data = request.get_json()
        customer_phone = data.get('phone_number')
        
        if not customer_phone:
            return Response("Phone number required", status=400)
        
        # For web scans, we can either:
        # 1. Start a voice call
        # 2. Return a URL for the customer to call
        
        # Option 1: Start voice call
        call = client.calls.create(
            url=f'{WEBHOOK_BASE_URL}/voice/incoming',
            to=customer_phone,
            from_=TWILIO_PHONE_NUMBER,
            method='POST',
            status_callback=f'{WEBHOOK_BASE_URL}/voice/status',
            status_callback_method='POST',
            status_callback_event=['initiated','ringing','answered','completed']
        )
        
        return Response(
            json.dumps({
                'success': True,
                'call_sid': call.sid,
                'message': 'Voice call initiated from QR scan'
            }),
            status=200,
            mimetype='application/json'
        )
        
    except Exception as e:
        logger.error(f"Error handling web QR scan: {e}")
        return Response(
            json.dumps({
                'success': False,
                'error': str(e)
            }),
            status=500,
            mimetype='application/json'
        )

if __name__ == '__main__':
    # Run the Flask app
    selected_port = int(os.environ.get('PORT') or os.environ.get('FLASK_RUN_PORT') or '7000')
    logger.info(f"Starting Twilio Voice Flask app on port {selected_port}")
    logger.info(f"Webhook base URL set to: {WEBHOOK_BASE_URL}")
    app.run(
        host='0.0.0.0',
        port=selected_port,
        debug=True
    )
