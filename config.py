import os
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

class Config:
    """Base configuration class."""
    
    # Flask Configuration
    SECRET_KEY = os.getenv('SECRET_KEY', 'default-secret-key')
    DEBUG = os.getenv('DEBUG', 'False').lower() == 'true'
    
    # Database Configuration
    SQLALCHEMY_DATABASE_URI = os.getenv('DATABASE_URI')
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    
    # Social Media API Configuration
    FACEBOOK = {
        'ACCESS_TOKEN': os.getenv('FACEBOOK_ACCESS_TOKEN'),
        'PAGE_ID': os.getenv('FACEBOOK_PAGE_ID')
    }
    
    TWITTER = {
        'API_KEY': os.getenv('TWITTER_API_KEY'),
        'API_SECRET': os.getenv('TWITTER_API_SECRET'),
        'ACCESS_TOKEN': os.getenv('TWITTER_ACCESS_TOKEN'),
        'ACCESS_TOKEN_SECRET': os.getenv('TWITTER_ACCESS_TOKEN_SECRET')
    }
    
    INSTAGRAM = {
        'ACCESS_TOKEN': os.getenv('INSTAGRAM_ACCESS_TOKEN'),
        'BUSINESS_ACCOUNT_ID': os.getenv('INSTAGRAM_BUSINESS_ACCOUNT_ID')
    }
    
    PINTEREST = {
        'ACCESS_TOKEN': os.getenv('PINTEREST_ACCESS_TOKEN'),
        'BOARD_ID': os.getenv('PINTEREST_BOARD_ID')
    }
    
    TIKTOK = {
        'ACCESS_TOKEN': os.getenv('TIKTOK_ACCESS_TOKEN'),
        'OPEN_ID': os.getenv('TIKTOK_OPEN_ID')
    }
    
    # Upload Configuration
    UPLOAD_FOLDER = 'uploads'
    MAX_CONTENT_LENGTH = 16 * 1024 * 1024  # 16MB max file size
    ALLOWED_IMAGE_EXTENSIONS = {'png', 'jpg', 'jpeg', 'gif'}
    ALLOWED_VIDEO_EXTENSIONS = {'mp4', 'mov', 'avi'}
    
    # Rate Limiting
    RATELIMIT_DEFAULT = os.getenv('RATELIMIT_DEFAULT', '300/day;30/hour;1/minute')
    
    @staticmethod
    def init_app(app):
        """Initialize application configuration."""
        # Create upload folder if it doesn't exist
        upload_folder = os.path.join(app.root_path, Config.UPLOAD_FOLDER)
        if not os.path.exists(upload_folder):
            os.makedirs(upload_folder)

class DevelopmentConfig(Config):
    """Development configuration."""
    DEBUG = True
    SQLALCHEMY_ECHO = True

class ProductionConfig(Config):
    """Production configuration."""
    DEBUG = False
    SQLALCHEMY_ECHO = False

# Configuration dictionary
config = {
    'development': DevelopmentConfig,
    'production': ProductionConfig,
    'default': DevelopmentConfig
}