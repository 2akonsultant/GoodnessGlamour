"""
QR Code Voice Trigger System
Integrates QR code scanning with AI voice booking calls
"""

import os
import json
import logging
import qrcode
import base64
from io import BytesIO
from flask import Flask, request, Response, jsonify, render_template_string
from twilio.rest import Client
import requests
from datetime import datetime

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Configuration
TWILIO_ACCOUNT_SID = os.getenv('TWILIO_ACCOUNT_SID', 'ACd8941e7d6933a9e031879bc28d7af7e8')
TWILIO_AUTH_TOKEN = os.getenv('TWILIO_AUTH_TOKEN', '815e90983ed99b02e52943cc14602d56')
TWILIO_PHONE_NUMBER = os.getenv('TWILIO_PHONE_NUMBER', '+917019035686')
WEBHOOK_BASE_URL = os.getenv('WEBHOOK_BASE_URL', 'https://your-domain.com')
VOICE_ASSISTANT_URL = os.getenv('VOICE_ASSISTANT_URL', 'https://virtualaisalon.onrender.com/')

# Initialize Twilio client
client = Client(TWILIO_ACCOUNT_SID, TWILIO_AUTH_TOKEN)

# Flask app
app = Flask(__name__)

# QR Code templates
QR_LANDING_PAGE_TEMPLATE = """
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Goodness Glamour - Voice Booking</title>
    <style>
        body {
            font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
            margin: 0;
            padding: 20px;
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            min-height: 100vh;
            display: flex;
            align-items: center;
            justify-content: center;
        }
        .container {
            background: white;
            border-radius: 20px;
            padding: 40px;
            box-shadow: 0 20px 40px rgba(0,0,0,0.1);
            text-align: center;
            max-width: 400px;
            width: 100%;
        }
        .logo {
            font-size: 2em;
            font-weight: bold;
            color: #667eea;
            margin-bottom: 10px;
        }
        .tagline {
            color: #666;
            margin-bottom: 30px;
        }
        .phone-input {
            width: 100%;
            padding: 15px;
            border: 2px solid #ddd;
            border-radius: 10px;
            font-size: 16px;
            margin-bottom: 20px;
            box-sizing: border-box;
        }
        .call-button {
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            color: white;
            border: none;
            padding: 15px 30px;
            border-radius: 10px;
            font-size: 16px;
            font-weight: bold;
            cursor: pointer;
            width: 100%;
            margin-bottom: 20px;
        }
        .call-button:hover {
            transform: translateY(-2px);
            box-shadow: 0 10px 20px rgba(102, 126, 234, 0.3);
        }
        .call-button:disabled {
            background: #ccc;
            cursor: not-allowed;
            transform: none;
            box-shadow: none;
        }
        .features {
            text-align: left;
            margin-top: 30px;
        }
        .feature {
            display: flex;
            align-items: center;
            margin-bottom: 15px;
            color: #666;
        }
        .feature-icon {
            margin-right: 10px;
            color: #667eea;
        }
        .status {
            margin-top: 20px;
            padding: 10px;
            border-radius: 5px;
            display: none;
        }
        .status.success {
            background: #d4edda;
            color: #155724;
            border: 1px solid #c3e6cb;
        }
        .status.error {
            background: #f8d7da;
            color: #721c24;
            border: 1px solid #f5c6cb;
        }
    </style>
</head>
<body>
    <div class="container">
        <div class="logo">💇‍♀️ Goodness Glamour</div>
        <div class="tagline">Premium Doorstep Beauty Services</div>
        
        <h2>Book Your Appointment via Voice Call</h2>
        <p>Enter your phone number and we'll call you instantly for a personalized booking experience!</p>
        
        <form id="bookingForm">
            <input type="tel" id="phoneInput" class="phone-input" 
                   placeholder="Enter your phone number (e.g., +919876543210)" 
                   required pattern="^\+?[1-9]\d{1,14}$">
            <button type="submit" class="call-button" id="callButton">
                📞 Call Me Now
            </button>
        </form>
        
        <div id="status" class="status"></div>
        
        <div class="features">
            <div class="feature">
                <span class="feature-icon">🎯</span>
                <span>AI-powered voice assistant</span>
            </div>
            <div class="feature">
                <span class="feature-icon">🏠</span>
                <span>Doorstep service</span>
            </div>
            <div class="feature">
                <span class="feature-icon">⚡</span>
                <span>Instant booking</span>
            </div>
            <div class="feature">
                <span class="feature-icon">📱</span>
                <span>SMS confirmation</span>
            </div>
        </div>
    </div>

    <script>
        document.getElementById('bookingForm').addEventListener('submit', async function(e) {
            e.preventDefault();
            
            const phoneInput = document.getElementById('phoneInput');
            const callButton = document.getElementById('callButton');
            const status = document.getElementById('status');
            
            const phoneNumber = phoneInput.value.trim();
            
            if (!phoneNumber) {
                showStatus('Please enter your phone number', 'error');
                return;
            }
            
            // Validate phone number format
            const phoneRegex = /^\+?[1-9]\d{1,14}$/;
            if (!phoneRegex.test(phoneNumber)) {
                showStatus('Please enter a valid phone number', 'error');
                return;
            }
            
            callButton.disabled = true;
            callButton.textContent = 'Calling...';
            
            try {
                const response = await fetch('/trigger-voice-call', {
                    method: 'POST',
                    headers: {
                        'Content-Type': 'application/json',
                    },
                    body: JSON.stringify({
                        phone_number: phoneNumber,
                        source: 'qr_code'
                    })
                });
                
                const result = await response.json();
                
                if (result.success) {
                    showStatus('Call initiated! We\'ll be calling you shortly...', 'success');
                    callButton.textContent = 'Call Initiated ✓';
                } else {
                    showStatus('Failed to initiate call. Please try again.', 'error');
                    callButton.disabled = false;
                    callButton.textContent = '📞 Call Me Now';
                }
            } catch (error) {
                console.error('Error:', error);
                showStatus('Network error. Please check your connection and try again.', 'error');
                callButton.disabled = false;
                callButton.textContent = '📞 Call Me Now';
            }
        });
        
        function showStatus(message, type) {
            const status = document.getElementById('status');
            status.textContent = message;
            status.className = 'status ' + type;
            status.style.display = 'block';
            
            if (type === 'success') {
                setTimeout(() => {
                    status.style.display = 'none';
                }, 5000);
            }
        }
    </script>
</body>
</html>
"""

