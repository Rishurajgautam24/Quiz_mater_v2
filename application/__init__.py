from flask import Flask
from flask_wtf.csrf import CSRFProtect, generate_csrf
from .email_views import email_bp

csrf = CSRFProtect()

def create_app():
    app = Flask(__name__)
    
    # Configure the app
    app.config['SECRET_KEY'] = 'your-secret-key'  # Change this!
    app.config['WTF_CSRF_ENABLED'] = True
    app.config['WTF_CSRF_SECRET_KEY'] = 'your-csrf-secret-key'  # Change this!
    
    # Initialize CSRF protection
    csrf.init_app(app)
    
    # Register context processor for CSRF token
    @app.context_processor
    def inject_csrf_token():
        return dict(csrf_token=generate_csrf())
    
    app.register_blueprint(email_bp, url_prefix='/api/email')
    
    return app
