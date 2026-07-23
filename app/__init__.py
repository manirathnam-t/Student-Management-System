import os
import cloudinary

from flask import Flask

from .config import Config
from .extensions import db, login_manager, bcrypt
from .routes import main
from .auth import auth


def create_app():

    app = Flask(__name__)

    # -------------------------------
    # Load Config
    # -------------------------------
    app.config.from_object(Config)

    # -------------------------------
    # Configure Cloudinary
    # -------------------------------
    cloudinary.config(
        cloud_name=app.config["CLOUDINARY_CLOUD_NAME"],
        api_key=app.config["CLOUDINARY_API_KEY"],
        api_secret=app.config["CLOUDINARY_API_SECRET"],
        secure=True
    )

    print("=" * 50)
    print("Cloud Name :", app.config.get("CLOUDINARY_CLOUD_NAME"))
    print("API Key    :", app.config.get("CLOUDINARY_API_KEY"))
    print("API Secret :", app.config.get("CLOUDINARY_API_SECRET"))
    print("=" * 50)

    # -------------------------------
    # Fix Render PostgreSQL URL
    # -------------------------------
    database_url = app.config["SQLALCHEMY_DATABASE_URI"]

    if database_url and database_url.startswith("postgres://"):
        app.config["SQLALCHEMY_DATABASE_URI"] = database_url.replace(
            "postgres://",
            "postgresql://",
            1
        )

    # -------------------------------
    # SQLAlchemy
    # -------------------------------
    app.config["SQLALCHEMY_ENGINE_OPTIONS"] = {
        "pool_pre_ping": True,
        "pool_recycle": 300
    }

    # -------------------------------
    # Local Upload Folder
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
    # Create Tables
    # -------------------------------
    with app.app_context():
        db.create_all()

    return app