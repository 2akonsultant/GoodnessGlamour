import nodemailer from 'nodemailer';
import axios from 'axios';
import XLSX from 'xlsx';
import * as fs from 'fs';
import * as path from 'path';
import { sendBookingConfirmationSMS } from './sms-service';

export interface ContactMessage {
  name: string;
  phone: string;
  serviceInterest: string;
  address: string;
  message: string;
  timestamp: string;
}

export interface BookingData {
  id: string;
  customerName: string;
  customerEmail: string;
  customerPhone: string;
  customerAddress: string;
  appointmentDate: string;
  appointmentTime: string;
  services: string[];
  totalAmount: number;
  notes: string;
  timestamp: string;
}

// Email configuration - supports both EMAIL_PASSWORD and EMAIL_PASS
const getEmailPassword = () => process.env.EMAIL_PASSWORD || process.env.EMAIL_PASS || '';

// EmailJS configuration for customer confirmation emails
const EMAILJS_API_URL =
  process.env.EMAILJS_API_URL || 'https://api.emailjs.com/api/v1.0/email/send';

const EMAILJS_SERVICE_ID_CUSTOMER =
  process.env.EMAILJS_SERVICE_ID_CUSTOMER ||
  process.env.EMAILJS_SERVICE_ID ||
  'service_ud02gf4';

const EMAILJS_TEMPLATE_ID_BOOKING =
  process.env.EMAILJS_TEMPLATE_ID_BOOKING ||
  process.env.EMAILJS_TEMPLATE_ID ||
  'template_teud7z7';

const EMAILJS_PUBLIC_KEY =
  process.env.EMAILJS_PUBLIC_KEY ||
  process.env.EMAILJS_USER_ID ||
  'x8poTA6boU0QKFefd';

const isEmailJSConfigured = () =>
  Boolean(EMAILJS_SERVICE_ID_CUSTOMER && EMAILJS_TEMPLATE_ID_BOOKING && EMAILJS_PUBLIC_KEY);

// Create transporter with fallback configurations
const createTransporter = () => {
  const user = process.env.EMAIL_USER || '2akonsultant@gmail.com';
  const pass = getEmailPassword();

  if (!pass || pass.trim() === '') {
    console.error('❌ EMAIL_PASSWORD (or EMAIL_PASS) is not set in .env. Booking emails will not be sent.');
    console.error('   Add to .env: EMAIL_PASSWORD=your-gmail-app-password');
    console.error('   Gmail requires App Password (not regular password). Generate at: https://myaccount.google.com/apppasswords');
  }

  // Try port 465 first (SSL) - more reliable on some networks
  // If that fails, fallback to port 587 (STARTTLS)
  const usePort465 = process.env.SMTP_PORT === '465' || process.env.EMAIL_USE_PORT_465 === 'true';
  
  if (usePort465) {
    console.log('📧 Using SMTP port 465 (SSL)');
    return nodemailer.createTransport({
      host: 'smtp.gmail.com',
      port: 465,
      secure: true, // SSL
      auth: {
        user,
        pass,
      },
      connectionTimeout: 30000,
      greetingTimeout: 30000,
      socketTimeout: 30000,
      tls: {
        rejectUnauthorized: true,
      },
      // Disable pooling for better reliability with timeouts
      pool: false,
    } as nodemailer.TransportOptions);
  }

  // Default: port 587 with STARTTLS
  console.log('📧 Using SMTP port 587 (STARTTLS)');
  return nodemailer.createTransport({
    host: 'smtp.gmail.com',
    port: 587,
    secure: false, // STARTTLS
    auth: {
      user,
      pass,
    },
    requireTLS: true,
    connectionTimeout: 30000,
    greetingTimeout: 30000,
    socketTimeout: 30000,
    tls: {
      rejectUnauthorized: true,
    },
    // Disable pooling for better reliability with timeouts
    pool: false,
  } as nodemailer.TransportOptions);
};

// Create transporter for specific port
const createTransporterForPort = (port: 465 | 587): nodemailer.Transporter => {
  const user = process.env.EMAIL_USER || '2akonsultant@gmail.com';
  const pass = getEmailPassword();

  if (port === 465) {
    return nodemailer.createTransport({
      host: 'smtp.gmail.com',
      port: 465,
      secure: true, // SSL
      auth: { user, pass },
      connectionTimeout: 30000,
      greetingTimeout: 30000,
      socketTimeout: 30000,
      tls: { rejectUnauthorized: true },
      pool: false,
    } as nodemailer.TransportOptions);
  } else {
    return nodemailer.createTransport({
      host: 'smtp.gmail.com',
      port: 587,
      secure: false, // STARTTLS
      auth: { user, pass },
      requireTLS: true,
      connectionTimeout: 30000,
      greetingTimeout: 30000,
      socketTimeout: 30000,
      tls: { rejectUnauthorized: true },
      pool: false,
    } as nodemailer.TransportOptions);
  }
};

