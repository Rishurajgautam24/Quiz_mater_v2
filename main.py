# ------------ Main Application File -----------
# Handles Flask app configuration, database setup, and security configuration
# Creates initial test user for development purposes

from flask import Flask, render_template
from flask_security import SQLAlchemyUserDatastore, Security
from application.models import db, User, Role
from config import DevelopmentConfig
from application.resources import api
from werkzeug.security import generate_password_hash
from flask_caching import Cache
import uuid
from datetime import datetime

# Initialize extensions
cache = Cache()

def create_app():
    # ------------ App Configuration -----------
    app = Flask(__name__, 
                template_folder='application/templates',
                static_folder='application/static')
    app.config.from_object(DevelopmentConfig)
    
    # ------------ Extensions Initialization -----------
    db.init_app(app)
    api.init_app(app)
    cache.init_app(app)  # Simplified cache initialization
    datastore = SQLAlchemyUserDatastore(db, User, Role)
    app.security = Security(app, datastore)
    
    # Make cache available globally
    app.extensions['cache'] = cache
    
    with app.app_context():
        # ------------ Database Setup -----------
        db.create_all()
        import application.views
        
        # ------------ Test User Creation -----------
        if not User.query.filter_by(email='test@example.com').first():
            test_user = User(
                email='test@example.com',
                username='TestUser',
                active=True,
                fs_uniquifier=str(uuid.uuid4())
            )
            test_user.set_password('password123')
            db.session.add(test_user)
            db.session.commit()

    # ------------ Route Definitions -----------
    @app.route('/')
    @cache.cached(timeout=5)  # Cache the index page for 60 seconds
    def index():
        current_time = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        print(f"Route accessed at: {current_time}")  # This will show in console
        return render_template('index.html')

    return app, datastore

# ------------ App Initialization -----------
app, datastore = create_app()

# Make cache globally available
cache.app = app

# ------------ Main Execution -----------
if __name__ == '__main__':
    app.run(debug=True)