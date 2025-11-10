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

try:
    from twilio.rest import Client
    from twilio.twiml.voice_response import VoiceResponse
    TWILIO_AVAILABLE = True
except ImportError:
    TWILIO_AVAILABLE = False
    Client = None
    VoiceResponse = None

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
    TWILIO_ACCOUNT_SID = config.TWILIO_ACCOUNT_SID
    TWILIO_AUTH_TOKEN = config.TWILIO_AUTH_TOKEN
    TWILIO_PHONE_NUMBER = config.TWILIO_PHONE_NUMBER
    WEBHOOK_URL = config.WEBHOOK_URL
except ImportError:
    # Fallback configuration
    GEMINI_API_KEY = "AIzaSyDEw4nW0xV_FQKf1SUX9fFJwnEY5n8_Jwc"
    TWILIO_ACCOUNT_SID = "ACd8941e7d6933a9e031879bc28d7af7e8"
    TWILIO_AUTH_TOKEN = "815e90983ed99b02e52943cc14602d56"
    TWILIO_PHONE_NUMBER = "+917019035686"
    WEBHOOK_URL = "https://your-domain.com"

# Configure Gemini AI
genai.configure(api_key=GEMINI_API_KEY)

# Note: We'll use Gemini for embeddings instead of OpenAI

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

# Data classes for agent communication
@dataclass
class BookingRequest:
    customer_name: str
    phone: str
    service: str
    date: str
    time: str
    address: str
    notes: Optional[str] = None

@dataclass
class AgentMessage:
    sender: str
    content: str
    timestamp: datetime
    message_type: str  # "voice", "text", "booking", "notification"
    data: Optional[Dict] = None

@dataclass
class ConversationContext:
    session_id: str
    customer_name: Optional[str] = None
    phone: Optional[str] = None
    current_step: str = "greeting"
    booking_data: Dict = None
    
    def __post_init__(self):
        if self.booking_data is None:
            self.booking_data = {}

