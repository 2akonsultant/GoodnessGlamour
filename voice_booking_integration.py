"""
Voice Booking Integration System
Connects AI voice bookings with existing SalonBooker system
"""

import os
import json
import logging
import requests
import pandas as pd
from datetime import datetime
from typing import Dict, List, Optional, Any
from dataclasses import dataclass, asdict
import sqlite3
from flask import Flask, request, Response, jsonify

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Configuration
SALONBOOKER_API_URL = os.getenv('SALONBOOKER_API_URL', 'http://localhost:5000')
BOOKINGS_EXCEL_PATH = os.getenv('BOOKINGS_EXCEL_PATH', 'data/bookings.xlsx')
DATABASE_PATH = os.getenv('DATABASE_PATH', 'data/salon_bookings.db')

@dataclass
class VoiceBooking:
    booking_id: str
    customer_name: str
    phone: str
    service: str
    date: str
    time: str
    address: str
    status: str = "confirmed"
    source: str = "voice_call"
    created_at: str = ""
    notes: str = ""
    
    def __post_init__(self):
        if not self.created_at:
            self.created_at = datetime.now().isoformat()

class VoiceBookingIntegration:
    """
    Integrates voice bookings with existing SalonBooker system
    """
    
    def __init__(self):
        self.voice_bookings = []
        self._ensure_data_directories()
    
    def _ensure_data_directories(self):
        """Ensure data directories exist"""
        os.makedirs("data", exist_ok=True)
        os.makedirs("logs", exist_ok=True)
    
    def save_voice_booking(self, booking_data: Dict) -> bool:
        """Save voice booking to multiple storage systems"""
        try:
            # Create voice booking object
            voice_booking = VoiceBooking(
                booking_id=booking_data.get('booking_id', f"VB{datetime.now().strftime('%Y%m%d%H%M%S')}"),
                customer_name=booking_data.get('customer_name', ''),
                phone=booking_data.get('phone', ''),
                service=booking_data.get('service', ''),
                date=booking_data.get('date', ''),
                time=booking_data.get('time', ''),
                address=booking_data.get('address', ''),
                status=booking_data.get('status', 'confirmed'),
                source=booking_data.get('source', 'voice_call'),
                notes=booking_data.get('notes', '')
            )
            
            # Save to multiple systems
            results = {
                'excel': self._save_to_excel(voice_booking),
                'database': self._save_to_database(voice_booking),
                'api': self._save_via_api(voice_booking)
            }
            
            # Store in memory for tracking
            self.voice_bookings.append(asdict(voice_booking))
            
            logger.info(f"Voice booking saved: {voice_booking.booking_id}")
            logger.info(f"Save results: {results}")
            
            return any(results.values())  # Return True if any save method succeeded
            
        except Exception as e:
            logger.error(f"Error saving voice booking: {e}")
            return False
    
    def _save_to_excel(self, booking: VoiceBooking) -> bool:
        """Save booking to Excel file"""
        try:
            # Prepare data for Excel
            excel_data = {
                'Booking ID': booking.booking_id,
                'Customer Name': booking.customer_name,
                'Phone': booking.phone,
                'Service': booking.service,
                'Date': booking.date,
                'Time': booking.time,
                'Address': booking.address,
                'Status': booking.status,
                'Source': booking.source,
                'Created At': booking.created_at,
                'Notes': booking.notes
            }
            
            # Load existing data or create new DataFrame
            if os.path.exists(BOOKINGS_EXCEL_PATH):
                df = pd.read_excel(BOOKINGS_EXCEL_PATH)
            else:
                df = pd.DataFrame(columns=list(excel_data.keys()))
            
            # Add new booking
            new_row = pd.DataFrame([excel_data])
            df = pd.concat([df, new_row], ignore_index=True)
            
            # Save to Excel
            df.to_excel(BOOKINGS_EXCEL_PATH, index=False)
            
            logger.info(f"Voice booking saved to Excel: {booking.booking_id}")
            return True
            
        except Exception as e:
            logger.error(f"Error saving to Excel: {e}")
            return False
    
    def _save_to_database(self, booking: VoiceBooking) -> bool:
        """Save booking to SQLite database"""
        try:
            conn = sqlite3.connect(DATABASE_PATH)
            cursor = conn.cursor()
            
            # Create table if not exists
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS voice_bookings (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    booking_id TEXT UNIQUE NOT NULL,
                    customer_name TEXT NOT NULL,
                    phone TEXT NOT NULL,
                    service TEXT NOT NULL,
                    date TEXT NOT NULL,
                    time TEXT NOT NULL,
                    address TEXT NOT NULL,
                    status TEXT DEFAULT 'confirmed',
                    source TEXT DEFAULT 'voice_call',
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    notes TEXT
                )
            ''')
            
            # Insert booking
            cursor.execute('''
                INSERT OR REPLACE INTO voice_bookings 
                (booking_id, customer_name, phone, service, date, time, address, status, source, notes)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            ''', (
                booking.booking_id,
                booking.customer_name,
                booking.phone,
                booking.service,
                booking.date,
                booking.time,
                booking.address,
                booking.status,
                booking.source,
                booking.notes
            ))
            
            conn.commit()
            conn.close()
            
            logger.info(f"Voice booking saved to database: {booking.booking_id}")
            return True
            
        except Exception as e:
            logger.error(f"Error saving to database: {e}")
            return False
    
    def _save_via_api(self, booking: VoiceBooking) -> bool:
        """Save booking via existing SalonBooker API"""
        try:
            # Convert voice booking to API format
            api_data = {
                "customerId": None,  # Will be created if not exists
                "serviceIds": [self._map_service_to_id(booking.service)],
                "appointmentDate": self._parse_appointment_datetime(booking.date, booking.time),
                "notes": f"Voice booking - {booking.notes}",
                "source": "voice_call",
                "voice_booking_id": booking.booking_id
            }
            
            # Try to create customer first
            customer_data = {
                "name": booking.customer_name,
                "phone": booking.phone,
                "email": "",
                "address": booking.address
            }
            
            # Create customer
            customer_response = requests.post(
                f"{SALONBOOKER_API_URL}/api/customers",
                json=customer_data,
                timeout=10
            )
            
            if customer_response.status_code == 201:
                customer = customer_response.json()
                api_data["customerId"] = customer["id"]
            
            # Create booking
            booking_response = requests.post(
                f"{SALONBOOKER_API_URL}/api/bookings",
                json=api_data,
                timeout=10
            )
            
            if booking_response.status_code == 201:
                logger.info(f"Voice booking saved via API: {booking.booking_id}")
                return True
            else:
                logger.error(f"API booking failed: {booking_response.text}")
                return False
                
        except Exception as e:
            logger.error(f"Error saving via API: {e}")
            return False
    
    def _map_service_to_id(self, service_name: str) -> str:
        """Map service name to service ID"""
        service_mapping = {
            "haircut": "women-haircut",
            "coloring": "women-coloring",
            "treatment": "women-treatment",
            "bridal": "women-bridal",
            "blowdry": "women-blowdry",
            "hairwash": "women-hairwash",
            "consultation": "women-consultation",
            "kids-haircut": "kids-haircut",
            "party": "kids-party",
            "kids-hairwash": "kids-hairwash",
            "braiding": "kids-braiding"
        }
        
        return service_mapping.get(service_name.lower(), "general-service")
    
    def _parse_appointment_datetime(self, date_str: str, time_str: str) -> str:
        """Parse date and time into ISO format"""
        try:
            # Simple parsing - can be enhanced
            if "tomorrow" in date_str.lower():
                appointment_date = datetime.now() + pd.Timedelta(days=1)
            elif "today" in date_str.lower():
                appointment_date = datetime.now()
            else:
                # Try to parse specific date
                appointment_date = datetime.now() + pd.Timedelta(days=1)  # Default to tomorrow
            
            # Parse time
            if "am" in time_str.lower():
                if "10" in time_str:
                    appointment_time = appointment_date.replace(hour=10, minute=0, second=0, microsecond=0)
                else:
                    appointment_time = appointment_date.replace(hour=9, minute=0, second=0, microsecond=0)
            elif "pm" in time_str.lower():
                if "2" in time_str or "14" in time_str:
                    appointment_time = appointment_date.replace(hour=14, minute=0, second=0, microsecond=0)
                elif "6" in time_str or "18" in time_str:
                    appointment_time = appointment_date.replace(hour=18, minute=0, second=0, microsecond=0)
                else:
                    appointment_time = appointment_date.replace(hour=14, minute=0, second=0, microsecond=0)
            else:
                appointment_time = appointment_date.replace(hour=10, minute=0, second=0, microsecond=0)
            
            return appointment_time.isoformat()
            
        except Exception as e:
            logger.error(f"Error parsing datetime: {e}")
            # Default to tomorrow at 10 AM
            tomorrow = datetime.now() + pd.Timedelta(days=1)
            return tomorrow.replace(hour=10, minute=0, second=0, microsecond=0).isoformat()
    
    def get_voice_bookings(self, limit: int = 50) -> List[Dict]:
        """Get recent voice bookings"""
        try:
            if os.path.exists(DATABASE_PATH):
                conn = sqlite3.connect(DATABASE_PATH)
                cursor = conn.cursor()
                
                cursor.execute('''
                    SELECT booking_id, customer_name, phone, service, date, time, 
                           address, status, source, created_at, notes
                    FROM voice_bookings 
                    ORDER BY created_at DESC 
                    LIMIT ?
                ''', (limit,))
                
                bookings = []
                for row in cursor.fetchall():
                    bookings.append({
                        'booking_id': row[0],
                        'customer_name': row[1],
                        'phone': row[2],
                        'service': row[3],
                        'date': row[4],
                        'time': row[5],
                        'address': row[6],
                        'status': row[7],
                        'source': row[8],
                        'created_at': row[9],
                        'notes': row[10]
                    })
                
                conn.close()
                return bookings
            else:
                return self.voice_bookings[-limit:] if self.voice_bookings else []
                
        except Exception as e:
            logger.error(f"Error getting voice bookings: {e}")
            return []
    
    def update_booking_status(self, booking_id: str, status: str) -> bool:
        """Update booking status"""
        try:
            # Update database
            if os.path.exists(DATABASE_PATH):
                conn = sqlite3.connect(DATABASE_PATH)
                cursor = conn.cursor()
                
                cursor.execute('''
                    UPDATE voice_bookings 
                    SET status = ? 
                    WHERE booking_id = ?
                ''', (status, booking_id))
                
                conn.commit()
                conn.close()
            
            # Update in-memory storage
            for booking in self.voice_bookings:
                if booking['booking_id'] == booking_id:
                    booking['status'] = status
                    break
            
            logger.info(f"Booking status updated: {booking_id} -> {status}")
            return True
            
        except Exception as e:
            logger.error(f"Error updating booking status: {e}")
            return False

# Initialize integration system
booking_integration = VoiceBookingIntegration()

# Flask app for API endpoints
app = Flask(__name__)

@app.route('/api/voice-bookings', methods=['POST'])
def create_voice_booking():
    """Create a new voice booking"""
    try:
        booking_data = request.get_json()
        
        if not booking_data:
            return jsonify({
                "success": False,
                "message": "Booking data is required"
            }), 400
        
        # Save booking
        success = booking_integration.save_voice_booking(booking_data)
        
        if success:
            return jsonify({
                "success": True,
                "message": "Voice booking created successfully",
                "booking_id": booking_data.get('booking_id')
            }), 201
        else:
            return jsonify({
                "success": False,
                "message": "Failed to create voice booking"
            }), 500
            
    except Exception as e:
        logger.error(f"Error creating voice booking: {e}")
        return jsonify({
            "success": False,
            "message": "Internal server error"
        }), 500

@app.route('/api/voice-bookings', methods=['GET'])
def get_voice_bookings():
    """Get voice bookings"""
    try:
        limit = request.args.get('limit', 50, type=int)
        bookings = booking_integration.get_voice_bookings(limit)
        
        return jsonify({
            "success": True,
            "bookings": bookings,
            "count": len(bookings)
        }), 200
        
    except Exception as e:
        logger.error(f"Error getting voice bookings: {e}")
        return jsonify({
            "success": False,
            "message": "Internal server error"
        }), 500

@app.route('/api/voice-bookings/<booking_id>/status', methods=['PUT'])
def update_voice_booking_status(booking_id):
    """Update voice booking status"""
    try:
        data = request.get_json()
        status = data.get('status')
        
        if not status:
            return jsonify({
                "success": False,
                "message": "Status is required"
            }), 400
        
        success = booking_integration.update_booking_status(booking_id, status)
        
        if success:
            return jsonify({
                "success": True,
                "message": "Booking status updated successfully"
            }), 200
        else:
            return jsonify({
                "success": False,
                "message": "Failed to update booking status"
            }), 500
            
    except Exception as e:
        logger.error(f"Error updating booking status: {e}")
        return jsonify({
            "success": False,
            "message": "Internal server error"
        }), 500

@app.route('/health', methods=['GET'])
def health_check():
    """Health check endpoint"""
    return jsonify({
        "status": "healthy",
        "service": "Voice Booking Integration",
        "timestamp": datetime.now().isoformat(),
        "voice_bookings_count": len(booking_integration.voice_bookings)
    })

if __name__ == '__main__':
    port = int(os.environ.get('PORT', 7004))
    logger.info(f"Starting Voice Booking Integration System on port {port}")
    app.run(host='0.0.0.0', port=port, debug=True)
