from flask import Flask, jsonify
from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate
from flask_login import LoginManager
from flask_wtf.csrf import CSRFProtect
from config import Config
from slugify import slugify
from sqlalchemy import event
from sqlalchemy.engine import Engine
from datetime import datetime, timedelta
from markupsafe import Markup

csrf = CSRFProtect()
db = SQLAlchemy()
migrate = Migrate()
login_manager = LoginManager()

@event.listens_for(Engine, "connect")
def set_sqlite_pragma(dbapi_connection, connection_record):
    cursor = dbapi_connection.cursor()
    cursor.execute("PRAGMA foreign_keys=ON")
    cursor.close()

def time_ago(value):
    if not isinstance(value, datetime):
        return value

    now = datetime.utcnow()
    diff = now - value

    if diff < timedelta(seconds=60):
        return "Just now"
    elif diff < timedelta(minutes=60):
        return f"{diff.seconds // 60} minutes ago"
    elif diff < timedelta(hours=24):
        return f"{diff.seconds // 3600} hours ago"
    else:
        return f"{diff.days} days ago"


def create_app(config_class=Config):
    app = Flask(__name__)
    app.config.from_object(config_class)

    csrf.init_app(app)
    db.init_app(app)
    migrate.init_app(app, db)
    login_manager.init_app(app)
    
    login_manager.login_view = 'main.login'
    login_manager.login_message_category = 'info'

    app.jinja_env.filters.update({
        'current_year': lambda _: datetime.now().year,
        'slugify': slugify,
        'time_ago': time_ago
    })

    with app.app_context():
        from lms_app import models
        from lms_app.routes import main as main_blueprint
        
        app.register_blueprint(main_blueprint)

    return app