class QRVoiceTriggerSystem:
    """
    System for generating QR codes that trigger voice calls
    """
    
    def __init__(self):
        self.qr_codes_generated = {}
    
    def generate_qr_code(self, service_id: str = None, source: str = "website") -> dict:
        """Generate QR code data and image"""
        try:
            # Create QR code data
            qr_data = {
                "url": f"{WEBHOOK_BASE_URL}/qr/voice-booking",
                "service_id": service_id,
                "source": source,
                "timestamp": datetime.now().isoformat(),
                "type": "voice_booking"
            }
            
            # Generate QR code
            qr = qrcode.QRCode(
                version=1,
                error_correction=qrcode.constants.ERROR_CORRECT_L,
                box_size=10,
                border=4,
            )
            qr.add_data(json.dumps(qr_data))
            qr.make(fit=True)
            
            # Create QR code image
            img = qr.make_image(fill_color="black", back_color="white")
            
            # Convert to base64
            buffer = BytesIO()
            img.save(buffer, format='PNG')
            buffer.seek(0)
            img_base64 = base64.b64encode(buffer.getvalue()).decode()
            
            qr_id = f"qr_{datetime.now().strftime('%Y%m%d%H%M%S')}"
            self.qr_codes_generated[qr_id] = qr_data
            
            return {
                "qr_id": qr_id,
                "qr_data": qr_data,
                "qr_image": img_base64,
                "qr_url": f"{WEBHOOK_BASE_URL}/qr/voice-booking"
            }
            
        except Exception as e:
            logger.error(f"Error generating QR code: {e}")
            return None
    
    def trigger_voice_call(self, phone_number: str, source: str = "qr_code") -> dict:
        """Trigger voice call to customer"""
        try:
            # Make outbound call to customer
            call = client.calls.create(
                url=f'{VOICE_ASSISTANT_URL}/voice/incoming',
                to=phone_number,
                from_=TWILIO_PHONE_NUMBER,
                method='POST',
                status_callback=f'{VOICE_ASSISTANT_URL}/voice/status',
                status_callback_method='POST'
            )
            
            logger.info(f"Voice call triggered to {phone_number} from {source}, SID: {call.sid}")
            
            return {
                "success": True,
                "call_sid": call.sid,
                "message": "Voice call initiated successfully",
                "phone_number": phone_number,
                "source": source
            }
            
        except Exception as e:
            logger.error(f"Error triggering voice call: {e}")
            return {
                "success": False,
                "error": str(e),
                "message": "Failed to initiate voice call"
            }

