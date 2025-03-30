from flask import Blueprint, jsonify
from flask_security import current_user, roles_required
from .mail_service import EmailService

email_bp = Blueprint('email', __name__)

@email_bp.route('/test-email')
@roles_required('admin')
def test_email():
    """Test email sending through MailHog"""
    try:
        success = EmailService.send_email(
            to_email=current_user.email,
            subject='Test Email',
            html_content='<h1>Test Email</h1><p>This is a test email sent through MailHog.</p>',
            text_content='Test Email\n\nThis is a test email sent through MailHog.'
        )
        
        if success:
            return jsonify({
                'status': 'success',
                'message': f'Test email sent to {current_user.email}. Check MailHog interface at http://0.0.0.0:8025'
            })
        else:
            return jsonify({
                'status': 'error',
                'message': 'Failed to send test email'
            }), 500
    except Exception as e:
        return jsonify({
            'status': 'error',
            'message': str(e)
        }), 500
