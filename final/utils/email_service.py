import os
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from dotenv import load_dotenv
import pathlib

# Get the absolute path to the root directory (where .env should be)
ROOT_DIR = pathlib.Path(__file__).parent.parent
ENV_PATH = os.path.join(ROOT_DIR, '.env')

# Debug print statements
print(f"Looking for .env file at: {ENV_PATH}")
print(f"Does .env file exist? {os.path.exists(ENV_PATH)}")

# Load environment variables from specific path
load_dotenv(ENV_PATH)

# Debug: Print all environment variables (excluding the values for security)
print("Available environment variables:", [key for key in os.environ.keys()])

def send_email(recipient_email, subject, body):
    """
    Send an email using Gmail SMTP
    """
    try:
        # Email configuration
        sender_email = os.getenv('EMAIL_ID')
        app_password = os.getenv('EMAIL_PASSWORD')
        
        # Debug: Print email configuration status (without exposing sensitive data)
        print(f"Email configuration status:")
        print(f"- EMAIL_ID found: {sender_email is not None}")
        print(f"- EMAIL_PASSWORD found: {app_password is not None}")
        print(f"- Using sender email: {sender_email}")
        
        # Debug: Check if credentials are available
        if not sender_email or not app_password:
            missing_vars = []
            if not sender_email:
                missing_vars.append("EMAIL_ID")
            if not app_password:
                missing_vars.append("EMAIL_PASSWORD")
            return False, f"""Missing environment variables: {', '.join(missing_vars)}. Please check:
1. Your .env file exists at: {ENV_PATH}
2. The .env file contains:
   EMAIL_ID=zenflowitapp@gmail.com
   EMAIL_PASSWORD=your_16_character_password
3. There are no extra spaces or quotes in the .env file
4. The file is properly saved with no hidden characters

Current environment variables available: {[key for key in os.environ.keys() if 'EMAIL' in key]}"""
        
        # Create message
        message = MIMEMultipart()
        message["From"] = sender_email
        message["To"] = recipient_email
        message["Subject"] = subject

        # Add body to email
        message.attach(MIMEText(body, "plain"))

        try:
            # Create SMTP session for sending the mail
            with smtplib.SMTP("smtp.gmail.com", 587) as server:
                server.set_debuglevel(1)  # Enable debug output
                server.starttls()
                
                try:
                    server.login(sender_email, app_password)
                except smtplib.SMTPAuthenticationError as auth_error:
                    return False, f"""Email authentication failed. Please ensure:
1. You've enabled 2-Step Verification in your Google Account
2. You've generated an App Password for this application
3. The App Password in .env file matches the 16-character password from Google
4. There are no spaces or quotes in the password in .env file

Current email being used: {sender_email}
Error details: {str(auth_error)}"""
                
                server.send_message(message)
                return True, None
                
        except smtplib.SMTPException as smtp_error:
            return False, f"SMTP error occurred: {str(smtp_error)}"
        except Exception as e:
            return False, f"Error sending email: {str(e)}"
            
    except Exception as e:
        return False, f"Configuration error: {str(e)}"

def send_welcome_email(user_email, user_first_name):
    """
    Send welcome email to newly registered users
    """
    subject = "Welcome to ZenFlowIt! Let's Unlock Your Productivity 🚀"
    
    body = f"""Hi {user_first_name},

Welcome to ZenFlowIt! 🎉

We're thrilled to have you join our community — where productivity meets simplicity.

With ZenFlowIt, you can:
- ✅ Stay focused with personalized task lists
- ✅ Track your progress effortlessly
- ✅ Celebrate every achievement, big or small!

Take your first step today. Log in and start setting your goals: https://zenflowit.com/login

Remember, small steps every day lead to extraordinary results. 🚀

If you ever need help or have questions, feel free to reach out to us at zenflowitapp@gmail.com.

Welcome aboard once again!

- The ZenFlowIt Team"""

    return send_email(user_email, subject, body)

def send_password_reminder_email(user_email, user_first_name, temp_password):
    """
    Send password reminder email to users with temporary password
    """
    subject = "ZenFlowIt - Your Temporary Password"
    
    body = f"""Hi {user_first_name},

We received a password recovery request for your ZenFlowIt account.

Your temporary password is: {temp_password}

For security reasons, please:
1. Log in using this temporary password
2. Change your password immediately after logging in
3. Do not share this temporary password with anyone

You can log in here: https://zenflowit.com/login

This temporary password will expire after your first login. If you didn't request this password recovery, please contact us immediately at zenflowitapp@gmail.com.

Best regards,
The ZenFlowIt Team"""

    return send_email(user_email, subject, body) 