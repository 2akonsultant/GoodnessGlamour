import axios from 'axios';

export interface SMSConfig {
  // Twilio Configuration
  twilioAccountSid?: string;
  twilioAuthToken?: string;
  twilioFromNumber?: string;
  
  // TextLocal Configuration (India-focused, cheaper alternative)
  textlocalApiKey?: string;
  textlocalSender?: string;
  
  // MSG91 Configuration (India-focused)
  msg91ApiKey?: string;
  msg91SenderId?: string;
  msg91TemplateId?: string; // For Flow API
  
  // Generic SMS Gateway Configuration
  smsGatewayUrl?: string;
  smsGatewayApiKey?: string;
  smsGatewaySender?: string;
}

export interface SMSMessage {
  to: string;
  message: string;
  bookingId?: string;
  customerName?: string;
}

export interface SMSResult {
  success: boolean;
  messageId?: string;
  error?: string;
  provider?: string;
}

class SMSService {
  private config: SMSConfig;

  constructor(config: SMSConfig) {
    this.config = config;
  }

  /**
   * Send SMS using multiple providers with fallback
   */
  async sendSMS(smsMessage: SMSMessage): Promise<SMSResult> {
    console.log(`📱 Attempting to send SMS to: ${smsMessage.to}`);
    
    // Try providers in order of preference (free/cheapest first)
    const providers = [
      { name: 'TextLocal', method: this.sendViaTextLocal.bind(this) },
      { name: 'MSG91', method: this.sendViaMSG91.bind(this) },
      { name: 'Twilio', method: this.sendViaTwilio.bind(this) },
      { name: 'Generic Gateway', method: this.sendViaGenericGateway.bind(this) }
    ];

    for (const provider of providers) {
      try {
        console.log(`📱 Trying ${provider.name}...`);
        const result = await provider.method(smsMessage);
        if (result.success) {
          console.log(`✅ SMS sent successfully via ${provider.name}`);
          return { ...result, provider: provider.name };
        }
      } catch (error) {
        console.log(`❌ ${provider.name} failed:`, error);
        continue;
      }
    }

    console.log('❌ All SMS providers failed');
    return {
      success: false,
      error: 'All SMS providers failed',
      provider: 'None'
    };
  }

  /**
   * Send SMS via TextLocal (India-focused, very cheap)
   */
  private async sendViaTextLocal(smsMessage: SMSMessage): Promise<SMSResult> {
    if (!this.config.textlocalApiKey) {
      throw new Error('TextLocal API key not configured');
    }

    const response = await axios.post('https://api.textlocal.in/send/', {
      apikey: this.config.textlocalApiKey,
      numbers: smsMessage.to.replace(/^\+91/, ''), // Remove +91 prefix for TextLocal
      message: smsMessage.message,
      sender: this.config.textlocalSender || 'GLAMOR'
    });

    if (response.data.status === 'success') {
      return {
        success: true,
        messageId: response.data.batch_id?.toString()
      };
    } else {
      throw new Error(response.data.errors?.[0]?.message || 'TextLocal API error');
    }
  }

  /**
   * Send SMS via MSG91 (India-focused) - Supports both Flow API and Basic API
   */
  private async sendViaMSG91(smsMessage: SMSMessage): Promise<SMSResult> {
    if (!this.config.msg91ApiKey) {
      throw new Error('MSG91 API key not configured');
    }

    // Try Flow API first if template ID is configured
    if (this.config.msg91TemplateId && smsMessage.bookingId && smsMessage.customerName) {
      try {
        return await this.sendViaMSG91FlowAPI(smsMessage);
      } catch (error) {
        console.log('📱 MSG91 Flow API failed, falling back to basic API:', error);
        // Fall back to basic API
      }
    }

    // Use basic MSG91 API
    const response = await axios.post(`https://api.msg91.com/api/sendhttp.php`, null, {
      params: {
        authkey: this.config.msg91ApiKey,
        mobiles: smsMessage.to.replace(/^\+91/, ''), // Remove +91 prefix
        message: smsMessage.message,
        sender: this.config.msg91SenderId || 'GLAMOR',
        route: 4 // Transactional route
      }
    });

    if (response.data && !response.data.includes('ERROR')) {
      return {
        success: true,
        messageId: response.data
      };
    } else {
      throw new Error(response.data || 'MSG91 API error');
    }
  }