# RAG System with Chroma Vector Database (with fallback)
class RAGSystem:
    def __init__(self):
        self.use_chromadb = CHROMADB_AVAILABLE
        self.knowledge_base = {}
        
        if self.use_chromadb and chromadb is not None and Settings is not None:
            try:
                self.client = chromadb.Client(Settings(
                    chroma_db_impl="duckdb+parquet",
                    persist_directory="./chroma_db"
                ))
                self.collection = self.client.get_or_create_collection(
                    name="salon_knowledge",
                    metadata={"hnsw:space": "cosine"}
                )
                logger.info("ChromaDB initialized successfully")
            except Exception as e:
                logger.warning(f"ChromaDB initialization failed: {e}. Using fallback.")
                self.use_chromadb = False
        
        self._initialize_salon_data()
    
    def _initialize_salon_data(self):
        """Initialize the vector database with salon information"""
        salon_documents = [
            {
                "text": "Goodness Glamour Salon offers doorstep beauty services for ladies and kids. We provide haircuts, styling, coloring, spa treatments, and bridal services.",
                "metadata": {"type": "general_info", "category": "services"}
            },
            {
                "text": "Hair coloring services range from ₹2,000 to ₹5,000 depending on the type and length of hair.",
                "metadata": {"type": "pricing", "category": "hair_coloring"}
            },
            {
                "text": "Kids haircut services cost between ₹300 to ₹700. Party hairstyles cost ₹800 to ₹1,500.",
                "metadata": {"type": "pricing", "category": "kids_services"}
            },
            {
                "text": "Bridal hair and makeup services range from ₹15,000 to ₹30,000. Party makeup costs ₹3,000 to ₹8,000.",
                "metadata": {"type": "pricing", "category": "bridal_party"}
            },
            {
                "text": "We provide doorstep services across the city. Our service hours are Monday to Sunday, 9:00 AM to 8:00 PM.",
                "metadata": {"type": "service_info", "category": "timing_location"}
            },
            {
                "text": "Contact us at 9036626642 or email 2akonsultant@gmail.com for bookings and inquiries.",
                "metadata": {"type": "contact", "category": "booking"}
            },
            {
                "text": "We use premium products and our stylists have 5+ years of experience. Keratin treatments cost ₹4,000 to ₹8,000.",
                "metadata": {"type": "quality", "category": "treatments"}
            },
            {
                "text": "Hair spa treatments cost ₹1,500 to ₹3,000. Haircut and styling services range from ₹500 to ₹1,500.",
                "metadata": {"type": "pricing", "category": "hair_treatments"}
            }
        ]
        
        if self.use_chromadb:
            try:
                # Add documents to collection if empty
                if self.collection.count() == 0:
                    documents = [doc["text"] for doc in salon_documents]
                    metadatas = [doc["metadata"] for doc in salon_documents]
                    ids = [f"doc_{i}" for i in range(len(documents))]
                    
                    self.collection.add(
                        documents=documents,
                        metadatas=metadatas,
                        ids=ids
                    )
                    logger.info(f"Initialized ChromaDB with {len(documents)} documents")
            except Exception as e:
                logger.warning(f"ChromaDB operation failed: {e}. Using fallback.")
                self.use_chromadb = False
        
        # Fallback: Store in simple dictionary
        if not self.use_chromadb:
            for i, doc in enumerate(salon_documents):
                self.knowledge_base[f"doc_{i}"] = doc
            logger.info(f"Initialized fallback knowledge base with {len(salon_documents)} documents")
    
    def search_relevant_info(self, query: str, n_results: int = 3) -> List[Dict]:
        """Search for relevant information using semantic similarity"""
        if self.use_chromadb:
            try:
                results = self.collection.query(
                    query_texts=[query],
                    n_results=n_results
                )
                
                relevant_info = []
                if results['documents'] and results['documents'][0]:
                    for i, doc in enumerate(results['documents'][0]):
                        relevant_info.append({
                            "text": doc,
                            "metadata": results['metadatas'][0][i] if results['metadatas'][0] else {},
                            "distance": results['distances'][0][i] if results['distances'][0] else 0
                        })
                
                return relevant_info
            except Exception as e:
                logger.error(f"Error in ChromaDB search: {e}")
                self.use_chromadb = False
        
        # Fallback: Enhanced keyword matching with Gemini
        query_lower = query.lower()
        relevant_info = []
        
        # Use Gemini to understand the query better
        try:
            enhanced_query = self._enhance_query_with_gemini(query)
            search_terms = query_lower.split() + enhanced_query.split()
        except:
            search_terms = query_lower.split()
        
        for doc_id, doc in self.knowledge_base.items():
            text_lower = doc['text'].lower()
            score = 0
            
            # Calculate relevance score based on keyword matches
            for term in search_terms:
                if term in text_lower:
                    score += 1
            
            # Bonus for exact phrase matches
            if query_lower in text_lower:
                score += 5
            
            if score > 0:
                relevant_info.append({
                    "text": doc['text'],
                    "metadata": doc['metadata'],
                    "distance": 1.0 / (score + 1)  # Lower distance = higher relevance
                })
        
        # Sort by relevance (lower distance = more relevant)
        relevant_info.sort(key=lambda x: x['distance'])
        
        # Return top results
        return relevant_info[:n_results]
    
    def _enhance_query_with_gemini(self, query: str) -> str:
        """Use Gemini to enhance the search query"""
        try:
            # Create a simple Gemini model for query enhancement
            model = genai.GenerativeModel("gemini-2.0-flash-exp")
            
            prompt = f"""
            Given this customer query: "{query}"
            
            Extract key terms and synonyms that would be useful for searching salon information.
            Focus on services, prices, treatments, and salon-related terms.
            
            Return only the key terms separated by spaces, no explanations.
            """
            
            response = model.generate_content(prompt)
            return response.text.lower()
        except Exception as e:
            logger.warning(f"Failed to enhance query with Gemini: {e}")
            return query
    
    def add_new_knowledge(self, text: str, metadata: Dict):
        """Add new knowledge to the vector database"""
        if self.use_chromadb:
            try:
                doc_id = f"doc_{uuid.uuid4().hex[:8]}"
                self.collection.add(
                    documents=[text],
                    metadatas=[metadata],
                    ids=[doc_id]
                )
                logger.info(f"Added new knowledge to ChromaDB: {doc_id}")
            except Exception as e:
                logger.error(f"Error adding knowledge to ChromaDB: {e}")
                self.use_chromadb = False
        
        # Fallback: Add to simple dictionary
        if not self.use_chromadb:
            doc_id = f"doc_{uuid.uuid4().hex[:8]}"
            self.knowledge_base[doc_id] = {
                "text": text,
                "metadata": metadata
            }
            logger.info(f"Added new knowledge to fallback: {doc_id}")

