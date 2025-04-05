import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
import logging

logger = logging.getLogger(__name__)

def send_email(recipient, subject, body, sender=None, smtp_server=None, smtp_port=None, username=None, password=None):
    """
    Send an email using SMTP.
    
    Args:
        recipient (str): Email address of the recipient
        subject (str): Email subject
        body (str): Email body content (HTML or plain text)
        sender (str, optional): Email address of the sender
        smtp_server (str, optional): SMTP server address
        smtp_port (int, optional): SMTP server port
        username (str, optional): SMTP authentication username
        password (str, optional): SMTP authentication password
        
    Returns:
        bool: True if email was sent successfully, False otherwise
    """
    # Default values if not provided
    sender = sender or "automation@example.com"
    smtp_server = smtp_server or "localhost"
    smtp_port = smtp_port or 25
    
    try:
        # Create message
        msg = MIMEMultipart()
        msg['From'] = sender
        msg['To'] = recipient
        msg['Subject'] = subject
        
        # Attach body
        msg.attach(MIMEText(body, 'html'))
        
        # Connect to server and send
        with smtplib.SMTP(smtp_server, smtp_port) as server:
            if username and password:
                server.starttls()
                server.login(username, password)
            
            server.send_message(msg)
            
        logger.info(f"Email sent to {recipient}: {subject}")
        return True
        
    except Exception as e:
        logger.error(f"Failed to send email to {recipient}: {str(e)}")
        return False