// Send email notification
export async function sendContactEmail(contact: ContactMessage): Promise<boolean> {
  try {
    const mailOptions = {
      from: process.env.EMAIL_USER || '2akonsultant@gmail.com',
      to: '2akonsultant@gmail.com',
      subject: `💐 New Inquiry from ${contact.name} | Goodness Glamour Salon`,
      html: `
        <!DOCTYPE html>
        <html>
        <head>
          <meta charset="UTF-8">
          <meta name="viewport" content="width=device-width, initial-scale=1.0">
        </head>
        <body style="margin: 0; padding: 0; background: linear-gradient(135deg, #fef5f1 0%, #fef9f5 50%, #f5f3f9 100%); font-family: 'Georgia', 'Times New Roman', serif;">
          
          <!-- Main Container -->
          <table width="100%" cellpadding="0" cellspacing="0" style="background: linear-gradient(135deg, #fef5f1 0%, #fef9f5 50%, #f5f3f9 100%); padding: 40px 20px;">
            <tr>
              <td align="center">
                
                <!-- Email Content -->
                <table width="620" cellpadding="0" cellspacing="0" style="background-color: #ffffff; border-radius: 24px; overflow: hidden; box-shadow: 0 8px 32px rgba(0,0,0,0.08);">
                  
                  <!-- Elegant Header -->
                  <tr>
                    <td style="background: linear-gradient(135deg, #ffeef5 0%, #fff0f3 50%, #f9f0ff 100%); padding: 50px 40px 40px 40px; text-align: center; position: relative;">
                      <!-- Subtle floral corner accent -->
                      <div style="position: absolute; top: 15px; right: 15px; opacity: 0.15; font-size: 40px;">🌸</div>
                      <div style="position: absolute; bottom: 15px; left: 15px; opacity: 0.15; font-size: 40px;">🌿</div>
                      
                      <h1 style="margin: 0; color: #d4a5a5; font-size: 36px; font-weight: 300; letter-spacing: 3px; font-family: 'Georgia', serif;">
                        Goodness Glamour
                      </h1>
                      <p style="margin: 8px 0 0 0; color: #b8a0a0; font-size: 15px; font-weight: 400; letter-spacing: 2px; font-family: 'Georgia', serif;">
                        Ladies & Kids Salon
                      </p>
                      <div style="margin-top: 25px; padding: 10px 30px; background-color: rgba(255,255,255,0.7); border-radius: 20px; display: inline-block; border: 1px solid rgba(212,165,165,0.2);">
                        <p style="margin: 0; color: #c9a0a0; font-size: 13px; font-weight: 500; letter-spacing: 1px;">
                          💐 New Customer Inquiry
                        </p>
                      </div>
                    </td>
                  </tr>
                  
                  <!-- Content Section -->
                  <tr>
                    <td style="padding: 40px;">
                      
                      <!-- Customer Name Card -->
                      <div style="background: linear-gradient(135deg, #fff5f0 0%, #fff8f5 100%); padding: 25px 30px; border-radius: 18px; margin-bottom: 30px; border: 1px solid #ffe8e0; box-shadow: 0 4px 16px rgba(255,200,180,0.1);">
                        <table width="100%" cellpadding="0" cellspacing="0">
                          <tr>
                            <td width="60" valign="middle">
                              <div style="width: 55px; height: 55px; background: linear-gradient(135deg, #ffd4c8 0%, #ffc4b8 100%); border-radius: 50%; display: flex; align-items: center; justify-content: center; box-shadow: 0 4px 12px rgba(255,180,160,0.25);">
                                <span style="font-size: 26px;">✨</span>
                              </div>
                            </td>
                            <td style="padding-left: 20px;">
                              <h2 style="margin: 0; color: #c88080; font-size: 26px; font-weight: 400; font-family: 'Georgia', serif;">${contact.name}</h2>
                              <p style="margin: 5px 0 0 0; color: #d4a5a5; font-size: 14px; font-weight: 400; letter-spacing: 0.5px;">New Inquiry Received</p>
                            </td>
                          </tr>
                        </table>
                      </div>
                      
                      <!-- Contact Information -->
                      <div style="background: linear-gradient(135deg, #f8f5ff 0%, #faf7ff 100%); padding: 30px; border-radius: 18px; margin-bottom: 30px; border: 1px solid #f0e8ff; box-shadow: 0 4px 16px rgba(200,180,220,0.08);">
                        <h3 style="margin: 0 0 25px 0; color: #a88cb8; font-size: 16px; font-weight: 500; letter-spacing: 1px; font-family: 'Georgia', serif; border-bottom: 1px solid rgba(200,180,220,0.2); padding-bottom: 12px;">
                          Contact Details
                        </h3>
                        
                        <!-- Phone -->
                        <div style="background-color: #ffffff; padding: 18px 20px; border-radius: 14px; margin-bottom: 15px; border-left: 3px solid #d4b5d4; box-shadow: 0 2px 8px rgba(0,0,0,0.03);">
                          <table width="100%" cellpadding="0" cellspacing="0">
                            <tr>
                              <td width="35" valign="middle">
                                <span style="font-size: 20px; opacity: 0.7;">📱</span>
                              </td>
                              <td>
                                <p style="margin: 0 0 4px 0; color: #b8a0b8; font-size: 11px; font-weight: 500; text-transform: uppercase; letter-spacing: 1px;">Phone Number</p>
                                <a href="tel:${contact.phone}" style="margin: 0; color: #c88080; font-size: 19px; font-weight: 500; text-decoration: none; display: block; font-family: 'Georgia', serif;">${contact.phone}</a>
                              </td>
                            </tr>
                          </table>
                        </div>
                        
                        <!-- Service -->
                        <div style="background-color: #ffffff; padding: 18px 20px; border-radius: 14px; margin-bottom: 15px; border-left: 3px solid #d4b5d4; box-shadow: 0 2px 8px rgba(0,0,0,0.03);">
                          <table width="100%" cellpadding="0" cellspacing="0">
                            <tr>
                              <td width="35" valign="middle">
                                <span style="font-size: 20px; opacity: 0.7;">💇‍♀️</span>
                              </td>
                              <td>
                                <p style="margin: 0 0 4px 0; color: #b8a0b8; font-size: 11px; font-weight: 500; text-transform: uppercase; letter-spacing: 1px;">Service Interest</p>
                                <p style="margin: 0; color: #9880a8; font-size: 16px; font-weight: 500; font-family: 'Georgia', serif;">${contact.serviceInterest}</p>
                              </td>
                            </tr>
                          </table>
                        </div>
                        
                        <!-- Address -->
                        <div style="background-color: #ffffff; padding: 18px 20px; border-radius: 14px; border-left: 3px solid #d4b5d4; box-shadow: 0 2px 8px rgba(0,0,0,0.03);">
                          <table width="100%" cellpadding="0" cellspacing="0">
                            <tr>
                              <td width="35" valign="top">
                                <span style="font-size: 20px; opacity: 0.7;">📍</span>
                              </td>
                              <td>
                                <p style="margin: 0 0 4px 0; color: #b8a0b8; font-size: 11px; font-weight: 500; text-transform: uppercase; letter-spacing: 1px;">Address</p>
                                <p style="margin: 0; color: #9880a8; font-size: 15px; font-weight: 400; line-height: 1.6; font-family: 'Georgia', serif;">${contact.address}</p>
                              </td>
                            </tr>
                          </table>
                        </div>
                      </div>
                      
                      <!-- Message Section -->
                      <div style="background: linear-gradient(135deg, #f0f9f8 0%, #f5faf9 100%); padding: 30px; border-radius: 18px; margin-bottom: 30px; border: 1px solid #e0f0ed; box-shadow: 0 4px 16px rgba(180,220,210,0.08);">
                        <h3 style="margin: 0 0 18px 0; color: #88b8a8; font-size: 16px; font-weight: 500; letter-spacing: 1px; font-family: 'Georgia', serif;">
                          Customer Message
                        </h3>
                        <div style="background-color: #ffffff; padding: 22px 25px; border-radius: 14px; border-left: 3px solid #a8d4c4; box-shadow: 0 2px 8px rgba(0,0,0,0.03);">
                          <p style="margin: 0; color: #687878; font-size: 15px; line-height: 1.8; white-space: pre-wrap; font-family: 'Georgia', serif;">${contact.message}</p>
                        </div>
                      </div>
                      
                      <!-- Action Button -->
                      <div style="background: linear-gradient(135deg, #f5fff8 0%, #f8fff9 100%); padding: 35px 30px; border-radius: 18px; text-align: center; border: 1px solid #e8f5ed; box-shadow: 0 4px 16px rgba(180,220,200,0.1);">
                        <p style="margin: 0 0 18px 0; color: #88b8a0; font-size: 14px; font-weight: 500; letter-spacing: 0.5px;">
                          Please Contact Customer
                        </p>
                        <a href="tel:${contact.phone}" style="display: inline-block; background: linear-gradient(135deg, #b8d4c8 0%, #a8c8b8 100%); color: #ffffff; padding: 16px 45px; border-radius: 25px; text-decoration: none; font-size: 17px; font-weight: 500; box-shadow: 0 6px 20px rgba(168,200,184,0.3); font-family: 'Georgia', serif; letter-spacing: 0.5px;">
                          📞 Call ${contact.name}
                        </a>
                        <p style="margin: 18px 0 0 0; color: #98b8a8; font-size: 13px; font-weight: 400;">
                          Service: <span style="color: #88a898; font-weight: 500;">${contact.serviceInterest}</span>
                        </p>
                      </div>
                      
                    </td>
                  </tr>
                  
                  <!-- Elegant Footer -->
                  <tr>
                    <td style="background: linear-gradient(135deg, #fafafa 0%, #f8f8f8 100%); padding: 30px 40px; text-align: center; border-top: 1px solid #f0f0f0;">
                      <p style="margin: 0 0 10px 0; color: #a8a8a8; font-size: 13px; line-height: 1.6; font-family: 'Georgia', serif;">
                        ⏰ ${new Date(contact.timestamp).toLocaleString('en-IN', { 
                          weekday: 'long', 
                          year: 'numeric', 
                          month: 'long', 
                          day: 'numeric',
                          hour: '2-digit',
                          minute: '2-digit',
                          hour12: true 
                        })}
                      </p>
                      <p style="margin: 0; color: #c0c0c0; font-size: 11px; letter-spacing: 0.5px;">
                        Automated notification • Goodness Glamour Salon<br>
                        All inquiries saved to Excel file
                      </p>
                      <!-- Subtle floral footer accent -->
                      <p style="margin: 15px 0 0 0; opacity: 0.2; font-size: 20px;">🌸 🌿 🌸</p>
                    </td>
                  </tr>
                  
                </table>
                
              </td>
            </tr>
          </table>
          
        </body>
        </html>
      `,
    };

    await retryEmailSend(
      async () => {
        return await sendEmailWithPortFallback(mailOptions, 'contact email');
      },
      'contact email',
      2
    );

    console.log('✅ Email sent successfully to 2akonsultant@gmail.com');
    return true;
  } catch (error) {
    console.error('❌ Error sending email:', error);
    logEmailError('Error sending contact email', error);
    return false;
  }
}