# Initialize RAG system
rag_system = RAGSystem()

# Initialize the Gemini model with salon context
model = genai.GenerativeModel(
    "gemini-2.0-flash-exp",
    system_instruction=SALON_CONTEXT
)

# Individual AI Agents
class VoiceAgent:
    """Handles speech-to-text and text-to-speech conversion"""
    
    def __init__(self):
        self.speech_recognition_available = SPEECH_RECOGNITION_AVAILABLE
        self.tts_available = TTS_AVAILABLE
        
        if self.speech_recognition_available and sr is not None:
            try:
                self.recognizer = sr.Recognizer()
                self.microphone = sr.Microphone()
                logger.info("Speech recognition initialized")
            except Exception as e:
                logger.warning(f"Speech recognition setup failed: {e}")
                self.speech_recognition_available = False
        
        if self.tts_available and pyttsx3 is not None:
            try:
                self.tts_engine = pyttsx3.init()
                self._setup_voice()
                logger.info("Text-to-speech initialized")
            except Exception as e:
                logger.warning(f"Text-to-speech setup failed: {e}")
                self.tts_available = False
    
    def _setup_voice(self):
        """Configure text-to-speech settings"""
        if not self.tts_available:
            return
            
        try:
            voices = self.tts_engine.getProperty('voices')
            if voices and len(voices) > 1:
                self.tts_engine.setProperty('voice', voices[1].id)  # Female voice
            self.tts_engine.setProperty('rate', 150)  # Speed of speech
        except Exception as e:
            logger.warning(f"Voice setup failed: {e}")
    
    def listen_to_customer(self) -> str:
        """Convert speech to text"""
        if not self.speech_recognition_available:
            return "Speech recognition not available. Please type your message."
        
        try:
            with self.microphone as source:
                self.recognizer.adjust_for_ambient_noise(source)
                logger.info("Listening...")
                audio = self.recognizer.listen(source, timeout=5)
            
            text = self.recognizer.recognize_google(audio)
            logger.info(f"Recognized: {text}")
            return text
        except sr.WaitTimeoutError:
            return "No speech detected"
        except sr.UnknownValueError:
            return "Could not understand audio"
        except Exception as e:
            logger.error(f"Speech recognition error: {e}")
            return "Error in speech recognition"
    
    def speak_to_customer(self, text: str):
        """Convert text to speech"""
        if not self.tts_available:
            logger.info(f"TTS not available. Would speak: {text}")
            return
            
        try:
            self.tts_engine.say(text)
            self.tts_engine.runAndWait()
            logger.info(f"Spoke: {text}")
        except Exception as e:
            logger.error(f"Text-to-speech error: {e}")

class RAGAgent:
    """Handles retrieval of relevant information from knowledge base"""
    
    def __init__(self, rag_system: RAGSystem):
        self.rag_system = rag_system
    
    def get_relevant_context(self, user_query: str) -> str:
        """Retrieve relevant context for the user query"""
        relevant_info = self.rag_system.search_relevant_info(user_query)
        
        if relevant_info:
            context = "Based on our salon information:\n"
            for info in relevant_info:
                context += f"- {info['text']}\n"
            return context
        return ""

