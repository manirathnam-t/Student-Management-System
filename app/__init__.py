import os

from flask import Flask

from .config import Config
from .extensions import db, login_manager, bcrypt
from .routes import main
from .auth import auth


def create_app():

    app = Flask(__name__)

    # Load configuration
    app.config.from_object(Config)

    # Fix Render PostgreSQL URL if needed
    database_url = app.config["SQLALCHEMY_DATABASE_URI"]

    if database_url and database_url.startswith("postgres://"):
        app.config["SQLALCHEMY_DATABASE_URI"] = database_url.replace(
            "postgres://",
            "postgresql://",
            1
        )

    # -------------------------------
    # SQLAlchemy Engine Options
    # Helps prevent Render database
    # connection timeout issues
    # -------------------------------
    app.config["SQLALCHEMY_ENGINE_OPTIONS"] = {
        "pool_pre_ping": True,
        "pool_recycle": 300
    }

    # -------------------------------
    # Upload Folder
    # -------------------------------
    app.config["UPLOAD_FOLDER"] = os.path.join(
        app.root_path,
        "static",
        "uploads",
        "students"
    )

    # -------------------------------
    # Initialize Extensions
    # -------------------------------
    db.init_app(app)
    bcrypt.init_app(app)
    login_manager.init_app(app)

    login_manager.login_view = "auth.login"

    # -------------------------------
    # Register Blueprints
    # -------------------------------
    app.register_blueprint(main)
    app.register_blueprint(auth)

    # -------------------------------
    # Create Database Tables
    # -------------------------------
    with app.app_context():
        db.create_all()

    return app