  /**
   * Send SMS via MSG91 Flow API (Template-based)
   */
  private async sendViaMSG91FlowAPI(smsMessage: SMSMessage): Promise<SMSResult> {
    if (!this.config.msg91TemplateId) {
      throw new Error('MSG91 template ID not configured for Flow API');
    }

    // Parse booking details from message for template variables
    const bookingDetails = this.parseBookingDetailsFromMessage(smsMessage.message);

    const response = await axios.post('https://control.msg91.com/api/v5/flow', {
      template_id: this.config.msg91TemplateId,
      short_url: "1",
      realTimeResponse: "1",
      recipients: [
        {
          mobiles: smsMessage.to.replace(/^\+91/, ''), // Remove +91 prefix
          VAR1: bookingDetails.customerName || smsMessage.customerName || 'Customer',
          VAR2: bookingDetails.date || 'Date',
          VAR3: bookingDetails.time || 'Time',
          VAR4: bookingDetails.services || 'Services',
          VAR5: bookingDetails.amount || 'Amount',
          VAR6: bookingDetails.address || 'Address',
          VAR7: bookingDetails.bookingId || smsMessage.bookingId || 'ID'
        }
      ]
    }, {
      headers: {
        'accept': 'application/json',
        'authkey': this.config.msg91ApiKey,
        'content-type': 'application/json'
      }
    });

    if (response.data && response.data.success !== false) {
      return {
        success: true,
        messageId: response.data.request_id || response.data.id
      };
    } else {
      throw new Error(response.data?.message || 'MSG91 Flow API error');
    }
  }

  /**
   * Parse booking details from SMS message for template variables
   */
  private parseBookingDetailsFromMessage(message: string): {
    customerName?: string;
    date?: string;
    time?: string;
    services?: string;
    amount?: string;
    address?: string;
    bookingId?: string;
  } {
    // Simple parsing logic - can be enhanced based on your message format
    const lines = message.split('\n');
    const details: any = {};

    lines.forEach(line => {
      if (line.includes('Hi ')) {
        details.customerName = line.replace('Hi ', '').replace('!', '');
      }
      if (line.includes('📅')) {
        const dateTimeMatch = line.match(/📅\s*(.+)/);
        if (dateTimeMatch) details.date = dateTimeMatch[1];
      }
      if (line.includes('💇‍♀️')) {
        const servicesMatch = line.match(/💇‍♀️\s*(.+)/);
        if (servicesMatch) details.services = servicesMatch[1];
      }
      if (line.includes('💰')) {
        const amountMatch = line.match(/💰\s*₹(.+)/);
        if (amountMatch) details.amount = amountMatch[1];
      }
      if (line.includes('📍')) {
        const addressMatch = line.match(/📍\s*(.+)/);
        if (addressMatch) details.address = addressMatch[1];
      }
      if (line.includes('🆔')) {
        const idMatch = line.match(/🆔\s*Booking ID:\s*(.+)/);
        if (idMatch) details.bookingId = idMatch[1];
      }
    });

    return details;
  }

  /**
   * Send SMS via Twilio (Global, more expensive but reliable)
   */
  private async sendViaTwilio(smsMessage: SMSMessage): Promise<SMSResult> {
    if (!this.config.twilioAccountSid || !this.config.twilioAuthToken) {
      throw new Error('Twilio credentials not configured');
    }

    const response = await axios.post(
      `https://api.twilio.com/2010-04-01/Accounts/${this.config.twilioAccountSid}/Messages.json`,
      new URLSearchParams({
        To: smsMessage.to,
        From: this.config.twilioFromNumber || '+1234567890',
        Body: smsMessage.message
      }),
      {
        auth: {
          username: this.config.twilioAccountSid,
          password: this.config.twilioAuthToken
        }
      }
    );

    return {
      success: true,
      messageId: response.data.sid
    };
  }

  /**
   * Send SMS via Generic SMS Gateway
   */
  private async sendViaGenericGateway(smsMessage: SMSMessage): Promise<SMSResult> {
    if (!this.config.smsGatewayUrl || !this.config.smsGatewayApiKey) {
      throw new Error('Generic SMS gateway not configured');
    }

    const response = await axios.post(this.config.smsGatewayUrl, {
      api_key: this.config.smsGatewayApiKey,
      to: smsMessage.to,
      message: smsMessage.message,
      sender: this.config.smsGatewaySender || 'GLAMOR'
    });

    if (response.data.success) {
      return {
        success: true,
        messageId: response.data.message_id
      };
    } else {
      throw new Error(response.data.error || 'Generic gateway error');
    }
  }