class BookingAgent:
    """Handles booking logic and appointment management"""
    
    def __init__(self):
        self.bookings_file = "data/bookings.xlsx"
    
    def process_booking_request(self, context: ConversationContext, user_input: str) -> Dict:
        """Process booking-related queries and requests"""
        current_step = context.current_step
        
        if current_step == "greeting":
            if any(word in user_input.lower() for word in ["book", "appointment", "schedule"]):
                context.current_step = "get_name"
                return {
                    "response": "I'd be happy to help you book an appointment! May I have your name please?",
                    "next_step": "get_name"
                }
            else:
                return {
                    "response": "How can I assist you today? Would you like to know about our services or book an appointment?",
                    "next_step": "greeting"
                }
        
        elif current_step == "get_name":
            context.customer_name = user_input
            context.current_step = "get_phone"
            return {
                "response": f"Nice to meet you, {user_input}! Could you please provide your phone number?",
                "next_step": "get_phone"
            }
        
        elif current_step == "get_phone":
            context.phone = user_input
            context.current_step = "get_service"
            return {
                "response": "Thank you! Which service would you like to book? We offer haircuts, styling, coloring, spa treatments, bridal services, and kids services.",
                "next_step": "get_service"
            }
        
        elif current_step == "get_service":
            context.booking_data["service"] = user_input
            context.current_step = "get_date"
            return {
                "response": f"Great choice! For {user_input}, what date would you prefer? Please mention the date or day.",
                "next_step": "get_date"
            }
        
        elif current_step == "get_date":
            context.booking_data["date"] = user_input
            context.current_step = "get_time"
            return {
                "response": f"Perfect! For {context.booking_data['date']}, what time would work best for you? Our service hours are 9 AM to 8 PM.",
                "next_step": "get_time"
            }
        
        elif current_step == "get_time":
            context.booking_data["time"] = user_input
            context.current_step = "get_address"
            return {
                "response": f"Excellent! What's your address for our doorstep service?",
                "next_step": "get_address"
            }
        
        elif current_step == "get_address":
            context.booking_data["address"] = user_input
            context.current_step = "confirm_booking"
            return self._confirm_booking(context)
        
        elif current_step == "confirm_booking":
            if any(word in user_input.lower() for word in ["yes", "confirm", "book"]):
                return self._finalize_booking(context)
            else:
                context.current_step = "greeting"
                return {
                    "response": "No problem! Let me know if you'd like to make any changes or if I can help with anything else.",
                    "next_step": "greeting"
                }
        
        return {"response": "I'm not sure how to help with that. Could you please rephrase?", "next_step": current_step}
    
    def _confirm_booking(self, context: ConversationContext) -> Dict:
        """Generate booking confirmation message"""
        booking_summary = f"""
Booking Summary:
- Name: {context.customer_name}
- Phone: {context.phone}
- Service: {context.booking_data['service']}
- Date: {context.booking_data['date']}
- Time: {context.booking_data['time']}
- Address: {context.booking_data['address']}

Does this look correct? Please say 'yes' to confirm or 'no' to make changes.
        """
        return {
            "response": booking_summary,
            "next_step": "confirm_booking"
        }
    
    def _finalize_booking(self, context: ConversationContext) -> Dict:
        """Finalize the booking and return booking details"""
        booking_id = f"BG{datetime.now().strftime('%Y%m%d%H%M%S')}"
        
        booking_data = {
            "booking_id": booking_id,
            "customer_name": context.customer_name,
            "phone": context.phone,
            "service": context.booking_data["service"],
            "date": context.booking_data["date"],
            "time": context.booking_data["time"],
            "address": context.booking_data["address"],
            "status": "confirmed",
            "created_at": datetime.now().isoformat()
        }
        
        # Reset context for new booking
        context.current_step = "greeting"
        context.booking_data = {}
        
        return {
            "response": f"Perfect! Your booking has been confirmed. Booking ID: {booking_id}. You will receive a confirmation message shortly. Thank you for choosing Goodness Glamour Salon!",
            "next_step": "greeting",
            "booking_data": booking_data
        }

