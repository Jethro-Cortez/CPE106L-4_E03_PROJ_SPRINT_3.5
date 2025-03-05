import os

class Config:
    """Configuration class for Flask application."""
    SECRET_KEY = os.environ.get('SECRET_KEY', 'dev_key_123')
    ADMIN_SECRET_KEY = os.environ.get('ADMIN_SECRET_KEY', 'admin123')
    SQLALCHEMY_DATABASE_URI = os.environ.get('DATABASE_URL', 'sqlite:///library.db')
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    UPLOAD_FOLDER = 'lms_app\static\covers'
    ALLOWED_EXTENSIONS = {'png', 'jpg', 'jpeg'}
    THEME_COLORS = {
    'primary': '#4361ee',
    'secondary': '#32CD32',
    'success': '#4CAF50',
    'danger': '#FF5252', 
    'text': '#FFFFFF',
    'background': '#1A1A1A'
} 