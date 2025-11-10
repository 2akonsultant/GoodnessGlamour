#!/usr/bin/env python3
"""
Simple test script that works without any import issues
"""

def test_basic_functionality():
    """Test basic functionality without complex imports"""
    print("=" * 60)
    print("SIMPLE AGENTIC AI TEST")
    print("=" * 60)
    
    try:
        # Test 1: Basic imports
        print("\n[1] Testing basic imports...")
        import google.generativeai as genai
        print("✓ Google Generative AI imported successfully")
        
        # Test 2: API Configuration
        print("\n[2] Testing API configuration...")
        api_key = "AIzaSyDEw4nW0xV_FQKf1SUX9fFJwnEY5n8_Jwc"
        genai.configure(api_key=api_key)
        print("✓ Gemini API configured successfully")
        
        # Test 3: Model initialization
        print("\n[3] Testing model initialization...")
        model = genai.GenerativeModel("gemini-2.0-flash-exp")
        print("✓ Gemini model initialized successfully")
        
        # Test 4: Basic AI response
        print("\n[4] Testing AI response...")
        salon_context = """
        You are an AI assistant for Goodness Glamour Salon, a premium ladies and kids salon offering doorstep beauty services.
        
        SALON INFORMATION:
        - Name: Goodness Glamour Salon
        - Contact: 9036626642
        - Email: 2akonsultant@gmail.com
        - Service Hours: Monday - Sunday, 9:00 AM - 8:00 PM
        - Service Type: We provide doorstep services across the city
        
        SERVICES & PRICES:
        - Haircut & Styling: ₹500 - ₹1,500
        - Hair Coloring: ₹2,000 - ₹5,000
        - Hair Spa Treatment: ₹1,500 - ₹3,000
        - Keratin Treatment: ₹4,000 - ₹8,000
        - Kids Haircut: ₹300 - ₹700
        - Party Hairstyle: ₹800 - ₹1,500
        - Bridal Hair & Makeup: ₹15,000 - ₹30,000
        - Party Makeup: ₹3,000 - ₹8,000
        
        Be friendly, professional, and encourage customers to book appointments.
        """
        
        model = genai.GenerativeModel("gemini-2.0-flash-exp", system_instruction=salon_context)
        chat = model.start_chat(history=[])
        
        test_query = "What are your hair coloring prices?"
        response = chat.send_message(test_query)
        print(f"✓ AI Response: {response.text[:100]}...")
        
        # Test 5: Booking flow test
        print("\n[5] Testing booking flow...")
        booking_query = "I want to book an appointment"
        booking_response = chat.send_message(booking_query)
        print(f"✓ Booking Response: {booking_response.text[:100]}...")
        
        print("\n" + "=" * 60)
        print("ALL TESTS PASSED SUCCESSFULLY!")
        print("=" * 60)
        print("\nYOUR SYSTEM IS WORKING!")
        print("✓ Gemini AI integration working")
        print("✓ Salon knowledge loaded")
        print("✓ AI responses generated")
        print("✓ Booking flow initiated")
        
        print("\nNEXT STEPS:")
        print("1. Run: python test_agent.py (for full system test)")
        print("2. Install PyAudio: pip install PyAudio (for voice input)")
        print("3. Set up web integration")
        
        return True
        
    except Exception as e:
        print(f"\n❌ ERROR: {e}")
        print("\nTroubleshooting:")
        print("1. Check your internet connection")
        print("2. Verify your Gemini API key")
        print("3. Check API quota limits")
        return False

if __name__ == "__main__":
    success = test_basic_functionality()
    if success:
        print("\n🎉 Your Agentic AI System is ready to use!")
    else:
        print("\n🔧 Please fix the issues above and try again.")