class TwilioVoiceHandler:
    """Handles Twilio voice calls and callbacks"""
    
    def __init__(self):
        # Try to import and initialize Twilio directly
        try:
            from twilio.rest import Client
            from twilio.twiml.voice_response import VoiceResponse
            self.client = Client(TWILIO_ACCOUNT_SID, TWILIO_AUTH_TOKEN)
            self.twilio_available = True
            logger.info("Twilio client initialized successfully")
        except ImportError as e:
            logger.error(f"Twilio import failed: {e}")
            self.twilio_available = False
            self.client = None
        except Exception as e:
            logger.error(f"Twilio initialization failed: {e}")
            self.twilio_available = False
            self.client = None
    
    def make_voice_call(self, customer_phone: str, webhook_url: str) -> bool:
        """Make a voice call to customer"""
        if not self.twilio_available:
            logger.warning("Twilio not available. Cannot make voice call.")
            return False
        
        try:
            call = self.client.calls.create(
                to=customer_phone,
                from_=TWILIO_PHONE_NUMBER,
                url=webhook_url,
                method='POST'
            )
            logger.info(f"Voice call initiated to {customer_phone}. Call SID: {call.sid}")
            return True
        except Exception as e:
            logger.error(f"Failed to make voice call: {e}")
            return False
    
    def generate_twiml_response(self, text: str) -> str:
        """Generate TwiML response for voice call"""
        if VoiceResponse is None:
            return ""
        
        response = VoiceResponse()
        response.say(text, voice='alice', language='en-IN')
        response.pause(length=1)
        response.gather(
            input='speech',
            action=f'{WEBHOOK_URL}/voice/process',
            speech_timeout='auto',
            timeout=10
        )
        response.say("I didn't hear anything. Please try again.")
        response.redirect(f'{WEBHOOK_URL}/voice/process')
        
        return str(response)
    
    def send_sms(self, to_phone: str, message: str) -> bool:
        """Send SMS via Twilio"""
        if not self.twilio_available:
            logger.warning("Twilio not available. Cannot send SMS.")
            return False
        
        try:
            message_obj = self.client.messages.create(
                body=message,
                from_=TWILIO_PHONE_NUMBER,
                to=to_phone
            )
            logger.info(f"SMS sent to {to_phone}. Message SID: {message_obj.sid}")
            return True
        except Exception as e:
            logger.error(f"Failed to send SMS: {e}")
            return False

