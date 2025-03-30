from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
import smtplib
from flask import current_app, render_template_string
import logging
from datetime import datetime

logger = logging.getLogger(__name__)

class EmailService:
    @staticmethod
    def send_email(to_email, subject, html_content, text_content=None):
        """Send email using SMTP"""
        try:
            msg = MIMEMultipart('alternative')
            msg['Subject'] = subject
            msg['From'] = current_app.config['MAIL_DEFAULT_SENDER']
            msg['To'] = to_email

            # Add text/plain and text/html parts
            if text_content:
                msg.attach(MIMEText(text_content, 'plain'))
            msg.attach(MIMEText(html_content, 'html'))

            # Connect to SMTP server
            with smtplib.SMTP(
                current_app.config['MAIL_SERVER'],
                current_app.config['MAIL_PORT']
            ) as smtp:
                smtp.send_message(msg)
                logger.info(f"Email sent to {to_email}")
                return True
        except Exception as e:
            logger.error(f"Failed to send email: {str(e)}")
            return False

    @staticmethod
    def send_reminder(user_email, username):
        """Send reminder email with better formatting"""
        html_content = f"""
        <html>
            <body style="font-family: Arial, sans-serif; line-height: 1.6; color: #333;">
                <div style="max-width: 600px; margin: 0 auto; padding: 20px;">
                    <h2 style="color: #2c3e50; border-bottom: 2px solid #3498db;">Quiz Activity Reminder</h2>
                    <p>Hello {username},</p>
                    <p>We noticed you haven't taken any quizzes recently. Stay on track with your learning journey!</p>
                    <div style="background-color: #f8f9fa; padding: 15px; border-radius: 5px; margin: 20px 0;">
                        <p style="margin: 0;">🎯 <strong>Quick Tips:</strong></p>
                        <ul>
                            <li>Set aside 30 minutes daily for quizzes</li>
                            <li>Try different subjects to maintain variety</li>
                            <li>Track your progress regularly</li>
                        </ul>
                    </div>
                    <p style="background-color: #e8f4fd; padding: 10px; border-radius: 5px;">
                        Ready to get back to learning? Login now to explore new quizzes!
                    </p>
                    <p style="font-size: 0.9em; color: #666; margin-top: 30px;">
                        Best regards,<br>
                        Quiz Master Team
                    </p>
                </div>
            </body>
        </html>
        """
        plain_text = f"""
        Quiz Activity Reminder

        Hello {username},

        We noticed you haven't taken any quizzes recently. Stay on track with your learning journey!

        Quick Tips:
        * Set aside 30 minutes daily for quizzes
        * Try different subjects to maintain variety
        * Track your progress regularly

        Ready to get back to learning? Login now to explore new quizzes!

        Best regards,
        Quiz Master Team
        """
        return EmailService.send_email(user_email, "Quiz Activity Reminder", html_content, plain_text)

    @staticmethod
    def send_report(user_email, username, report_data):
        """Send enhanced performance report email"""
        html_content = f"""
        <html>
            <body style="font-family: Arial, sans-serif; line-height: 1.6; color: #333;">
                <div style="max-width: 600px; margin: 0 auto; padding: 20px;">
                    <h2 style="color: #2c3e50; border-bottom: 2px solid #3498db;">Monthly Performance Report</h2>
                    <p>Hello {username},</p>
                    <p>Here's your learning progress for the past month:</p>
                    
                    <div style="background-color: #f8f9fa; padding: 20px; border-radius: 5px; margin: 20px 0;">
                        <h3 style="color: #2c3e50; margin-top: 0;">Your Statistics</h3>
                        <table style="width: 100%; border-collapse: collapse;">
                            <tr>
                                <td style="padding: 10px; border-bottom: 1px solid #dee2e6;">
                                    <strong>Quizzes Completed:</strong>
                                </td>
                                <td style="padding: 10px; border-bottom: 1px solid #dee2e6;">
                                    {report_data['total_quizzes']}
                                </td>
                            </tr>
                            <tr>
                                <td style="padding: 10px; border-bottom: 1px solid #dee2e6;">
                                    <strong>Average Score:</strong>
                                </td>
                                <td style="padding: 10px; border-bottom: 1px solid #dee2e6;">
                                    {report_data['avg_score']}%
                                </td>
                            </tr>
                            <tr>
                                <td style="padding: 10px;">
                                    <strong>Total Time Invested:</strong>
                                </td>
                                <td style="padding: 10px;">
                                    {report_data['total_time']} minutes
                                </td>
                            </tr>
                        </table>
                    </div>
                    
                    <div style="background-color: #e8f4fd; padding: 15px; border-radius: 5px;">
                        <p style="margin: 0;">
                            <strong>💡 Pro Tip:</strong> Regular practice leads to better retention. 
                            Try to attempt at least one quiz every day!
                        </p>
                    </div>

                    <p style="font-size: 0.9em; color: #666; margin-top: 30px;">
                        Keep up the great work!<br>
                        Quiz Master Team
                    </p>
                    <p style="font-size: 0.8em; color: #999;">
                        Report generated on: {datetime.now().strftime('%Y-%m-%d %H:%M')}
                    </p>
                </div>
            </body>
        </html>
        """
        plain_text = f"""
        Monthly Performance Report

        Hello {username},

        Here's your learning progress for the past month:

        Your Statistics:
        - Quizzes Completed: {report_data['total_quizzes']}
        - Average Score: {report_data['avg_score']}%
        - Total Time Invested: {report_data['total_time']} minutes

        Pro Tip: Regular practice leads to better retention. Try to attempt at least one quiz every day!

        Keep up the great work!
        Quiz Master Team

        Report generated on: {datetime.now().strftime('%Y-%m-%d %H:%M')}
        """
        return EmailService.send_email(user_email, "Monthly Performance Report", html_content, plain_text)

    @staticmethod
    def send_quiz_completion(user_email, username, quiz_data):
        """Send quiz completion notification"""
        html_content = f"""
        <html>
            <body style="font-family: Arial, sans-serif; line-height: 1.6; color: #333;">
                <div style="max-width: 600px; margin: 0 auto; padding: 20px;">
                    <h2 style="color: #2c3e50; border-bottom: 2px solid #3498db;">Quiz Completed!</h2>
                    <p>Well done, {username}!</p>
                    
                    <div style="background-color: #f8f9fa; padding: 20px; border-radius: 5px; margin: 20px 0;">
                        <h3 style="color: #2c3e50; margin-top: 0;">Quiz Results</h3>
                        <p><strong>Quiz:</strong> {quiz_data['title']}</p>
                        <p><strong>Score:</strong> {quiz_data['score']}%</p>
                        <p><strong>Time Taken:</strong> {quiz_data['time_taken']} minutes</p>
                        <p><strong>Correct Answers:</strong> {quiz_data['correct_answers']}/{quiz_data['total_questions']}</p>
                    </div>

                    <p style="background-color: #e8f4fd; padding: 10px; border-radius: 5px;">
                        View your detailed results and performance analytics on the dashboard.
                    </p>
                </div>
            </body>
        </html>
        """
        plain_text = f"""
        Quiz Completed!

        Well done, {username}!

        Quiz Results:
        - Quiz: {quiz_data['title']}
        - Score: {quiz_data['score']}%
        - Time Taken: {quiz_data['time_taken']} minutes
        - Correct Answers: {quiz_data['correct_answers']}/{quiz_data['total_questions']}

        View your detailed results and performance analytics on the dashboard.
        """
        return EmailService.send_email(user_email, "Quiz Completed!", html_content, plain_text)