// Update Excel file with new contact message
export async function updateExcelFile(contact: ContactMessage): Promise<boolean> {
  try {
    const dataDir = path.join(process.cwd(), 'data');
    const excelPath = path.join(dataDir, 'contact-messages.xlsx');

    // Ensure data directory exists
    if (!fs.existsSync(dataDir)) {
      fs.mkdirSync(dataDir, { recursive: true });
    }

    let workbook: XLSX.WorkBook;
    let worksheet: XLSX.WorkSheet;
    let existingData: any[] = [];

    // Check if file exists and read existing data
    if (fs.existsSync(excelPath)) {
      workbook = XLSX.readFile(excelPath);
      worksheet = workbook.Sheets['Contact Messages'];
      if (worksheet) {
        existingData = XLSX.utils.sheet_to_json(worksheet);
      }
    } else {
      workbook = XLSX.utils.book_new();
    }

    // Add new contact to data
    const newRow = {
      'Submission Date': new Date(contact.timestamp).toLocaleString('en-IN', {
        day: '2-digit',
        month: '2-digit',
        year: 'numeric',
        hour: '2-digit',
        minute: '2-digit',
        hour12: true
      }),
      'Name': contact.name,
      'Phone Number': contact.phone,
      'Service Interest': contact.serviceInterest,
      'Address': contact.address,
      'Message': contact.message,
    };

    existingData.push(newRow);

    // Create new worksheet with all data
    const newWorksheet = XLSX.utils.json_to_sheet(existingData);

    // Set column widths for better readability
    newWorksheet['!cols'] = [
      { wch: 20 }, // Submission Date
      { wch: 25 }, // Name
      { wch: 15 }, // Phone
      { wch: 25 }, // Service Interest
      { wch: 35 }, // Address
      { wch: 50 }, // Message
    ];

    // Add or update the worksheet
    if (workbook.Sheets['Contact Messages']) {
      workbook.Sheets['Contact Messages'] = newWorksheet;
    } else {
      XLSX.utils.book_append_sheet(workbook, newWorksheet, 'Contact Messages');
    }

    // Write to file
    XLSX.writeFile(workbook, excelPath);
    
    console.log(`✅ Excel file updated: ${excelPath}`);
    console.log(`📊 Total contact messages: ${existingData.length}`);
    
    return true;
  } catch (error) {
    console.error('❌ Error updating Excel file:', error);
    return false;
  }
}

// Process contact form submission
export async function processContactMessage(contact: ContactMessage): Promise<{ 
  success: boolean; 
  emailSent: boolean; 
  excelUpdated: boolean; 
}> {
  console.log('📧 Processing contact message from:', contact.name);
  
  const emailSent = await sendContactEmail(contact);
  const excelUpdated = await updateExcelFile(contact);
  
  return {
    success: emailSent || excelUpdated, // Success if at least one succeeds
    emailSent,
    excelUpdated,
  };
}

// Helper to log email errors with actionable hints
const logEmailError = (context: string, error: unknown) => {
  const err = error instanceof Error ? error : new Error(String(error));
  const msg = err.message || '';
  const errCode = (err as any).code || '';
  
  console.error(`❌ ${context}:`, msg);
  
  // Check for timeout errors
  if (msg.includes('timeout') || msg.includes('Timeout') || msg.includes('ETIMEDOUT') || errCode === 'ETIMEDOUT') {
    console.error('   → Connection timeout detected. Possible causes:');
    console.error('      • Network connectivity issues');
    console.error('      • Firewall blocking SMTP port 587');
    console.error('      • Gmail SMTP server temporarily unavailable');
    console.error('      • VPN or proxy interfering with connection');
    console.error('   → Try: Check internet connection, firewall settings, or retry later');
  }
  
  // Check for connection errors
  if (msg.includes('ECONNREFUSED') || msg.includes('ENOTFOUND') || errCode === 'ECONNREFUSED' || errCode === 'ENOTFOUND') {
    console.error('   → Connection refused. Check:');
    console.error('      • Internet connectivity');
    console.error('      • Firewall allows outbound connections on port 587');
    console.error('      • DNS resolution for smtp.gmail.com');
  }
  
  // Check for authentication errors
  if (msg.includes('Invalid login') || msg.includes('EAUTH') || msg.includes('authentication') || errCode === 'EAUTH') {
    console.error('   → Gmail auth failed. Use App Password (not regular password): https://myaccount.google.com/apppasswords');
    console.error('   → Set EMAIL_PASSWORD=your-app-password in .env');
  }
};