class DatabaseHandler:
    """Handles database operations for bookings and customer data"""
    
    def __init__(self, db_path: str = "data/salon_bookings.db"):
        self.db_path = db_path
        self.database_available = DATABASE_AVAILABLE
        
        if self.database_available and sqlite3 is not None:
            self._initialize_database()
        else:
            logger.warning("Database not available. Using file-based storage.")
    
    def _initialize_database(self):
        """Initialize SQLite database with required tables"""
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            
            # Create bookings table
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS bookings (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    booking_id TEXT UNIQUE NOT NULL,
                    customer_name TEXT NOT NULL,
                    phone TEXT NOT NULL,
                    service TEXT NOT NULL,
                    date TEXT NOT NULL,
                    time TEXT NOT NULL,
                    address TEXT NOT NULL,
                    status TEXT DEFAULT 'confirmed',
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    notes TEXT
                )
            ''')
            
            # Create customers table
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS customers (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    name TEXT NOT NULL,
                    phone TEXT UNIQUE NOT NULL,
                    email TEXT,
                    address TEXT,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    last_visit TIMESTAMP
                )
            ''')
            
            conn.commit()
            conn.close()
            logger.info("Database initialized successfully")
        except Exception as e:
            logger.error(f"Database initialization failed: {e}")
            self.database_available = False
    
    def save_booking(self, booking_data: Dict) -> bool:
        """Save booking to database"""
        if not self.database_available:
            return self._save_booking_to_file(booking_data)
        
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            
            cursor.execute('''
                INSERT INTO bookings 
                (booking_id, customer_name, phone, service, date, time, address, status, notes)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
            ''', (
                booking_data['booking_id'],
                booking_data['customer_name'],
                booking_data['phone'],
                booking_data['service'],
                booking_data['date'],
                booking_data['time'],
                booking_data['address'],
                booking_data.get('status', 'confirmed'),
                booking_data.get('notes', '')
            ))
            
            # Also save/update customer info
            cursor.execute('''
                INSERT OR REPLACE INTO customers (name, phone, address, last_visit)
                VALUES (?, ?, ?, CURRENT_TIMESTAMP)
            ''', (
                booking_data['customer_name'],
                booking_data['phone'],
                booking_data['address']
            ))
            
            conn.commit()
            conn.close()
            logger.info(f"Booking saved to database: {booking_data['booking_id']}")
            return True
        except Exception as e:
            logger.error(f"Failed to save booking: {e}")
            return False
    
    def _save_booking_to_file(self, booking_data: Dict) -> bool:
        """Fallback: Save booking to Excel file"""
        try:
            import pandas as pd
            import os
            
            os.makedirs("data", exist_ok=True)
            file_path = "data/bookings.xlsx"
            
            # Load existing data or create new
            if os.path.exists(file_path):
                df = pd.read_excel(file_path)
            else:
                df = pd.DataFrame(columns=[
                    'booking_id', 'customer_name', 'phone', 'service', 
                    'date', 'time', 'address', 'status', 'created_at', 'notes'
                ])
            
            # Add new booking
            new_row = pd.DataFrame([booking_data])
            df = pd.concat([df, new_row], ignore_index=True)
            
            # Save to Excel
            df.to_excel(file_path, index=False)
            logger.info(f"Booking saved to Excel: {booking_data['booking_id']}")
            return True
        except Exception as e:
            logger.error(f"Failed to save booking to file: {e}")
            return False
    
    def get_customer_history(self, phone: str) -> List[Dict]:
        """Get customer booking history"""
        if not self.database_available:
            return []
        
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            
            cursor.execute('''
                SELECT booking_id, service, date, time, status, created_at
                FROM bookings 
                WHERE phone = ? 
                ORDER BY created_at DESC
            ''', (phone,))
            
            history = []
            for row in cursor.fetchall():
                history.append({
                    'booking_id': row[0],
                    'service': row[1],
                    'date': row[2],
                    'time': row[3],
                    'status': row[4],
                    'created_at': row[5]
                })
            
            conn.close()
            return history
        except Exception as e:
            logger.error(f"Failed to get customer history: {e}")
            return []

class NotificationAgent:
    """Handles sending notifications via SMS, email, and WhatsApp"""
    
    def __init__(self):
        self.salon_phone = "9036626642"
        self.salon_email = "2akonsultant@gmail.com"
        self.twilio_handler = TwilioVoiceHandler()
    
    def send_booking_confirmation(self, booking_data: Dict):
        """Send booking confirmation to customer and salon"""
        try:
            # Customer SMS
            customer_message = f"""Goodness Glamour Salon - Booking Confirmed!

Booking ID: {booking_data['booking_id']}
Service: {booking_data['service']}
Date: {booking_data['date']}
Time: {booking_data['time']}
Address: {booking_data['address']}

We'll be at your doorstep at the scheduled time. Thank you!"""
            
            # Salon notification
            salon_message = f"""New Booking Alert!

Customer: {booking_data['customer_name']}
Phone: {booking_data['phone']}
Service: {booking_data['service']}
Date: {booking_data['date']}
Time: {booking_data['time']}
Address: {booking_data['address']}
Booking ID: {booking_data['booking_id']}"""
            
            # Send SMS to customer
            if self.twilio_handler.twilio_available:
                self.twilio_handler.send_sms(booking_data['phone'], customer_message)
                self.twilio_handler.send_sms(self.salon_phone, salon_message)
            else:
                logger.info(f"Customer message: {customer_message}")
                logger.info(f"Salon message: {salon_message}")
            
            return True
        except Exception as e:
            logger.error(f"Error sending notifications: {e}")
            return False