  /**
   * Send booking confirmation SMS to customer
   */
  async sendBookingConfirmationSMS(booking: {
    id: string;
    customerName: string;
    customerPhone: string;
    appointmentDate: string;
    appointmentTime: string;
    services: string[];
    totalAmount: number;
    customerAddress: string;
  }): Promise<SMSResult> {
    const message = this.formatBookingConfirmationMessage(booking);
    
    return this.sendSMS({
      to: booking.customerPhone,
      message: message,
      bookingId: booking.id,
      customerName: booking.customerName
    });
  }

  /**
   * Format booking confirmation message
   */
  private formatBookingConfirmationMessage(booking: {
    customerName: string;
    appointmentDate: string;
    appointmentTime: string;
    services: string[];
    totalAmount: number;
    customerAddress: string;
    id: string;
  }): string {
    const date = new Date(booking.appointmentDate).toLocaleDateString('en-IN', {
      weekday: 'short',
      day: 'numeric',
      month: 'short'
    });
    
    const serviceList = booking.services.length > 2 
      ? `${booking.services.slice(0, 2).join(', ')} & ${booking.services.length - 2} more`
      : booking.services.join(', ');

    return `💐 Goodness Glamour Salon\n\nHi ${booking.customerName}!\n\n✅ Your booking is confirmed!\n📅 ${date} at ${booking.appointmentTime}\n💇‍♀️ ${serviceList}\n💰 ₹${booking.totalAmount}\n📍 ${booking.customerAddress}\n\n🆔 Booking ID: ${booking.id}\n\n📞 Need help? Call: 9036626642\n\nThank you for choosing us! 🌸`;
  }

  /**
   * Send appointment reminder SMS
   */
  async sendAppointmentReminderSMS(booking: {
    customerName: string;
    customerPhone: string;
    appointmentDate: string;
    appointmentTime: string;
    services: string[];
  }): Promise<SMSResult> {
    const message = `💐 Goodness Glamour Salon\n\nHi ${booking.customerName}!\n\n⏰ Reminder: Your appointment is tomorrow at ${booking.appointmentTime}\n💇‍♀️ Services: ${booking.services.join(', ')}\n\n📍 Please be ready at your specified address.\n\n📞 Any changes? Call: 9036626642\n\nSee you soon! 🌸`;

    return this.sendSMS({
      to: booking.customerPhone,
      message: message,
      customerName: booking.customerName
    });
  }

  /**
   * Test SMS configuration
   */
  async testSMSConfig(testPhoneNumber: string): Promise<SMSResult> {
    const testMessage = `💐 Goodness Glamour Salon\n\n🧪 Test SMS - Configuration working!\n\nIf you received this, SMS notifications are properly set up.\n\n📞 Contact: 9036626642`;

    return this.sendSMS({
      to: testPhoneNumber,
      message: testMessage
    });
  }
}

// Create and export SMS service instance
const createSMSService = (): SMSService => {
  const config: SMSConfig = {
    // TextLocal Configuration (Recommended for India - very cheap)
    textlocalApiKey: process.env.TEXTLOCAL_API_KEY,
    textlocalSender: process.env.TEXTLOCAL_SENDER || 'GLAMOR',
    
    // MSG91 Configuration (Alternative for India)
    msg91ApiKey: process.env.MSG91_API_KEY,
    msg91SenderId: process.env.MSG91_SENDER_ID || 'GLAMOR',
    msg91TemplateId: process.env.MSG91_TEMPLATE_ID,
    
    // Twilio Configuration (Global but more expensive)
    twilioAccountSid: process.env.TWILIO_ACCOUNT_SID,
    twilioAuthToken: process.env.TWILIO_AUTH_TOKEN,
    twilioFromNumber: process.env.TWILIO_FROM_NUMBER,
    
    // Generic SMS Gateway Configuration
    smsGatewayUrl: process.env.SMS_GATEWAY_URL,
    smsGatewayApiKey: process.env.SMS_GATEWAY_API_KEY,
    smsGatewaySender: process.env.SMS_GATEWAY_SENDER || 'GLAMOR'
  };

  return new SMSService(config);
};

export const smsService = createSMSService();

// Export individual functions for easy use
export const sendBookingConfirmationSMS = (booking: any) => smsService.sendBookingConfirmationSMS(booking);
export const sendAppointmentReminderSMS = (booking: any) => smsService.sendAppointmentReminderSMS(booking);
export const testSMSConfiguration = (phoneNumber: string) => smsService.testSMSConfig(phoneNumber);
export const sendCustomSMS = (to: string, message: string) => smsService.sendSMS({ to, message });