# Initialize the QR voice trigger system
qr_system = QRVoiceTriggerSystem()

# Flask routes
@app.route('/qr/voice-booking', methods=['GET'])
def qr_landing_page():
    """Landing page for QR code scans"""
    return render_template_string(QR_LANDING_PAGE_TEMPLATE)

@app.route('/trigger-voice-call', methods=['POST'])
def trigger_voice_call():
    """API endpoint to trigger voice call"""
    try:
        data = request.get_json()
        phone_number = data.get('phone_number')
        source = data.get('source', 'qr_code')
        
        if not phone_number:
            return jsonify({
                "success": False,
                "message": "Phone number is required"
            }), 400
        
        # Trigger voice call
        result = qr_system.trigger_voice_call(phone_number, source)
        
        if result["success"]:
            return jsonify(result), 200
        else:
            return jsonify(result), 500
            
    except Exception as e:
        logger.error(f"Error in trigger voice call endpoint: {e}")
        return jsonify({
            "success": False,
            "message": "Internal server error"
        }), 500

@app.route('/api/qr/generate', methods=['GET'])
def generate_qr_code():
    """Generate QR code for voice booking"""
    try:
        service_id = request.args.get('service_id')
        source = request.args.get('source', 'website')
        
        qr_result = qr_system.generate_qr_code(service_id, source)
        
        if qr_result:
            return jsonify(qr_result), 200
        else:
            return jsonify({
                "error": "Failed to generate QR code"
            }), 500
            
    except Exception as e:
        logger.error(f"Error generating QR code: {e}")
        return jsonify({
            "error": "Internal server error"
        }), 500

@app.route('/api/qr/voice-trigger', methods=['POST'])
def api_trigger_voice_call():
    """API endpoint for triggering voice calls from external systems"""
    try:
        data = request.get_json()
        phone_number = data.get('phone_number')
        source = data.get('source', 'api')
        
        if not phone_number:
            return jsonify({
                "success": False,
                "message": "Phone number is required"
            }), 400
        
        # Trigger voice call
        result = qr_system.trigger_voice_call(phone_number, source)
        
        return jsonify(result), 200 if result["success"] else 500
        
    except Exception as e:
        logger.error(f"Error in API trigger voice call: {e}")
        return jsonify({
            "success": False,
            "message": "Internal server error"
        }), 500

@app.route('/api/qr/stats', methods=['GET'])
def get_qr_stats():
    """Get QR code generation statistics"""
    try:
        stats = {
            "total_qr_codes": len(qr_system.qr_codes_generated),
            "active_qr_codes": len(qr_system.qr_codes_generated),
            "timestamp": datetime.now().isoformat()
        }
        
        return jsonify(stats), 200
        
    except Exception as e:
        logger.error(f"Error getting QR stats: {e}")
        return jsonify({
            "error": "Internal server error"
        }), 500

@app.route('/health', methods=['GET'])
def health_check():
    """Health check endpoint"""
    return jsonify({
        "status": "healthy",
        "service": "QR Voice Trigger System",
        "timestamp": datetime.now().isoformat(),
        "qr_codes_generated": len(qr_system.qr_codes_generated)
    })

# Integration with existing booking system
def integrate_with_booking_system(booking_data: dict):
    """Integrate voice bookings with existing booking system"""
    try:
        # This would integrate with your existing booking API
        booking_endpoint = f"{WEBHOOK_BASE_URL}/api/bookings"
        
        response = requests.post(booking_endpoint, json=booking_data)
        
        if response.status_code == 201:
            logger.info(f"Voice booking integrated successfully: {booking_data}")
            return True
        else:
            logger.error(f"Failed to integrate voice booking: {response.text}")
            return False
            
    except Exception as e:
        logger.error(f"Error integrating with booking system: {e}")
        return False

if __name__ == '__main__':
    port = int(os.environ.get('PORT', 7003))
    logger.info(f"Starting QR Voice Trigger System on port {port}")
    logger.info(f"QR Landing Page: {WEBHOOK_BASE_URL}/qr/voice-booking")
    app.run(host='0.0.0.0', port=port, debug=True)