// Helper function to send email with port fallback
const sendEmailWithPortFallback = async (
  mailOptions: nodemailer.SendMailOptions,
  context: string
): Promise<nodemailer.SentMessageInfo> => {
  const ports: Array<{ port: 465 | 587; name: string }> = [
    { port: 587, name: '587 (STARTTLS)' },
    { port: 465, name: '465 (SSL)' }
  ];

  let lastError: any;

  for (const { port, name } of ports) {
    try {
      console.log(`📧 Attempting to send ${context} via port ${name}...`);
      const transporter = createTransporterForPort(port);
      const result = await transporter.sendMail(mailOptions);
      console.log(`✅ Email sent successfully via port ${name}`);
      return result;
    } catch (error: any) {
      lastError = error;
      const err = error instanceof Error ? error : new Error(String(error));
      const msg = err.message || '';
      const errCode = error?.code || '';
      
      const isTimeout = 
        msg.includes('timeout') || 
        msg.includes('Timeout') || 
        msg.includes('ETIMEDOUT') || 
        errCode === 'ETIMEDOUT';
      
      if (isTimeout && port === 587) {
        // Port 587 timed out, try port 465
        console.log(`⚠️ Port ${name} timed out, trying alternative port...`);
        continue;
      }
      
      // If it's the last port or not a timeout, throw
      if (port === 465) {
        throw error;
      }
    }
  }

  throw lastError || new Error(`Failed to send ${context} on all ports`);
};

// Helper function to retry email sending with exponential backoff
const retryEmailSend = async <T>(
  emailFunction: () => Promise<T>,
  context: string,
  maxRetries: number = 2
): Promise<T> => {
  let lastError: any;
  
  for (let attempt = 1; attempt <= maxRetries; attempt++) {
    try {
      return await emailFunction();
    } catch (error: any) {
      lastError = error;
      const err = error instanceof Error ? error : new Error(String(error));
      const msg = err.message || '';
      const errCode = error?.code || '';
      
      // Check if error is retryable (timeout, connection errors)
      const isRetryable = 
        msg.includes('timeout') || 
        msg.includes('Timeout') || 
        msg.includes('ETIMEDOUT') || 
        errCode === 'ETIMEDOUT' ||
        msg.includes('ECONNREFUSED') ||
        errCode === 'ECONNREFUSED' ||
        msg.includes('ENOTFOUND') ||
        errCode === 'ENOTFOUND';
      
      if (isRetryable && attempt < maxRetries) {
        const delay = Math.min(1000 * Math.pow(2, attempt - 1), 5000); // Exponential backoff, max 5s
        console.log(`   ⏳ Retrying ${context} (attempt ${attempt + 1}/${maxRetries}) after ${delay}ms...`);
        await new Promise(resolve => setTimeout(resolve, delay));
        continue;
      }
      
      // If not retryable or max retries reached, throw the error
      throw error;
    }
  }
  
  // This should never be reached, but TypeScript needs it
  throw lastError || new Error(`Failed to send ${context} after ${maxRetries} attempts`);
};

// Send customer booking confirmation via EmailJS (for customers only)
const sendCustomerEmailViaEmailJS = async (booking: BookingData): Promise<boolean> => {
  if (!isEmailJSConfigured()) {
    console.error(
      '❌ EmailJS is not configured. Missing EMAILJS_SERVICE_ID_CUSTOMER / EMAILJS_TEMPLATE_ID_BOOKING / EMAILJS_PUBLIC_KEY in environment.'
    );
    return false;
  }

  try {
    // Format appointment date for better readability
    const formattedDate = new Date(booking.appointmentDate).toLocaleDateString('en-IN', {
      weekday: 'long',
      year: 'numeric',
      month: 'long',
      day: 'numeric',
    });

    const templateParams = {
      customer_name: booking.customerName,
      customer_email: booking.customerEmail,
      customer_phone: booking.customerPhone,
      appointment_date: formattedDate,
      appointment_time: booking.appointmentTime,
      services: booking.services.join(', '),
      total_amount: `₹${booking.totalAmount}`,
      customer_address: booking.customerAddress,
      booking_id: booking.id,
      notes: booking.notes || '',
    };

    const payload = {
      service_id: EMAILJS_SERVICE_ID_CUSTOMER,
      template_id: EMAILJS_TEMPLATE_ID_BOOKING,
      user_id: EMAILJS_PUBLIC_KEY,
      template_params: templateParams,
    };

    console.log('📧 Sending customer confirmation via EmailJS with payload:', {
      service_id: payload.service_id,
      template_id: payload.template_id,
      has_template_params: Boolean(payload.template_params),
    });

    const response = await axios.post(EMAILJS_API_URL, payload, {
      timeout: 30000,
      headers: {
        'Content-Type': 'application/json',
      },
    });

    console.log('✅ EmailJS customer confirmation response:', response.data);
    return true;
  } catch (error) {
    logEmailError('Error sending customer booking confirmation via EmailJS', error);
    return false;
  }
};

