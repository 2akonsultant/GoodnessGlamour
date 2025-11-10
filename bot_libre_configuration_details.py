#!/usr/bin/env python3
"""
Bot Libre configuration details for Goodness Glamour Salon
Complete setup checklist
"""

def show_basic_bot_details():
    """Show basic bot configuration details"""
    print("🤖 BASIC BOT CONFIGURATION:")
    print("="*35)
    
    print("\n📝 BOT DETAILS:")
    print("• Bot Name: Goodness Glamour Assistant")
    print("• Description: AI booking assistant for Goodness Glamour Salon")
    print("• Language: English")
    print("• Voice: Female (Indian accent if available)")
    print("• Persona: Friendly, professional, helpful")
    
    print("\n🏷️ CATEGORIES & TAGS:")
    print("• Categories: Business, Service")
    print("• Tags: salon, booking, appointment, beauty, hair, doorstep")
    
    print("\n🔒 ACCESS SETTINGS:")
    print("• Private: No (unchecked)")
    print("• Hidden: No (unchecked)")
    print("• Access Mode: Everyone")
    print("• Content Rating: Teen")

def show_salon_information():
    """Show salon information to input"""
    print("\n🏢 SALON INFORMATION:")
    print("="*25)
    
    print("\n📋 BASIC DETAILS:")
    print("• Salon Name: Goodness Glamour Salon")
    print("• Contact: 9036626642")
    print("• Email: 2akonsultant@gmail.com")
    print("• Service Hours: Monday - Sunday, 9:00 AM - 8:00 PM")
    print("• Service Type: Doorstep services across the city")
    
    print("\n✨ KEY FEATURES:")
    print("• Doorstep service (we come to your home)")
    print("• Professional stylists with 5+ years experience")
    print("• Premium products used")
    print("• Flexible timing (9 AM - 8 PM)")

def show_services_and_prices():
    """Show services and pricing information"""
    print("\n💇 SERVICES & PRICING:")
    print("="*25)
    
    print("\n👩 WOMEN'S HAIR SERVICES:")
    print("• Haircut & Styling: ₹500 - ₹1,500")
    print("• Hair Coloring: ₹2,000 - ₹5,000")
    print("• Hair Spa Treatment: ₹1,500 - ₹3,000")
    print("• Keratin Treatment: ₹4,000 - ₹8,000")
    
    print("\n👶 KIDS HAIR SERVICES:")
    print("• Kids Haircut: ₹300 - ₹700")
    print("• Party Hairstyle: ₹800 - ₹1,500")
    print("• Creative Braiding: ₹500 - ₹1,200")
    
    print("\n💄 BRIDAL & PARTY SERVICES:")
    print("• Bridal Hair & Makeup: ₹15,000 - ₹30,000")
    print("• Party Makeup: ₹3,000 - ₹8,000")

def show_conversation_flow():
    """Show conversation flow script"""
    print("\n💬 CONVERSATION FLOW:")
    print("="*25)
    
    print("\n👋 GREETING:")
    print("""• "Hello! Welcome to Goodness Glamour Salon. 
  How can I help you today?" """)
    
    print("\n🎯 SERVICE SELECTION:")
    print("""• "What service would you like to book today? 
  We offer women's haircuts, kids' haircuts, bridal styling, 
  hair treatments, and more." """)
    
    print("\n📅 DATE & TIME:")
    print("""• "What date and time would work best for you? 
  We're available Monday to Sunday, 9 AM to 8 PM." """)
    
    print("\n✅ CONFIRMATION:")
    print("""• "Just to confirm, you'd like to book [Service] 
  on [Date] at [Time]. Is that correct?" """)
    
    print("\n🎉 BOOKING FINALIZATION:")
    print("""• "Great! Your appointment for [Service] on [Date] 
  at [Time] has been confirmed. You'll receive a 
  confirmation message shortly." """)
    
    print("\n👋 CLOSING:")
    print("""• "Thank you for choosing Goodness Glamour Salon. 
  We look forward to seeing you!" """)

def show_technical_details():
    """Show technical configuration details"""
    print("\n⚙️ TECHNICAL CONFIGURATION:")
    print("="*30)
    
    print("\n🔗 INTEGRATION DETAILS:")
    print("• Website URL: Your salon website URL")
    print("• QR Code Action: Open Bot Libre chat")
    print("• SMS Integration: Optional (for confirmations)")
    print("• Email Integration: Optional (for confirmations)")
    
    print("\n📱 COMMUNICATION CHANNELS:")
    print("• Web Chat: Primary (embedded on website)")
    print("• Mobile: Responsive web chat")
    print("• QR Code: Direct link to chat")
    print("• Voice: Text-to-speech enabled")
    
    print("\n🔧 API CONFIGURATION:")
    print("• Bot Libre API Key: (provided after creation)")
    print("• Webhook URL: (for booking confirmations)")
    print("• Calendar Integration: (if using Google Calendar)")

def show_template_recommendation():
    """Show template recommendation"""
    print("\n📋 RECOMMENDED TEMPLATE:")
    print("="*30)
    
    print("\n🥇 BEST CHOICE: 'scheduler_template'")
    print("• Purpose: Schedule and book appointments")
    print("• Features: Google Calendar integration")
    print("• Perfect for: Salon booking system")
    
    print("\n🥈 ALTERNATIVE: 'basic_template'")
    print("• Purpose: Common greetings and responses")
    print("• Features: Names, dates, topical questions")
    print("• Good for: Simple booking flow")
    
    print("\n🥉 ADVANCED: 'virtual_assistant_template'")
    print("• Purpose: Virtual assistant with commands")
    print("• Features: Scheduling, email, apps")
    print("• Best for: Advanced integrations")

def show_setup_checklist():
    """Show setup checklist"""
    print("\n✅ SETUP CHECKLIST:")
    print("="*20)
    
    print("\n📝 STEP 1: BOT CREATION")
    print("□ Choose 'scheduler_template'")
    print("□ Enter bot name: 'Goodness Glamour Assistant'")
    print("□ Set language: English")
    print("□ Configure access settings")
    print("□ Click 'Create'")
    
    print("\n💬 STEP 2: CONVERSATION SETUP")
    print("□ Add greeting message")
    print("□ Configure service selection")
    print("□ Set up date/time booking")
    print("□ Add confirmation flow")
    print("□ Test conversation")
    
    print("\n🏢 STEP 3: SALON INFORMATION")
    print("□ Add salon details")
    print("□ Input services and prices")
    print("□ Set business hours")
    print("□ Add contact information")
    print("□ Configure key features")
    
    print("\n🔗 STEP 4: INTEGRATION")
    print("□ Get embed code for website")
    print("□ Test web chat")
    print("□ Configure QR code link")
    print("□ Set up confirmations")
    print("□ Deploy and test")

def main():
    """Main function"""
    print("📋 BOT LIBRE CONFIGURATION DETAILS")
    print("🎯 Complete setup guide for Goodness Glamour Assistant")
    print("="*60)
    
    show_basic_bot_details()
    show_salon_information()
    show_services_and_prices()
    show_conversation_flow()
    show_technical_details()
    show_template_recommendation()
    show_setup_checklist()
    
    print("\n🚀 QUICK START:")
    print("1. Choose 'scheduler_template'")
    print("2. Name: 'Goodness Glamour Assistant'")
    print("3. Copy the conversation flow above")
    print("4. Add salon information")
    print("5. Test and deploy!")

if __name__ == '__main__':
    main()
