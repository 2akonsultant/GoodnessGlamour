"""
Configuration file for Agentic Salon AI System
Copy this to config.py and update with your actual values
"""

import os
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Gemini AI Configuration
GEMINI_API_KEY = os.getenv('GEMINI_API_KEY', 'your_gemini_api_key_here')

# OpenAI Configuration (for embeddings)
OPENAI_API_KEY = os.getenv('OPENAI_API_KEY', 'your_openai_api_key_here')

# Twilio Configuration
TWILIO_ACCOUNT_SID = os.getenv('TWILIO_ACCOUNT_SID', 'your_twilio_account_sid')
TWILIO_AUTH_TOKEN = os.getenv('TWILIO_AUTH_TOKEN', 'your_twilio_auth_token')
TWILIO_PHONE_NUMBER = os.getenv('TWILIO_PHONE_NUMBER', '+1234567890')

# Flask Configuration
FLASK_ENV = os.getenv('FLASK_ENV', 'development')
FLASK_DEBUG = os.getenv('FLASK_DEBUG', 'True').lower() == 'true'

# Server Configuration
SERVER_HOST = os.getenv('SERVER_HOST', '0.0.0.0')
SERVER_PORT = int(os.getenv('SERVER_PORT', '5000'))

# Database Configuration
CHROMA_DB_PATH = os.getenv('CHROMA_DB_PATH', './chroma_db')

# Salon Configuration
SALON_NAME = os.getenv('SALON_NAME', 'Goodness Glamour Salon')
SALON_PHONE = os.getenv('SALON_PHONE', '9036626642')
SALON_EMAIL = os.getenv('SALON_EMAIL', '2akonsultant@gmail.com')
SALON_ADDRESS = os.getenv('SALON_ADDRESS', 'Your Salon Address Here')

# Voice Configuration
VOICE_RATE = int(os.getenv('VOICE_RATE', '150'))
VOICE_VOLUME = float(os.getenv('VOICE_VOLUME', '0.8'))
VOICE_TIMEOUT = int(os.getenv('VOICE_TIMEOUT', '5'))

# RAG Configuration
RAG_RESULTS_LIMIT = int(os.getenv('RAG_RESULTS_LIMIT', '3'))
RAG_SIMILARITY_THRESHOLD = float(os.getenv('RAG_SIMILARITY_THRESHOLD', '0.7'))

# Notification Configuration
SEND_SMS_CONFIRMATIONS = os.getenv('SEND_SMS_CONFIRMATIONS', 'True').lower() == 'true'
SEND_EMAIL_CONFIRMATIONS = os.getenv('SEND_EMAIL_CONFIRMATIONS', 'True').lower() == 'true'
SEND_WHATSAPP_CONFIRMATIONS = os.getenv('SEND_WHATSAPP_CONFIRMATIONS', 'False').lower() == 'true'

# Logging Configuration
LOG_LEVEL = os.getenv('LOG_LEVEL', 'INFO')
LOG_FILE = os.getenv('LOG_FILE', 'salon_ai.log')

# API Configuration
API_RATE_LIMIT = int(os.getenv('API_RATE_LIMIT', '100'))  # requests per minute
API_TIMEOUT = int(os.getenv('API_TIMEOUT', '30'))  # seconds

# Security Configuration
SECRET_KEY = os.getenv('SECRET_KEY', 'your_secret_key_here')
ENCRYPTION_KEY = os.getenv('ENCRYPTION_KEY', 'your_encryption_key_here')

# Development/Production flags
IS_PRODUCTION = os.getenv('ENVIRONMENT', 'development') == 'production'
ENABLE_DEBUG_MODE = not IS_PRODUCTION

# Webhook Configuration
WEBHOOK_BASE_URL = os.getenv('WEBHOOK_BASE_URL', 'https://your-domain.com')
VERIFY_WEBHOOK_SIGNATURES = os.getenv('VERIFY_WEBHOOK_SIGNATURES', 'True').lower() == 'true'

# Database URLs (for production)
DATABASE_URL = os.getenv('DATABASE_URL', 'sqlite:///salon_ai.db')
REDIS_URL = os.getenv('REDIS_URL', 'redis://localhost:6379')