// Send booking confirmation email
export async function sendBookingEmail(booking: BookingData): Promise<boolean> {
  try {
    if (!getEmailPassword()?.trim()) {
      console.error('❌ Skipping admin booking email: EMAIL_PASSWORD not configured');
      return false;
    }

    const mailOptions = {
      from: process.env.EMAIL_USER || '2akonsultant@gmail.com',
      to: '2akonsultant@gmail.com',
      subject: `💐 New Booking Confirmation | ${booking.customerName} | Goodness Glamour Salon`,
      html: `
        <!DOCTYPE html>
        <html>
        <head>
          <meta charset="UTF-8">
          <meta name="viewport" content="width=device-width, initial-scale=1.0">
        </head>
        <body style="margin: 0; padding: 0; background: linear-gradient(135deg, #fef5f1 0%, #fef9f5 50%, #f5f3f9 100%); font-family: 'Georgia', 'Times New Roman', serif;">
          
          <!-- Main Container -->
          <table width="100%" cellpadding="0" cellspacing="0" style="background: linear-gradient(135deg, #fef5f1 0%, #fef9f5 50%, #f5f3f9 100%); padding: 40px 20px;">
            <tr>
              <td align="center">
                
                <!-- Email Content -->
                <table width="620" cellpadding="0" cellspacing="0" style="background-color: #ffffff; border-radius: 24px; overflow: hidden; box-shadow: 0 8px 32px rgba(0,0,0,0.08);">
                  
                  <!-- Elegant Header -->
                  <tr>
                    <td style="background: linear-gradient(135deg, #ffeef5 0%, #fff0f3 50%, #f9f0ff 100%); padding: 50px 40px 40px 40px; text-align: center; position: relative;">
                      <!-- Subtle floral corner accent -->
                      <div style="position: absolute; top: 15px; right: 15px; opacity: 0.15; font-size: 40px;">🌸</div>
                      <div style="position: absolute; bottom: 15px; left: 15px; opacity: 0.15; font-size: 40px;">🌿</div>
                      
                      <h1 style="margin: 0; color: #d4a5a5; font-size: 36px; font-weight: 300; letter-spacing: 3px; font-family: 'Georgia', serif;">
                        Goodness Glamour
                      </h1>
                      <p style="margin: 8px 0 0 0; color: #b8a0a0; font-size: 15px; font-weight: 400; letter-spacing: 2px; font-family: 'Georgia', serif;">
                        Ladies & Kids Salon
                      </p>
                      <div style="margin-top: 25px; padding: 10px 30px; background-color: rgba(255,255,255,0.7); border-radius: 20px; display: inline-block; border: 1px solid rgba(212,165,165,0.2);">
                        <p style="margin: 0; color: #c9a0a0; font-size: 13px; font-weight: 500; letter-spacing: 1px;">
                          💐 New Booking Confirmation
                        </p>
                      </div>
                    </td>
                  </tr>
                  
                  <!-- Content Section -->
                  <tr>
                    <td style="padding: 40px;">
                      
                      <!-- Customer Name Card -->
                      <div style="background: linear-gradient(135deg, #fff5f0 0%, #fff8f5 100%); padding: 25px 30px; border-radius: 18px; margin-bottom: 30px; border: 1px solid #ffe8e0; box-shadow: 0 4px 16px rgba(255,200,180,0.1);">
                        <table width="100%" cellpadding="0" cellspacing="0">
                          <tr>
                            <td width="60" valign="middle">
                              <div style="width: 55px; height: 55px; background: linear-gradient(135deg, #ffd4c8 0%, #ffc4b8 100%); border-radius: 50%; display: flex; align-items: center; justify-content: center; box-shadow: 0 4px 12px rgba(255,180,160,0.25);">
                                <span style="font-size: 26px;">✨</span>
                              </div>
                            </td>
                            <td style="padding-left: 20px;">
                              <h2 style="margin: 0; color: #c88080; font-size: 26px; font-weight: 400; font-family: 'Georgia', serif;">${booking.customerName}</h2>
                              <p style="margin: 5px 0 0 0; color: #d4a5a5; font-size: 14px; font-weight: 400; letter-spacing: 0.5px;">New Booking Confirmed</p>
                            </td>
                          </tr>
                        </table>
                      </div>
                      
                      <!-- Booking Details -->
                      <div style="background: linear-gradient(135deg, #f8f5ff 0%, #faf7ff 100%); padding: 30px; border-radius: 18px; margin-bottom: 30px; border: 1px solid #f0e8ff; box-shadow: 0 4px 16px rgba(200,180,220,0.08);">
                        <h3 style="margin: 0 0 25px 0; color: #a88cb8; font-size: 16px; font-weight: 500; letter-spacing: 1px; font-family: 'Georgia', serif; border-bottom: 1px solid rgba(200,180,220,0.2); padding-bottom: 12px;">
                          Booking Details
                        </h3>
                        
                        <!-- Booking ID -->
                        <div style="background-color: #ffffff; padding: 18px 20px; border-radius: 14px; margin-bottom: 15px; border-left: 3px solid #d4b5d4; box-shadow: 0 2px 8px rgba(0,0,0,0.03);">
                          <table width="100%" cellpadding="0" cellspacing="0">
                            <tr>
                              <td width="35" valign="middle">
                                <span style="font-size: 20px; opacity: 0.7;">🆔</span>
                              </td>
                              <td>
                                <p style="margin: 0 0 4px 0; color: #b8a0b8; font-size: 11px; font-weight: 500; text-transform: uppercase; letter-spacing: 1px;">Booking ID</p>
                                <p style="margin: 0; color: #9880a8; font-size: 16px; font-weight: 500; font-family: 'Georgia', serif;">${booking.id}</p>
                              </td>
                            </tr>
                          </table>
                        </div>
                        
                        <!-- Date & Time -->
                        <div style="background-color: #ffffff; padding: 18px 20px; border-radius: 14px; margin-bottom: 15px; border-left: 3px solid #d4b5d4; box-shadow: 0 2px 8px rgba(0,0,0,0.03);">
                          <table width="100%" cellpadding="0" cellspacing="0">
                            <tr>
                              <td width="35" valign="middle">
                                <span style="font-size: 20px; opacity: 0.7;">📅</span>
                              </td>
                              <td>
                                <p style="margin: 0 0 4px 0; color: #b8a0b8; font-size: 11px; font-weight: 500; text-transform: uppercase; letter-spacing: 1px;">Appointment Date & Time</p>
                                <p style="margin: 0; color: #9880a8; font-size: 16px; font-weight: 500; font-family: 'Georgia', serif;">${new Date(booking.appointmentDate).toLocaleDateString('en-IN', { weekday: 'long', year: 'numeric', month: 'long', day: 'numeric' })} at ${booking.appointmentTime}</p>
                              </td>
                            </tr>
                          </table>
                        </div>
                        
                        <!-- Services -->
                        <div style="background-color: #ffffff; padding: 18px 20px; border-radius: 14px; margin-bottom: 15px; border-left: 3px solid #d4b5d4; box-shadow: 0 2px 8px rgba(0,0,0,0.03);">
                          <table width="100%" cellpadding="0" cellspacing="0">
                            <tr>
                              <td width="35" valign="top">
                                <span style="font-size: 20px; opacity: 0.7;">💇‍♀️</span>
                              </td>
                              <td>
                                <p style="margin: 0 0 4px 0; color: #b8a0b8; font-size: 11px; font-weight: 500; text-transform: uppercase; letter-spacing: 1px;">Services Booked</p>
                                <div style="margin: 0;">
                                  ${booking.services.map(service => `<div style="margin: 2px 0; color: #9880a8; font-size: 15px; font-weight: 500; font-family: 'Georgia', serif;">• ${service}</div>`).join('')}
                                </div>
                              </td>
                            </tr>
                          </table>
                        </div>
                        
                        <!-- Total Amount -->
                        <div style="background-color: #ffffff; padding: 18px 20px; border-radius: 14px; margin-bottom: 15px; border-left: 3px solid #d4b5d4; box-shadow: 0 2px 8px rgba(0,0,0,0.03);">
                          <table width="100%" cellpadding="0" cellspacing="0">
                            <tr>
                              <td width="35" valign="middle">
                                <span style="font-size: 20px; opacity: 0.7;">💰</span>
                              </td>
                              <td>
                                <p style="margin: 0 0 4px 0; color: #b8a0b8; font-size: 11px; font-weight: 500; text-transform: uppercase; letter-spacing: 1px;">Total Amount</p>
                                <p style="margin: 0; color: #9880a8; font-size: 18px; font-weight: 600; font-family: 'Georgia', serif;">₹${booking.totalAmount}</p>
                              </td>
                            </tr>
                          </table>
                        </div>
                        
                        <!-- Address -->
                        <div style="background-color: #ffffff; padding: 18px 20px; border-radius: 14px; border-left: 3px solid #d4b5d4; box-shadow: 0 2px 8px rgba(0,0,0,0.03);">
                          <table width="100%" cellpadding="0" cellspacing="0">
                            <tr>
                              <td width="35" valign="top">
                                <span style="font-size: 20px; opacity: 0.7;">📍</span>
                              </td>
                              <td>
                                <p style="margin: 0 0 4px 0; color: #b8a0b8; font-size: 11px; font-weight: 500; text-transform: uppercase; letter-spacing: 1px;">Service Address</p>
                                <p style="margin: 0; color: #9880a8; font-size: 15px; font-weight: 400; line-height: 1.6; font-family: 'Georgia', serif;">${booking.customerAddress}</p>
                              </td>
                            </tr>
                          </table>
                        </div>
                      </div>
                      
                      <!-- Contact Information -->
                      <div style="background: linear-gradient(135deg, #f0f9f8 0%, #f5faf9 100%); padding: 30px; border-radius: 18px; margin-bottom: 30px; border: 1px solid #e0f0ed; box-shadow: 0 4px 16px rgba(180,220,210,0.08);">
                        <h3 style="margin: 0 0 18px 0; color: #88b8a8; font-size: 16px; font-weight: 500; letter-spacing: 1px; font-family: 'Georgia', serif;">
                          Customer Contact Information
                        </h3>
                        <div style="background-color: #ffffff; padding: 22px 25px; border-radius: 14px; border-left: 3px solid #a8d4c4; box-shadow: 0 2px 8px rgba(0,0,0,0.03);">
                          <div style="margin-bottom: 15px;">
                            <p style="margin: 0 0 4px 0; color: #88b8a8; font-size: 11px; font-weight: 500; text-transform: uppercase; letter-spacing: 1px;">Phone Number</p>
                            <a href="tel:${booking.customerPhone}" style="margin: 0; color: #c88080; font-size: 18px; font-weight: 500; text-decoration: none; display: block; font-family: 'Georgia', serif;">${booking.customerPhone}</a>
                          </div>
                          ${booking.customerEmail ? `
                          <div>
                            <p style="margin: 0 0 4px 0; color: #88b8a8; font-size: 11px; font-weight: 500; text-transform: uppercase; letter-spacing: 1px;">Email Address</p>
                            <a href="mailto:${booking.customerEmail}" style="margin: 0; color: #c88080; font-size: 16px; font-weight: 500; text-decoration: none; display: block; font-family: 'Georgia', serif;">${booking.customerEmail}</a>
                          </div>
                          ` : ''}
                        </div>
                      </div>
                      
                      ${booking.notes ? `
                      <!-- Notes Section -->
                      <div style="background: linear-gradient(135deg, #fff8f0 0%, #fffbf5 100%); padding: 30px; border-radius: 18px; margin-bottom: 30px; border: 1px solid #ffe8d0; box-shadow: 0 4px 16px rgba(255,200,160,0.08);">
                        <h3 style="margin: 0 0 18px 0; color: #d4a080; font-size: 16px; font-weight: 500; letter-spacing: 1px; font-family: 'Georgia', serif;">
                          Special Instructions
                        </h3>
                        <div style="background-color: #ffffff; padding: 22px 25px; border-radius: 14px; border-left: 3px solid #d4a080; box-shadow: 0 2px 8px rgba(0,0,0,0.03);">
                          <p style="margin: 0; color: #687878; font-size: 15px; line-height: 1.8; white-space: pre-wrap; font-family: 'Georgia', serif;">${booking.notes}</p>
                        </div>
                      </div>
                      ` : ''}
                      
                      <!-- Action Button -->
                      <div style="background: linear-gradient(135deg, #f5fff8 0%, #f8fff9 100%); padding: 35px 30px; border-radius: 18px; text-align: center; border: 1px solid #e8f5ed; box-shadow: 0 4px 16px rgba(180,220,200,0.1);">
                        <p style="margin: 0 0 18px 0; color: #88b8a0; font-size: 14px; font-weight: 500; letter-spacing: 0.5px;">
                          Please Contact Customer to Confirm
                        </p>
                        <a href="tel:${booking.customerPhone}" style="display: inline-block; background: linear-gradient(135deg, #b8d4c8 0%, #a8c8b8 100%); color: #ffffff; padding: 16px 45px; border-radius: 25px; text-decoration: none; font-size: 17px; font-weight: 500; box-shadow: 0 6px 20px rgba(168,200,184,0.3); font-family: 'Georgia', serif; letter-spacing: 0.5px;">
                          📞 Call ${booking.customerName}
                        </a>
                        <p style="margin: 18px 0 0 0; color: #98b8a8; font-size: 13px; font-weight: 400;">
                          Booking: <span style="color: #88a898; font-weight: 500;">${booking.services.join(', ')}</span>
                        </p>
                      </div>
                      
                    </td>
                  </tr>
                  
                  <!-- Elegant Footer -->
                  <tr>
                    <td style="background: linear-gradient(135deg, #fafafa 0%, #f8f8f8 100%); padding: 30px 40px; text-align: center; border-top: 1px solid #f0f0f0;">
                      <p style="margin: 0 0 10px 0; color: #a8a8a8; font-size: 13px; line-height: 1.6; font-family: 'Georgia', serif;">
                        ⏰ ${new Date(booking.timestamp).toLocaleString('en-IN', { 
                          weekday: 'long', 
                          year: 'numeric', 
                          month: 'long', 
                          day: 'numeric',
                          hour: '2-digit',
                          minute: '2-digit',
                          hour12: true 
                        })}
                      </p>
                      <p style="margin: 0; color: #c0c0c0; font-size: 11px; letter-spacing: 0.5px;">
                        Automated booking confirmation • Goodness Glamour Salon<br>
                        All bookings saved to Excel file
                      </p>
                      <!-- Subtle floral footer accent -->
                      <p style="margin: 15px 0 0 0; opacity: 0.2; font-size: 20px;">🌸 🌿 🌸</p>
                    </td>
                  </tr>
                  
                </table>
                
              </td>
            </tr>
          </table>
          
        </body>
        </html>
      `,
    };

    await retryEmailSend(
      async () => {
        return await sendEmailWithPortFallback(mailOptions, 'admin booking email');
      },
      'admin booking email',
      2
    );

    console.log('✅ Booking confirmation email sent successfully to 2akonsultant@gmail.com');
    return true;
  } catch (error) {
    logEmailError('Error sending admin booking email', error);
    return false;
  }
}

