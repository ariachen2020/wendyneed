from sendgrid import SendGridAPIClient
from sendgrid.helpers.mail import Mail, Email, To, Content
from dotenv import load_dotenv
import os
import logging

# Load environment variables from .env file if present
load_dotenv()

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)

class EmailSender:
    def __init__(self):
        self.api_key = os.getenv('SENDGRID_API_KEY')
        self.from_email = os.getenv('SENDGRID_FROM_EMAIL')
        
        if not self.api_key:
            logging.error("SendGrid API key not found in environment variables")
            raise ValueError("SendGrid API key is missing")
            
        if not self.from_email:
            logging.error("SendGrid sender email not found in environment variables")
            raise ValueError("SendGrid sender email is missing")
            
        logging.info(f"EmailSender initialized with sender: {self.from_email}")

    def send_email(self, to_email, subject, body):
        """
        使用 SendGrid 發送郵件
        """
        try:
            logging.info(f"Attempting to send email to {to_email}")
            logging.info(f"Subject: {subject}")
            
            # 創建郵件
            message = Mail(
                from_email=Email(self.from_email),
                to_emails=To(to_email),
                subject=subject,
                plain_text_content=Content("text/plain", body)
            )
            
            # 初始化 SendGrid 客戶端
            sg = SendGridAPIClient(self.api_key)
            
            # 發送郵件
            response = sg.send(message)
            
            # 檢查回應
            if response.status_code in [200, 201, 202]:
                logging.info(f"Email sent successfully to {to_email}")
                logging.info(f"SendGrid response status code: {response.status_code}")
                return True
            else:
                logging.error(f"Failed to send email. Status code: {response.status_code}")
                logging.error(f"Response body: {response.body}")
                return False
                
        except Exception as e:
            logging.error(f"Error sending email: {str(e)}")
            logging.error("Full error details:", exc_info=True)
            return False

def send_test_email(recipient: str) -> bool:
    """
    Send a test email to verify the email configuration.
    
    Args:
        recipient (str): Email address to send the test email to
        
    Returns:
        bool: True if test email was sent successfully, False otherwise
    """
    try:
        sender = EmailSender()
        test_subject = "Test Email - Email Sender Configuration"
        test_body = """
        This is a test email to verify the email sender configuration.
        
        If you received this email, the email sender is working correctly!
        """
        
        return sender.send_email(recipient, test_subject, test_body)
    
    except Exception as e:
        logging.error(f"Error sending test email: {str(e)}")
        return False

if __name__ == "__main__":
    # Example usage and testing
    recipient_email = os.getenv("TEST_EMAIL")
    if recipient_email:
        if send_test_email(recipient_email):
            print("Test email sent successfully!")
        else:
            print("Failed to send test email.")
    else:
        print("Please set TEST_EMAIL environment variable for testing.") 