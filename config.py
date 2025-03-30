class Config(object):
    DEBUG = False
    TESTING = False

    # MailHog Configuration
    MAIL_SERVER = '0.0.0.0'  # MailHog server address
    MAIL_PORT = 1025         # MailHog SMTP port
    MAIL_USE_TLS = False     # MailHog doesn't need TLS
    MAIL_USE_SSL = False     # MailHog doesn't need SSL
    MAIL_DEBUG = True        # Enable debug mode
    MAIL_DEFAULT_SENDER = 'quizmaster@example.com'
    MAIL_MAX_EMAILS = None   # No limit
    MAIL_SUPPRESS_SEND = False
    MAIL_ASCII_ATTACHMENTS = False
    CACHE_TYPE = "RedisCache"
    CACHE_DEFAULT_TIMEOUT = 300


class DevelopmentConfig(Config):
    DEBUG = True
    SQLALCHEMY_DATABASE_URI = 'sqlite:///quiz.db'
    SECRET_KEY = "rishu"
    SECURITY_PASSWORD_SALT = "rishu"
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    WTF_CSRF_ENABLED = False
    SECURITY_TOKEN_AUTHENTICATION_HEADER = 'Authentication-Token'
    # Redis Cache Configuration
    
    CACHE_TYPE = "RedisCache"
    CACHE_REDIS_HOST = "localhost"
    CACHE_REDIS_PORT = 6379
    CACHE_REDIS_DB = 3

    # Email Configuration
    MAIL_SERVER = '0.0.0.0'  # MailHog server address
    MAIL_PORT = 1025         # MailHog SMTP port
    MAIL_USE_TLS = False     # MailHog doesn't need TLS
    MAIL_USE_SSL = False     # MailHog doesn't need SSL
    MAIL_DEBUG = True        # Enable debug mode
    MAIL_DEFAULT_SENDER = 'quizmaster@example.com'

    # Celery Configuration
    broker_url = 'redis://localhost:6379/0'
    result_backend = 'redis://localhost:6379/0'
    accept_content = ['json']
    task_serializer = 'json'
    result_serializer = 'json'
    timezone = 'Asia/Kolkata'