// Send booking confirmation email to customer (via EmailJS)
export async function sendCustomerBookingConfirmation(booking: BookingData): Promise<boolean> {
  try {
    console.log(`📧 Sending customer confirmation (via EmailJS) to: ${booking.customerEmail}`);
    
    // Check if customer email is provided
    console.log(`📧 Validating customer email: "${booking.customerEmail}"`);
    if (!booking.customerEmail || booking.customerEmail.trim() === '') {
      console.log('❌ No customer email provided, skipping customer confirmation');
      return false;
    }
    
    // Basic email validation
    const emailRegex = /^[^\s@]+@[^\s@]+\.[^\s@]+$/;
    if (!emailRegex.test(booking.customerEmail)) {
      console.log(`❌ Invalid email format: "${booking.customerEmail}", skipping customer confirmation`);
      return false;
    }
    
    console.log(`✅ Customer email validation passed: "${booking.customerEmail}"`);

    if (!isEmailJSConfigured()) {
      console.error(
        '❌ Skipping customer confirmation email: EmailJS is not configured (missing service/template/public key).'
      );
      return false;
    }

    const success = await sendCustomerEmailViaEmailJS(booking);
    console.log(`📧 EmailJS customer booking confirmation result: ${success}`);
    return success;
  } catch (error) {
    logEmailError('Error sending customer booking confirmation via EmailJS', error);
    return false;
  }
}

