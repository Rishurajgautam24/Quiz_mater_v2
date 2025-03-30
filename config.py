class Config(object):
    DEBUG = False
    TESTING = False

    # Email Configuration
    MAIL_SERVER = 'localhost'
    MAIL_PORT = 1025  # Mailhog SMTP port
    MAIL_USE_TLS = False
    MAIL_USE_SSL = False
    MAIL_DEBUG = True
    MAIL_USERNAME = None
    MAIL_PASSWORD = None
    MAIL_DEFAULT_SENDER = 'quiz-master@example.com'
    MAIL_MAX_EMAILS = None
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
    MAIL_SERVER = 'localhost'
    MAIL_PORT = 1025  # Mailhog SMTP port
    MAIL_USE_TLS = False
    MAIL_USE_SSL = False
    MAIL_DEBUG = True
    MAIL_DEFAULT_SENDER = 'quizmaster@example.com'

    # Celery Configuration
    broker_url = 'redis://localhost:6379/0'
    result_backend = 'redis://localhost:6379/0'
    accept_content = ['json']
    task_serializer = 'json'
    result_serializer = 'json'
    timezone = 'Asia/Kolkata'
