"""
Configuration file for Agentic Salon AI Voice Assistant
Update these values with your actual API keys and settings
"""

import os
from typing import Optional

class Config:
    """Configuration class for the Salon AI system"""
    
    # Gemini AI Configuration
    GEMINI_API_KEY: str = os.getenv("GEMINI_API_KEY", "AIzaSyDEw4nW0xV_FQKf1SUX9fFJwnEY5n8_Jwc")
    
    # Twilio Configuration
    TWILIO_ACCOUNT_SID: str = os.getenv("TWILIO_ACCOUNT_SID", "ACd8941e7d6933a9e031879bc28d7af7e8")
    TWILIO_AUTH_TOKEN: str = os.getenv("TWILIO_AUTH_TOKEN", "815e90983ed99b02e52943cc14602d56")
    TWILIO_PHONE_NUMBER: str = os.getenv("TWILIO_PHONE_NUMBER", "+917019035686")
    
    # Webhook Configuration
    WEBHOOK_URL: str = os.getenv("WEBHOOK_URL", "https://your-domain.com")  # Replace with your domain
    
    # Database Configuration
    DATABASE_URL: str = os.getenv("DATABASE_URL", "sqlite:///data/salon_bookings.db")
    
    # Salon Information
    SALON_NAME: str = "Goodness Glamour Salon"
    SALON_PHONE: str = "9036626642"
    SALON_EMAIL: str = "2akonsultant@gmail.com"
    SALON_HOURS: str = "Monday - Sunday, 9:00 AM - 8:00 PM"
    
    # API Server Configuration
    API_HOST: str = os.getenv("API_HOST", "0.0.0.0")
    API_PORT: int = int(os.getenv("API_PORT", "8000"))
    DEBUG: bool = os.getenv("DEBUG", "False").lower() == "true"
    
    # Voice Configuration
    VOICE_LANGUAGE: str = "en-IN"
    VOICE_NAME: str = "alice"
    SPEECH_TIMEOUT: int = 10
    
    # RAG Configuration
    CHROMA_PERSIST_DIRECTORY: str = "./chroma_db"
    VECTOR_SEARCH_RESULTS: int = 3
    
    # Notification Configuration
    ENABLE_SMS_NOTIFICATIONS: bool = os.getenv("ENABLE_SMS_NOTIFICATIONS", "True").lower() == "true"
    ENABLE_EMAIL_NOTIFICATIONS: bool = os.getenv("ENABLE_EMAIL_NOTIFICATIONS", "False").lower() == "true"
    
    @classmethod
    def validate_config(cls) -> bool:
        """Validate that all required configuration is present"""
        required_fields = [
            "GEMINI_API_KEY",
            "TWILIO_ACCOUNT_SID", 
            "TWILIO_AUTH_TOKEN",
            "TWILIO_PHONE_NUMBER",
            "WEBHOOK_URL"
        ]
        
        missing_fields = []
        for field in required_fields:
            value = getattr(cls, field)
            if not value or value.startswith("your_") or value == "https://your-domain.com":
                missing_fields.append(field)
        
        if missing_fields:
            print(f"❌ Missing or invalid configuration for: {', '.join(missing_fields)}")
            return False
        
        print("✅ Configuration validation passed")
        return True
    
    @classmethod
    def get_salon_context(cls) -> str:
        """Get the salon context for AI"""
        return f"""
You are an AI assistant for {cls.SALON_NAME}, a premium ladies and kids salon offering doorstep beauty services.

SALON INFORMATION:
- Name: {cls.SALON_NAME}
- Contact: {cls.SALON_PHONE}
- Email: {cls.SALON_EMAIL}
- Service Hours: {cls.SALON_HOURS}
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

# Create global config instance
config = Config()