// Update Excel file with booking data
export async function updateBookingExcelFile(booking: BookingData): Promise<boolean> {
  try {
    const dataDir = path.join(process.cwd(), 'data');
    
    // Ensure data directory exists
    if (!fs.existsSync(dataDir)) {
      fs.mkdirSync(dataDir, { recursive: true });
    }
    
    const filePath = path.join(dataDir, 'bookings.xlsx');
    
    let workbook;
    let worksheet;
    let bookings: any[] = [];
    
    // Check if file exists
    if (fs.existsSync(filePath)) {
      workbook = XLSX.readFile(filePath);
      worksheet = workbook.Sheets['Bookings'];
      
      if (worksheet) {
        bookings = XLSX.utils.sheet_to_json(worksheet);
      }
    } else {
      workbook = XLSX.utils.book_new();
    }
    
    // Add new booking
    const newBooking = {
      'Booking ID': booking.id,
      'Name': booking.customerName,
      'Email': booking.customerEmail || '',
      'Phone': booking.customerPhone,
      'Date': new Date(booking.appointmentDate).toLocaleDateString('en-IN'),
      'Time': booking.appointmentTime,
      'Services': booking.services.join(', '),
      'Location': booking.customerAddress,
      'Total Amount': booking.totalAmount,
      'Notes': booking.notes || '',
      'Timestamp': new Date(booking.timestamp).toLocaleString('en-IN')
    };
    
    bookings.push(newBooking);
    
    // Create new worksheet
    worksheet = XLSX.utils.json_to_sheet(bookings);
    workbook.Sheets['Bookings'] = worksheet;
    
    // Write file
    XLSX.writeFile(workbook, filePath);
    
    console.log(`✅ Excel file updated: ${filePath}`);
    console.log(`📊 Total bookings: ${bookings.length}`);
    
    return true;
  } catch (error) {
    console.error('❌ Error updating booking Excel file:', error);
    return false;
  }
}

// Test email configuration
export async function testEmailConfiguration(): Promise<boolean> {
  try {
    console.log('🧪 Testing email configuration...');
    
    const testMailOptions = {
      from: process.env.EMAIL_USER || '2akonsultant@gmail.com',
      to: process.env.EMAIL_USER || '2akonsultant@gmail.com',
      subject: 'Test Email - Configuration Check',
      html: '<p>This is a test email to verify email configuration is working.</p>'
    };
    
    const result = await sendEmailWithPortFallback(testMailOptions, 'test email');
    console.log('✅ Test email sent successfully:', result.messageId);
    return true;
  } catch (error) {
    console.error('❌ Test email failed:', error);
    logEmailError('Test email failed', error);
    return false;
  }
}

// Process booking (save to Excel, send emails, and send SMS)
export async function processBooking(booking: BookingData): Promise<{ 
  emailSent: boolean; 
  excelUpdated: boolean; 
  customerEmailSent: boolean;
  smsSent: boolean;
  smsProvider?: string;
}> {
  try {
    console.log(`📧 Processing booking from: ${booking.customerName}`);

    // Update Excel file (don't let Excel failures block emails)
    let excelUpdated = false;
    try {
      excelUpdated = await updateBookingExcelFile(booking);
    } catch (excelErr) {
      console.error('❌ Excel update failed (emails will still be sent):', excelErr);
    }

    // Send email to admin
    const adminEmailSent = await sendBookingEmail(booking);
    
    // Send confirmation email to customer
    console.log(`📧 Attempting to send customer email to: ${booking.customerEmail}`);
    const customerEmailSent = await sendCustomerBookingConfirmation(booking);
    console.log(`📧 Customer email result: ${customerEmailSent}`);
    
    // Send SMS confirmation to customer
    console.log(`📱 Attempting to send SMS to: ${booking.customerPhone}`);
    const smsResult = await sendBookingConfirmationSMS({
      id: booking.id,
      customerName: booking.customerName,
      customerPhone: booking.customerPhone,
      appointmentDate: booking.appointmentDate,
      appointmentTime: booking.appointmentTime,
      services: booking.services,
      totalAmount: booking.totalAmount,
      customerAddress: booking.customerAddress
    });
    console.log(`📱 SMS result: ${smsResult.success} via ${smsResult.provider}`);
    
    const emailSent = adminEmailSent; // Keep existing return format for compatibility
    
    console.log(`✅ Booking processed: Admin Email=${adminEmailSent}, Customer Email=${customerEmailSent}, SMS=${smsResult.success} (${smsResult.provider}), Excel=${excelUpdated}`);
    
    return { 
      emailSent, 
      excelUpdated, 
      customerEmailSent,
      smsSent: smsResult.success,
      smsProvider: smsResult.provider
    };
  } catch (error) {
    console.error('❌ Error processing booking:', error);
    return { 
      emailSent: false, 
      excelUpdated: false, 
      customerEmailSent: false,
      smsSent: false
    };
  }
}

/**
 * Send OTP verification email
 */