# External Service URLs
GEMINI_API_URL = 'https://generativelanguage.googleapis.com/v1beta'
OPENAI_API_URL = 'https://api.openai.com/v1'
TWILIO_API_URL = 'https://api.twilio.com/2010-04-01'

# Feature Flags
ENABLE_VOICE_RECOGNITION = os.getenv('ENABLE_VOICE_RECOGNITION', 'True').lower() == 'true'
ENABLE_TEXT_TO_SPEECH = os.getenv('ENABLE_TEXT_TO_SPEECH', 'True').lower() == 'true'
ENABLE_RAG_SYSTEM = os.getenv('ENABLE_RAG_SYSTEM', 'True').lower() == 'true'
ENABLE_BOOKING_SYSTEM = os.getenv('ENABLE_BOOKING_SYSTEM', 'True').lower() == 'true'
ENABLE_NOTIFICATIONS = os.getenv('ENABLE_NOTIFICATIONS', 'True').lower() == 'true'

# Monitoring and Analytics
ENABLE_ANALYTICS = os.getenv('ENABLE_ANALYTICS', 'True').lower() == 'true'
ANALYTICS_SERVICE_URL = os.getenv('ANALYTICS_SERVICE_URL', '')
GOOGLE_ANALYTICS_ID = os.getenv('GOOGLE_ANALYTICS_ID', '')

# Backup and Storage
BACKUP_ENABLED = os.getenv('BACKUP_ENABLED', 'True').lower() == 'true'
BACKUP_FREQUENCY = os.getenv('BACKUP_FREQUENCY', 'daily')  # daily, weekly, monthly
STORAGE_BUCKET = os.getenv('STORAGE_BUCKET', '')

# Performance Settings
MAX_CONCURRENT_CALLS = int(os.getenv('MAX_CONCURRENT_CALLS', '10'))
CALL_TIMEOUT = int(os.getenv('CALL_TIMEOUT', '300'))  # 5 minutes
SESSION_TIMEOUT = int(os.getenv('SESSION_TIMEOUT', '1800'))  # 30 minutes

# Error Handling
MAX_RETRIES = int(os.getenv('MAX_RETRIES', '3'))
RETRY_DELAY = int(os.getenv('RETRY_DELAY', '1'))  # seconds
ENABLE_CIRCUIT_BREAKER = os.getenv('ENABLE_CIRCUIT_BREAKER', 'True').lower() == 'true'

# Custom Configuration
CUSTOM_SALON_INFO = {
    'services': [
        'Haircut & Styling',
        'Hair Coloring',
        'Hair Spa Treatment',
        'Keratin Treatment',
        'Kids Haircut',
        'Party Hairstyle',
        'Creative Braiding',
        'Bridal Hair & Makeup',
        'Party Makeup'
    ],
    'working_hours': {
        'monday': '9:00 AM - 8:00 PM',
        'tuesday': '9:00 AM - 8:00 PM',
        'wednesday': '9:00 AM - 8:00 PM',
        'thursday': '9:00 AM - 8:00 PM',
        'friday': '9:00 AM - 8:00 PM',
        'saturday': '9:00 AM - 8:00 PM',
        'sunday': '9:00 AM - 8:00 PM'
    },
    'service_areas': [
        'Mumbai',
        'Delhi',
        'Bangalore',
        'Chennai',
        'Kolkata'
    ]
}

# Validation
def validate_config():
    """Validate that all required configuration is present"""
    required_vars = [
        'GEMINI_API_KEY',
        'OPENAI_API_KEY',
        'TWILIO_ACCOUNT_SID',
        'TWILIO_AUTH_TOKEN',
        'TWILIO_PHONE_NUMBER'
    ]
    
    missing_vars = []
    for var in required_vars:
        if not globals().get(var) or globals().get(var).startswith('your_'):
            missing_vars.append(var)
    
    if missing_vars:
        raise ValueError(f"Missing required configuration: {', '.join(missing_vars)}")
    
    return True

# Auto-validate on import
if __name__ != '__main__':
    try:
        validate_config()
    except ValueError as e:
        print(f"Configuration Error: {e}")
        print("Please update your configuration file with actual values.")
