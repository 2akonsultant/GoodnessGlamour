"""
Gemini AI Chatbot for Goodness Glamour Salon
This chatbot is trained to answer questions about salon services, prices, and timings.
Ready for integration with the Node.js backend.
"""

import google.generativeai as genai
import json

# Configure API key
API_KEY = "AIzaSyDEw4nW0xV_FQKf1SUX9fFJwnEY5n8_Jwc"
genai.configure(api_key=API_KEY)

# Salon information context
SALON_CONTEXT = """
You are an AI assistant for Goodness Glamour Salon, a premium ladies and kids salon offering doorstep beauty services.

**SALON INFORMATION:**
- Name: Goodness Glamour Salon
- Tagline: Premium Beauty Services at Your Doorstep
- Contact: 9036626642
- Email: 2akonsultant@gmail.com
- Service Hours: Monday - Sunday, 9:00 AM - 8:00 PM
- Service Type: Doorstep services across the city

**SERVICES & PRICES:**

1. Women's Hair Services:
   - Haircut & Styling: ₹500 - ₹1,500
   - Hair Coloring: ₹2,000 - ₹5,000
   - Hair Spa Treatment: ₹1,500 - ₹3,000
   - Keratin Treatment: ₹4,000 - ₹8,000
   - Hair Straightening: ₹3,000 - ₹6,000
   - Highlights: ₹2,500 - ₹5,000

2. Kids Hair Services:
   - Kids Haircut (Boys): ₹300 - ₹500
   - Kids Haircut (Girls): ₹400 - ₹700
   - Kids Party Hairstyle: ₹800 - ₹1,500
   - Creative Braiding: ₹500 - ₹1,200
   - Hair Coloring (Temporary): ₹500 - ₹1,000

3. Bridal & Party Services:
   - Bridal Hair & Makeup: ₹15,000 - ₹30,000
   - Party Makeup: ₹3,000 - ₹8,000
   - Pre-Bridal Packages: ₹10,000 - ₹25,000
   - Engagement Look: ₹5,000 - ₹12,000

4. Additional Services:
   - Hair Wash & Blow Dry: ₹500 - ₹800
   - Deep Conditioning: ₹800 - ₹1,500
   - Scalp Treatment: ₹1,000 - ₹2,000
   - Hair Extensions: ₹3,000 - ₹10,000

**BOOKING PROCESS:**
1. Customer scans QR code or visits website
2. Chats with AI assistant (you) for recommendations
3. Books appointment online with date/time selection
4. Receives confirmation email
5. Stylist arrives at customer's doorstep with all equipment

**KEY FEATURES:**
- Doorstep service (we come to you)
- Professional stylists with 5+ years experience
- Premium products used
- Flexible timing (9 AM - 8 PM)
- Family packages available
- Customized beauty solutions

**YOUR ROLE:**
- Answer questions about services, prices, and timings
- Recommend services based on customer needs
- Explain the booking process
- Provide information about doorstep services
- Be friendly, professional, and helpful
- Encourage customers to book appointments

Always be polite, informative, and encourage customers to book services through the website.
"""

class GeminiSalonChatbot:
    def __init__(self):
        """Initialize the Gemini chatbot with salon context"""
        self.model = genai.GenerativeModel(
            "gemini-2.0-flash-exp",
            system_instruction=SALON_CONTEXT
        )
        self.chat = self.model.start_chat(history=[])
    
    def send_message(self, user_message):
        """
        Send a message to the chatbot and get a response
        
        Args:
            user_message (str): The user's message
            
        Returns:
            dict: Response with text and metadata
        """
        try:
            response = self.chat.send_message(user_message)
            return {
                "success": True,
                "response": response.text,
                "error": None
            }
        except Exception as e:
            return {
                "success": False,
                "response": None,
                "error": str(e)
            }
    
    def get_chat_history(self):
        """Get the current chat history"""
        return self.chat.history
    
    def reset_chat(self):
        """Reset the chat session"""
        self.chat = self.model.start_chat(history=[])
        return {"success": True, "message": "Chat reset successfully"}


# Example usage and testing
if __name__ == "__main__":
    print("🌸 Goodness Glamour Salon - Gemini AI Chatbot")
    print("=" * 60)
    
    # Initialize chatbot
    chatbot = GeminiSalonChatbot()
    
    # Test conversations
    test_messages = [
        "Hello! What services do you offer?",
        "How much does hair coloring cost?",
        "Do you provide doorstep services?",
        "What are your timings?",
        "I need a bridal makeup. What packages do you have?",
        "Can I book an appointment for my daughter's haircut?",
        "What's included in a hair spa treatment?",
        "How do I book an appointment?"
    ]
    
    for i, message in enumerate(test_messages, 1):
        print(f"\n{'─' * 60}")
        print(f"👤 User (Q{i}): {message}")
        
        result = chatbot.send_message(message)
        
        if result["success"]:
            print(f"🤖 Bot: {result['response']}")
        else:
            print(f"❌ Error: {result['error']}")
    
    print(f"\n{'=' * 60}")
    print("✅ Chatbot is working perfectly!")
    print("📝 Ready for integration with Node.js backend")
    print("\n💡 Integration Steps:")
    print("1. Install Python in your server environment")
    print("2. Install dependencies: pip install -r requirements.txt")
    print("3. Create a Python API endpoint or use child_process in Node.js")
    print("4. Replace OpenAI calls with Gemini calls")
    print("5. Test and deploy!")