# Main Orchestration System
class AgenticSalonAI:
    """Main orchestration system for all agents"""
    
    def __init__(self):
        self.voice_agent = VoiceAgent()
        self.rag_agent = RAGAgent(rag_system)
        self.booking_agent = BookingAgent()
        self.notification_agent = NotificationAgent()
        self.twilio_handler = TwilioVoiceHandler()
        self.database_handler = DatabaseHandler()
        self.conversation_context = ConversationContext(session_id=str(uuid.uuid4()))
        self.chat = model.start_chat(history=[])
    
    def process_user_input(self, user_input: str, use_voice: bool = False) -> str:
        """Process user input through the agentic AI system"""
        try:
            # Check if this is a booking-related query
            if any(word in user_input.lower() for word in ["book", "appointment", "schedule", "name", "phone", "service", "date", "time", "address"]):
                # Use booking agent
                booking_response = self.booking_agent.process_booking_request(
                    self.conversation_context, user_input
                )
                
                # If booking is finalized, save to database and send notifications
                if "booking_data" in booking_response:
                    # Save booking to database
                    self.database_handler.save_booking(booking_response["booking_data"])
                    
                    # Send notifications
                    self.notification_agent.send_booking_confirmation(
                        booking_response["booking_data"]
                    )
                
                response = booking_response["response"]
            else:
                # Use RAG system to get relevant context
                rag_context = self.rag_agent.get_relevant_context(user_input)
                
                # Prepare enhanced prompt with RAG context
                enhanced_prompt = user_input
                if rag_context:
                    enhanced_prompt = f"{rag_context}\n\nCustomer Question: {user_input}"
                
                # Get response from Gemini
                gemini_response = self.chat.send_message(enhanced_prompt)
                response = gemini_response.text
            
            # Speak response if voice mode is enabled
            if use_voice:
                self.voice_agent.speak_to_customer(response)
            
            return response
            
        except Exception as e:
            error_msg = f"I apologize, but I'm having trouble processing your request right now. Please try again."
            logger.error(f"Error in process_user_input: {e}")
            
            if use_voice:
                self.voice_agent.speak_to_customer(error_msg)
            
            return error_msg
    
    def start_voice_conversation(self):
        """Start a voice-based conversation"""
        if not self.voice_agent.speech_recognition_available:
            print("WARNING: Voice input not available. Starting text conversation instead.")
            print("TEXT CONVERSATION started! Type 'exit' to end.")
            
            while True:
                try:
                    user_input = input("\nYou: ").strip()
                    if user_input.lower() == "exit":
                        break
                    
                    response = self.process_user_input(user_input)
                    print(f"Assistant: {response}")
                    
                except KeyboardInterrupt:
                    print("\nConversation ended by user.")
                    break
                except Exception as e:
                    logger.error(f"Error in text conversation: {e}")
                    print("I'm sorry, I encountered an error. Please try again.")
            
            return
        
        print("VOICE CONVERSATION started! Say 'exit' to end.")
        self.voice_agent.speak_to_customer("Hello! Welcome to Goodness Glamour Salon. How can I help you today?")
        
        while True:
            try:
                # Listen to customer
                user_input = self.voice_agent.listen_to_customer()
                
                if user_input.lower() in ["exit", "quit", "stop", "goodbye"]:
                    self.voice_agent.speak_to_customer("Thank you for calling Goodness Glamour Salon. Have a great day!")
                    break
                
                if user_input in ["No speech detected", "Could not understand audio", "Error in speech recognition"]:
                    self.voice_agent.speak_to_customer("I didn't catch that. Could you please repeat?")
                    continue
                
                # Process the input
                response = self.process_user_input(user_input, use_voice=True)
                print(f"Customer: {user_input}")
                print(f"Assistant: {response}")
                
            except KeyboardInterrupt:
                print("\nConversation ended by user.")
                break
            except Exception as e:
                logger.error(f"Error in voice conversation: {e}")
                self.voice_agent.speak_to_customer("I'm sorry, I encountered an error. Please try again.")
    
    def trigger_voice_call(self, customer_phone: str, webhook_url: str) -> bool:
        """Trigger a voice call to customer when QR code is scanned"""
        try:
            if self.twilio_handler.twilio_available:
                return self.twilio_handler.make_voice_call(customer_phone, webhook_url)
            else:
                logger.warning("Twilio not available. Cannot make voice call.")
                return False
        except Exception as e:
            logger.error(f"Error triggering voice call: {e}")
            return False
    
    def process_voice_call(self, speech_input: str) -> str:
        """Process voice call input and return TwiML response"""
        try:
            # Process the speech input
            response = self.process_user_input(speech_input, use_voice=False)
            
            # Generate TwiML response
            twiml_response = self.twilio_handler.generate_twiml_response(response)
            return twiml_response
        except Exception as e:
            logger.error(f"Error processing voice call: {e}")
            error_response = "I'm sorry, I'm having trouble understanding. Please try again."
            return self.twilio_handler.generate_twiml_response(error_response)

