from main import create_app
from application.mail_service import EmailService

# Get the Flask app instance
app, _ = create_app()  # Modified to unpack tuple returned by create_app()

def test_emails():
    with app.app_context():
        print("Testing email service...")
        
        try:
            # Test basic email
            result = EmailService.send_email(
                "stud1@example.com",
                "Test Email",
                "<h1>This is a test email</h1><p>Hello from Quiz Master!</p>",
                "This is a test email. Hello from Quiz Master!"  # Added plain text version
            )
            print(f"Basic email sent: {result}")
            
            # Test reminder email
            result = EmailService.send_reminder(
                "student@example.com",
                "John Doe"
            )
            print(f"Reminder email sent: {result}")
            
            # Test report email
            report_data = {
                'total_quizzes': 5,
                'avg_score': 85.5,
                'total_time': 120
            }
            result = EmailService.send_report(
                "student@example.com",
                "John Doe",
                report_data
            )
            print(f"Report email sent: {result}")
            
        except Exception as e:
            print(f"Error during email testing: {str(e)}")

def verify_mailhog():
    """Verify MailHog is running"""
    import socket
    try:
        sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        result = sock.connect_ex(('localhost', 1025))
        if result == 0:
            print("MailHog is running on port 1025")
            return True
        else:
            print("ERROR: MailHog is not running! Please start MailHog first.")
            return False
    finally:
        sock.close()

if __name__ == "__main__":
    if verify_mailhog():
        test_emails()
    else:
        print("Please start MailHog using the command: mailhog")