export async function sendOTPEmail(
  email: string,
  name: string,
  otp: string
): Promise<boolean> {
  try {
    console.log(`📧 Sending OTP to: ${email}`);

    const mailOptions = {
      from: process.env.EMAIL_USER || '2akonsultant@gmail.com',
      to: email,
      subject: '🔐 Verify Your Email - Goodness Glamour Salon',
      html: `
        <!DOCTYPE html>
        <html>
        <head>
          <meta charset="UTF-8">
          <meta name="viewport" content="width=device-width, initial-scale=1.0">
        </head>
        <body style="margin: 0; padding: 0; background: linear-gradient(135deg, #fef5f1 0%, #fef9f5 50%, #f5f3f9 100%); font-family: 'Georgia', 'Times New Roman', serif;">
          
          <table width="100%" cellpadding="0" cellspacing="0" style="background: linear-gradient(135deg, #fef5f1 0%, #fef9f5 50%, #f5f3f9 100%); padding: 40px 20px;">
            <tr>
              <td align="center">
                
                <table width="620" cellpadding="0" cellspacing="0" style="background-color: #ffffff; border-radius: 24px; overflow: hidden; box-shadow: 0 8px 32px rgba(0,0,0,0.08);">
                  
                  <tr>
                    <td style="background: linear-gradient(135deg, #ffeef5 0%, #fff0f3 50%, #f9f0ff 100%); padding: 50px 40px 40px 40px; text-align: center; position: relative;">
                      <h1 style="margin: 0; color: #d4a5a5; font-size: 36px; font-weight: 300; letter-spacing: 3px; font-family: 'Georgia', serif;">
                        Goodness Glamour
                      </h1>
                      <p style="margin: 8px 0 0 0; color: #b8a0a0; font-size: 15px; font-weight: 400; letter-spacing: 2px; font-family: 'Georgia', serif;">
                        Ladies & Kids Salon
                      </p>
                      <div style="margin-top: 25px; padding: 10px 30px; background-color: rgba(255,255,255,0.7); border-radius: 20px; display: inline-block; border: 1px solid rgba(212,165,165,0.2);">
                        <p style="margin: 0; color: #c9a0a0; font-size: 13px; font-weight: 500; letter-spacing: 1px;">
                          🔐 Email Verification
                        </p>
                      </div>
                    </td>
                  </tr>
                  
                  <tr>
                    <td style="padding: 40px;">
                      
                      <div style="background: linear-gradient(135deg, #fff5f0 0%, #fff8f5 100%); padding: 25px 30px; border-radius: 18px; margin-bottom: 30px; border: 1px solid #ffe8e0; box-shadow: 0 4px 16px rgba(255,200,180,0.1); text-align: center;">
                        <h2 style="margin: 0 0 10px 0; color: #c88080; font-size: 24px; font-weight: 400; font-family: 'Georgia', serif;">Welcome, ${name}! 💐</h2>
                        <p style="margin: 0; color: #d4a5a5; font-size: 16px; font-weight: 400; line-height: 1.6;">
                          Thank you for signing up! Please verify your email address to complete your registration.
                        </p>
                      </div>
                      
                      <div style="background: linear-gradient(135deg, #f8f5ff 0%, #faf7ff 100%); padding: 40px 30px; border-radius: 18px; margin-bottom: 30px; border: 1px solid #f0e8ff; box-shadow: 0 4px 16px rgba(200,180,220,0.08); text-align: center;">
                        <p style="margin: 0 0 20px 0; color: #a88cb8; font-size: 14px; font-weight: 500; letter-spacing: 1px; text-transform: uppercase;">
                          Your Verification Code
                        </p>
                        
                        <div style="background-color: #ffffff; padding: 25px; border-radius: 14px; border: 2px solid #d4b5d4; box-shadow: 0 4px 16px rgba(0,0,0,0.05); margin-bottom: 20px;">
                          <p style="margin: 0; font-size: 48px; font-weight: 700; color: #8080c0; letter-spacing: 8px; font-family: 'Courier New', monospace;">
                            ${otp}
                          </p>
                        </div>
                        
                        <p style="margin: 0; color: #b8a0b8; font-size: 14px; line-height: 1.6;">
                          This code will expire in <strong style="color: #8080c0;">10 minutes</strong>
                        </p>
                      </div>
                      
                      <div style="background: linear-gradient(135deg, #fff0f5 0%, #fff5f0 100%); padding: 25px 30px; border-radius: 18px; margin-bottom: 30px; border: 1px solid #ffe0e8; box-shadow: 0 4px 16px rgba(255,180,200,0.08);">
                        <h3 style="margin: 0 0 15px 0; color: #c880a0; font-size: 16px; font-weight: 500; letter-spacing: 1px; font-family: 'Georgia', serif;">
                          📝 How to Verify
                        </h3>
                        <ol style="margin: 0; padding-left: 20px; color: #b880a0; font-size: 14px; line-height: 1.8;">
                          <li>Enter the 6-digit code on the verification page</li>
                          <li>Click "Verify Email" button</li>
                          <li>You'll be automatically logged in</li>
                          <li>Start booking your favorite salon services!</li>
                        </ol>
                      </div>
                      
                      <div style="background: linear-gradient(135deg, #f0f8ff 0%, #f5faff 100%); padding: 20px 25px; border-radius: 18px; border: 1px solid #e0e8ff; box-shadow: 0 4px 16px rgba(180,200,255,0.08);">
                        <p style="margin: 0; color: #8080c0; font-size: 13px; line-height: 1.6; text-align: center;">
                          🔒 <strong>Security Tip:</strong> Never share this code with anyone. We'll never ask for it via phone or email.
                        </p>
                      </div>
                      
                    </td>
                  </tr>
                  
                  <tr>
                    <td style="background: linear-gradient(135deg, #f8f5f0 0%, #faf7f5 100%); padding: 30px 40px; text-align: center; border-top: 1px solid rgba(212,165,165,0.1);">
                      <p style="margin: 0; color: #d4a5a5; font-size: 14px; font-weight: 400; line-height: 1.6; font-family: 'Georgia', serif;">
                        If you didn't sign up for <strong style="color: #c88080;">Goodness Glamour Salon</strong>,<br>
                        please ignore this email.
                      </p>
                      <p style="margin: 20px 0 0 0; color: #c0c0c0; font-size: 11px; letter-spacing: 0.5px;">
                        Need help? Contact us: 9036626642 | 2akonsultant@gmail.com
                      </p>
                    </td>
                  </tr>
                  
                </table>
                
              </td>
            </tr>
          </table>
          
        </body>
        </html>
      `,
    };

    await sendEmailWithPortFallback(mailOptions, 'OTP email');
    console.log(`✅ OTP email sent successfully to ${email}`);
    return true;
  } catch (error: any) {
    console.error('❌ Error sending OTP email:', error.message);
    logEmailError('Error sending OTP email', error);
    return false;
  }
}