# Test the chatbot
def send_message(user_message):
    """Legacy function for backward compatibility"""
    try:
        ai_system = AgenticSalonAI()
        return ai_system.process_user_input(user_message, use_voice=False)
    except Exception as e:
        return f"Error: {str(e)}"

# Example usage and testing
if __name__ == "__main__":
    print("AGENTIC SALON AI SYSTEM")
    print("=" * 50)
    
    # Initialize the AI system
    salon_ai = AgenticSalonAI()
    
    print("\nChoose interaction mode:")
    print("1. Text conversation")
    print("2. Voice conversation")
    print("3. Test RAG system")
    print("4. Test booking flow")
    
    choice = input("\nEnter your choice (1-4): ").strip()
    
    if choice == "1":
        print("\nTEXT CONVERSATION MODE")
        print("Type 'exit' to quit")
        while True:
            user_input = input("\nYou: ").strip()
            if user_input.lower() == "exit":
                break
            response = salon_ai.process_user_input(user_input)
            print(f"Assistant: {response}")
    
    elif choice == "2":
        print("\nVOICE CONVERSATION MODE")
        salon_ai.start_voice_conversation()
    
    elif choice == "3":
        print("\nTESTING RAG SYSTEM")
        test_queries = [
            "What are your hair coloring prices?",
            "Do you provide doorstep services?",
            "What time do you open?",
            "How much does bridal makeup cost?"
        ]
        
        for query in test_queries:
            print(f"\nQuery: {query}")
            context = salon_ai.rag_agent.get_relevant_context(query)
            if context:
                print(f"RAG Context: {context}")
            else:
                print("No relevant context found")
    
    elif choice == "4":
        print("\nTESTING BOOKING FLOW")
        test_booking = [
            "I want to book an appointment",
            "My name is Sarah",
            "My phone is 9876543210",
            "I want hair coloring",
            "Tomorrow",
            "2 PM",
            "123 Main Street, Mumbai"
        ]
        
        for step in test_booking:
            print(f"\nCustomer: {step}")
            response = salon_ai.process_user_input(step)
            print(f"Assistant: {response}")
    
    else:
        print("Invalid choice. Running basic tests...")
        
        # Basic functionality tests
        print("\nRUNNING BASIC TESTS")
        print("-" * 30)
        
        test_messages = [
            "Hello! What services does Goodness Glamour Salon offer?",
            "What are your prices for hair coloring?",
            "Do you provide doorstep services?",
            "I want to book an appointment"
        ]
        
        for msg in test_messages:
            print(f"\nUser: {msg}")
            response = salon_ai.process_user_input(msg)
            print(f"Bot: {response}")
    
    print("\n" + "=" * 50)
    print("SUCCESS: Agentic Salon AI System is ready!")
    print("FEATURES IMPLEMENTED:")
    print("   - Voice input/output with speech recognition")
    print("   - RAG system with Gemini-enhanced search")
    print("   - Multi-agent architecture (Voice, RAG, Booking, Notification)")
    print("   - Intelligent conversation flow management")
    print("   - Booking confirmation and notifications")
    print("   - Ready for Twilio integration")
