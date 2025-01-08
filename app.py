from flask import Flask, render_template, request, redirect, url_for, flash, abort, g
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy.orm import DeclarativeBase
from flask_mail import Mail, Message
from datetime import datetime
import logging
import os

# Set up logging
logging.basicConfig(level=logging.DEBUG)
logger = logging.getLogger(__name__)

# Define base model class
class Base(DeclarativeBase):
    pass

# Initialize extensions
db = SQLAlchemy(model_class=Base)
mail = Mail()

def create_app():
    """Application factory function"""
    app = Flask(__name__)

    # Configure the app
    app.secret_key = os.environ.get("FLASK_SECRET_KEY") or "golf-tracker-secret"
    app.config["SQLALCHEMY_DATABASE_URI"] = os.environ.get("DATABASE_URL")
    app.config["SQLALCHEMY_ENGINE_OPTIONS"] = {
        "pool_recycle": 300,
        "pool_pre_ping": True,
    }

    # Configure email settings
    app.config['MAIL_SERVER'] = 'smtp.gmail.com'
    app.config['MAIL_PORT'] = 587
    app.config['MAIL_USE_TLS'] = True
    app.config['MAIL_USERNAME'] = os.environ.get('MAIL_USERNAME')
    app.config['MAIL_PASSWORD'] = os.environ.get('MAIL_PASSWORD')
    app.config['MAIL_DEFAULT_SENDER'] = os.environ.get('MAIL_DEFAULT_SENDER')

    # Initialize the extensions
    db.init_app(app)
    mail.init_app(app)

    with app.app_context():
        # Import models here to avoid circular imports
        import models
        logger.info("Creating database tables...")
        try:
            db.create_all()
            logger.info("Database tables created successfully")
        except Exception as e:
            logger.error(f"Error creating database tables: {e}")
            raise

    # Register template filters
    @app.template_filter('ordinal_date')
    def ordinal_date(dt):
        """Format date as '3rd January 2025'"""
        day = dt.day
        if 10 <= day % 100 <= 20:
            suffix = 'th'
        else:
            suffix = {1: 'st', 2: 'nd', 3: 'rd'}.get(day % 10, 'th')
        return f"{day}{suffix} {dt.strftime('%B %Y')}"

    @app.before_request
    def load_game_details():
        """Load game details for the navigation menu if in game context"""
        path_parts = request.path.split('/')
        if len(path_parts) > 2 and path_parts[1] in ['game', 'history', 'stats']:
            game_code = path_parts[2]
            from models import Game
            g.games = [Game.query.filter_by(game_code=game_code).first()]
        else:
            g.games = []

    @app.context_processor
    def inject_games():
        """Make games available in all templates"""
        return dict(games=getattr(g, 'games', []))

    # Register routes
    from views import register_routes
    register_routes(app)

    return app

# Create the application instance
app = create_app()

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000, debug=True)